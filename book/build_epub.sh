#!/bin/bash
# Build EPUB from Markdown using Pandoc for Hebrew

cd "$(dirname "$0")"

mkdir -p build

OUTPUT="build/book.epub"

# Check dependencies
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed."
    echo "Please install pandoc (e.g. 'brew install pandoc')."
    exit 1
fi

# List files in order
FILES="00_front_matter.md 01_study_guide.md"
FILES="$FILES $(ls chapters/*.md | sort)"
FILES="$FILES 89_quick_reference.md 90_glossary.md 91_exam_review.md 92_question_bank.md"

echo "Building EPUB from:"
echo $FILES

pandoc $FILES \
    -o "$OUTPUT" \
    --css=rtl_style.css \
    --metadata title="וירוסים: איך מנצחים אותם?" \
    --metadata author="Campus IL (AI Generated)" \
    --metadata language="he" \
    -V dir=rtl \
    --toc \
    --toc-depth=2

if [ $? -eq 0 ]; then
    echo "EPUB generated successfully at $OUTPUT"
else
    echo "EPUB generation failed."
    exit 1
fi
