# נגיפים, תאים וחיסונים – ספר לימוד

## Viruses, Cells, and Vaccines – Study Guide

ספר לימוד מקיף בעברית, מבוסס על קורס Campus IL.

---

## Quick Start

**Build the book:**

```bash
./book/build_pdf.sh
```

**Output:**

- `book/build/book.pdf` – PDF version
- `book/build/book.html` – HTML version

---

## Project Structure

```
├── book/
│   ├── 00_front_matter.md      # Title, disclaimer, TOC
│   ├── chapters/               # 9 chapter files
│   │   ├── 01_cells.md
│   │   ├── 02_macromolecules.md
│   │   ├── 03_viruses.md
│   │   ├── 04_diseases.md
│   │   ├── 05_innate_immunity.md
│   │   ├── 06_adaptive_immunity.md
│   │   ├── 07_vaccines.md
│   │   ├── 08_coronavirus.md
│   │   └── 09_epilogue.md
│   ├── 90_glossary.md          # Terminology glossary
│   ├── 91_exam_review.md       # High-yield summary
│   ├── 92_question_bank.md     # Practice questions
│   ├── style_guide.md          # Writing conventions
│   ├── manifest.json           # Chapter→transcript mapping
│   └── build_pdf.sh            # Build script
│
├── ops/
│   ├── artifacts/
│   │   └── traceability.json   # Source audit trail
│   ├── reports/
│   │   ├── inventory.md        # Agent output inventory
│   │   ├── consistency_report.md
│   │   └── todos.md
│   └── terminology.yml         # Term definitions
│
└── course_transcripts/         # Original source files
```

---

## Requirements

**For HTML only:**

```bash
brew install pandoc
```

**For PDF with Hebrew RTL support:**

```bash
brew install --cask mactex
```

*or*

```bash
brew install wkhtmltopdf
```

---

## Building Without Dependencies

If pandoc/latex aren't available:

1. Open `book/build/book.html` in browser
2. Print → Save as PDF

---

## Source Verification

All content is derived from the original transcripts in `course_transcripts/`.

See:

- `book/manifest.json` – chapter-to-transcript mapping
- `ops/artifacts/traceability.json` – full audit trail

---

## License

Educational use only. Based on Campus IL course materials.
