#!/usr/bin/env python3
"""
Convert Hebrew Virology Ebook to HTML

Creates a single-page HTML ebook with:
- Right-to-left Hebrew text support
- Professional styling
- Table of contents with navigation
- Print-friendly CSS (can print to PDF from browser)
"""

import json
from pathlib import Path
import re


def load_manifest(book_dir: Path) -> dict:
    """Load book manifest."""
    manifest_path = book_dir / "manifest.json"

    if not manifest_path.exists():
        return {}

    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_chapters(book_dir: Path) -> list:
    """Collect chapter files in order."""
    chapters_dir = book_dir / "chapters"
    chapters = []

    # Front matter
    front_matter = book_dir / "00_front_matter.md"
    if front_matter.exists():
        chapters.append(("front", front_matter))

    # Main chapters
    for ch_file in sorted(chapters_dir.glob("*.md")):
        chapters.append(("chapter", ch_file))

    # Back matter
    for bm_file in ["90_glossary.md", "91_exam_review.md", "92_question_bank.md"]:
        bm_path = book_dir / bm_file
        if bm_path.exists():
            chapters.append(("back", bm_path))

    return chapters


def markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML (basic implementation)."""
    html = md_content

    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # Lists
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap lists
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Paragraphs
    lines = html.split('\n')
    in_list = False
    result = []

    for line in lines:
        if line.strip().startswith('<'):
            result.append(line)
        elif line.strip():
            if not in_list:
                result.append(f'<p>{line}</p>')
            else:
                result.append(line)
        else:
            result.append('')

    return '\n'.join(result)


def create_html(book_dir: Path, output_path: Path, chapters: list, manifest: dict):
    """Create HTML ebook."""
    title = manifest.get("title", "נגיפים וירולוגיה")
    subtitle = manifest.get("subtitle", "קורס מקוון Campus IL")

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Assistant', 'Arial Hebrew', Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            direction: rtl;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}

        header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 3px solid #2c3e50;
            margin-bottom: 40px;
        }}

        h1.title {{
            font-size: 48px;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .subtitle {{
            font-size: 24px;
            color: #7f8c8d;
        }}

        nav {{
            background: #ecf0f1;
            padding: 20px;
            margin-bottom: 40px;
            border-radius: 8px;
        }}

        nav h2 {{
            margin-bottom: 15px;
            color: #2c3e50;
        }}

        nav ul {{
            list-style: none;
        }}

        nav li {{
            margin: 8px 0;
        }}

        nav a {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.3s;
        }}

        nav a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}

        .chapter {{
            margin: 60px 0;
            page-break-before: always;
        }}

        h1 {{
            font-size: 36px;
            color: #2c3e50;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}

        h2 {{
            font-size: 28px;
            color: #34495e;
            margin: 25px 0 15px 0;
        }}

        h3 {{
            font-size: 22px;
            color: #7f8c8d;
            margin: 20px 0 12px 0;
        }}

        h4 {{
            font-size: 18px;
            color: #95a5a6;
            margin: 15px 0 10px 0;
        }}

        p {{
            margin: 15px 0;
            text-align: justify;
        }}

        ul, ol {{
            margin: 15px 0 15px 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        strong {{
            color: #2c3e50;
            font-weight: 700;
        }}

        em {{
            color: #7f8c8d;
        }}

        code {{
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        blockquote {{
            border-right: 4px solid #3498db;
            padding-right: 20px;
            margin: 20px 0;
            color: #7f8c8d;
            font-style: italic;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: right;
        }}

        th {{
            background: #3498db;
            color: white;
            font-weight: 700;
        }}

        tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        @media print {{
            body {{
                background: white;
            }}

            .container {{
                box-shadow: none;
                max-width: 100%;
                padding: 20px;
            }}

            nav {{
                display: none;
            }}

            .chapter {{
                page-break-before: always;
            }}

            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}

        @page {{
            size: A4;
            margin: 2cm;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="title">{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </header>

        <nav id="toc">
            <h2>תוכן עניינים</h2>
            <ul>
"""

    # Build TOC
    for idx, (section_type, ch_path) in enumerate(chapters):
        ch_id = f"chapter-{idx}"
        with open(ch_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            ch_title = first_line.replace('#', '').strip()

        html += f'                <li><a href="#{ch_id}">{ch_title}</a></li>\n'

    html += """            </ul>
        </nav>
"""

    # Add chapters
    for idx, (section_type, ch_path) in enumerate(chapters):
        print(f"✓ Processing: {ch_path.name}")

        ch_id = f"chapter-{idx}"

        with open(ch_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert markdown to HTML (basic)
        html_content = markdown_to_html(content)

        html += f'        <div id="{ch_id}" class="chapter">\n'
        html += f'            {html_content}\n'
        html += '        </div>\n\n'

    html += """    </div>
</body>
</html>"""

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ HTML created: {output_path}")
    print(f"📄 Size: {output_path.stat().st_size / 1024:.2f} KB")
    print("\n💡 To convert to PDF:")
    print(f"   1. Open in browser: open {output_path}")
    print("   2. Print (Cmd+P / Ctrl+P)")
    print("   3. Save as PDF")


def main():
    """Main conversion process."""
    print("="*70)
    print("HEBREW VIROLOGY EBOOK - HTML CONVERSION")
    print("="*70)
    print()

    # Setup paths
    base_dir = Path(__file__).parent
    book_dir = base_dir / "book"
    output_path = base_dir / "Viruses_Ebook_Hebrew.html"

    # Load manifest
    print("Loading book manifest...")
    manifest = load_manifest(book_dir)
    print()

    # Collect chapters
    print("Collecting chapters...")
    chapters = collect_chapters(book_dir)
    print(f"✓ Found {len(chapters)} files\n")

    # Create HTML
    print("Converting to HTML...")
    create_html(book_dir, output_path, chapters, manifest)

    print("\n🎉 Done! Your ebook is ready:")
    print(f"   {output_path}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
