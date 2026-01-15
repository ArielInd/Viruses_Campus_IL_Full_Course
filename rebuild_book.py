#!/usr/bin/env python3
"""
Book Rebuild Script: Integrate Enhanced Chapters with Generated Images

This script:
1. Collects all enhanced final chapter files (01-08_chapter.md)
2. Replaces image placeholders with actual image references
3. Compiles into complete book formats (single MD, PDF-ready)
4. Generates table of contents with proper linking

Usage:
    python rebuild_book.py --format markdown    # Single MD file
    python rebuild_book.py --format all         # MD + metadata for PDF conversion
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class BookRebuilder:
    """Rebuild enhanced book with integrated images."""

    def __init__(self, book_dir: str, output_dir: str):
        self.book_dir = Path(book_dir)
        self.chapters_dir = self.book_dir / "chapters"
        self.images_dir = self.book_dir / "images"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Chapter order
        self.chapter_files = [
            "00_cover.md",
            "01_chapter.md",
            "02_chapter.md",
            "03_chapter.md",
            "04_chapter.md",
            "05_chapter.md",
            "06_chapter.md",
            "07_chapter.md",
            "08_chapter.md",
            "90_glossary.md",
            "91_exam_review.md",
            "92_question_bank.md"
        ]

    def read_chapter(self, filename: str) -> str:
        """Read chapter content."""
        # Try chapters directory for chapter files (01-09_chapter.md)
        if filename.endswith("_chapter.md"):
            chapter_path = self.chapters_dir / filename
        # Try book directory for cover and appendices (00_, 90_, 91_, 92_)
        else:
            chapter_path = self.book_dir / filename

        if not chapter_path.exists():
            print(f"  Warning: {filename} not found, skipping")
            return ""

        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"  ✓ Loaded: {filename} ({len(content):,} chars)")
        return content

    def replace_image_placeholders(self, content: str) -> Tuple[str, int]:
        """
        Replace image placeholders with actual image markdown.

        Supports two formats:
        1. **[הצעה לאיור 5.1: Title]** with *תיאור האיור: ...*
        2. **[איור X.Y: Title. Description...]**

        After:  **איור X.Y: Title**
                ![Title](images/fig_X_Y.png)
        """
        replacements = 0

        # Pattern 1: **[הצעה לאיור X.Y: Title]** with description
        pattern1 = r'\*\*\[הצעה לאיור (\d+)\.(\d+): ([^\]]+)\]\*\*\s*\n\*תיאור האיור: ([^*]+)\*'

        # Pattern 2: **[איור X.Y: Full description with title and description]**
        pattern2 = r'\*\*\[איור (\d+)\.(\d+): ([^\]]+)\]\*\*'

        def replace_func1(match):
            """Handle pattern 1: **[הצעה לאיור X.Y: Title]** with description"""
            nonlocal replacements
            chapter_num = match.group(1)
            fig_num = match.group(2)
            title = match.group(3)
            description = match.group(4).strip()

            # Generate figure ID (e.g., fig_5_1)
            fig_id = f"fig_{chapter_num}_{fig_num}"
            image_path = f"images/{fig_id}.png"

            # Check if image exists
            image_exists = (self.images_dir / f"{fig_id}.png").exists()
            replacements += 1

            # Build replacement
            if image_exists:
                replacement = f"""**איור {chapter_num}.{fig_num}: {title}**

![{title}]({image_path})

*תיאור: {description}*"""
            else:
                replacement = f"""**איור {chapter_num}.{fig_num}: {title}** *(תמונה בהכנה)*

*תיאור: {description}*

