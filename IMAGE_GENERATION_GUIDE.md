# Image Generation & Book Rebuild Guide

## Overview

This guide explains how to generate scientific illustrations using **Google's Nano Banana API** (Gemini image generation) and rebuild the complete virology ebook with integrated images.

---

## Prerequisites

### 1. Install Dependencies

```bash
pip install google-genai
```

### 2. Set API Key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or pass directly via `--api-key` flag.

---

## Step 1: Generate Images with Nano Banana

The book requires **17 scientific diagrams** across 6 chapters.

### Quick Start (Preview Mode)

Generate first 3 images to test:

```bash
python generate_book_images.py --mode preview
```

**Output:**
- `book/images/fig_5_1.png` - PAMP-PRR recognition mechanism
- `book/images/fig_5_2.png` - Inflammatory response stages
- `book/images/fig_5_3.png` - Dendritic cell function

**Cost:** ~$0.12 (3 images × $0.039)

### Full Generation (All 17 Images)

```bash
python generate_book_images.py --mode all --model flash
```

**Output:**
- 17 PNG images in `book/images/`
- Manifest file: `book/images/image_manifest.json`

**Cost:** ~$0.66 (17 images × $0.039)

### High-Quality Mode (Nano Banana Pro)

For publication-quality images with better text rendering:

```bash
python generate_book_images.py --mode all --model pro
```

**Note:** Nano Banana Pro is more expensive but produces studio-quality results.

### Generate Specific Chapter

```bash
python generate_book_images.py --mode chapter --chapter 05
```

Generates only images for Chapter 5 (3 images).

---

## Step 2: Rebuild the Book

### Option A: Single Markdown File

Compile all enhanced chapters into one file:

```bash
python rebuild_book.py --format markdown
```

**Output:**
- `book/compiled/viruses_book_complete_YYYYMMDD_HHMMSS.md`
- Single file with all 8 chapters, cover, glossary, exam review
- Image placeholders replaced with actual image references
- Auto-generated table of contents

### Option B: PDF-Ready Format

Generate markdown with YAML frontmatter for Pandoc conversion:

```bash
python rebuild_book.py --format pdf-ready
```

**Output:**
- `book/compiled/viruses_book_pdf_ready_YYYYMMDD_HHMMSS.md`
- `book/compiled/convert_to_pdf.sh` (conversion script)

**Convert to PDF:**

```bash
cd book/compiled
./convert_to_pdf.sh
```

**Requirements for PDF:**
- `pandoc` installed
- `xelatex` installed (for Hebrew support)
- Hebrew fonts: "David CLM" or similar

### Option C: Both Formats

```bash
python rebuild_book.py --format all
```

Generates both markdown and PDF-ready versions.

---

## Image Definitions

All 17 images are defined in `generate_book_images.py`:

### Chapter 2: Coronavirus (4 images)
- `fig_2_1` - SARS-CoV-2 structure
- `fig_2_2` - Coronavirus replication cycle
- `fig_2_3` - Spike protein binding to ACE2
- `fig_2_4` - COVID-19 variants phylogenetic tree

### Chapter 3: Macromolecules (2 images)
- `fig_3_1` - DNA vs RNA structure comparison
- `fig_3_2` - Baltimore Classification flowchart

### Chapter 4: Viral Diseases (4 images)
- `fig_4_1` - Four transmission routes
- `fig_4_2` - Variola virus structure
- `fig_4_3` - 1918 flu pandemic spread map
- `fig_4_4` - Polio infection outcomes pie chart

### Chapter 5: Innate Immunity (3 images)
- `fig_5_1` - PAMP-PRR recognition mechanism ✓ *just added*
- `fig_5_2` - Inflammatory response stages
- `fig_5_3` - Dendritic cell function ✓ *just added*

### Chapter 6: Adaptive Immunity (2 images)
- `fig_6_1` - MHC Class I vs II comparison ✓ *just added*
- `fig_6_2` - CD4+ and CD8+ T cell roles ✓ *just added*

### Chapter 8: COVID-19 Pandemic (2 images)
- `fig_8_1` - mRNA vaccine mechanism
- `fig_8_2` - COVID-19 vs flu mortality comparison ✓ *just fixed*

---

## Cost Breakdown

### Nano Banana (gemini-2.5-flash-image)

**Pricing:** $30.00 per 1M output tokens
- Each image: 1,290 tokens = **$0.039 per image**

**Full book (17 images):**
- Tokens: 21,930
- Cost: **$0.66**

