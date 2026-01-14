#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
import yaml

ENTITIES_FILE = Path("ops/artifacts/entities.jsonl")
TERMINOLOGY_FILE = Path("ops/artifacts/terminology.yml")
GLOSSARY_FILE = Path("book/90_glossary.md")

def main():
    if not ENTITIES_FILE.exists():
        print("Entities file not found.")
        return
        
    entities = []
    with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entities.append(json.loads(line))
            except:
                pass
                
    print(f"Loaded {len(entities)} entity mentions.")
    
    # Consolidate by Hebrew term
    # normalization: lowercase, strip
    
    consolidated = {}
    
    for e in entities:
        term = e.get("term_hebrew", "").strip()
        if not term:
            continue
        
        norm_term = term # In Hebrew usually casing doesn't matter much but helpful for consistency
        
        if norm_term not in consolidated:
            consolidated[norm_term] = {
                "term_hebrew": term,
                "term_english": set(),
                "definitions": []
            }
        
        eng = e.get("term_english")
        if eng:
            consolidated[norm_term]["term_english"].add(eng)
        
        definition = e.get("definition")
        if definition:
            consolidated[norm_term]["definitions"].append(definition)
            
    # Select best definition (longest? most frequent?)
    # For now: longest
    
    final_terms = []
    for norm, data in consolidated.items():
        best_def = max(data["definitions"], key=len) if data["definitions"] else ""
        best_eng = next(iter(data["term_english"])) if data["term_english"] else ""
        
        final_terms.append({
            "hebrew": data["term_hebrew"],
            "english": best_eng,
            "definition": best_def
        })
        
    final_terms.sort(key=lambda x: x["hebrew"])
    
    # Save YAML
    with open(TERMINOLOGY_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(final_terms, f, allow_unicode=True)
    print(f"Wrote {len(final_terms)} terms to {TERMINOLOGY_FILE}")
    
    # Write Glossary
    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        f.write("# מילון מושגים (Glossary)\n\n")
        f.write("| מונח | אנגלית | הגדרה |\n")
        f.write("|------|--------|-------|\n")
        for t in final_terms:
            eng = t["english"] if t["english"] else "-"
            f.write(f"| **{t['hebrew']}** | {eng} | {t['definition']} |\n")
            
    print(f"Wrote glossary to {GLOSSARY_FILE}")

if __name__ == "__main__":
    main()
