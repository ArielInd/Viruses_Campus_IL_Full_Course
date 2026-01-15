#!/usr/bin/env python3
"""
Nano Banana Image Generation for Viruses Ebook
Generates all 17 scientific diagrams using Gemini's Nano Banana API.

Usage:
    python generate_book_images.py --mode preview  # Generate first 3 images
    python generate_book_images.py --mode all      # Generate all 17 images
    python generate_book_images.py --model pro     # Use Nano Banana Pro (higher quality)
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai not installed. Run: pip install google-genai")
    exit(1)


# Image definitions extracted from chapters
IMAGES = [
    # Chapter 5: Innate Immunity (3 images)
    {
        "id": "fig_5_1",
        "chapter": "05",
        "title": "מנגנון זיהוי PAMP-PRR",
        "hebrew_desc": "איור סכמטי המציג תא חיסון גדול (מקרופאג') עם קולטן מסוג TLR4 (ה'מנעול') על פני הממברנה שלו. חיידק גראם-שלילי מתקרב, ועליו מולקולות LPS (ה'מפתח'). חץ מראה את הקישור הספציפי בין ה-LPS ל-TLR4, וחץ נוסף מראה 'אות' שנוצר בתוך המקרופאג' כתוצאה מהקישור.",
        "prompt": "Scientific medical illustration: A large macrophage immune cell with TLR4 receptor (labeled as 'lock') on its membrane surface. A gram-negative bacterium approaches with LPS molecules (labeled as 'key') on its surface. Arrow showing specific binding between LPS and TLR4. Second arrow showing signal generated inside macrophage. Educational diagram style, professional medical textbook quality, clear labels, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_5_2",
        "chapter": "05",
        "title": "שלבי התגובה הדלקתית",
        "hebrew_desc": "איור המציג חתך ברקמה. שלב 1: חיידקים חודרים דרך פצע בעור. שלב 2: מקרופאג' מקומי מזהה ובולע חיידק, ומפריש ציטוקינים וכימוקינים. שלב 3: כלי הדם הסמוך מתרחב והופך לחדיר יותר. שלב 4: נויטרופילים נצמדים לדופן כלי הדם ונודדים החוצה, בעקבות מפל הריכוזים של הכימוקינים, אל עבר החיידקים.",
        "prompt": "Scientific medical illustration showing inflammatory response stages in tissue cross-section: Stage 1 - bacteria entering through skin wound. Stage 2 - local macrophage recognizing and engulfing bacterium, secreting cytokines and chemokines. Stage 3 - nearby blood vessel dilating and becoming more permeable. Stage 4 - neutrophils adhering to vessel wall and migrating out, following chemokine concentration gradient toward bacteria. Sequential diagram with numbered stages, professional immunology textbook style, clear anatomical detail, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_5_3",
        "chapter": "05",
        "title": "תפקיד התאים הדנדריטיים",
        "hebrew_desc": "שלושה שלבים - (1) תא דנדריטי לא בשל ברקמה בולע פתוגן. (2) התא נודד דרך כלי לימפה לקשר לימפה, תוך כדי בשלה. (3) בקשר הלימפה, התא הבשל מציג פפטיד על MHC II שלו לתא T נאיבי, המופעל כתוצאה מכך.",
        "prompt": "Scientific medical illustration showing dendritic cell function in three stages: (1) Immature dendritic cell in tissue engulfing pathogen with pseudopods. (2) Dendritic cell migrating through lymphatic vessel to lymph node while maturing, showing morphological changes. (3) In lymph node, mature dendritic cell presenting peptide on MHC II molecule to naive T cell, which becomes activated. Professional immunology textbook diagram, clear sequential stages, labeled cell types, white background.",
        "aspect_ratio": "16:9"
    },

    # Chapter 6: Adaptive Immunity (2 images)
    {
        "id": "fig_6_1",
        "chapter": "06",
        "title": "מנגנון הצגת אנטיגן MHC",
        "hebrew_desc": "השוואה בין MHC Class I ו-MHC Class II במצגת אנטיגנים.",
        "prompt": "Scientific medical illustration comparing MHC Class I and Class II antigen presentation mechanisms. Left side: MHC Class I on all nucleated cells presenting intracellular peptides to CD8+ T cells. Right side: MHC Class II on professional APCs presenting extracellular peptides to CD4+ helper T cells. Split diagram showing both pathways side by side, molecular detail, professional immunology textbook style, clear labels, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_6_2",
        "chapter": "06",
        "title": "תאי T עוזרים ותאי T ציטוטוקסיים",
        "hebrew_desc": "תפקידים משלימים של CD4+ ו-CD8+ במערכת החיסון הנרכשת.",
        "prompt": "Scientific medical illustration showing complementary roles of CD4+ helper T cells and CD8+ cytotoxic T cells in adaptive immunity. Central helper T cell (CD4+) coordinating immune response, sending signals to activate B cells, macrophages, and cytotoxic T cells. Cytotoxic T cell (CD8+) killing virus-infected target cell. Professional immunology diagram, clear cellular interactions, labeled cell types and signals, white background.",
        "aspect_ratio": "16:9"
    },

    # Chapter 3: Macromolecules (2 images)
    {
        "id": "fig_3_1",
        "chapter": "03",
        "title": "מבנה DNA ו-RNA",
        "hebrew_desc": "השוואה מבנית בין DNA דו-גדילי ל-RNA חד-גדילי.",
        "prompt": "Scientific molecular biology illustration comparing DNA double helix structure with single-stranded RNA. Left: DNA showing double helix, complementary base pairs (A-T, G-C), sugar-phosphate backbone, antiparallel strands. Right: RNA showing single strand, uracil instead of thymine, different sugar (ribose). Molecular detail with clear nucleotide structure, professional biochemistry textbook style, labeled components, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_3_2",
        "chapter": "03",
        "title": "שכפול ויראלי - Baltimore Classification",
        "hebrew_desc": "תרשים זרימה של 7 קבוצות Baltimore לשכפול נגיפים.",
        "prompt": "Scientific virology flowchart showing Baltimore Classification system with all 7 groups of viral replication strategies. Central branching diagram showing pathways from different genome types (dsDNA, ssDNA, dsRNA, (+)ssRNA, (-)ssRNA, ssRNA-RT, dsDNA-RT) to mRNA production. Each group clearly labeled with representative virus examples. Professional virology textbook diagram, clear arrows showing replication flow, white background.",
        "aspect_ratio": "3:4"
    },

    # Chapter 4: Viral Diseases (4 images)
    {
        "id": "fig_4_1",
        "chapter": "04",
        "title": "דרכי העברת נגיפים",
        "hebrew_desc": "ארבע דרכי העברה עיקריות: אווירנית, מגע, פקו-אוראלית, וקטורים.",
        "prompt": "Scientific medical illustration showing four main viral transmission routes. Divided into quadrants: (1) Airborne - respiratory droplets from coughing/sneezing. (2) Direct contact - handshake transmitting virus. (3) Fecal-oral route - contaminated water/food. (4) Vector-borne - mosquito transmitting virus. Professional epidemiology diagram, clear human figures, pathogen visualization, educational style, white background.",
        "aspect_ratio": "1:1"
    },
    {
        "id": "fig_4_2",
        "chapter": "04",
        "title": "מבנה נגיף האבעבועות השחורות",
        "hebrew_desc": "מבנה מורכב של Variola virus עם מעטפת DNA.",
        "prompt": "Scientific virology illustration of Variola (smallpox) virus structure. Detailed cross-section showing: outer envelope with surface proteins, brick-shaped virion morphology, internal core containing dsDNA genome, viral enzymes. Cutaway view revealing internal architecture. Professional medical virology textbook quality, molecular detail, clear labels, white background.",
        "aspect_ratio": "1:1"
    },
    {
        "id": "fig_4_3",
        "chapter": "04",
        "title": "מפת התפשטות מגפת השפעת 1918",
        "hebrew_desc": "מפת עולם המציגה גלי התפשטות השפעת הספרדית.",
        "prompt": "Historical scientific map showing global spread of 1918 Spanish Flu pandemic. World map with color-coded waves of transmission spreading from initial outbreak sites. Timeline arrows showing progression over months. Death toll statistics by region. Professional historical epidemiology visualization, clear geographical detail, legend with wave dates, muted historical color palette, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_4_4",
        "chapter": "04",
        "title": "סטטיסטיקות פוליו",
        "hebrew_desc": "תרשים עוגה של תוצאות הדבקה בפוליו: 72% א-סימפטומטי, 24% קל, 1-5% דלקת קרום מוח, <1% משתק.",
        "prompt": "Scientific medical infographic showing polio infection outcomes as pie chart. Large segments: 72% asymptomatic (light blue), 24% minor symptoms (yellow). Small segments: 1-5% meningitis (orange), <1% paralytic polio (red). Professional epidemiology statistics visualization, clear percentages, labeled segments, clean design, white background.",
        "aspect_ratio": "1:1"
    },

    # Chapter 2: Coronavirus (4 images)
    {
        "id": "fig_2_1",
        "chapter": "02",
        "title": "מבנה נגיף הקורונה SARS-CoV-2",
        "hebrew_desc": "מבנה הנגיף עם חלבון הספייק, מעטפת ליפידית וגנום RNA.",
        "prompt": "Scientific virology illustration of SARS-CoV-2 coronavirus structure. Spherical virion with prominent spike (S) proteins protruding from lipid envelope. Cross-section showing: spike proteins (red), envelope (E) proteins, membrane (M) proteins, nucleocapsid (N) protein wrapped around positive-sense ssRNA genome. Professional medical virology textbook quality, molecular detail, clearly labeled components, white background.",
        "aspect_ratio": "1:1"
    },
    {
        "id": "fig_2_2",
        "chapter": "02",
        "title": "מחזור שכפול קורונה",
        "hebrew_desc": "שלבי השכפול: הידבקות, חדירה, שכפול RNA, תרגום, הרכבה ושחרור.",
        "prompt": "Scientific virology diagram showing SARS-CoV-2 replication cycle in numbered steps: (1) Spike protein binding to ACE2 receptor. (2) Membrane fusion and RNA release into cell. (3) Translation of viral proteins. (4) RNA genome replication. (5) Assembly of new virions in ER/Golgi. (6) Release by exocytosis. Circular sequential diagram, professional virology textbook style, clear numbered stages, white background.",
        "aspect_ratio": "1:1"
    },
    {
        "id": "fig_2_3",
        "chapter": "02",
        "title": "קולטן ACE2 וקישור הספייק",
        "hebrew_desc": "מבנה תלת-ממדי של חלבון הספייק קושר ל-ACE2 על תא אנושי.",
        "prompt": "Scientific molecular biology illustration showing 3D structure of SARS-CoV-2 spike protein (trimeric structure in red/pink) binding to human ACE2 receptor (blue) on cell surface. Detailed protein structure showing receptor-binding domain (RBD) interaction. Cell membrane with ACE2 embedded. Professional structural biology visualization, molecular surface rendering, clear binding site, white background.",
        "aspect_ratio": "1:1"
    },
    {
        "id": "fig_2_4",
        "chapter": "02",
        "title": "השוואת וריאנטים של COVID-19",
        "hebrew_desc": "עץ פילוגנטי של וריאנטים עיקריים: אלפא, בטא, דלתא, אומיקרון.",
        "prompt": "Scientific phylogenetic tree showing SARS-CoV-2 major variants evolution. Original Wuhan strain at root, branching to Alpha, Beta, Gamma, Delta, and Omicron variants. Each variant labeled with key spike protein mutations and emergence date. Timeline axis showing 2020-2023. Professional virology evolutionary diagram, clear branching structure, color-coded lineages, white background.",
        "aspect_ratio": "3:4"
    },

    # Chapter 8: COVID-19 Pandemic (2 images)
    {
        "id": "fig_8_1",
        "chapter": "08",
        "title": "מנגנון חיסון mRNA",
        "hebrew_desc": "שלבי פעולת חיסון mRNA: הזרקה, כניסה לתא, תרגום ספייק, הצגה ל-MHC, הפעלת תגובה חיסונית.",
        "prompt": "Scientific medical illustration showing mRNA vaccine mechanism in sequential steps: (1) Lipid nanoparticle (LNP) containing mRNA injected into muscle. (2) LNP enters cell, releases mRNA. (3) Ribosome translates mRNA into spike protein. (4) Spike protein displayed on cell surface via MHC. (5) Immune cells recognize spike, initiate adaptive immune response. Professional immunology diagram, clear numbered sequence, molecular detail, white background.",
        "aspect_ratio": "16:9"
    },
    {
        "id": "fig_8_2",
        "chapter": "08",
        "title": "השוואת תמותה COVID-19 vs שפעת",
        "hebrew_desc": "גרף עמודות משווה תמותה שנתית: COVID-19 (~3.15M) vs שפעת עונתית (~650K).",
        "prompt": "Scientific epidemiology bar chart comparing annual mortality: COVID-19 (approximately 3.15 million deaths per year, tall red bar) versus seasonal influenza (approximately 650,000 deaths per year, shorter blue bar). Clear y-axis with mortality scale, labeled bars, ratio indicator showing ~5x difference. Professional public health statistics visualization, clean design, white background.",
        "aspect_ratio": "3:2"
    }
]


class NanoBananaImageGenerator:
    """Generate scientific illustrations using Gemini Nano Banana API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        """
        Initialize the image generator.

        Args:
            api_key: Google Gemini API key
            model: Either "gemini-2.5-flash-image" (fast) or "gemini-3-pro-image-preview" (quality)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.output_dir = Path("book/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track costs
        self.images_generated = 0
        self.tokens_used = 0

    def generate_image(self, image_def: Dict) -> Optional[str]:
        """
        Generate a single image from definition.

        Returns:
            Path to saved image file, or None if failed
        """
        print(f"\n[Nano Banana] Generating {image_def['id']}: {image_def['title']}")
        print(f"  Description: {image_def['hebrew_desc'][:80]}...")

        try:
            # Configure generation
            config = types.GenerateContentConfig(
                temperature=0.4,  # Lower for more consistent scientific diagrams
                response_modalities=['Image'],
            )

            # Add aspect ratio to prompt
            full_prompt = f"{image_def['prompt']} --ar {image_def['aspect_ratio']}"

            # Generate
            response = self.client.models.generate_content(
                model=self.model,
                contents=[full_prompt],
                config=config
            )

            # Save image
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Save image bytes
                            image_data = part.inline_data.data
                            output_path = self.output_dir / f"{image_def['id']}.png"

                            with open(output_path, 'wb') as f:
                                f.write(image_data)

                            print(f"  ✓ Saved: {output_path}")

                            # Track usage
                            self.images_generated += 1
                            self.tokens_used += 1290  # Standard token cost

                            return str(output_path)

            print(f"  ✗ Failed: No image data in response")
            return None

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None

    def generate_all(self, images: List[Dict], limit: Optional[int] = None):
        """Generate all images (or limited subset)."""

        total = limit if limit else len(images)
        print(f"\n{'='*60}")
        print(f"Nano Banana Image Generation")
        print(f"Model: {self.model}")
        print(f"Images to generate: {total}/{len(images)}")
        print(f"{'='*60}")

        images_to_process = images[:limit] if limit else images
        results = []

        for i, img_def in enumerate(images_to_process, 1):
            print(f"\n[{i}/{total}] Processing...")
            result = self.generate_image(img_def)
            results.append({
                "id": img_def["id"],
                "title": img_def["title"],
                "path": result,
                "success": result is not None
            })

        # Print summary
        print(f"\n{'='*60}")
        print(f"Generation Complete")
        print(f"{'='*60}")
        print(f"Successful: {sum(1 for r in results if r['success'])}/{total}")
        print(f"Failed: {sum(1 for r in results if not r['success'])}/{total}")
        print(f"\nUsage:")
        print(f"  Images generated: {self.images_generated}")
        print(f"  Tokens used: {self.tokens_used:,}")

        if self.model == "gemini-2.5-flash-image":
            cost = (self.tokens_used / 1_000_000) * 30.00
            print(f"  Estimated cost: ${cost:.2f}")

        print(f"\nOutput directory: {self.output_dir.absolute()}")

        # Save manifest
        manifest_path = self.output_dir / "image_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Manifest saved: {manifest_path}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Generate scientific illustrations for Viruses Ebook")
    parser.add_argument(
        "--mode",
        choices=["preview", "all", "chapter"],
        default="preview",
        help="preview: first 3 images, all: all 17 images, chapter: specific chapter"
    )
    parser.add_argument(
        "--model",
        choices=["flash", "pro"],
        default="flash",
        help="flash: Nano Banana (fast), pro: Nano Banana Pro (quality)"
    )
    parser.add_argument(
        "--chapter",
        type=str,
        help="Chapter ID (e.g., '05') when mode=chapter"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("GEMINI_API_KEY"),
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: GEMINI_API_KEY not set. Use --api-key or set environment variable.")
        exit(1)

    # Select model
    model_name = "gemini-2.5-flash-image" if args.model == "flash" else "gemini-3-pro-image-preview"

    # Initialize generator
    generator = NanoBananaImageGenerator(api_key=args.api_key, model=model_name)

    # Select images
    if args.mode == "preview":
        images_to_generate = IMAGES[:3]
        print("\n[Preview Mode] Generating first 3 images...")
    elif args.mode == "chapter":
        if not args.chapter:
            print("Error: --chapter required when mode=chapter")
            exit(1)
        images_to_generate = [img for img in IMAGES if img["chapter"] == args.chapter]
        print(f"\n[Chapter Mode] Generating {len(images_to_generate)} images for chapter {args.chapter}...")
    else:  # all
        images_to_generate = IMAGES
        print(f"\n[Full Mode] Generating all {len(IMAGES)} images...")

    # Generate
    results = generator.generate_all(images_to_generate)

    # Exit status
    all_success = all(r["success"] for r in results)
    exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
