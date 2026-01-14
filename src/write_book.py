#!/usr/bin/env python3
import os
import json
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

CHAPTER_PLAN_FILE = Path("ops/artifacts/chapter_plan.json")
CLAIMS_FILE = Path("ops/artifacts/claims.jsonl")
CHAPTERS_DIR = Path("book/chapters")
TRACEABILITY_FILE = Path("ops/artifacts/traceability.json")

def load_claims():
    """Load all claims into a dictionary by claim_id."""
    claims = {}
    if CLAIMS_FILE.exists():
        with open(CLAIMS_FILE, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    data = json.loads(line)
                    # Assign ID consistent with plan.py
                    claim_id = f"claim_{i:05d}"
                    data["claim_id"] = claim_id
                    claims[claim_id] = data
                except:
                    pass
    return claims

def generate_chapter_content(client, chapter_plan, relevant_claims, model="gemini-2.0-flash"):
    """Generate chapter content using evidence."""
    
    # Prepare evidence text
    evidence_text = ""
    for c in relevant_claims:
        evidence_text += f"- [{c['claim_id']}] {c['text']} ({c['type']})\n"
        
    prompt = f"""
    You are writing a strict, evidence-based textbook chapter designed for EXAM PREPARATION.
    
    Chapter Title: {chapter_plan['title']}
    Chapter ID: {chapter_plan['chapter_id']}
    
    Source Evidence (CLAIMS):
    {evidence_text[:100000]}
    
    Instructions:
    1. Write a comprehensive chapter following the exact structure below.
    2. USE ONLY THE PROVIDED EVIDENCE. Do not hallucinate or use external knowledge.
    3. If the evidence is insufficient for a section, write "אין מספיק ראיות בתמלילים."
    4. Write in fluent, academic Hebrew.
    5. Maintain medical disclaimer: conceptual only, no protocols.
    6. PRIORITIZE information by exam relevance using the markers below.
    
    Priority Markers (USE THESE):
    - ✅ **חובה למבחן** — Core concepts likely to appear on exam
    - ℹ️ **רקע מעניין** — Nice context, lower exam priority
    
    Structure:
    # פרק {chapter_plan['chapter_id']}: {chapter_plan['title']}

    ## מטרות למידה
    (List 3-5 objectives derived from the evidence, each starting with פועל: להגדיר, להסביר, לתאר, להשוות)

    ## ✅ חובה למבחן – עיקרי הפרק
    (THE MOST IMPORTANT CONCEPTS - Format as bullet points, max 5-7 items. These are must-memorize facts.)
    
    ## מפת דרכים
    (Brief overview of what is covered, 2-3 sentences max)

    ## תוכן מרכזי
    (Organize into logical sub-sections using ### headers. 
    - Mark key definitions with **bold term** = definition
    - Use tables for comparisons
    - Mark exam-critical content with ✅
    - Cite claim IDs in comments, e.g. <!-- claim_001 -->)

    ## תיבה: נקודת מבט של מומחה
    (ℹ️ רקע מעניין - If evidence supports it. Brief insight.)

    ## תיבה: מעבדה כהדגמה
    (ℹ️ רקע מעניין - Conceptual only. MUST NOT include protocols/volumes/times.)

    ## טעויות נפוצות ומלכודות
    (Based on 'comparison' or 'fact' claims - format as: ❌ טעות: ... → ✓ תיקון: ...)

    ## סיכום מהיר
    (Key bullets, max 5 items. Start each with ✅ if exam-critical)

    ## מושגי מפתח
    (Format as: **מונח** — הגדרה קצרה)

    ## שאלות לתרגול
    (Generate 3 multiple choice questions based on the text. Format:
    1. שאלה?
       *   (א) אפשרות
       *   (ב) אפשרות
       *   (ג) אפשרות
       *   (ד) אפשרות
       **תשובה:** [letter])
    """
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2 # Low temperature for grounding
        )
    )
    
    return response.text

def main():
    if not CHAPTER_PLAN_FILE.exists():
        print("Chapter plan not found.")
        return
        
    client = genai.Client(api_key=API_KEY)
    
    with open(CHAPTER_PLAN_FILE, 'r', encoding='utf-8') as f:
        plans = json.load(f)
        
    claims_map = load_claims()
    print(f"Loaded {len(claims_map)} claims.")
    
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    
    traceability = {}
    
    for plan in tqdm(plans, desc="Writing Chapters"):
        chap_id = plan["chapter_id"]
        claim_ids = plan["claim_ids"]
        
        # Gather full claim objects
        relevant_claims = [claims_map[cid] for cid in claim_ids if cid in claims_map]
        
        if not relevant_claims:
            print(f"Skipping chapter {chap_id} - no claims.")
            continue
            
        # Generate
        try:
            content = generate_chapter_content(client, plan, relevant_claims)
            
            # Post-processing: Add sources (Disabled per user request)
            # transcripts = plan.get("transcripts", [])
            # content += "\n\n## מקורות לפרק\n"
            # for t in transcripts:
            #     content += f"- {t}\n"
            
            # Save
            out_path = CHAPTERS_DIR / f"{chap_id}_{plan['title'].replace(' ', '_').replace('/', '-')}.md"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Traceability (Conceptual)
            traceability[chap_id] = {
                "claims_used": claim_ids,
                "transcripts": plan.get("transcripts", [])
            }
            
        except Exception as e:
            print(f"Failed to write chapter {chap_id}: {e}")
            
    # Save traceability
    with open(TRACEABILITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(traceability, f, indent=2)
        
    print("Book generation complete.")

if __name__ == "__main__":
    main()
