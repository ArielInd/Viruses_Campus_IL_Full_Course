#!/usr/bin/env python3
"""
Create Valid EPUB3 for Virology Book

This script generates a properly formatted EPUB3 file that works with Apple Books
and other ebook readers, with full Hebrew RTL support.

Usage:
    python3 create_valid_epub.py
"""

import os
import re
from pathlib import Path
from datetime import datetime
import markdown2
from ebooklib import epub

# Configuration
BOOK_DIR = Path("book")
COMPILED_DIR = BOOK_DIR / "compiled"
IMAGES_DIR = BOOK_DIR / "images"
OUTPUT_DIR = COMPILED_DIR


def find_latest_markdown():
    """Find the most recent compiled markdown file."""
    md_files = list(COMPILED_DIR.glob("viruses_book_complete_*.md"))
    if not md_files:
        raise FileNotFoundError("No compiled markdown files found")
    md_files.sort(reverse=True)
    return md_files[0]


def create_epub(markdown_file: Path, output_dir: Path, images_dir: Path):
    """Generate properly formatted EPUB3 from markdown."""

    print(f"\n{'='*60}")
    print("Creating Valid EPUB3 for Apple Books")
    print(f"{'='*60}")
    print(f"Source: {markdown_file.name}")

    # Read markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Remove YAML frontmatter if present
    if markdown_content.startswith('---'):
        parts = markdown_content.split('---', 2)
        if len(parts) >= 3:
            markdown_content = parts[2].strip()

    # Create EPUB book
    print("  → Creating EPUB3 structure...")
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('viruses-campus-il-2026')
    book.set_title('וירוסים וחיסון')
    book.set_language('he')
    book.add_author('Viruses Campus IL')

    # Add RTL CSS
    rtl_css = """
    @namespace epub "http://www.idpf.org/2007/ops";

    body {
        font-family: Arial, "David", "Noto Sans Hebrew", sans-serif;
        direction: rtl;
        text-align: right;
        line-height: 1.8;
        margin: 1em;
        unicode-bidi: embed;
    }

    h1, h2, h3, h4, h5, h6 {
        text-align: right;
        font-weight: bold;
        direction: rtl;
    }

    h1 {
        font-size: 2em;
        color: #1a1a1a;
        margin: 1.5em 0 0.8em 0;
    }

    h2 {
        font-size: 1.7em;
        color: #2c3e50;
        margin: 1.3em 0 0.7em 0;
    }

    h3 {
        font-size: 1.4em;
        color: #34495e;
        margin: 1.2em 0 0.6em 0;
    }

    p {
        text-align: justify;
        margin: 1em 0;
        direction: rtl;
    }

    ul, ol {
        text-align: right;
        direction: rtl;
        margin: 1em 0;
        padding-right: 2em;
    }

    li {
        text-align: right;
        direction: rtl;
    }

    img {
        max-width: 100%;
        height: auto;
        margin: 1em auto;
        display: block;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        direction: rtl;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: right;
    }

    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }

    blockquote {
        margin: 1em 2em;
        padding: 0.5em 1em;
        border-right: 4px solid #ccc;
        direction: rtl;
    }

    code {
        font-family: monospace;
        background-color: #f4f4f4;
        padding: 2px 5px;
    }

    pre {
        background-color: #f4f4f4;
        padding: 1em;
        overflow-x: auto;
    }
    """

    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=rtl_css
    )
    book.add_item(nav_css)

    # Split content by page breaks and process chapters
    print("  → Processing chapters...")
    chapters_raw = re.split(r'<!-- Page Break -->', markdown_content)

    epub_chapters = []
    spine_items = ['nav']
    chapter_num = 1

    for chapter_text in chapters_raw:
        chapter_text = chapter_text.strip()
        if not chapter_text or len(chapter_text) < 50:
            continue

        # Convert markdown to HTML
        chapter_html = markdown2.markdown(
            chapter_text,
            extras=['tables', 'fenced-code-blocks', 'header-ids']
        )

        # Fix image paths
        chapter_html = re.sub(
            r'src="images/([^"]+)"',
            r'src="../images/\1"',
            chapter_html
        )

        # Extract chapter title
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', chapter_html)
        if not title_match:
            title_match = re.search(r'<h2[^>]*>([^<]+)</h2>', chapter_html)

        chapter_title = title_match.group(1) if title_match else f"פרק {chapter_num}"

        # Clean up title (remove HTML entities)
        chapter_title = re.sub(r'<[^>]+>', '', chapter_title)

        # Create chapter
        chapter_file = f'chapter_{chapter_num:02d}.xhtml'
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'text/{chapter_file}',
            lang='he'
        )
        
        # ebooklib expects just the body content, it wraps it automatically
        # Add RTL styling inline
        body_content = f'''<div dir="rtl" style="direction: rtl; text-align: right;">
{chapter_html}
</div>'''
        chapter.set_content(body_content)
        chapter.add_link(href='../style/nav.css', rel='stylesheet', type='text/css')

        book.add_item(chapter)
        epub_chapters.append(chapter)
        spine_items.append(chapter)

        chapter_num += 1

    print(f"     ✓ Created {len(epub_chapters)} chapters")

    # Add images
    print("  → Embedding images...")
    if images_dir.exists():
        img_count = 0
        for img_file in sorted(images_dir.glob("*.png")):
            if img_file.name == "image_manifest.json":
                continue

            with open(img_file, 'rb') as f:
                img_content = f.read()

            epub_img = epub.EpubItem(
                uid=f"img_{img_file.stem}",
                file_name=f"images/{img_file.name}",
                media_type="image/png",
                content=img_content
            )
            book.add_item(epub_img)
            img_count += 1

        print(f"     ✓ Embedded {img_count} images")

    # Create table of contents
    book.toc = tuple(epub_chapters)

    # Add navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = spine_items

    # Write EPUB
    print("  → Writing EPUB3 file...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    epub_path = output_dir / f"viruses_book_valid_{timestamp}.epub"

    epub.write_epub(str(epub_path), book, {})

    size_kb = epub_path.stat().st_size / 1024
    print(f"\n✓ Valid EPUB3 created: {epub_path.name}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Chapters: {len(epub_chapters)}")
    print(f"\n  Compatible with:")
    print(f"    - Apple Books (macOS, iOS)")
    print(f"    - Calibre")
    print(f"    - Adobe Digital Editions")
    print(f"    - Most ebook readers")

    return epub_path


def main():
    """Main conversion function."""

    print("\n" + "="*60)
    print("Valid EPUB3 Generator for Apple Books")
    print("="*60)

    # Find latest markdown file
    try:
        markdown_file = find_latest_markdown()
        print(f"\nInput: {markdown_file}")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return

    # Convert to EPUB
    try:
        epub_path = create_epub(markdown_file, OUTPUT_DIR, IMAGES_DIR)
        print("\n" + "="*60)
        print("Conversion Complete!")
        print("="*60)
        print(f"\nTo test:")
        print(f"  open {epub_path}")
    except Exception as e:
        print(f"\n✗ EPUB conversion failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