<!-- Image placeholder: {fig_id}.png -->"""

            return replacement

        def replace_func2(match):
            """Handle pattern 2: **[איור X.Y: Full description]**"""
            nonlocal replacements
            chapter_num = match.group(1)
            fig_num = match.group(2)
            full_text = match.group(3)

            # Extract title (first sentence or first 100 chars)
            title_match = re.match(r'^([^.]+)', full_text)
            title = title_match.group(1) if title_match else full_text[:100]

            # Generate figure ID (e.g., fig_2_1)
            fig_id = f"fig_{chapter_num}_{fig_num}"
            image_path = f"images/{fig_id}.png"

            # Check if image exists
            image_exists = (self.images_dir / f"{fig_id}.png").exists()
            replacements += 1

            # Build replacement
            if image_exists:
                replacement = f"""**איור {chapter_num}.{fig_num}: {title}**

![{title}]({image_path})"""
            else:
                replacement = f"""**איור {chapter_num}.{fig_num}: {title}** *(תמונה בהכנה)*

<!-- Image placeholder: {fig_id}.png -->"""

            return replacement

        # Apply both patterns
        updated_content = re.sub(pattern1, replace_func1, content)
        updated_content = re.sub(pattern2, replace_func2, updated_content)

        return updated_content, replacements

    def generate_toc(self, chapters_content: List[Tuple[str, str]]) -> str:
        """Generate table of contents from chapter headings."""

        toc = ["# תוכן עניינים\n"]

        for filename, content in chapters_content:
            # Skip cover
            if filename == "00_cover.md":
                continue

            # Extract main heading
            heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if heading_match:
                heading = heading_match.group(1).strip()

                # Create anchor (GitHub-style)
                anchor = heading.lower()
                anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
                anchor = re.sub(r'[-\s]+', '-', anchor)   # Replace spaces with hyphens

                # Determine chapter number
                if "פרק" in heading:
                    chapter_num_match = re.search(r'\d+', heading)
                    if chapter_num_match:
                        chapter_num = chapter_num_match.group()
                        toc.append(f"- [פרק {chapter_num}: {heading}](#{anchor})")
                elif "מילון" in heading or "glossary" in filename:
                    toc.append(f"- [נספח א': {heading}](#{anchor})")
                elif "בחינה" in heading or "exam" in filename:
                    toc.append(f"- [נספח ב': {heading}](#{anchor})")
                elif "שאלות" in heading or "question" in filename:
                    toc.append(f"- [נספח ג': {heading}](#{anchor})")

        toc.append("\n---\n")
        return "\n".join(toc)

    def add_metadata_header(self) -> str:
        """Add YAML frontmatter for Pandoc PDF conversion."""

        metadata = f"""---
title: "וירוסים וחיסון: מבוא מקיף לווירולוגיה ואימונולוגיה"
subtitle: "ספר לימוד אקדמי - מהדורה ראשונה"
author: "Multi-Agent AI Pipeline (Gemini 2.5 Pro)"
date: "{datetime.now().strftime('%Y-%m-%d')}"
lang: he
dir: rtl
documentclass: book
geometry: "a4paper,margin=2.5cm"
fontsize: 12pt
mainfont: "David CLM"
colorlinks: true
toc: true
toc-depth: 2
numbersections: true
---

