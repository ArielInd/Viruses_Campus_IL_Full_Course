#!/bin/bash
# Convert HTML to PDF using macOS built-in tools
#
# This script opens the HTML file in the default browser
# Instructions for manual PDF creation will be shown

HTML_FILE=$(ls -t viruses_book_*.html | head -1)

if [ -z "$HTML_FILE" ]; then
    echo "Error: No HTML file found"
    exit 1
fi

echo "============================================"
echo "HTML to PDF Conversion"
echo "============================================"
echo ""
echo "Opening: $HTML_FILE"
echo ""
echo "To create PDF:"
echo "  1. Press Cmd+P (Print)"
echo "  2. In the print dialog, select 'Save as PDF'"
echo "  3. Choose destination and filename"
echo "  4. Click 'Save'"
echo ""
echo "Recommended settings:"
echo "  - Paper size: A4"
echo "  - Margins: Default or Minimum"
echo "  - Scale: 100% (or adjust to fit)"
echo ""

# Open HTML file in default browser
open "$HTML_FILE"

echo "✓ HTML file opened in browser"
echo ""
echo "After saving the PDF, it will include:"
echo "  - All 8 chapters with Hebrew RTL text"
echo "  - All 17 embedded scientific diagrams"
echo "  - Table of contents"
echo "  - Glossary and appendices"
