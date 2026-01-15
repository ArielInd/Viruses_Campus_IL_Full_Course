"""
Agent K: VisualChronicler (Quality-First Round 2)

Extracts visual evidence from transcripts (slides, animations, diagrams) 
and creates descriptive "Visual Insight" callout boxes.

Also suggests prompts for AI image generation.

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

AGENT_NAME = "VisualChronicler"

# Gemini configuration - PRO for multimodal reasoning
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class VisualChronicler:
    """
    Agent K: Extracts visual context from transcripts and enhances chapters with images/diagrams descriptions.
    
    Output: Updated chapters with > [!TIP] Visual Insight boxes.
    """
    
    SYSTEM_PROMPT = """אתה עורך חזותי (Visual Editor) לספרי לימוד מדעיים.

תפקידך: לסרוק תמלילי הרצאות ולמצוא רגעים שבהם המרצה מתאר שקף, איור או אנימציה.

## המשימה:
1. זהה תיאורים של מבנים ויזואליים (למשל: "כאן רואים את המעטפת", "החלבון הזה נראה כמו מפתח").
2. צור תיבת "תובנה חזותית" (Visual Insight) שתסביר לקורא מה הוא אמור היה לראות באותו רגע.
3. הצע תיאור (Prompt) ליצירת איור מדעי רלוונטי ב-AI.

החזר JSON בפורמט:
{
  "visual_insights": [
    {
      "topic": "שם הנושא",
      "context": "הקשר מהתמליל",
      "description_hebrew": "תיאור בעברית עבור הקורא (מה רואים באיור)",
      "image_prompt": "A professional scientific 3D illustration of [concept]..."
    }
  ]
}
"""
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(book_dir)), "course_transcripts")
        
        # Initialize Gemini client
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[{AGENT_NAME}] Error: {e}")
        
    def _generate(self, prompt: str) -> Optional[str]:
        if not self.client: return None
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
            return response.text
        except Exception: return None
            
    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        output_files = []
        
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            draft_path = self._get_chapter_path(chapter_id)
            if not draft_path: continue
            
            # Load transcript context
            sources = plan.get("source_files", [])
            transcript_text = ""
            for s in sources:
                if os.path.exists(s):
                    transcript_text += read_file(s) + "\n"
            
            if not transcript_text: continue
            
            # Extract visual insights
            insights = self._extract_insights(chapter_id, transcript_text[:30000])
            if insights:
                self._apply_insights(draft_path, insights)
                output_files.append(draft_path)
                print(f"[{AGENT_NAME}] ✓ Enhanced Chapter {chapter_id} with {len(insights)} visual insights")
        
        self.logger.log_end(AGENT_NAME, start_time, output_files)
        return {"enhanced_files": len(output_files)}

    def _get_chapter_path(self, chapter_id: str) -> Optional[str]:
        names = [f"{chapter_id}_chapter.md", f"0{chapter_id}_chapter.md"]
        for n in names:
            p = os.path.join(self.chapters_dir, n)
            if os.path.exists(p): return p
        return None

    def _extract_insights(self, chapter_id: str, transcript: str) -> List[Dict]:
        prompt = f"{self.SYSTEM_PROMPT}\n\nתמליל:\n{transcript}\n\nחלץ תובנות חזותיות ב-JSON."
        text = self._generate(prompt)
        if text:
            try:
                # Simple extraction
                start = text.find('{')
                end = text.rfind('}') + 1
                return json.loads(text[start:end]).get("visual_insights", [])
            except: pass
        return []

    def _apply_insights(self, path: str, insights: List[Dict]):
        content = read_file(path)
        
        added_content = "\n\n---\n\n## 🖼️ נספח חזותי לפרק\n\n"
        for ins in insights:
            added_content += f"> [!TIP] **תובנה חזותית: {ins['topic']}**\n"
            added_content += f"> {ins['description_hebrew']}\n"
            added_content += f"> \n"
            added_content += f"> *הערה לסטודנט: דמיינו {ins['topic']} כפי שמתואר לעיל.*\n\n"
            
        save_markdown(content + added_content, path)
