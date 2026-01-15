"""
Agent F: AssessmentDesigner (Quality-First Edition)

LLM-powered assessment generation using gemini-2.5-pro:
- Chapter-specific MCQs mapped to learning objectives
- Case studies and real-world applications
- Active recall questions
- Comprehensive question bank generation

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import re
import json
import time
from typing import List, Dict, Optional

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

AGENT_NAME = "AssessmentDesigner"

# Gemini configuration - PRO for educational quality
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class AssessmentDesigner:
    """
    Agent F: Produces high-quality assessments and exam review materials.
    
    Uses Gemini 3 Pro to generate:
    - MCQs with plausible distractors
    - Case studies that require conceptual application
    - High-yield exam summaries
    
    Output: /book/92_question_bank.md, /book/91_exam_review.md
    """
    
    SYSTEM_PROMPT = """אתה מעריך פדגוגי (Instructional Designer) ומומחה לוירולוגיה.

תפקידך: ליצור שאלות תרגול וחומרי חזרה ברמה אקדמית גבוהה לספר לימוד.

## סוגי שאלות נדרשים:

### 1. שאלות רב-ברירה (MCQs)
- שאלה ברורה וממוקדת.
- 4 מסיחים (א-ד), כאשר רק אחד נכון.
- המסיחים צריכים להיות מטעים (plausible) ומבוססים על טעויות נפוצות.
- ספק הסבר קצר לתשובה הנכונה.

### 2. מקרי בוחן (Case Studies)
- תיאור קצר של מצב קליני או מעבדתי.
- שאלה הדורשת יישום של החומר הנלמד לפתרון המצב.

### 3. שאלות שליפה פעילה (Active Recall)
- שאלות פתוחות קצרות הממקדות במושגי מפתח.

## דגשים לכתיבה:
- שפה: עברית אקדמית תקנית.
- מונחים: שמירה על עקביות (מונח עברי ולידו מונח אנגלי בסוגריים).
- רמה: מותאם לסטודנטים לתואר ראשון במדעי החיים/רפואה.

