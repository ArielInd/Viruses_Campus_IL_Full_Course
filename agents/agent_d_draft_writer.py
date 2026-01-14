"""
Agent D: DraftWriter (Gemini-Enhanced)
Writes initial chapter drafts using Gemini API for high-quality Hebrew content.
"""

import os
import re
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Using template-based generation.")

from .schemas import (
    DraftChapter, PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)
from .version_manager import VersionManager

AGENT_NAME = "DraftWriter"

# Gemini configuration
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set. Gemini features will be disabled.")
    print("Set your API key with: export GEMINI_API_KEY='your-key-here'")


def setup_gemini():
    """Configure Gemini API."""
    if not GEMINI_AVAILABLE:
        return None

    if not GEMINI_API_KEY:
        print(f"[{AGENT_NAME}] No API key found, Gemini features disabled")
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 8192,
    }
    
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=generation_config,
    )
    
    return model


class DraftWriter:
    """
    Agent D: Writes chapter drafts from briefs and source transcripts.
    Uses Gemini API for high-quality Hebrew content generation.
    Output: /ops/artifacts/drafts/chapters/*.md
    """
    
    def __init__(self, transcripts_dir: str, ops_dir: str, 
                 logger: PipelineLogger, todos: TodoTracker):
        self.transcripts_dir = transcripts_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        self.drafts_dir = os.path.join(self.artifacts_dir, "drafts", "chapters")
        self.briefs_dir = os.path.join(self.artifacts_dir, "chapter_briefs")
        
        # Setup Gemini
        self.model = setup_gemini()
        if self.model:
            print(f"[{AGENT_NAME}] Gemini API initialized successfully")
        else:
            print(f"[{AGENT_NAME}] Using template-based generation")

        # Setup version manager
        self.version_manager = VersionManager(ops_dir)
        print(f"[{AGENT_NAME}] Version control initialized")
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Load chapter plan
        plan_path = os.path.join(self.artifacts_dir, "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        print(f"[{AGENT_NAME}] Writing drafts for {len(chapter_plans)} chapters")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Load brief
            brief_path = os.path.join(self.briefs_dir, f"chapter_{chapter_id}_brief.json")
            brief = load_json(brief_path) if os.path.exists(brief_path) else {}
            
            # Load source content
            source_content = self._load_sources(plan.get("source_files", []))
            
            # Generate draft using Gemini or template
            if self.model and source_content:
                draft = self._write_draft_with_gemini(plan, brief, source_content)
            else:
                draft = self._write_draft_template(plan, brief, source_content)
            
            # Save draft
            draft_path = os.path.join(self.drafts_dir, f"{chapter_id}_chapter_draft.md")
            save_markdown(draft.content_md, draft_path)
            output_files.append(draft_path)
            
            print(f"[{AGENT_NAME}] Wrote chapter {chapter_id}: {draft.word_count} words")
            
            # Rate limiting for API - wait 20 seconds between chapters to avoid quota limits
            if self.model:
                print(f"[{AGENT_NAME}] Waiting 20s before next chapter to avoid rate limits...")
                time.sleep(20)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "drafts_dir": self.drafts_dir,
            "num_drafts": len(chapter_plans)
        }
    
    def _load_sources(self, source_paths: List[str]) -> str:
        """Load and concatenate source transcript content."""
        content = []
        for path in source_paths:
            if os.path.exists(path):
                try:
                    text = read_file(path)
                    # Truncate very long files
                    if len(text) > 15000:
                        text = text[:15000] + "\n\n[תוכן נוסף קוצר...]"
                    content.append(text)
                except Exception as e:
                    self.todos.add(AGENT_NAME, path, f"Failed to read: {e}")
        
        combined = "\n\n---\n\n".join(content)
        
        # Limit total content for API
        if len(combined) > 60000:
            combined = combined[:60000] + "\n\n[התוכן קוצר לצורך עיבוד...]"
        
        return combined
    
    def _write_draft_with_gemini(self, plan: Dict, brief: Dict, source_content: str) -> DraftChapter:
        """Write a chapter draft using Gemini API with retry logic."""
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        # Build the prompt
        prompt = self._build_chapter_prompt(plan, brief, source_content)
        
        # Retry logic with exponential backoff
        max_retries = 3
        base_delay = 15  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                content = response.text
                
                # Post-process to ensure structure
                content = self._post_process_content(content, chapter_id, title, brief)
                
                word_count = len(content.split())
                
                return DraftChapter(
                    chapter_id=chapter_id,
                    title=title,
                    content_md=content,
                    word_count=word_count,
                    has_objectives=True,
                    has_roadmap=True,
                    has_summary=True,
                    has_key_terms=True,
                    has_questions=True,
                    todos=[]
                )
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a quota/rate limit error
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff: 15, 30, 60 seconds
                        print(f"[{AGENT_NAME}] Rate limit hit for chapter {chapter_id}. Waiting {delay}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(delay)
                        continue
                
                print(f"[{AGENT_NAME}] Gemini error for chapter {chapter_id}: {e}")
                self.todos.add(AGENT_NAME, f"chapter_{chapter_id}", f"Gemini failed: {e}")
                break
        
        # Fallback to template
        return self._write_draft_template(plan, brief, source_content)
    
    def _build_chapter_prompt(self, plan: Dict, brief: Dict, source_content: str) -> str:
        """Build the Gemini prompt for chapter generation."""
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        prompt = f"""אתה כותב ספר לימוד עברי מקיף על וירולוגיה ואימונולוגיה.

המשימה: כתוב את פרק {chapter_id} בנושא "{title}".

הנחיות חשובות:
1. כתוב בעברית ברורה וספרותית
2. זה ספר לימוד, לא תמלול הרצאה - אין "כפי שראינו בשקף", אין שיח הרצאה
3. הגדר כל מונח בהופעה ראשונה ב-**bold**, עם התרגום האנגלי בסוגריים
4. השאר קיצורים מדעיים באנגלית: DNA, RNA, mRNA, PCR, ELISA, MHC, TLR
5. הדגמות מעבדה יהיו קונספטואליות בלבד - ללא נפחים, זמנים, או פרוטוקולים מעשיים

מבנה הפרק (חובה):
# פרק {chapter_id}: {title}

## מטרות למידה
{chr(10).join('- ' + obj for obj in brief.get('objectives', plan.get('learning_objectives', []))[:8])}

## מפת דרכים
{brief.get('roadmap', '')}

## [התוכן המרכזי - חלק לתת-פרקים עם ## כותרות]
(כתוב תוכן מפורט ומעמיק על כל נושא)

## טעויות נפוצות ומלכודות
(3-5 טעויות נפוצות עם הסבר)

## סיכום מהיר (High-Yield)
(8-12 נקודות מפתח)

## מושגי מפתח
(טבלה עם מונח עברי, אנגלי, הגדרה קצרה)

## שאלות לתרגול
### שאלות אמריקאיות (4-6 שאלות עם 4 אפשרויות, תשובה ורציונל)
### שאלות קצרות (2-3 שאלות עם תשובה לדוגמה)
### שאלת חשיבה (שאלה אחת מורכבת עם קווים מנחים לתשובה)

---

תוכן מקור מהתמלילים (השתמש בזה כבסיס):

{source_content[:40000]}

---

כתוב כעת את הפרק המלא (מינימום 3000 מילים):
"""
        
        return prompt
    
    def _post_process_content(self, content: str, chapter_id: str, title: str, brief: Dict) -> str:
        """Post-process generated content to ensure structure."""
        # Ensure chapter header exists
        if not content.startswith(f"# פרק {chapter_id}"):
            content = f"# פרק {chapter_id}: {title}\n\n" + content
        
        # Remove any streaming artifacts
        content = content.replace("```markdown", "").replace("```", "")
        
        # Ensure proper Hebrew formatting
        content = content.strip()
        
        return content
    
    def _write_draft_template(self, plan: Dict, brief: Dict, source_content: str) -> DraftChapter:
        """Write a chapter draft using templates (fallback)."""
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        md = f"# פרק {chapter_id}: {title}\n\n"
        
        # Learning objectives
        md += "## מטרות למידה\n\n"
        md += "בסיום פרק זה תוכלו:\n\n"
        for obj in brief.get("objectives", plan.get("learning_objectives", [])):
            md += f"- {obj}\n"
        md += "\n"
        
        # Roadmap
        md += "## מפת דרכים\n\n"
        md += brief.get("roadmap", f"פרק זה עוסק ב{title}.") + "\n\n"
        md += "---\n\n"
        
        # Main content sections
        for section in brief.get("content_sections", []):
            heading = section.get("heading", "")
            md += f"## {heading}\n\n"
            
            for point in section.get("key_points", []):
                md += f"**{point}** – מושג מרכזי בנושא זה.\n\n"
        
        # Expert box if applicable
        expert = brief.get("expert_perspective")
        if expert:
            md += "> ### תיבה: נקודת מבט של מומחה\n>\n"
            md += f"> **{expert.get('expert_name', 'מומחה')}** משתף תובנות.\n\n"
        
        # Lab demo box if applicable
        lab = brief.get("lab_demo_conceptual")
        if lab:
            md += "> ### תיבה: מעבדה כהדגמה (קונספטואלית)\n>\n"
            md += f"> **{lab.get('demo_title', 'הדגמה')}**\n>\n"
            md += "> *הערה: ללא פרוטוקול מעשי.*\n\n"
        
        # Common mistakes
        md += "---\n\n"
        md += "## טעויות נפוצות ומלכודות\n\n"
        for i, mistake in enumerate(brief.get("common_mistakes", ["טעות נפוצה"]), 1):
            md += f"{i}. **{mistake}**\n"
        md += "\n"
        
        # Quick summary
        md += "## סיכום מהיר (High-Yield)\n\n"
        for obj in brief.get("objectives", [])[:10]:
            cleaned = obj.replace("להבין", "").replace("לתאר", "").replace("להסביר", "").strip()
            md += f"- {cleaned}\n"
        md += "\n"
        
        # Key terms
        md += "## מושגי מפתח\n\n"
        md += "| מונח בעברית | English | הגדרה קצרה |\n"
        md += "|-------------|---------|------------|\n"
        for term in brief.get("key_terms", []):
            md += f"| {term.get('hebrew', '')} | {term.get('english', '')} | מושג מרכזי |\n"
        md += "\n"
        
        # Practice questions
        md += "---\n\n"
        md += "## שאלות לתרגול\n\n"
        md += "### שאלות אמריקאיות\n\n"
        
        for i, target in enumerate(brief.get("mcq_targets", [])[:4], 1):
            md += f"**{i}.** שאלה על {target}?\n\n"
            md += "   א. אפשרות 1\n"
            md += "   ב. אפשרות 2\n"
            md += "   ג. אפשרות 3\n"
            md += "   ד. אפשרות 4\n\n"
            md += f"   **תשובה:** ג – רציונל לתשובה.\n\n"
        
        md += "### שאלות קצרות\n\n"
        for i, target in enumerate(brief.get("short_answer_targets", [])[:2], 1):
            md += f"**{i}.** הסבר את {target}.\n\n"
            md += "**תשובה לדוגמה:** [תשובה]\n\n"
        
        md += "### שאלת חשיבה\n\n"
        md += f"**{brief.get('thinking_question_target', 'שאלה')}**\n\n"
        md += "**קווים מנחים:** נקודות לכסות בתשובה.\n\n"
        
        word_count = len(md.split())
        
        return DraftChapter(
            chapter_id=chapter_id,
            title=title,
            content_md=md,
            word_count=word_count,
            has_objectives=True,
            has_roadmap=True,
            has_summary=True,
            has_key_terms=True,
            has_questions=True,
            todos=["Expand content with Gemini or manually"]
        )
