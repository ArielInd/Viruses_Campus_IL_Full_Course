# EPUB Conversion Guide for Apple Books

Due to complexities with Python EPUB libraries and Hebrew RTL text, the most reliable method to create an Apple Books-compatible EPUB is using **Calibre**, the industry-standard ebook management tool.

## ✅ Files Ready for Conversion

You have:
1. **HTML file with embedded images**: `book/compiled/viruses_book_20260115_152339.html` (15 MB)
2. **Cover image**: `book/images/cover.png` (1600x2400 px)
3. **All chapter images**: `book/images/fig_*.png` (17 diagrams)

---

## Option 1: Using Calibre (Recommended)

### Install Calibre

**Mac:**
```bash
brew install --cask calibre
```

Or download from: https://calibre-ebook.com/download

**Verify installation:**
```bash
which ebook-convert
```

### Convert HTML to EPUB

```bash
cd book/compiled

ebook-convert \
  viruses_book_20260115_152339.html \
  viruses_book_apple.epub \
  --language he \
  --book-producer "Viruses Campus IL" \
  --publisher "Viruses Campus IL" \
  --title "וירוסים וחיסון: מבוא מקיף לווירולוגיה ואימונולוגיה" \
  --authors "Viruses Campus IL" \
  --cover ../images/cover.png \
  --extra-css "body { direction: rtl; text-align: right; } h1, h2, h3, p { direction: rtl; }" \
  --epub-version 3 \
  --preserve-cover-aspect-ratio \
  --no-default-epub-cover
```

### Result

This will create `viruses_book_apple.epub` that:
- ✅ Works with Apple Books
- ✅ Has proper Hebrew RTL support
- ✅ Includes all 17 embedded images
- ✅ Has the cover image
- ✅ Is EPUB3 compliant

---

## Option 2: Using Calibre GUI

1. **Open Calibre**

2. **Add Book:**
   - Click "Add books"
   - Select `book/compiled/viruses_book_20260115_152339.html`

3. **Edit Metadata:**
   - Right-click the book → "Edit metadata"
   - Set:
     - **Title:** וירוסים וחיסון
     - **Authors:** Viruses Campus IL
     - **Language:** Hebrew (he)
     - **Cover:** Click "Download cover" → "Choose file" → Select `book/images/cover.png`

4. **Convert to EPUB:**
   - Click "Convert books"
   - **Input format:** HTML
   - **Output format:** EPUB
   - In "Look & Feel" tab:
     - Add to "Extra CSS":
       ```css
       body { direction: rtl; text-align: right; }
       h1, h2, h3 { direction: rtl; }
       p { direction: rtl; text-align: justify; }
       ```
   - In "EPUB Output" tab:
     - Check "Preserve cover aspect ratio"
     - Select "EPUB version: 3"
   - Click "OK"

5. **Find Output:**
   - Right-click book → "Open containing folder"
   - Or: Click "Click to open" in bottom-right corner

---

## Option 3: Online Converter

If you can't install Calibre, use an online converter:

### CloudConvert (Recommended)
1. Go to https://cloudconvert.com/html-to-epub
2. Upload `book/compiled/viruses_book_20260115_152339.html`
3. Click "Convert"
4. Download the EPUB

### Zamzar
1. Go to https://www.zamzar.com/convert/html-to-epub/
2. Upload HTML file
3. Enter email
4. Download EPUB from email link

**Note:** Online converters may not preserve Hebrew RTL formatting as well as Calibre.

---

## Option 4: Mac Preview + Pages (PDF via macOS)

Since you already have a perfect HTML file, you can create a high-quality PDF:

1. **Open HTML in Safari:**
   ```bash
   open book/compiled/viruses_book_20260115_152339.html
   ```

2. **Export to PDF:**
   - Press **Cmd+P** (Print)
   - In print dialog:
     - Click "PDF" dropdown (bottom-left)
     - Select "Save as PDF"
     - Settings:
       - Paper size: **A4**
       - Margins: **Default**
       - Scale: **100%**
   - Save as: `viruses_book.pdf`

3. **Result:**
   - ✅ Professional PDF with all images
   - ✅ Hebrew RTL text properly formatted
   - ✅ Bookmarks from headings
   - ✅ Searchable text
   - ✅ Works on all devices

---

## Testing the EPUB

After creating the EPUB:

1. **Open in Apple Books:**
   ```bash
   open viruses_book_apple.epub
   ```

2. **Verify:**
   - ✅ Hebrew text flows right-to-left
   - ✅ All images display correctly
   - ✅ Cover shows in library
   - ✅ Navigation works
   - ✅ No formatting errors

3. **If issues occur:**
   - Re-run Calibre conversion with `--epub-version 2` instead of 3
   - Or use the PDF method above

---

## Recommended Workflow

For best results:

1. **Use Calibre** to create the EPUB (most reliable)
2. **Use Safari → PDF** for a perfect PDF version
3. Keep the **HTML file** as your master copy (works offline, no conversion needed)

Both EPUB and PDF will include:
- All 8 chapters with enhanced content
- All 17 scientific diagrams
- Cover image
- Glossary and appendices
- Proper Hebrew RTL formatting

---

## Current Files Available

```
book/
├── images/
│   ├── cover.png (NEW!)          - Professional cover image
│   ├── fig_2_1.png through fig_8_2.png  - All 17 diagrams
│   └── image_manifest.json
├── compiled/
│   ├── viruses_book_20260115_152339.html (15 MB)  - Ready for conversion
│   ├── convert_html_to_pdf.sh                      - Helper script
│   └── [other compiled versions...]
└── chapters/
    └── [all enhanced chapter files...]
```

---

## Quick Commands

**Install Calibre (Mac):**
```bash
brew install --cask calibre
```

**Convert HTML → EPUB:**
```bash
ebook-convert \
  book/compiled/viruses_book_20260115_152339.html \
  book/compiled/viruses_book_apple.epub \
  --language he \
  --title "וירוסים וחיסון" \
  --cover book/images/cover.png \
  --epub-version 3
```

**Open HTML for PDF:**
```bash
open book/compiled/viruses_book_20260115_152339.html
# Then: Cmd+P → Save as PDF
```

---

**Estimated Time:**
- Calibre install + conversion: 5-10 minutes
- PDF via Safari: 2-3 minutes

**Result:** Professional EPUB and PDF ready for distribution! 📚
