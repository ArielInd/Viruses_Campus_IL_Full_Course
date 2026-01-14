#!/bin/bash
# Build EPUB from markdown sources
# Requires: pandoc (https://pandoc.org/)

set -e

BOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOOK_DIR"

OUTPUT="ebook.epub"

echo "Building EPUB..."

pandoc \
  -o "$OUTPUT" \
  --metadata title="נגיפים, תאים וחיסונים" \
  --metadata author="מבוסס על הקורס של פרופ' ג'ון גרשוני" \
  --metadata lang=he \
  --metadata dir=rtl \
  --css=style.css \
  --toc \
  --toc-depth=2 \
  --epub-chapter-level=1 \
  00_front_matter.md \
  chapters/01_introduction_cells.md \
  chapters/02_macromolecules.md \
  chapters/03_viruses_structure.md \
  chapters/04_viral_diseases.md \
  chapters/05_innate_immunity.md \
  chapters/06_adaptive_immunity.md \
  chapters/07_vaccines.md \
  chapters/08_coronavirus.md \
  chapters/09_epilogue.md \
  90_glossary.md \
  91_exam_review.md \
  92_question_bank.md

echo "Created: $OUTPUT"
echo "Done!"