"""
        return metadata

    def compile_markdown(self, include_metadata: bool = False) -> str:
        """Compile all chapters into single markdown file."""

        print("\n" + "="*60)
        print("Compiling Book from Enhanced Chapters")
        print("="*60)

        compiled_content = []
        total_replacements = 0

        # Add metadata if requested
        if include_metadata:
            compiled_content.append(self.add_metadata_header())

        # Load and process each chapter
        chapters_data = []
        for filename in self.chapter_files:
            content = self.read_chapter(filename)
            if content:
                # Replace image placeholders
                if filename.endswith("_chapter.md"):
                    updated_content, replacements = self.replace_image_placeholders(content)
                    total_replacements += replacements
                    if replacements > 0:
                        print(f"    → Replaced {replacements} image placeholder(s)")
                else:
                    updated_content = content

                chapters_data.append((filename, updated_content))
                compiled_content.append(updated_content)
                compiled_content.append("\n\n<!-- Page Break -->\n<div style=\"page-break-after: always;\"></div>\n\n")

        # Generate TOC and insert after cover
        if len(chapters_data) > 0:
            toc = self.generate_toc(chapters_data)
            # Insert TOC after cover (index 1)
            compiled_content.insert(2, toc)

        print(f"\n{'='*60}")
        print(f"Compilation Summary")
        print(f"{'='*60}")
        print(f"Chapters processed: {len(chapters_data)}")
        print(f"Image placeholders replaced: {total_replacements}")
        print(f"Total content length: {sum(len(c) for c in compiled_content):,} characters")

        return "\n".join(compiled_content)

    def save_output(self, content: str, format_type: str):
        """Save compiled book."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == "markdown":
            output_file = self.output_dir / f"viruses_book_complete_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✓ Markdown saved: {output_file}")
            print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

        elif format_type == "pdf-ready":
            # Save with metadata for Pandoc
            output_file = self.output_dir / f"viruses_book_pdf_ready_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✓ PDF-ready markdown saved: {output_file}")
            print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

            # Create conversion script
            conversion_script = self.output_dir / "convert_to_pdf.sh"
            with open(conversion_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Convert markdown to PDF using Pandoc
# Requires: pandoc, xelatex, Hebrew fonts

pandoc "{output_file.name}" \\
  --pdf-engine=xelatex \\
  --from=markdown+emoji \\
  --to=pdf \\
  --output=viruses_book.pdf \\
  --toc \\
  --toc-depth=2 \\
  --number-sections \\
  --highlight-style=tango \\
  --verbose

echo "PDF generated: viruses_book.pdf"
""")
            conversion_script.chmod(0o755)
            print(f"\n✓ Conversion script: {conversion_script}")
            print(f"  Run: cd {self.output_dir} && ./convert_to_pdf.sh")

        return output_file

    def generate_image_report(self):
        """Generate report on image status."""

        manifest_path = self.images_dir / "image_manifest.json"

        if not manifest_path.exists():
            print("\n⚠ No image manifest found. Run generate_book_images.py first.")
            return

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        print(f"\n{'='*60}")
        print("Image Generation Report")
        print(f"{'='*60}")

        successful = [img for img in manifest if img.get("success")]
        failed = [img for img in manifest if not img.get("success")]

        print(f"Total images: {len(manifest)}")
        print(f"✓ Generated: {len(successful)}")
        print(f"✗ Failed: {len(failed)}")

        if failed:
            print(f"\nFailed images:")
            for img in failed:
                print(f"  - {img['id']}: {img['title']}")

        print(f"\nImages directory: {self.images_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Rebuild Viruses Ebook with enhanced chapters")
    parser.add_argument(
        "--format",
        choices=["markdown", "pdf-ready", "all"],
        default="markdown",
        help="Output format(s)"
    )
    parser.add_argument(
        "--book-dir",
        type=str,
        default="book",
        help="Book directory (default: book/)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="book/compiled",
        help="Output directory (default: book/compiled/)"
    )

    args = parser.parse_args()

    # Initialize rebuilder
    rebuilder = BookRebuilder(
        book_dir=args.book_dir,
        output_dir=args.output_dir
    )

    # Check image status
    rebuilder.generate_image_report()

    # Compile book
    if args.format == "all":
        # Markdown version (no metadata)
        content_md = rebuilder.compile_markdown(include_metadata=False)
        rebuilder.save_output(content_md, "markdown")

        # PDF-ready version (with metadata)
        content_pdf = rebuilder.compile_markdown(include_metadata=True)
        rebuilder.save_output(content_pdf, "pdf-ready")
    else:
        include_meta = (args.format == "pdf-ready")
        content = rebuilder.compile_markdown(include_metadata=include_meta)
        rebuilder.save_output(content, args.format)

    print(f"\n{'='*60}")
    print("Book Rebuild Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
