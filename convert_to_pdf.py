#!/usr/bin/env python3
"""
Convert Hebrew Virology Ebook to PDF

This script converts the markdown ebook to a professional PDF using pandoc with:
- Right-to-left Hebrew text support
- XeLaTeX for proper Hebrew rendering
- Custom styling and formatting
- Table of contents
- Chapter breaks
"""

import os
import subprocess
import sys
from pathlib import Path
import json


def check_dependencies():
    """Check if required tools are installed."""
    required = ["pandoc"]
    missing = []

    for tool in required:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"✓ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
            print(f"✗ {tool} is NOT installed")

    # Check for either xelatex OR Chrome
    xelatex_installed = False
    try:
        subprocess.run(["xelatex", "--version"], capture_output=True, check=True)
        xelatex_installed = True
        print("✓ xelatex is installed")
    except:
        print("✗ xelatex is NOT installed")

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_installed = os.path.exists(chrome_path)
    if chrome_installed:
        print("✓ Google Chrome is installed (can be used as PDF engine)")
    else:
        print("✗ Google Chrome is NOT found at expected path")

    if missing or (not xelatex_installed and not chrome_installed):
        print("\n⚠️  Missing critical dependencies for PDF generation:")
        if not xelatex_installed and not chrome_installed:
            print("  Either 'xelatex' or 'Google Chrome' is required for PDF conversion.")
        
        print("\nInstall with:")
        if sys.platform == "darwin":  # macOS
            print("  brew install pandoc basictex")
            print("  # OR ensure Google Chrome is in /Applications/")
        
        return False

    return True


def load_manifest(book_dir: Path) -> dict:
    """Load book manifest."""
    manifest_path = book_dir / "manifest.json"

    if not manifest_path.exists():
        print(f"✗ Manifest not found: {manifest_path}")
        return None

    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_chapters(book_dir: Path, manifest: dict) -> list:
    """Collect chapter files in order."""
    chapters_dir = book_dir / "chapters"
    chapters = []

    # 1. Front matter (00_*.md)
    front_matter = list(book_dir.glob("00_*.md"))
    if front_matter:
        chapters.extend(sorted(front_matter))
        for f in front_matter:
            print(f"✓ Added front matter: {f.name}")
    else:
        # Try exact
        fm = book_dir / "00_front_matter.md"
        if fm.exists():
            chapters.append(fm)
            print(f"✓ Added front matter: {fm.name}")

    # 2. Main chapters from chapters/ directory (sorted)
    # The manifest IDs often don't match the complex filenames, 
    # so we rely on the filesystem sorting which uses the numeric prefixes.
    if chapters_dir.exists():
        ch_files = sorted(chapters_dir.glob("*.md"))
        if ch_files:
            chapters.extend(ch_files)
            for f in ch_files:
                print(f"✓ Added chapter: {f.name}")
        else:
            print("⚠️  No .md files found in chapters/ directory")
    else:
        print(f"⚠️  Chapters directory not found: {chapters_dir}")

    # 3. Back matter (89_*, 90_*, etc.)
    # We collect them from the book_dir and sort them
    back_matter_patterns = ["89_*.md", "90_*.md", "91_*.md", "92_*.md"]
    back_matter = []
    for pattern in back_matter_patterns:
        back_matter.extend(list(book_dir.glob(pattern)))
    
    if back_matter:
        for f in sorted(back_matter):
            if f not in chapters:
                chapters.append(f)
                print(f"✓ Added back matter: {f.name}")

    return chapters


def create_metadata_file(book_dir: Path, manifest: dict) -> Path:
    """Create YAML metadata file for pandoc."""
    metadata_path = book_dir / "metadata.yaml"

    title = manifest.get("title", "נגיפים וירולוגיה") if manifest else "נגיפים וירולוגיה"
    subtitle = manifest.get("subtitle", "קורס מקוון Campus IL") if manifest else "קורס מקוון Campus IL"
    author = manifest.get("author", "Campus IL + Claude") if manifest else "Campus IL + Claude"

    metadata = f"""---
title: "{title}"
subtitle: "{subtitle}"
author: "{author}"
date: "\\today"
lang: he
dir: rtl
fontsize: 12pt
documentclass: book
geometry: margin=2.5cm
mainfont: "David CLM"
sansfont: "Simple CLM"
monofont: "Miriam Mono CLM"
toc: true
toc-depth: 2
numbersections: true
links-as-notes: false
colorlinks: true
linkcolor: blue
urlcolor: blue
---
"""

    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(metadata)

    print(f"✓ Created metadata: {metadata_path}")
    return metadata_path