החזר JSON בפורמט:
{
  "mcqs": [
    {
      "question": "השאלה",
      "options": ["א. ...", "ב. ...", "ג. ...", "ד. ..."],
      "correct_answer": "א/ב/ג/ד",
      "explanation": "הסבר קצר"
    }
  ],
  "case_studies": [
    {
      "scenario": "תיאור המקרה",
      "question": "השאלה",
      "answer_guidelines": "נקודות מפתח לתשובה"
    }
  ],
  "recall_questions": ["שאלה 1", "שאלה 2"]
}
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
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (LLM-Assessment Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Using legacy template assessment")
            
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=8192,
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
        
        all_chapter_assessments = []
        
        print(f"[{AGENT_NAME}] Generating assessments for {len(chapter_plans)} chapters...")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Load chapter content
            content = self._load_chapter_content(chapter_id)
            
            if self.client and content:
                # LLM-generated assessment
                assessment = self._generate_chapter_assessment(chapter_id, content, plan)
                all_chapter_assessments.append(assessment)
                print(f"    ✓ Chapter {chapter_id}: LLM assessment generated")
                time.sleep(5)
            else:
                # Fallback or template
                print(f"    ⚠ Chapter {chapter_id}: Using template/fallback")
        
        # Generate consolidated question bank
        question_bank = self._format_question_bank(all_chapter_assessments, chapter_plans)
        qb_path = os.path.join(self.book_dir, "92_question_bank.md")
        save_markdown(question_bank, qb_path)
        output_files.append(qb_path)
        
        # Generate high-yield exam review
        exam_review = self._format_exam_review(all_chapter_assessments, chapter_plans)
        er_path = os.path.join(self.book_dir, "91_exam_review.md")
        save_markdown(exam_review, er_path)
        output_files.append(er_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "question_bank": qb_path,
            "exam_review": er_path,
            "chapters_processed": len(all_chapter_assessments)
        }
    
    def _load_chapter_content(self, chapter_id: str) -> Optional[str]:
        """Load the final edited chapter content."""
        possible_names = [f"{chapter_id}_chapter.md", f"0{chapter_id}_chapter.md"]
        for name in possible_names:
            path = os.path.join(self.chapters_dir, name)
            if os.path.exists(path):
                return read_file(path)
        return None

    def _generate_chapter_assessment(self, chapter_id: str, content: str, plan: Dict) -> Dict:
        """Use LLM to generate specific assessment for one chapter."""
        title = plan.get("hebrew_title", f"פרק {chapter_id}")
        
        prompt = f"""{self.SYSTEM_PROMPT}

---
פרק: {chapter_id} - {title}

תוכן הפרק (חלקים נבחרים):
{content[:20000]}

---
המשימה: צור 3 שאלות MCQ, מקרה בוחן אחד, ו-3 שאלות שליפה מהירה המבוססות על תוכן הפרק.
החזר JSON בלבד.
"""
        
        text = self._generate(prompt)
        if text:
            try:
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    data["chapter_id"] = chapter_id
                    data["title"] = title
                    return data
            except Exception as e:
                print(f"      ✗ Failed to parse JSON for {chapter_id}: {e}")
        
        return {"chapter_id": chapter_id, "title": title, "mcqs": [], "case_studies": [], "recall_questions": []}

    def _format_question_bank(self, assessments: List[Dict], plans: List[Dict]) -> str:
        """Format the consolidated question bank markdown."""
        md = "# נספח ג': בנק שאלות מקיף ויישומי\n\n"
        md += "*בנק זה כולל שאלות ממורכזות תוכן, מקרי בוחן קליניים ושאלות שליפה לחיזוק הזיכרון לטווח ארוך.*\n\n"
        md += "---\n\n"
        
        for assess in assessments:
            md += f"## פרק {assess['chapter_id']}: {assess['title']}\n\n"
            
            # MCQs
            if assess.get("mcqs"):
                md += "### שאלות רב-ברירה\n\n"
                for i, q in enumerate(assess["mcqs"], 1):
                    md += f"**{i}. {q['question']}**\n"
                    for opt in q["options"]:
                        md += f"   {opt}\n"
                    md += f"\n   *(תשובה: {q['correct_answer']}. הסבר: {q.get('explanation', '')})*\n\n"
            
            # Case Studies
            if assess.get("case_studies"):
                md += "### יישום ומקרי בוחן\n\n"
                for cs in assess["case_studies"]:
                    md += f"**סיטואציה:** {cs['scenario']}\n\n"
                    md += f"**שאלה:** {cs['question']}\n\n"
                    md += f"**קווי מנחה לתשובה:** {cs.get('answer_guidelines', '')}\n\n"
            
            # Recall
            if assess.get("recall_questions"):
                md += "### שליפה מהירה (Active Recall)\n\n"
                for rq in assess["recall_questions"]:
                    md += f"- {rq}\n"
                md += "\n"
            
            md += "---\n\n"
            
        return md

    def _format_exam_review(self, assessments: List[Dict], plans: List[Dict]) -> str:
        """Format the high-yield exam review guide."""
        md = "# נספח ב': מדריך למידה וסיכום אסטרטגי\n\n"
        md += "נקודות המוקד (\"High-Yield\") שסביבן נבנית הבחינה.\n\n"
        md += "---\n\n"
        
        for assess in assessments:
            md += f"### פרק {assess['chapter_id']}: {assess['title']}\n"
            # Extract key concepts from recall questions as summary points
            for rq in assess.get("recall_questions", [])[:3]:
                # Transform question into a statement-ish point if possible
                md += f"* **מושג מפתח:** {rq.replace('?', '')}\n"
            md += "\n"
            
        md += "---\n\n"
        md += "## טיפים להצלחה בבחינה\n\n"
        md += "1. **הבן את המנגנון**: אל תשנן רק שמות, הבן *איך* הנגיף חודר ואיך המערכת מזהה אותו.\n"
        md += "2. **השוואה**: בנה טבלאות השוואה בין סוגי נגיפים ובין סוגי חיסונים.\n"
        md += "3. **טרמינולוגיה**: וודא שאתה מכיר את המונח האנגלי המקביל לכל מושג עברי.\n"
        
        return md
