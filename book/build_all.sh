#!/bin/bash
# Master build script for Viruses Book

cd "$(dirname "$0")"

echo "=== Building EPUB ==="
bash build_epub.sh

echo ""
echo "=== Building PDF ==="
bash build_pdf.sh

echo ""
echo "=== Build Summary ==="
ls -lh build/book.epub build/book.pdf
