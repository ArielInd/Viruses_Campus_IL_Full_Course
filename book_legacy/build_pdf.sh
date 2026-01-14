#!/bin/bash
# build_pdf.sh - Build the virology ebook as PDF
# Usage: ./build_pdf.sh

set -e

BOOK_DIR="$(dirname "$0")"
cd "$BOOK_DIR"

OUTPUT_DIR="build"
OUTPUT_PDF="$OUTPUT_DIR/book.pdf"
OUTPUT_HTML="$OUTPUT_DIR/book.html"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📚 Building Virology Ebook..."
echo ""

# Check for pandoc
if ! command -v pandoc &> /dev/null; then
    echo "❌ Error: pandoc is not installed."
    echo "   Install with: brew install pandoc"
    exit 1
fi

# Build file list in correct order
FILES=(
    "00_front_matter.md"
    "chapters/01_cells.md"
    "chapters/02_macromolecules.md"
    "chapters/03_viruses.md"
    "chapters/04_diseases.md"
    "chapters/05_innate_immunity.md"
    "chapters/06_adaptive_immunity.md"
    "chapters/07_vaccines.md"
    "chapters/08_coronavirus.md"
    "chapters/09_epilogue.md"
    "90_glossary.md"
    "91_exam_review.md"
    "92_question_bank.md"
)

# Verify all files exist
echo "📋 Verifying files..."
for f in "${FILES[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "   ⚠️  Missing: $f"
    else
        echo "   ✓ $f"
    fi
done
echo ""

# Try PDF generation with xelatex (for Hebrew RTL support)
echo "📄 Attempting PDF generation with XeLaTeX..."

# Check for xelatex
if command -v xelatex &> /dev/null; then
    # Look for Hebrew-capable fonts
    FONT="DejaVu Sans"
    if fc-list | grep -qi "heebo"; then
        FONT="Heebo"
    elif fc-list | grep -qi "david"; then
        FONT="David CLM"
    fi
    
    pandoc "${FILES[@]}" \
        -o "$OUTPUT_PDF" \
        --pdf-engine=xelatex \
        -V mainfont="$FONT" \
        -V geometry:margin=1in \
        -V lang=he \
        -V dir=rtl \
        --toc \
        --toc-depth=2 \
        -M title="נגיפים, תאים וחיסונים" \
        -M author="פרופ' יונתן גרשוני" \
        2>/dev/null && {
            echo "✅ PDF created: $OUTPUT_PDF"
            PDF_SUCCESS=true
        } || {
            echo "⚠️  XeLaTeX PDF failed, trying HTML fallback..."
            PDF_SUCCESS=false
        }
else
    echo "⚠️  xelatex not found, using HTML fallback..."
    PDF_SUCCESS=false
fi

# Always generate HTML version
echo ""
echo "🌐 Generating HTML version..."
pandoc "${FILES[@]}" \
    -o "$OUTPUT_HTML" \
    --standalone \
    --toc \
    --toc-depth=2 \
    -M title="נגיפים, תאים וחיסונים" \
    -M author="פרופ' יונתן גרשוני" \
    --metadata lang=he \
    --css=style.css \
    2>/dev/null && echo "✅ HTML created: $OUTPUT_HTML" || echo "❌ HTML generation failed"

# If PDF failed, try wkhtmltopdf from HTML
if [[ "$PDF_SUCCESS" != "true" ]]; then
    if command -v wkhtmltopdf &> /dev/null; then
        echo ""
        echo "📄 Trying wkhtmltopdf..."
        wkhtmltopdf "$OUTPUT_HTML" "$OUTPUT_PDF" 2>/dev/null && {
            echo "✅ PDF created via wkhtmltopdf: $OUTPUT_PDF"
        } || {
            echo "❌ wkhtmltopdf also failed"
        }
    else
        echo ""
        echo "ℹ️  No PDF engine available. Open $OUTPUT_HTML in browser and print to PDF."
        echo "   Install options:"
        echo "   - brew install --cask mactex (for xelatex)"
        echo "   - brew install wkhtmltopdf"
    fi
fi

echo ""
echo "🎉 Build complete!"
echo ""
echo "Files created in $OUTPUT_DIR/:"
ls -lh "$OUTPUT_DIR" 2>/dev/null || echo "(no files created)"
