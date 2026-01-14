#!/usr/bin/env python3
"""Refactor glossary to alphabetized, standardized format"""

import re
from pathlib import Path
from collections import defaultdict

# Hebrew letter order for sorting
HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"

def get_hebrew_sort_key(term):
    """Get sorting key based on first Hebrew character"""
    for char in term:
        if char in HEBREW_LETTERS:
            return (0, HEBREW_LETTERS.index(char), term)
    # Non-Hebrew terms go at the end
    return (1, 0, term.lower())

def is_hebrew_term(term):
    """Check if term starts with a Hebrew letter"""
    for char in term:
        if char in HEBREW_LETTERS:
            return True
        elif char.isalpha():
            return False
    return False

def parse_existing_glossary(glossary_path):
    """Parse the existing markdown glossary table"""
    content = glossary_path.read_text(encoding='utf-8')
    
    # Find table rows (skip header and separator)
    pattern = r'\| \*\*(.+?)\*\* \| (.+?) \| (.+?) \|'
    
    terms = []
    for match in re.finditer(pattern, content):
        hebrew = match.group(1).strip()
        english = match.group(2).strip()
        definition = match.group(3).strip()
        
        # Skip empty or invalid entries
        if hebrew and definition:
            terms.append({
                'hebrew': hebrew,
                'english': english if english != '-' else '—',
                'definition': definition
            })
    
    return terms

def group_by_first_letter(terms):
    """Group Hebrew terms by first letter"""
    grouped = defaultdict(list)
    english_terms = []
    
    for term in terms:
        if is_hebrew_term(term['hebrew']):
            first_letter = None
            for char in term['hebrew']:
                if char in HEBREW_LETTERS:
                    first_letter = char
                    break
            if first_letter:
                grouped[first_letter].append(term)
        else:
            english_terms.append(term)
    
    # Sort within each letter group
    for letter in grouped:
        grouped[letter].sort(key=lambda x: x['hebrew'])
    
    return grouped, english_terms

def generate_glossary_markdown(hebrew_grouped, english_terms):
    """Generate the new glossary markdown"""
    output = []
    output.append("# מילון מושגים")
    output.append("")
    output.append("*מילון מונחים מקצועיים לשימוש במהלך הלימוד*")
    output.append("")
    output.append("---")
    output.append("")
    
    # Hebrew letter names for headers
    letter_names = {
        'א': 'א (Alef)', 'ב': 'ב (Bet)', 'ג': 'ג (Gimel)', 'ד': 'ד (Dalet)',
        'ה': 'ה (Heh)', 'ו': 'ו (Vav)', 'ז': 'ז (Zayin)', 'ח': 'ח (Chet)',
        'ט': 'ט (Tet)', 'י': 'י (Yod)', 'כ': 'כ (Kaf)', 'ל': 'ל (Lamed)',
        'מ': 'מ (Mem)', 'נ': 'נ (Nun)', 'ס': 'ס (Samech)', 'ע': 'ע (Ayin)',
        'פ': 'פ (Peh)', 'צ': 'צ (Tzadi)', 'ק': 'ק (Qof)', 'ר': 'ר (Resh)',
        'ש': 'ש (Shin)', 'ת': 'ת (Tav)'
    }
    
    # Output Hebrew terms grouped by letter
    for letter in HEBREW_LETTERS:
        if letter in hebrew_grouped and hebrew_grouped[letter]:
            header = letter_names.get(letter, letter)
            output.append(f"## {header}")
            output.append("")
            output.append("| מונח עברית | English | הגדרה |")
            output.append("|------------|---------|-------|")
            
            for term in hebrew_grouped[letter]:
                heb = term['hebrew']
                eng = term['english']
                defn = term['definition'][:100] + '...' if len(term['definition']) > 100 else term['definition']
                output.append(f"| **{heb}** | {eng} | {defn} |")
            
            output.append("")
    
    # English terms section
    if english_terms:
        output.append("---")
        output.append("")
        output.append("## מונחים באנגלית (English Terms)")
        output.append("")
        output.append("| Term | Hebrew | Definition |")
        output.append("|------|--------|------------|")
        
        english_terms.sort(key=lambda x: x['hebrew'].lower())
        for term in english_terms:
            eng = term['hebrew']  # These are English-first terms
            heb = term['english'] if term['english'] != '—' else '—'
            defn = term['definition'][:100] + '...' if len(term['definition']) > 100 else term['definition']
            output.append(f"| **{eng}** | {heb} | {defn} |")
        
        output.append("")
    
    return '\n'.join(output)

def main():
    glossary_path = Path("book/90_glossary.md")
    
    if not glossary_path.exists():
        print(f"❌ Glossary not found: {glossary_path}")
        return
    
    print("📖 Parsing existing glossary...")
    terms = parse_existing_glossary(glossary_path)
    print(f"   Found {len(terms)} terms")
    
    print("🔤 Grouping by Hebrew letter...")
    hebrew_grouped, english_terms = group_by_first_letter(terms)
    print(f"   Hebrew letters with terms: {len(hebrew_grouped)}")
    print(f"   English-first terms: {len(english_terms)}")
    
    print("📝 Generating new glossary...")
    new_content = generate_glossary_markdown(hebrew_grouped, english_terms)
    
    # Backup original
    backup_path = Path("book/90_glossary_backup.md")
    glossary_path.rename(backup_path)
    print(f"   Backup saved to: {backup_path}")
    
    # Write new glossary
    glossary_path.write_text(new_content, encoding='utf-8')
    
    print(f"✅ New glossary written to: {glossary_path}")
    print(f"   New size: {len(new_content) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
