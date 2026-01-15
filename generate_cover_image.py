#!/usr/bin/env python3
"""
Generate Cover Image for Virology Book

Creates a professional cover image using PIL/Pillow.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("book/images")
OUTPUT_FILE = OUTPUT_DIR / "cover.png"

# Cover dimensions (standard ebook cover ratio 2:3)
WIDTH = 1600
HEIGHT = 2400

# Colors
BG_COLOR = (25, 60, 90)  # Dark blue
ACCENT_COLOR = (52, 152, 219)  # Light blue
TEXT_COLOR = (255, 255, 255)  # White
SUBTITLE_COLOR = (200, 220, 240)  # Light gray-blue


def create_cover():
    """Generate the cover image."""

    print("\n" + "="*60)
    print("Generating Cover Image")
    print("="*60)

    # Create image with gradient background
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Create gradient background
    for y in range(HEIGHT):
        # Gradient from dark blue to slightly lighter blue
        r = int(25 + (y / HEIGHT) * 30)
        g = int(60 + (y / HEIGHT) * 40)
        b = int(90 + (y / HEIGHT) * 50)
        draw.rectangle([(0, y), (WIDTH, y+1)], fill=(r, g, b))

    # Add decorative elements (virus-like circles)
    virus_positions = [
        (200, 300, 80),
        (1400, 500, 60),
        (300, 1900, 70),
        (1300, 2100, 90),
        (800, 200, 50),
        (1200, 1800, 55)
    ]

    for x, y, radius in virus_positions:
        # Outer circle (transparent)
        draw.ellipse(
            [(x-radius, y-radius), (x+radius, y+radius)],
            outline=ACCENT_COLOR,
            width=3
        )
        # Inner circle
        inner_r = radius // 2
        draw.ellipse(
            [(x-inner_r, y-inner_r), (x+inner_r, y+inner_r)],
            fill=ACCENT_COLOR,
            outline=None
        )

        # Add spikes (virus-like)
        for angle in range(0, 360, 45):
            import math
            rad = math.radians(angle)
            x1 = x + int(radius * math.cos(rad))
            y1 = y + int(radius * math.sin(rad))
            x2 = x + int((radius + 20) * math.cos(rad))
            y2 = y + int((radius + 20) * math.sin(rad))
            draw.line([(x1, y1), (x2, y2)], fill=ACCENT_COLOR, width=2)

    # Add text (since we can't use custom fonts easily, use default)
    # Title
    title_bbox = draw.textbbox((0, 0), "וירוסים וחיסון", font=None)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2

    # Main title (in Hebrew)
    draw.text(
        (WIDTH // 2, 800),
        "וירוסים וחיסון",
        fill=TEXT_COLOR,
        anchor="mm",
        font=None  # Will use default font
    )

    # Subtitle
    draw.text(
        (WIDTH // 2, 1000),
        "מבוא מקיף לווירולוגיה",
        fill=SUBTITLE_COLOR,
        anchor="mm"
    )

    draw.text(
        (WIDTH // 2, 1100),
        "ואימונולוגיה",
        fill=SUBTITLE_COLOR,
        anchor="mm"
    )

    # Course name
    draw.text(
        (WIDTH // 2, 1400),
        "Viruses Campus IL",
        fill=ACCENT_COLOR,
        anchor="mm"
    )

    # Edition
    draw.text(
        (WIDTH // 2, 2200),
        "מהדורה ראשונה • 2026",
        fill=SUBTITLE_COLOR,
        anchor="mm"
    )

    # Add decorative line
    draw.rectangle(
        [(WIDTH // 4, 1250), (3 * WIDTH // 4, 1260)],
        fill=ACCENT_COLOR
    )

    # Save image
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_FILE, 'PNG', quality=95)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n✓ Cover image created: {OUTPUT_FILE}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Dimensions: {WIDTH}x{HEIGHT} pixels")
    print(f"  Format: PNG")


if __name__ == "__main__":
    create_cover()
