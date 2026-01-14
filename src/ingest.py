#!/usr/bin/env python3
import json
import re
from pathlib import Path
from tqdm import tqdm

# Configuration
TRANSCRIPT_DIR = Path("/Users/arielindenbaum/Downloads/Viruses_Campus_IL_Full_Course/course_transcripts")
OUTPUT_FILE = Path("ops/artifacts/chunks.jsonl")
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 300

def normalize_text(text):
    """Normalize whitespace and remove non-printable characters."""
    # Replace multiple whitespaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, size, overlap):
    """Yield chunks of text with overlap."""
    if len(text) <= size:
        yield text, 0, len(text)
        return
    
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        
        # If we are not at the end, try to find a sentence break or space to cut nicely
        if end < len(text):
            # Look for a period or space in the last 10% of the chunk
            lookback = int(size * 0.1)
            # Find last space
            last_space = text.rfind(' ', end - lookback, end)
            if last_space != -1:
                end = last_space + 1 # Include the space
        
        yield text[start:end], start, end
        
        if end == len(text):
            break
            
        start = end - overlap
        # ensuring we progress
        if start >= end:
            start = end

def main():
    if not TRANSCRIPT_DIR.exists():
        print(f"Error: Transcript directory not found: {TRANSCRIPT_DIR}")
        return

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(list(TRANSCRIPT_DIR.rglob("*.txt")))
    print(f"Found {len(files)} transcript files.")
    
    total_chunks = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        for file_path in tqdm(files, desc="Ingesting"):
            path = Path(file_path)
            basename = path.stem
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue

            normalized = normalize_text(raw_text)
            if not normalized:
                continue

            chunk_idx = 1
            for chunk_content, start, end in chunk_text(normalized, CHUNK_SIZE, CHUNK_OVERLAP):
                chunk_id = f"{basename}_{chunk_idx:04d}"
                
                record = {
                    "chunk_id": chunk_id,
                    "source_file": path.name,
                    "text": chunk_content,
                    "offset_start": start,
                    "offset_end": end,
                    "original_length": len(raw_text)
                }
                
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                chunk_idx += 1
                total_chunks += 1

    print(f"Ingestion complete. Written {total_chunks} chunks to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
