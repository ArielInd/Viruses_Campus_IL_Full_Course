#!/usr/bin/env python3
"""
Convert Virology Book to PDF and EPUB

This script converts the compiled markdown book to both PDF and EPUB formats
with proper Hebrew RTL support and embedded images.

Usage:
    python3 convert_book_to_pdf_epub.py
"""

import os
import re
from pathlib import Path
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
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

    # Sort by timestamp in filename
    md_files.sort(reverse=True)
    return md_files[0]


def prepare_html_for_pdf(markdown_content: str, images_dir: Path) -> str:
    """Convert markdown to HTML with RTL support and embedded images."""

    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['extra', 'nl2br', 'sane_lists', 'toc']
    )

    # Fix image paths to be absolute
    def fix_image_path(match):
        img_path = match.group(1)
        if img_path.startswith("images/"):
            abs_path = (images_dir / img_path.replace("images/", "")).absolute()
            return f'<img src="{abs_path}"'
        return match.group(0)

    html_content = re.sub(r'<img src="([^"]+)"', fix_image_path, html_content)

    # Wrap in full HTML document with RTL CSS
    full_html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>וירוסים וחיסון: מבוא מקיף לווירולוגיה ואימונולוגיה</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 2.5cm;

            @top-center {{
                content: "וירוסים וחיסון";
                font-size: 10pt;
                color: #666;
            }}

            @bottom-center {{
                content: counter(page);
                font-size: 10pt;
            }}
        }}

        body {{
            font-family: "Arial", "David", "Noto Sans Hebrew", sans-serif;
            direction: rtl;
            text-align: right;
            line-height: 1.6;
            font-size: 11pt;
            color: #333;
        }}

        h1 {{
            font-size: 24pt;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            page-break-after: avoid;
            color: #1a1a1a;
        }}

        h2 {{
            font-size: 18pt;
            font-weight: bold;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
            page-break-after: avoid;
            color: #2c2c2c;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            page-break-after: avoid;
            color: #404040;
        }}

        p {{
            margin: 0.5em 0;
            text-align: justify;
        }}

        ul, ol {{
            margin: 0.5em 0;
            padding-right: 2em;
        }}

        li {{
            margin: 0.3em 0;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            page-break-inside: avoid;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: right;
        }}

        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}

        blockquote {{
            border-right: 3px solid #ccc;
            margin: 1em 0;
            padding: 0.5em 1em;
            background-color: #f9f9f9;
        }}

        code {{
            font-family: "Courier New", monospace;
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }}

        pre {{
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            direction: ltr;
            text-align: left;
        }}

        .page-break {{
            page-break-after: always;
        }}

        /* English text inside Hebrew context */
        .en {{
            direction: ltr;
            display: inline-block;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    return full_html


def create_pdf(markdown_file: Path, output_dir: Path, images_dir: Path):
    """Generate PDF from markdown with WeasyPrint."""

    print(f"\n{'='*60}")
    print("Converting to PDF")
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

    # Convert to HTML
    print("  → Converting markdown to HTML...")
    html_content = prepare_html_for_pdf(markdown_content, images_dir)

    # Generate PDF
    print("  → Generating PDF (this may take a few minutes)...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = output_dir / f"viruses_book_{timestamp}.pdf"

    HTML(string=html_content, base_url=str(images_dir)).write_pdf(
        pdf_path,
        stylesheets=None,
        presentational_hints=True
    )

    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"\n✓ PDF created: {pdf_path}")
    print(f"  Size: {size_mb:.1f} MB")

    return pdf_path


def create_epub(markdown_file: Path, output_dir: Path, images_dir: Path):
    """Generate EPUB from markdown with ebooklib."""

    print(f"\n{'='*60}")
    print("Converting to EPUB")
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
    print("  → Creating EPUB structure...")
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('viruses-book-campus-il-2026')
    book.set_title('וירוסים וחיסון: מבוא מקיף לווירולוגיה ואימונולוגיה')
    book.set_language('he')
    book.add_author('Viruses Campus IL Full Course')

    # Add RTL CSS
    rtl_css = epub.EpubItem(
        uid="style_rtl",
        file_name="style/rtl.css",
        media_type="text/css",
        content="""
        body {
            font-family: Arial, "David", "Noto Sans Hebrew", sans-serif;
            direction: rtl;
            text-align: right;
            line-height: 1.6;
        }
        h1, h2, h3, h4, h5, h6 {
            text-align: right;
        }
        p {
            text-align: justify;
        }
        ul, ol {
            text-align: right;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        """
    )
    book.add_item(rtl_css)

    # Split content into chapters
    print("  → Processing chapters...")
    chapters_content = re.split(r'<!-- Page Break -->', markdown_content)

    epub_chapters = []
    toc = []

    for i, chapter_text in enumerate(chapters_content):
        if not chapter_text.strip():
            continue

        # Convert markdown to HTML
        chapter_html = markdown.markdown(
            chapter_text,
            extensions=['extra', 'nl2br', 'sane_lists']
        )

        # Extract chapter title
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', chapter_html)
        chapter_title = title_match.group(1) if title_match else f"פרק {i+1}"

        # Create chapter
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter_{i+1:02d}.xhtml',
            lang='he',
            direction='rtl'
        )
        chapter.content = f'<html dir="rtl"><body>{chapter_html}</body></html>'
        chapter.add_item(rtl_css)

        book.add_item(chapter)
        epub_chapters.append(chapter)
        toc.append(chapter)

    # Add images
    print("  → Embedding images...")
    if images_dir.exists():
        for img_file in images_dir.glob("*.png"):
            with open(img_file, 'rb') as f:
                img_content = f.read()

            epub_img = epub.EpubItem(
                uid=f"image_{img_file.stem}",
                file_name=f"images/{img_file.name}",
                media_type="image/png",
                content=img_content
            )
            book.add_item(epub_img)

    # Define Table of Contents
    book.toc = toc

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define reading order
    book.spine = ['nav'] + epub_chapters

    # Write EPUB
    print("  → Writing EPUB file...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    epub_path = output_dir / f"viruses_book_{timestamp}.epub"

    epub.write_epub(epub_path, book)

    size_kb = epub_path.stat().st_size / 1024
    print(f"\n✓ EPUB created: {epub_path}")
    print(f"  Size: {size_kb:.1f} KB")

    return epub_path


def main():
    """Main conversion function."""

    print("\n" + "="*60)
    print("Virology Book Converter: Markdown → PDF & EPUB")
    print("="*60)

    # Find latest markdown file
    try:
        markdown_file = find_latest_markdown()
        print(f"\nInput: {markdown_file}")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return

    # Convert to PDF
    try:
        pdf_path = create_pdf(markdown_file, OUTPUT_DIR, IMAGES_DIR)
    except Exception as e:
        print(f"\n✗ PDF conversion failed: {e}")
        import traceback
        traceback.print_exc()

    # Convert to EPUB
    try:
        epub_path = create_epub(markdown_file, OUTPUT_DIR, IMAGES_DIR)
    except Exception as e:
        print(f"\n✗ EPUB conversion failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("Conversion Complete!")
    print("="*60)
    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
