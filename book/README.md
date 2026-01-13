# Viruses: How to Beat Them (Hebrew Ebook)

This directory contains the source Markdown files for the ebook "נגיפים וכיצד לנצח אותם", based on the Campus IL course by Prof. Jonathan Gershoni.

## Structure

* `manifest.json`: Maps original transcript files to their logical units.
* `00_front_matter.md`: Title page and introduction.
* `01_outline.md`: Table of Contents.
* `chapters/`: The core content, divided into 8 chapters.
* `90_glossary.md`: Definitions of key terms.
* `91_exam_review.md`: High-yield summary for exam prep.
* `92_question_bank.md`: Practice questions.

## How to Build (Requires Pandoc)

If you have [Pandoc](https://pandoc.org/) installed, you can generate an EPUB or PDF book.

### 1. Make the script executable

```bash
chmod +x build_book.sh
```

### 2. Run the build script

```bash
./build_book.sh
```

This will create `viruses_book.epub` and `viruses_book.html` in the current directory.

## Editing

To edit the content, simply modify the `.md` files in the `chapters` folder. The files use standard Markdown syntax.
