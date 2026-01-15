"""
LLM Utilities for Ebook Pipeline
"""

import os
from typing import Optional
from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_cover_from_book(full_text: str, output_path: str):
    """
    Generates a cover prompt based on book content and logs it.
    Actual image generation is handled by the assistant.
    """
    print(f"[LLM Utils] Analyzing book content to generate cover prompt...")
    
    if not GEMINI_API_KEY:
        print("⚠️ No API key found for cover prompt generation.")
        return
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""נתח את תוכן הספר הבא וצור הנחיה (Prompt) באנגלית ליצירת כריכת ספר אקדמית יוקרתית ב-AI.
ההנחיה צריכה לתאר סגנון מודרני, מינימליסטי, תלת-ממדי (Glassmorphism), עם אלמנטים של וירולוגיה (נגיפים, DNA).

תוכן הספר (חלקים נבחרים):
{full_text[:10000]}

החזר רק את ה-Prompt באנגלית.
"""
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        cover_prompt = response.text.strip()
        
        # Save prompt to a file so the assistant can read it
        prompt_file = os.path.join(os.path.dirname(output_path), "cover_prompt.txt")
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(cover_prompt)
            
        print(f"✅ Cover prompt generated and saved to {prompt_file}")
        print(f"Prompt: {cover_prompt[:100]}...")
        
    except Exception as e:
        print(f"⚠️ Failed to generate cover prompt: {e}")