def convert_to_pdf(book_dir: Path, output_path: Path, chapters: list, metadata_path: Path):
    """Convert markdown chapters to PDF using pandoc."""

    print(f"\n📚 Converting {len(chapters)} files to PDF...")

    # Step 1: Check if xelatex is available for direct PDF generation
    xelatex_available = False
    try:
        subprocess.run(["xelatex", "--version"], capture_output=True, check=True)
        xelatex_available = True
    except:
        pass

    if xelatex_available:
        cmd = [
            "pandoc",
            str(metadata_path),
            *[str(ch) for ch in chapters],
            "-o", str(output_path),
            "--pdf-engine=xelatex",
            "--toc",
            "--number-sections",
            "--highlight-style=tango",
            "-V", "documentclass=book",
            "-V", "papersize=a4",
            "-V", "geometry:margin=2.5cm",
            "-V", "lang=he",
            "-V", "dir=rtl"
        ]
        print(f"\nRunning: {' '.join(cmd[:3])} with xelatex...")
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"\n✅ PDF created successfully via xelatex: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            print("\n❌ xelatex conversion failed, falling back to Chrome...")
            print(e.stderr)

    # Step 2: Fallback to Chrome Headless via intermediate HTML
    print("\n🌐 Using Google Chrome for PDF conversion...")
    html_temp = book_dir / "book_temp.html"
    css_path = book_dir / "rtl_style.css"
    
    # Generate Standalone HTML
    html_cmd = [
        "pandoc",
        str(metadata_path),
        *[str(ch) for ch in chapters],
        "-o", str(html_temp),
        "--standalone",
        "--toc",
        "--number-sections",
        "-V", "lang=he",
        "-V", "dir=rtl"
    ]
    if css_path.exists():
        html_cmd.extend(["--css", str(css_path)])

    try:
        subprocess.run(html_cmd, check=True)
        
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if not os.path.exists(chrome_path):
             # Try common linux paths if needed, but we are on mac
             chrome_path = "google-chrome" # assume in path

        chrome_cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={output_path}",
            str(html_temp)
        ]
        
        subprocess.run(chrome_cmd, check=True, capture_output=True)
        print(f"\n✅ PDF created successfully via Chrome: {output_path}")
        
        if html_temp.exists():
            html_temp.unlink()
            
        return True
    except Exception as e:
        print(f"\n❌ PDF conversion failed: {e}")
        return False


def main():
    """Main conversion process."""
    print("="*70)
    print("HEBREW VIROLOGY EBOOK - PDF CONVERSION")
    print("="*70)
    print()

    # Setup paths
    base_dir = Path(__file__).parent
    book_dir = base_dir / "book"
    output_path = base_dir / "Viruses_Ebook_Hebrew.pdf"

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        return 1

    print()

    # Load manifest
    print("Loading book manifest...")
    manifest = load_manifest(book_dir)

    if not manifest:
        print("⚠️  No manifest found, will use all chapters from directory")

    print()

    # Collect chapters
    print("Collecting chapters...")
    chapters = collect_chapters(book_dir, manifest)

    if not chapters:
        print("❌ No chapters found!")
        return 1

    print(f"\n✓ Found {len(chapters)} files")
    print()

    # Create metadata
    print("Creating metadata...")
    metadata_path = create_metadata_file(book_dir, manifest)
    print()

    # Convert to PDF
    success = convert_to_pdf(book_dir, output_path, chapters, metadata_path)

    # Cleanup
    if metadata_path.exists():
        metadata_path.unlink()
        print("✓ Cleaned up temporary files")

    if success:
        print("\n🎉 Done! Your ebook is ready:")
        print(f"   {output_path}")
        print("\nOpen with:")
        print(f"   open {output_path}  # macOS")
        print(f"   xdg-open {output_path}  # Linux")
        return 0
    else:
        print("\n❌ PDF conversion failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
