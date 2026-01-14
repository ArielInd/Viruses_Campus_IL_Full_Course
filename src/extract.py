#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # Fallback to key provided in chat if not in env
    API_KEY = "AIzaSyAs2g85eFx98EjcFFPy931zGUy_VBWCa60"

# Configuration
CHUNKS_FILE = Path("ops/artifacts/chunks.jsonl")
CLAIMS_FILE = Path("ops/artifacts/claims.jsonl")
ENTITIES_FILE = Path("ops/artifacts/entities.jsonl")
LOG_FILE = Path("ops/logs/extraction.jsonl")

# Schema Definitions
class Claim(BaseModel):
    text: str = Field(..., description="The factual claim in Hebrew.")
    type: str = Field(..., enum=["definition", "mechanism", "comparison", "example", "fact"], description="Type of the claim.")
    confidence: str = Field(..., enum=["high", "low"], description="Confidence in the extraction.")

class Entity(BaseModel):
    term_hebrew: str = Field(..., description="Canonical Hebrew term.")
    term_english: Optional[str] = Field(None, description="English term if mentioned or implied.")
    definition: str = Field(..., description="Short definition based on the text.")

class ChunkExtraction(BaseModel):
    claims: List[Claim]
    entities: List[Entity]

def get_processed_chunk_ids():
    """Load IDs of chunks already processed."""
    ids = set()
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("status") == "success":
                        ids.add(data.get("chunk_id"))
                except:
                    pass
    return ids

def process_chunk(client, chunk, model="gemini-2.0-flash"):
    """Call Gemini to extract info from a chunk."""
    text = chunk["text"]
    
    prompt = f"""
    You are an expert virology research assistant. Analyze the following Hebrew transcript text.
    Extract:
    1. Atomic factual claims (definitions, mechanisms, comparisons, facts).
       - MUST be grounded in the text.
    2. Terminology entities (Hebrew term, English equivalent, definition).
    
    Transcript Text:
    {text}
    """
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChunkExtraction,
                temperature=0.0
            )
        )
        
        return response.parsed
        
    except Exception as e:
        print(f"Error processing chunk {chunk['chunk_id']}: {e}")
        raise

def main():
    if not CHUNKS_FILE.exists():
        print(f"Chunks file not found: {CHUNKS_FILE}")
        return

    # Initialize client
    client = genai.Client(api_key=API_KEY)
    
    # Load chunks
    chunks = []
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
            
    processed_ids = get_processed_chunk_ids()
    to_process = [c for c in chunks if c["chunk_id"] not in processed_ids]
    
    print(f"Total chunks: {len(chunks)}. Processed: {len(processed_ids)}. To process: {len(to_process)}")
    
    # Ensure dirs
    CLAIMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CLAIMS_FILE, 'a', encoding='utf-8') as claims_f, \
         open(ENTITIES_FILE, 'a', encoding='utf-8') as entities_f, \
         open(LOG_FILE, 'a', encoding='utf-8') as log_f:
         
        for chunk in tqdm(to_process, desc="Extracting"):
            chunk_id = chunk["chunk_id"]
            
            retries = 3
            wait = 2
            result = None
            
            start_time = time.time()
            
            for attempt in range(retries):
                try:
                    result = process_chunk(client, chunk)
                    break
                except Exception as e:
                    # simplistic backoff
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        print(f"Rate limit hit. Waiting {wait}s...")
                        time.sleep(wait)
                        wait *= 2
                    else:
                        print(f"Retry {attempt+1}/{retries} for {chunk_id}: {e}")
                        time.sleep(1)
            
            duration = time.time() - start_time
            
            if result:
                # Save claims
                for claim in result.claims:
                    record = claim.model_dump()
                    record["evidence_chunk_id"] = chunk_id
                    claims_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    
                # Save entities
                for entity in result.entities:
                    record = entity.model_dump()
                    record["evidence_chunk_id"] = chunk_id
                    entities_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                
                # Log success
                log_f.write(json.dumps({
                    "chunk_id": chunk_id,
                    "status": "success",
                    "duration": duration,
                    "claims_count": len(result.claims),
                    "entities_count": len(result.entities)
                }) + "\n")
                claims_f.flush()
                entities_f.flush()
                log_f.flush()
                
            else:
                # Log failure
                log_f.write(json.dumps({
                    "chunk_id": chunk_id,
                    "status": "failed",
                    "duration": duration
                }) + "\n")

    print("Extraction complete.")

if __name__ == "__main__":
    main()
