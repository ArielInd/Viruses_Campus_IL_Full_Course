"""
Agent E: DevelopmentalEditor (Quality-First Edition)

Active editing using gemini-2.5-pro:
- Rewriting transitions between sections
- Pedagogical flow optimization
- Opening hooks and closing summaries
- Complexity adaptation per topic

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import json
from typing import Dict, Optional

# Use the new unified Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")

from .schemas import (
    EditedChapter, PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "DevelopmentalEditor"

# Gemini configuration - PRO for quality
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Map of existing high-quality chapters
EXISTING_CHAPTERS = {
    "01": "01_introduction_cells.md",
    "02": "02_macromolecules.md",
    "03": "03_chapter_viruses_intro.md",
    "04": "04_chapter_human_diseases.md",
    "05": "05_chapter_innate_immunity.md",
    "06": "06_chapter_adaptive_immunity.md",
    "07": "07_chapter_vaccines.md",
    "08": "08_chapter_coronavirus.md",
}


class DevelopmentalEditor:
    """
    Agent E: Quality-First Developmental Editor
    
    Uses Gemini 3 Pro for active editing:
    - Rewrites weak transitions
    - Improves opening hooks
    - Ensures learning objectives match content
    - Adapts complexity to topic difficulty
    
    Output: /book/chapters/*.md and edit memos in /ops/reports/edit_memos/
    """
    
    SYSTEM_PROMPT = """אתה עורך פיתוח (Developmental Editor) בכיר לספרי לימוד אקדמיים.

תפקידך: לשפר את הטקסט מבחינה פדגוגית ומבנית.

## בדיקות נדרשות

### 1. מבנה פדגוגי
- האם מטרות הלמידה ברורות ומדידות?
- האם יש התקדמות מפשוט למורכב?
- האם הסיכום תואם את המטרות?

### 2. מעברים (Transitions)
- האם יש חיבור לוגי בין חלקים?
- האם יש הקדמה לכל נושא חדש?
- האם יש סיכום ביניים בחלקים ארוכים?

### 3. פתיחה וסיום
- האם יש "Hook" מעניין בתחילת הפרק?
- האם הסיכום מגבש את הנלמד?

### 4. דוגמאות והמחשות
- האם יש מספיק דוגמאות מציאותיות?
- האם יש המחשות ויזואליות (תיאורי איורים)?

### 5. רמת קושי
- האם הטקסט מותאם לרמת הסטודנט?
- האם מונחים מוסברים לפני השימוש בהם?

## פלט נדרש

החזר JSON בפורמט:
{
  "analysis": {
    "structure_score": 0.0-1.0,
    "transitions_score": 0.0-1.0,
    "examples_score": 0.0-1.0,
    "overall_score": 0.0-1.0
  },
  "issues": [
    {
      "location": "## כותרת הסעיף",
      "type": "transition|structure|examples|complexity",
      "severity": "minor|moderate|major",
      "description": "תיאור הבעיה",
      "suggestion": "הצעה לתיקון"
    }
  ],
  "improvements_made": [
    "שיפור 1",
    "שיפור 2"
  ],
  "edited_content": "התוכן המלא אחרי עריכה"
}
"""
    
    def __init__(self, ops_dir: str, book_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.book_dir = book_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.memos_dir = os.path.join(ops_dir, "reports", "edit_memos")
        self.drafts_dir = os.path.join(ops_dir, "artifacts", "drafts", "chapters")
        
        # Initialize Gemini client (new SDK)
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (Active Editing Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Using passive validation mode")
        
        os.makedirs(self.chapters_dir, exist_ok=True)
        os.makedirs(self.memos_dir, exist_ok=True)
    
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,  # Balanced for editing
                    max_output_tokens=16384,
                )
            )
            return response.text
        except Exception as e:
            print(f"[{AGENT_NAME}] Generation error: {e}")
            return None
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Load chapter plan
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        print(f"[{AGENT_NAME}] Processing {len(chapter_plans)} chapters (Active Editing Mode)")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Check for existing high-quality chapter
            existing_file = EXISTING_CHAPTERS.get(chapter_id)
            existing_path = os.path.join(self.chapters_dir, existing_file) if existing_file else None
            
            if existing_path and os.path.exists(existing_path):
                # Enhance existing chapter
                result = self._enhance_existing(chapter_id, existing_path, plan)
                output_files.append(existing_path)
            else:
                # Develop from draft
                draft_path = os.path.join(self.drafts_dir, f"{chapter_id}_chapter_draft.md")
                if os.path.exists(draft_path):
                    result = self._develop_draft(chapter_id, draft_path, plan)
                    output_path = os.path.join(self.chapters_dir, f"{chapter_id}_chapter.md")
                    save_markdown(result.content_md, output_path)
                    output_files.append(output_path)
                else:
                    warnings.append(f"No draft found for chapter {chapter_id}")
                    continue
            
            # Generate and save memo
            memo = self._generate_memo(chapter_id, result)
            memo_path = os.path.join(self.memos_dir, f"chapter_{chapter_id}_memo.md")
            save_markdown(memo, memo_path)
            
            print(f"[{AGENT_NAME}] ✓ Chapter {chapter_id}: score={result.quality_score:.0%}")
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "chapters_dir": self.chapters_dir,
            "memos_dir": self.memos_dir,
            "num_chapters": len(output_files)
        }
    
    def _enhance_existing(self, chapter_id: str, path: str, plan: Dict) -> EditedChapter:
        """Enhance an existing high-quality chapter with active editing."""
        content = read_file(path)
        
        if self.client:
            return self._edit_with_llm(chapter_id, content, plan, path)
        else:
            return self._validate_passively(chapter_id, content, plan)
    
    def _develop_draft(self, chapter_id: str, path: str, plan: Dict) -> EditedChapter:
        """Develop a draft into a fully edited chapter."""
        content = read_file(path)
        
        if self.client:
            return self._edit_with_llm(chapter_id, content, plan, path)
        else:
            return self._validate_passively(chapter_id, content, plan)
    
    def _edit_with_llm(self, chapter_id: str, content: str, plan: Dict, 
                       source_path: str) -> EditedChapter:
        """Active editing using Gemini 3 Pro."""
        import time
        
        title = plan.get("hebrew_title", f"פרק {chapter_id}")
        
        prompt = f"""{self.SYSTEM_PROMPT}

---
פרק: {chapter_id} - {title}

תוכן לעריכה:
{content}

---
ערוך את התוכן ושפר אותו. החזר JSON מלא כולל edited_content.
"""
        
        text = self._generate(prompt)
        
        if text:
            try:
                # Extract JSON
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    
                    analysis = data.get("analysis", {})
                    issues = data.get("issues", [])
                    improvements = data.get("improvements_made", [])
                    edited_content = data.get("edited_content", content)
                    
                    # Use edited content if valid
                    if edited_content and len(edited_content) > len(content) * 0.5:
                        final_content = edited_content
                    else:
                        final_content = content
                    
                    word_count = len(final_content.split())
                    quality_score = analysis.get("overall_score", 0.8)
                    
                    edit_notes = improvements + [f"Issue: {i['description']}" for i in issues[:5]]
                    
                    time.sleep(5)  # Rate limiting
                    
                    return EditedChapter(
                        chapter_id=chapter_id,
                        title=title,
                        content_md=final_content,
                        word_count=word_count,
                        edit_notes=edit_notes,
                        quality_score=quality_score
                    )
            except Exception as e:
                print(f"[{AGENT_NAME}] JSON parsing error for chapter {chapter_id}: {e}")
                self.todos.add(AGENT_NAME, source_path, f"LLM editing failed: {e}")
        
        # Fallback to passive validation
        return self._validate_passively(chapter_id, content, plan)
    
    def _validate_passively(self, chapter_id: str, content: str, plan: Dict) -> EditedChapter:
        """Passive validation without LLM (fallback)."""
        title = plan.get("hebrew_title", f"פרק {chapter_id}")
        edit_notes = []
        
        # Check required sections
        required_sections = [
            ("מטרות למידה", "## מטרות למידה"),
            ("מפת דרכים", "## מפת דרכים"),
            ("סיכום מהיר", "## סיכום מהיר"),
            ("מושגי מפתח", "## מושגי מפתח"),
            ("שאלות לתרגול", "## שאלות לתרגול"),
        ]
        
        for name, marker in required_sections:
            if marker not in content:
                edit_notes.append(f"Missing: {name}")
                self.todos.add(AGENT_NAME, f"chapter_{chapter_id}", f"Add {name} section")
        
        # Check for misconceptions section
        if "טעויות נפוצות" not in content:
            edit_notes.append("Consider adding טעויות נפוצות section")
        
        # Remove lecture-style phrases
        lecture_phrases = [
            "כפי שראינו בשקף",
            "בשקף הזה",
            "כפי שאמרתי",
            "בואו נראה",
            "שלום לכולם",
            "היי",
        ]
        
        cleaned_content = content
        for phrase in lecture_phrases:
            if phrase in cleaned_content:
                cleaned_content = cleaned_content.replace(phrase, "")
                edit_notes.append(f"Removed lecture phrase: {phrase}")
        
        word_count = len(cleaned_content.split())
        quality_score = 1.0 - (len(edit_notes) * 0.05)  # Deduct for issues
        
        return EditedChapter(
            chapter_id=chapter_id,
            title=title,
            content_md=cleaned_content,
            word_count=word_count,
            edit_notes=edit_notes,
            quality_score=max(0.5, quality_score)
        )
    
    def _generate_memo(self, chapter_id: str, result: EditedChapter) -> str:
        """Generate detailed edit memo."""
        md = f"# Edit Memo: Chapter {chapter_id}\n\n"
        md += f"**Title:** {result.title}\n\n"
        md += f"**Word Count:** {result.word_count}\n\n"
        md += f"**Quality Score:** {result.quality_score:.0%}\n\n"
        
        md += "---\n\n"
        md += "## Edit Notes\n\n"
        if result.edit_notes:
            for note in result.edit_notes:
                md += f"- {note}\n"
        else:
            md += "✅ No significant issues found.\n"
        
        md += f"\n---\n\n*Generated by {AGENT_NAME} (Active Editing Mode)*\n"
        
        return md
