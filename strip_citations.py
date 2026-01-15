#!/usr/bin/env python3
"""
strip_citations.py - Final step before EPUB build

Removes all [SRC-XXX] citations and [NEEDS SOURCE] markers from
chapter files before publication.

Usage:
    python3 strip_citations.py [book_dir]
"""

import os
import sys
import re
from pathlib import Path


def strip_citations(book_dir: str):
    """Remove all citations from chapter files."""
    chapters_dir = Path(book_dir) / "chapters"
    
    if not chapters_dir.exists():
        print(f"Error: {chapters_dir} not found")
        return
    
    total_stripped = 0
    
    for filepath in chapters_dir.glob("*.md"):
        content = filepath.read_text(encoding='utf-8')
        original_len = len(content)
        
        # Remove [SRC-XXX] citations
        content = re.sub(r'\s*\[SRC-\d{3}\]', '', content)
        
        # Remove [NEEDS SOURCE] markers
        content = re.sub(r'\s*<!-- \[NEEDS SOURCE\] -->', '', content)
        
        # Clean up double spaces
        content = re.sub(r'  +', ' ', content)
        
        if len(content) != original_len:
            filepath.write_text(content, encoding='utf-8')
            stripped = original_len - len(content)
            total_stripped += stripped
            print(f"✓ {filepath.name}: stripped {stripped} characters")
    
    print(f"\n✅ Total: {total_stripped} characters stripped from chapters")
    print("   Chapters are now ready for EPUB build.")


if __name__ == "__main__":
    book_dir = sys.argv[1] if len(sys.argv) > 1 else "book"
    strip_citations(book_dir)
