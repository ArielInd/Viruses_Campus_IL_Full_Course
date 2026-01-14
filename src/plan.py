#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Configuration
TRANSCRIPT_DIR = Path("/Users/arielindenbaum/Downloads/Viruses_Campus_IL_Full_Course/course_transcripts")
CLAIMS_FILE = Path("ops/artifacts/claims.jsonl")
MANIFEST_FILE = Path("book/manifest.json")
OUTLINE_FILE = Path("book/01_outline.md")
CHAPTER_PLAN_FILE = Path("ops/artifacts/chapter_plan.json")

def get_transcripts():
    """Get sorted list of transcript files."""
    files = sorted(list(TRANSCRIPT_DIR.rglob("*.txt")))
    return files

def infer_chapter_structure(files):
    """Group files into chapters based on directory or filename."""
    chapters = {}
    
    for f in files:
        # Strategy: Use parent directory name as chapter or first part of filename
        # Example: "02_Virology/01_Intro.txt" -> Chapter 02
        
        parent = f.parent.name
        # Try to extract number from parent
        match = re.match(r"(\d+)", parent)
        if match:
            chap_num = int(match.group(1))
            chap_title = parent
        else:
            # Try filename
            match = re.match(r"(\d+)", f.name)
            if match:
                chap_num = int(match.group(1))
                # Heuristic: use filename as title if parent has no number
                chap_title = f.stem
            else:
                chap_num = 99 # Misc
                chap_title = "Misc"
        
        if chap_num not in chapters:
            chapters[chap_num] = {
                "chapter_id": f"{chap_num:02d}",
                "title": chap_title,
                "transcripts": []
            }
        
        chapters[chap_num]["transcripts"].append(str(f.relative_to(TRANSCRIPT_DIR)))
        
    # Sort by chapter number
    return [chapters[k] for k in sorted(chapters.keys())]

def load_claims_map():
    """Map chunk_id to list of claim_ids."""
    # This is a bit complex because claims need IDs. 
    # Current extract.py outputs claims with evidence_chunk_id.
    # We can group claims by evidence_chunk_id.
    
    claims_by_chunk = {}
    if CLAIMS_FILE.exists():
        with open(CLAIMS_FILE, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    data = json.loads(line)
                    evidence = data.get("evidence_chunk_id")
                    if evidence:
                        if evidence not in claims_by_chunk:
                            claims_by_chunk[evidence] = []
                        # Assign a temporary claim ID if not present
                        # In a real DB we'd have stable IDs.
                        # Here we use line number or hash.
                        claim_id = f"claim_{i:05d}"
                        data["claim_id"] = claim_id
                        claims_by_chunk[evidence].append(data)
                except:
                    pass
    return claims_by_chunk

def generate_outline(manifest):
    """Generate Markdown outline."""
    md = "# Book Outline\n\n"
    for chap in manifest:
        md += f"## Chapter {chap['chapter_id']}: {chap['title']}\n"
        md += "### Sources\n"
        for src in chap['transcripts']:
            md += f"- `{src}`\n"
        md += "\n"
    return md

def main():
    files = get_transcripts()
    print(f"Found {len(files)} transcripts.")
    
    manifest_data = infer_chapter_structure(files)
    
    # Write Manifest
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump({"chapters": manifest_data}, f, indent=2, ensure_ascii=False)
    print(f"Wrote manifest to {MANIFEST_FILE}")
    
    # Write Outline
    outline = generate_outline(manifest_data)
    with open(OUTLINE_FILE, 'w', encoding='utf-8') as f:
        f.write(outline)
    print(f"Wrote outline to {OUTLINE_FILE}")
    
    # Create Chapter Plan (joining claims)
    claims_map = load_claims_map()
    
    chapter_plans = []
    for chap in manifest_data:
        chap_claims = []
        for src in chap['transcripts']:
            # Find chunks for this transcript
            # Chunk ID convention: basename_0001
            basename = Path(src).stem
            # We need to find all chunks that start with this basename
            # This is inefficient if we iterate all keys.
            # Better: filtered list.
            
            # Since we processed files, we know the basename.
            # But the chunk ID adds _0001.
            # Let's search keys in claims_map that contain basename.
            # optimization: claims_map keys are chunk_ids.
            
            for chunk_id, claims in claims_map.items():
                if chunk_id.startswith(basename + "_"):
                    for c in claims:
                        chap_claims.append(c["claim_id"])
                        
        chapter_plans.append({
            "chapter_id": chap["chapter_id"],
            "title": chap["title"],
            "claim_ids": chap_claims,
            "transcripts": chap["transcripts"]
        })

    with open(CHAPTER_PLAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(chapter_plans, f, indent=2, ensure_ascii=False)
    print(f"Wrote chapter plan to {CHAPTER_PLAN_FILE} (Claims found: {sum(len(c['claim_ids']) for c in chapter_plans)})")

if __name__ == "__main__":
    main()
