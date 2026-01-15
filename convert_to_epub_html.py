#!/usr/bin/env python3
"""
Convert Virology Book to EPUB and HTML

This script converts the compiled markdown book to EPUB and a standalone HTML file
with proper Hebrew RTL support and embedded images.

The HTML can be opened in a browser and saved as PDF using the browser's print function.

Usage:
    python3 convert_to_epub_html.py
"""

import os
import re
import base64
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

    # Sort by timestamp in filename
    md_files.sort(reverse=True)
    return md_files[0]


def embed_images_as_base64(html_content: str, images_dir: Path) -> str:
    """Convert image references to embedded base64 data URIs."""

    def replace_img(match):
        img_src = match.group(1)

        # Extract filename from path
        if img_src.startswith("images/"):
            img_filename = img_src.replace("images/", "")
            img_path = images_dir / img_filename

            if img_path.exists():
                try:
                    with open(img_path, 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode('utf-8')
                    return f'<img src="data:image/png;base64,{img_data}"'
                except Exception as e:
                    print(f"  Warning: Failed to embed {img_filename}: {e}")

        return match.group(0)

    return re.sub(r'<img src="([^"]+)"', replace_img, html_content)


def create_html(markdown_file: Path, output_dir: Path, images_dir: Path):
    """Generate standalone HTML with embedded images."""

    print(f"\n{'='*60}")
    print("Converting to Standalone HTML")
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

    # Convert markdown to HTML
    print("  → Converting markdown to HTML...")
    html_body = markdown2.markdown(
        markdown_content,
        extras=['tables', 'fenced-code-blocks', 'header-ids', 'toc']
    )

    # Embed images as base64
    print("  → Embedding images as base64...")
    html_body = embed_images_as_base64(html_body, images_dir)

    # Create full HTML document with print-friendly CSS
    full_html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>וירוסים וחיסון: מבוא מקיף לווירולוגיה ואימונולוגיה</title>
    <style>
        /* Screen styles */
        body {{
            font-family: Arial, "David", "Noto Sans Hebrew", "Segoe UI", sans-serif;
            direction: rtl;
            text-align: right;
            line-height: 1.8;
            font-size: 16px;
            color: #2c3e50;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}

        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            font-size: 2.5em;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            color: #1a1a1a;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        h2 {{
            font-size: 2em;
            font-weight: bold;
            margin-top: 1.3em;
            margin-bottom: 0.7em;
            color: #2c3e50;
        }}

        h3 {{
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
            color: #34495e;
        }}

        h4 {{
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            color: #555;
        }}

        p {{
            margin: 1em 0;
            text-align: justify;
        }}

        ul, ol {{
            margin: 1em 0;
            padding-right: 2em;
        }}

        li {{
            margin: 0.5em 0;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 2em auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: right;
        }}

        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        blockquote {{
            border-right: 4px solid #3498db;
            margin: 1.5em 0;
            padding: 1em 1.5em;
            background-color: #ecf0f1;
            border-radius: 4px;
        }}

        code {{
            font-family: "Courier New", "Consolas", monospace;
            background-color: #f4f4f4;
            padding: 3px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 1.5em;
            border-radius: 6px;
            overflow-x: auto;
            direction: ltr;
            text-align: left;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
        }}

        strong {{
            font-weight: bold;
            color: #2c3e50;
        }}

        em {{
            font-style: italic;
            color: #555;
        }}

        /* Print styles */
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 0;
                font-size: 11pt;
            }}

            .container {{
                box-shadow: none;
                padding: 0;
            }}

            h1 {{
                page-break-after: avoid;
                font-size: 20pt;
            }}

            h2 {{
                page-break-after: avoid;
                font-size: 16pt;
            }}

            h3 {{
                page-break-after: avoid;
                font-size: 14pt;
            }}

            img {{
                page-break-inside: avoid;
                max-width: 100%;
            }}

            table {{
                page-break-inside: avoid;
            }}

            @page {{
                size: A4;
                margin: 2cm;

                @top-center {{
                    content: "וירוסים וחיסון";
                    font-size: 10pt;
                    color: #666;
                }}

                @bottom-center {{
                    content: "עמוד " counter(page);
                    font-size: 10pt;
                }}
            }}
        }}

        /* Instructions banner */
        .print-instructions {{
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}

        @media print {{
            .print-instructions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-instructions">
        <strong>💡 להמרה ל-PDF:</strong> השתמש בתפריט הדפסה של הדפדפן (Ctrl/Cmd+P) ובחר "שמור כ-PDF"
    </div>
    <div class="container">
{html_body}
    </div>
</body>
</html>"""

    # Save HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = output_dir / f"viruses_book_{timestamp}.html"

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    size_kb = html_path.stat().st_size / 1024
    print(f"\n✓ HTML created: {html_path}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"\n  📄 To create PDF:")
    print(f"     1. Open {html_path.name} in your browser")
    print(f"     2. Press Cmd+P (Mac) or Ctrl+P (Windows)")
    print(f"     3. Select 'Save as PDF' as destination")
    print(f"     4. Adjust margins and scale if needed")

    return html_path


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
    book.add_metadata('DC', 'description', 'ספר לימוד מקיף בנושא ווירולוגיה ואימונולוגיה בעברית')

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
            line-height: 1.8;
            margin: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            text-align: right;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }
        h1 { font-size: 2em; color: #1a1a1a; }
        h2 { font-size: 1.7em; color: #2c3e50; }
        h3 { font-size: 1.4em; color: #34495e; }
        p {
            text-align: justify;
            margin: 1em 0;
        }
        ul, ol {
            text-align: right;
            margin: 1em 0;
            padding-right: 2em;
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
        """
    )
    book.add_item(rtl_css)

    # Split content into chapters by page breaks
    print("  → Processing chapters...")
    chapters_content = re.split(r'<!-- Page Break -->', markdown_content)

    epub_chapters = []
    toc = []
    chapter_num = 1

    for chapter_text in chapters_content:
        if not chapter_text.strip():
            continue

        # Convert markdown to HTML
        chapter_html = markdown2.markdown(
            chapter_text,
            extras=['tables', 'fenced-code-blocks', 'header-ids']
        )

        # Fix image references for EPUB
        def fix_img_src(match):
            src = match.group(1)
            if src.startswith("images/"):
                return f'<img src="{src}"'
            return match.group(0)

        chapter_html = re.sub(r'<img src="([^"]+)"', fix_img_src, chapter_html)

        # Extract chapter title
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', chapter_html)
        if title_match:
            chapter_title = title_match.group(1)
        else:
            # Try h2
            title_match = re.search(r'<h2[^>]*>([^<]+)</h2>', chapter_html)
            chapter_title = title_match.group(1) if title_match else f"פרק {chapter_num}"

        # Create chapter
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter_{chapter_num:02d}.xhtml',
            lang='he',
            direction='rtl'
        )
        chapter.content = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" dir="rtl" lang="he">
<head>
    <title>{chapter_title}</title>
    <link href="../style/rtl.css" rel="stylesheet" type="text/css"/>
</head>
<body>
{chapter_html}
</body>
</html>"""
        chapter.add_item(rtl_css)

        book.add_item(chapter)
        epub_chapters.append(chapter)
        toc.append(chapter)

        chapter_num += 1

    # Add images
    print("  → Embedding images...")
    if images_dir.exists():
        img_count = 0
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
            img_count += 1

        print(f"     ✓ Embedded {img_count} images")

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
    print(f"  Chapters: {len(epub_chapters)}")

    return epub_path


def main():
    """Main conversion function."""

    print("\n" + "="*60)
    print("Virology Book Converter: Markdown → HTML & EPUB")
    print("="*60)

    # Find latest markdown file
    try:
        markdown_file = find_latest_markdown()
        print(f"\nInput: {markdown_file}")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return

    # Convert to HTML
    try:
        html_path = create_html(markdown_file, OUTPUT_DIR, IMAGES_DIR)
    except Exception as e:
        print(f"\n✗ HTML conversion failed: {e}")
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
    print(f"\n💡 Note: For PDF, open the HTML file in a browser")
    print(f"   and use Print → Save as PDF")


if __name__ == "__main__":
    main()
