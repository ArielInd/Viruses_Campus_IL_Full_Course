#!/bin/bash

OUTPUT_EPUB="viruses_book.epub"
OUTPUT_HTML="viruses_book.html"

# List of files in order
FILES="book/00_front_matter.md book/01_outline.md book/chapters/01_chapter_intro_cell.md book/chapters/02_chapter_macromolecules.md book/chapters/03_chapter_viruses_intro.md book/chapters/04_chapter_human_diseases.md book/chapters/05_chapter_innate_immunity.md book/chapters/06_chapter_adaptive_immunity.md book/chapters/07_chapter_vaccines.md book/chapters/08_chapter_coronavirus.md book/chapters/09_epilogue.md book/90_glossary.md book/91_exam_review.md book/92_question_bank.md"

echo "Building EPUB..."
pandoc $FILES -o $OUTPUT_EPUB \
  --metadata title="נגיפים וכיצד לנצח אותם" \
  --metadata author="פרופ' ג'ון גרשוני (עריכה: Conductor)" \
  --metadata lang=he \
  --toc

echo "Building HTML (for preview)..."
pandoc $FILES -o $OUTPUT_HTML \
  --metadata title="נגיפים וכיצד לנצח אותם" \
  --metadata lang=he \
  --toc --standalone

echo "Done! Created $OUTPUT_EPUB and $OUTPUT_HTML"