### Nano Banana Pro (gemini-3-pro-image-preview)

**Higher quality, better text rendering:**
- 1K/2K resolution: 1,120 tokens = **$0.034 per image**
- 4K resolution: 2,000 tokens = **$0.060 per image**

**Full book (17 images at 2K):**
- Cost: **~$0.58**

---

## Image Quality Guidelines

The prompts are optimized for:
- **Scientific accuracy** - Anatomically correct, molecularly detailed
- **Educational clarity** - Clear labels, numbered sequences, white backgrounds
- **Textbook style** - Professional medical/virology textbook aesthetic
- **Hebrew compatibility** - Diagrams work with Hebrew captions

### Best Practices

1. **Use Nano Banana (flash)** for initial generation and iteration
2. **Use Nano Banana Pro** for final publication-quality images
3. **Regenerate failed images** individually with refined prompts
4. **Verify scientific accuracy** - Have domain expert review anatomical details

---

## Troubleshooting

### Issue: "google-genai not installed"

```bash
pip install google-genai
```

### Issue: "GEMINI_API_KEY not set"

Set environment variable:

```bash
export GEMINI_API_KEY="your-key"
```

Or pass directly:

```bash
python generate_book_images.py --api-key "your-key" --mode preview
```

### Issue: Image generation fails with rate limit

**Free tier:** 200 calls/day (as of Sept 2025)

If you hit the limit:
1. Wait 24 hours, or
2. Generate in batches using `--mode chapter`

### Issue: Images don't match scientific accuracy

1. Edit the prompt in `generate_book_images.py`
2. Regenerate specific image:
   ```python
   generator = NanoBananaImageGenerator(api_key="...", model="gemini-2.5-flash-image")
   generator.generate_image(IMAGES[0])  # Regenerate first image
   ```

### Issue: PDF conversion fails

Ensure dependencies:

```bash
# macOS
brew install pandoc basictex

# Ubuntu
sudo apt-get install pandoc texlive-xetex texlive-lang-hebrew fonts-sil-ezra
```

---

## Advanced Usage

### Customize Image Generation

Edit `generate_book_images.py` and modify the `IMAGES` list:

```python
{
    "id": "fig_5_1",
    "chapter": "05",
    "title": "מנגנון זיהוי PAMP-PRR",
    "prompt": "Your custom prompt here...",
    "aspect_ratio": "16:9"  # Options: 1:1, 16:9, 3:2, 3:4, 4:3, 9:16
}
```

### Batch Processing by Chapter

```bash
for chapter in 02 03 04 05 06 08; do
    python generate_book_images.py --mode chapter --chapter $chapter
done
```

### Regenerate Single Image

```python
from generate_book_images import NanoBananaImageGenerator, IMAGES

generator = NanoBananaImageGenerator(
    api_key="your-key",
    model="gemini-3-pro-image-preview"  # Use Pro for quality
)

# Find and regenerate specific image
image_def = next(img for img in IMAGES if img["id"] == "fig_5_1")
generator.generate_image(image_def)
```

---

## Output Structure

```
book/
├── images/                          # Generated images
│   ├── fig_2_1.png
│   ├── fig_2_2.png
│   ├── ...
│   ├── fig_8_2.png
│   └── image_manifest.json          # Generation metadata
├── compiled/                        # Compiled books
│   ├── viruses_book_complete_*.md   # Single markdown
│   ├── viruses_book_pdf_ready_*.md  # PDF-ready with metadata
│   └── convert_to_pdf.sh            # Pandoc conversion script
└── chapters/                        # Enhanced source chapters
    ├── 00_cover.md
    ├── 01_chapter.md
    ├── 02_chapter.md
    ├── ...
    └── 08_chapter.md
```

---

## Next Steps

1. **Generate preview images** to verify quality
2. **Regenerate any failed images** with refined prompts
3. **Review scientific accuracy** with domain expert
4. **Compile final book** with all images integrated
5. **Convert to PDF** for publication

---

## References

- **Nano Banana Documentation:** https://ai.google.dev/gemini-api/docs/nanobanana
- **Nano Banana Pro Blog:** https://blog.google/technology/ai/nano-banana-pro/
- **Gemini 2.5 Flash Image:** https://developers.googleblog.com/en/introducing-gemini-2-5-flash-image/

---

**Status:**
- ✅ All 11 content fixes complete (95% publication ready)
- ✅ Image generation scripts ready
- ⏳ Images pending generation
- ⏳ Final book compilation pending

**Estimated time:** 30-45 minutes for complete image generation and book compilation.
