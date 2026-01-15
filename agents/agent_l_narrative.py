"""
Agent L: PedagogicalBridge (Quality-First Round 2)

Ensures cross-chapter continuity and a cumulative narrative arc.
Adds "Recall Hooks" (linking back) and "Preview Hooks" (linking forward).

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import json
import time
from typing import Dict, List, Optional

# Use the new unified Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")

from .schemas import (
    PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "PedagogicalBridge"

# Gemini configuration
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class PedagogicalBridge:
    """
    Agent L: Adds cross-references and narrative continuity between chapters.
    
    Output: Updated chapters with internal links and context.
    """
    
    SYSTEM_PROMPT = """אתה עורך פדגוגי האחראי על הקישוריות (Connectivity) בין חלקי הספר.

תפקידך: להוסיף משפטי קישור שיקשרו את הפרק הנוכחי לפרקים קודמים ולפרקים הבאים.

## המשימה:
1. זהה מושגים שהוזכרו בפרקים קודמים והוסף "Recall Hook" (למשל: "כפי שלמדנו בפרק 2 על חלבוני מבנה...").
2. זהה נושאים שיורחבו בהמשך והוסף "Preview Hook" (למשל: "נראה בהרחבה כיצד מנגנון זה מנוצל על ידי נגיף הקורונה בפרק 8...").
3. ודא שהספר מרגיש כמו יחידה אחת מגובשת.

החזר את תוכן הפרק המעובד.
"""
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        
        # Initialize Gemini client
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception: pass
            
    def _generate(self, prompt: str) -> Optional[str]:
        if not self.client: return None
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.4)
            )
            return response.text
        except Exception: return None
            
    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        output_files = []
        
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        # Build chapter map for context
        chapter_map = {p["chapter_id"]: p["hebrew_title"] for p in chapter_plans}
        
        print(f"[{AGENT_NAME}] Linking chapters for narrative continuity...")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            path = self._get_chapter_path(chapter_id)
            if not path: continue
            
            content = read_file(path)
            
            prompt = f"""{self.SYSTEM_PROMPT}

כותרת הפרק הנוכחי: {plan['hebrew_title']}
מספר הפרק: {chapter_id}

מפת הספר:
{json.dumps(chapter_map, ensure_ascii=False, indent=2)}

תוכן הפרק:
{content[:15000]}

המשימה: הוסף 2-3 משפטי קישור (Recall/Preview) במקומות רלוונטיים בטקסט. החזר את הטקסט המעובד במלואו.
"""
            
            refined = self._generate(prompt)
            if refined:
                save_markdown(refined, path)
                output_files.append(path)
                print(f"    ✓ Linked Chapter {chapter_id}")
            
            time.sleep(3)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files)
        return {"linked_files": len(output_files)}

    def _get_chapter_path(self, chapter_id: str) -> Optional[str]:
        names = [f"{chapter_id}_chapter.md", f"0{chapter_id}_chapter.md"]
        for n in names:
            p = os.path.join(self.chapters_dir, n)
            if os.path.exists(p): return p
        return None
