#!/bin/bash
# Convert markdown to PDF using Pandoc
# Requires: pandoc, xelatex, Hebrew fonts

pandoc "viruses_book_pdf_ready_20260115_154804.md" \
  --pdf-engine=xelatex \
  --from=markdown+emoji \
  --to=pdf \
  --output=viruses_book.pdf \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --highlight-style=tango \
  --verbose

echo "PDF generated: viruses_book.pdf"
