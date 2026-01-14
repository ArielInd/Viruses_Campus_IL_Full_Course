#!/bin/bash
# Build PDF from Markdown using Pandoc and Chrome Headless fallback for Hebrew

cd "$(dirname "$0")"

mkdir -p build

OUTPUT="build/book.pdf"
HTML_TEMP="build/book_temp.html"

# Check dependencies
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed."
    exit 1
fi

# List files in order (matching build_epub.sh)
FILES="00_front_matter.md 01_study_guide.md"
FILES="$FILES $(ls chapters/*.md | sort)"
FILES="$FILES 89_quick_reference.md 90_glossary.md 91_exam_review.md 92_question_bank.md"

echo "Building PDF/HTML from:"
echo $FILES

# Step 1: Generate HTML with proper RTL CSS
echo "Generating intermediate HTML..."
pandoc $FILES \
    -o "$HTML_TEMP" \
    --standalone \
    --css=rtl_style.css \
    --metadata title="וירוסים: איך מנצחים אותם?" \
    --metadata language="he" \
    -V dir=rtl \
    --toc \
    --toc-depth=2

# Step 2: Convert to PDF using xelatex if available, else Chrome
if command -v xelatex &> /dev/null; then
    echo "Using xelatex for direct PDF generation..."
    pandoc $FILES \
        -o "$OUTPUT" \
        --pdf-engine=xelatex \
        -V mainfont="Arial" \
        -V dir=rtl \
        -V lang=he \
        --toc \
        --toc-depth=2
else
    echo "xelatex not found. Using Google Chrome for PDF conversion..."
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    if [ -f "$CHROME_PATH" ]; then
        "$CHROME_PATH" --headless --disable-gpu --print-to-pdf="$OUTPUT" "$HTML_TEMP"
        if [ $? -eq 0 ]; then
            echo "PDF generated successfully via Chrome at $OUTPUT"
            # Cleanup temp HTML if desired, but keeping it for debug for now
            # rm "$HTML_TEMP"
        else
            echo "Chrome PDF conversion failed."
            exit 1
        fi
    else
        echo "Error: Google Chrome not found at $CHROME_PATH"
        echo "Please install Chrome or xelatex."
        exit 1
    fi
fi

echo "Process complete."
