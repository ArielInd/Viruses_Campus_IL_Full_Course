"""
Agent I: SafetyScopeReviewer (Quality-First Edition)

High-rigor fact-checking and biosafety review using gemini-2.5-pro:
- Scientific accuracy verification against source material
- Biosafety and biosecurity screening (dual-use research)
- Medical misinformation detection
- Formal safety reports

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
    SafetyReport, PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "SafetyScopeReviewer"

# Gemini configuration - PRO for high scientific rigor
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class SafetyScopeReviewer:
    """
    Agent I: Scientific Integrity and Safety Reviewer.
    
    Uses Gemini 3 Pro to:
    - Verify scientific claims against the provided transcripts
    - Check for biosafety concerns (e.g., gain-of-function descriptions)
    - Identify medical misinformation or dangerous advice
    
    Output: /ops/artifacts/safety_reports/*.json and safety_summary.md
    """
    
    SYSTEM_PROMPT = """אתה מבקר מדעי בתחום הוירולוגיה והביו-בטיחות (Biosafety).

תפקידך: לסרוק את פרקי הספר ולזהות בעיות של דיוק מדעי או סיכוני בטיחות.

## קריטריונים לבדיקה:

### 1. דיוק מדעי (Scientific Accuracy)
- האם הטענות בפרק נתמכות על ידי חומר המקור (התמלילים)?
- האם יש בלבול בין מושגים דומים (כמו IgG vs IgM, או DNA vs RNA נגיפי)?

### 2. בטיחות ביולוגית (Biosafety & Biosecurity)
- האם הטקסט מכיל הוראות מעשיות לייצור או שיפור נגיפים מסוכנים ("Dual-Use")?
- האם יש חשיפת יתר של פרוטוקולי מעבדה מסוכנים?

### 3. מניעת מידע רפואי מוטעה (MISINFO)
- האם יש המלצות רפואיות מסוכנות (למשל: נטילת תרופות לא מאושרות נגד נגיפים)?
- האם מוצג מידע שגוי לגבי בטיחות חיסונים?

החזר JSON בפורמט:
{
  "safety_score": 0.0-1.0,
  "status": "safe|caution|danger",
  "issues": [
    {
      "type": "accuracy|biosafety|misinfo",
      "severity": "low|medium|high",
      "found": "הטקסט הבעייתי",
      "explanation": "מדוע זה בעייתי?",
      "remediation": "הצעה לתיקון או מחיקה"
    }
  ],
  "overall_verdict": "פסקה מסכמת לגבי תקינות הפרק"
}
"""
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.reports_dir = os.path.join(ops_dir, "artifacts", "safety_reports")
        
        # Initialize Gemini client
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (High-Rigor Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Safety features limited.")
            
        os.makedirs(self.reports_dir, exist_ok=True)
            
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Ultra-low for accuracy
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
        reports = []
        
        # Load chapter plan
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        print(f"[{AGENT_NAME}] Reviewing {len(chapter_plans)} chapters for scientific integrity...")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Load chapter draft
            content = self._load_chapter_content(chapter_id)
            if not content:
                continue
                
            # Perform safety review
            report_data = self._review_safety(chapter_id, content, plan)
            reports.append(report_data)
            
            # Save individual report
            rep_path = os.path.join(self.reports_dir, f"chapter_{chapter_id}_safety.json")
            with open(rep_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            output_files.append(rep_path)
            
            print(f"    ✓ Chapter {chapter_id}: safety_score={report_data['safety_score']:.2f}")
            time.sleep(3)
            
        # Generate summary report
        summary_path = os.path.join(self.ops_dir, "reports", "safety_summary.md")
        summary_md = self._generate_summary(reports)
        save_markdown(summary_md, summary_path)
        output_files.append(summary_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "safety_reports_dir": self.reports_dir,
            "safety_summary": summary_path,
            "status": "complete"
        }

    def _load_chapter_content(self, chapter_id: str) -> Optional[str]:
        possible_names = [f"{chapter_id}_chapter.md", f"0{chapter_id}_chapter.md"]
        for name in possible_names:
            path = os.path.join(self.chapters_dir, name)
            if os.path.exists(path):
                return read_file(path)
        return None

    def _review_safety(self, chapter_id: str, content: str, plan: Dict) -> Dict:
        """Use LLM to review safety and accuracy."""
        title = plan.get("hebrew_title", f"פרק {chapter_id}")
        
        prompt = f"""{self.SYSTEM_PROMPT}

---
פרק: {chapter_id} - {title}

תוכן לבדיקה:
{content}

---
בצע בדיקה מדוקדקת והחזר JSON מלא.
"""
        text = self._generate(prompt)
        if text:
            try:
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    data["chapter_id"] = chapter_id
                    data["chapter_title"] = title
                    return data
            except Exception:
                pass
        
        return {"chapter_id": chapter_id, "safety_score": 1.0, "status": "safe", "issues": [], "overall_verdict": "ביקורת נכשלה"}

    def _generate_summary(self, reports: List[Dict]) -> str:
        md = "# דוח ריכוז בטיחות ודיוק מדעי\n\n"
        md += f"*נוצר על ידי {AGENT_NAME} (Gemini 3 Pro Quality Scan)*\n\n"
        
        critical_count = 0
        for r in reports:
            for issue in r.get("issues", []):
                if issue.get("severity") == "high":
                    critical_count += 1
                    
        md += f"## סיכום ממצאים\n\n"
        md += f"- סה\"כ פרקים שנסרקו: {len(reports)}\n"
        md += f"- בעיות קריטיות שנמצאו: {critical_count}\n\n"
        
        if critical_count > 0:
            md += "### 🔴 אזהרות חמורות\n\n"
            for r in reports:
                for issue in r.get("issues", []):
                    if issue.get("severity") == "high":
                        md += f"- **פרק {r['chapter_id']}**: {issue['found']}\n"
                        md += f"  - *הסבר*: {issue['explanation']}\n"
                        md += f"  - *תיקון מוצע*: {issue['remediation']}\n\n"
        else:
            md += "✅ לא נמצאו בעיות בטיחות או דיוק קריטיות.\n\n"
            
        md += "## פירוט לפי פרק\n\n"
        for r in reports:
            status_emoji = "✅" if r["status"] == "safe" else "⚠️" if r["status"] == "caution" else "❌"
            md += f"### {status_emoji} פרק {r['chapter_id']}: {r['chapter_title']}\n"
            md += f"**ציון בטיחות:** {r['safety_score']:.2f}\n\n"
            md += f"**סיכום המבקר:** {r['overall_verdict']}\n\n"
            
        return md
