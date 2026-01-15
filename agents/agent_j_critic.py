"""
Agent J: Adversarial Critic (NEW)

A "Devil's Advocate" agent that finds flaws before the Dev Editor.
Uses gemini-2.5-pro to critically analyze drafts and provide structured feedback.

This agent does NOT write content - it only finds problems.

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

AGENT_NAME = "AdversarialCritic"

# Gemini configuration - PRO for deep analysis
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class AdversarialCritic:
    """
    Agent J: Adversarial Critic
    
    A "Devil's Advocate" that tries to find flaws in drafts before editing.
    
    Critique Dimensions:
    1. Clarity: Where is this explanation confusing?
    2. Consistency: Does terminology match previous chapters?
    3. Completeness: What key concepts from the source are missing?
    4. Accuracy: Does anything contradict the source material?
    
    Output: /ops/artifacts/critiques/*.json with structured feedback
    """
    
    SYSTEM_PROMPT = """אתה מבקר אקדמי חמור (Adversarial Critic) לספרי לימוד.

תפקידך: למצוא בעיות בטיוטה לפני שהיא עוברת לעריכה.
אתה לא כותב תוכן - רק מוצא בעיות.

## ממדי הביקורת

### 1. בהירות (Clarity)
- איפה ההסבר מבלבל?
- אילו משפטים ארוכים מדי או מסורבלים?
- איפה חסר הקשר לקורא מתחיל?

### 2. עקביות (Consistency)
- האם המונחים תואמים את הגלוסרי?
- האם יש סתירות פנימיות בפרק?
- האם הסגנון אחיד לאורך הטקסט?

### 3. שלמות (Completeness)
- אילו מושגי מפתח חסרים?
- האם יש "קפיצות" לוגיות?
- האם כל מטרת הלמידה מכוסה?

### 4. דיוק (Accuracy)
- האם יש טענות שלא נתמכות במקור?
- האם יש הגזמות או פישוטי יתר?
- האם המספרים והנתונים נכונים?

### 5. פדגוגיה (Pedagogy)
- האם יש מספיק דוגמאות?
- האם רמת הקושי מותאמת?
- האם יש "Hook" מעניין?

## חומרת בעיות

- **critical**: חייב לתקן לפני פרסום (שגיאה עובדתית, סתירה חמורה)
- **major**: משפיע משמעותית על הלמידה (בלבול, חוסר שלמות)
- **minor**: ראוי לתיקון אך לא הכרחי (סגנון, ניסוח)

## פלט נדרש

החזר JSON בפורמט:
{
  "chapter_id": "XX",
  "overall_assessment": "pass|needs_revision|reject",
  "confidence_score": 0.0-1.0,
  "critique_summary": "סיכום קצר של הבעיות העיקריות",
  "issues": [
    {
      "id": 1,
      "dimension": "clarity|consistency|completeness|accuracy|pedagogy",
      "severity": "critical|major|minor",
      "location": "## כותרת או מספר שורה",
      "quote": "הציטוט הבעייתי",
      "problem": "תיאור הבעיה",
      "suggestion": "הצעה לתיקון"
    }
  ],
  "strengths": [
    "נקודת חוזק 1",
    "נקודת חוזק 2"
  ],
  "revision_priority": [
    "תיקון 1 (הכי חשוב)",
    "תיקון 2",
    "תיקון 3"
  ]
}
"""
    
    def __init__(self, ops_dir: str, book_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.book_dir = book_dir
        self.logger = logger
        self.todos = todos
        self.drafts_dir = os.path.join(ops_dir, "artifacts", "drafts", "chapters")
        self.critiques_dir = os.path.join(ops_dir, "artifacts", "critiques")
        
        # Initialize Gemini client (new SDK)
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (Adversarial Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] No LLM available - skipping critique")
        
        os.makedirs(self.critiques_dir, exist_ok=True)
    
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower for analytical thinking
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
        critiques = []
        
        if not self.client:
            print(f"[{AGENT_NAME}] Skipping - no LLM available")
            return {"critiques": [], "skipped": True}
        
        # Load chapter plan
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        print(f"[{AGENT_NAME}] Critiquing {len(chapter_plans)} drafts...")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Load draft
            draft_path = os.path.join(self.drafts_dir, f"{chapter_id}_chapter_draft.md")
            if not os.path.exists(draft_path):
                warnings.append(f"No draft found for chapter {chapter_id}")
                continue
            
            content = read_file(draft_path)
            
            # Generate critique
            critique = self._critique_chapter(chapter_id, content, plan)
            critiques.append(critique)
            
            # Save critique
            critique_path = os.path.join(self.critiques_dir, f"chapter_{chapter_id}_critique.json")
            with open(critique_path, 'w', encoding='utf-8') as f:
                json.dump(critique, f, ensure_ascii=False, indent=2)
            output_files.append(critique_path)
            
            # Report status
            assessment = critique.get("overall_assessment", "unknown")
            num_issues = len(critique.get("issues", []))
            critical = sum(1 for i in critique.get("issues", []) if i.get("severity") == "critical")
            
            status_emoji = "✓" if assessment == "pass" else "⚠" if assessment == "needs_revision" else "✗"
            print(f"[{AGENT_NAME}] {status_emoji} Chapter {chapter_id}: {assessment} ({num_issues} issues, {critical} critical)")
            
            time.sleep(5)  # Rate limiting
        
        # Generate summary report
        reports_dir = os.path.join(self.ops_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, "critique_summary.md")
        report_md = self._generate_summary_report(critiques)
        save_markdown(report_md, report_path)
        output_files.append(report_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        # Count chapters needing revision
        needs_revision = sum(1 for c in critiques if c.get("overall_assessment") != "pass")
        
        return {
            "critiques_dir": self.critiques_dir,
            "num_critiques": len(critiques),
            "needs_revision": needs_revision,
            "summary_report": report_path
        }
    
    def _critique_chapter(self, chapter_id: str, content: str, plan: Dict) -> Dict:
        """Generate adversarial critique for a chapter draft."""
        title = plan.get("hebrew_title", f"פרק {chapter_id}")
        
        prompt = f"""{self.SYSTEM_PROMPT}

---
פרק: {chapter_id} - {title}

טיוטה לביקורת:
{content}

---
בצע ביקורת מפורטת והחזר JSON.
"""
        
        text = self._generate(prompt)
        
        if text:
            try:
                # Extract JSON
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    critique = json.loads(text[json_start:json_end])
                    critique["chapter_id"] = chapter_id
                    return critique
            except Exception as e:
                print(f"[{AGENT_NAME}] Critique parsing failed for chapter {chapter_id}: {e}")
                self.todos.add(AGENT_NAME, f"chapter_{chapter_id}", f"Critique failed: {e}")
        
        # Return minimal critique on failure
        return {
            "chapter_id": chapter_id,
            "overall_assessment": "unknown",
            "confidence_score": 0.0,
            "critique_summary": "Critique generation failed",
            "issues": [],
            "strengths": [],
            "revision_priority": []
        }
    
    def _generate_summary_report(self, critiques: List[Dict]) -> str:
        """Generate summary report of all critiques."""
        md = "# דוח ביקורת (Critique Summary)\n\n"
        md += f"*נוצר על ידי {AGENT_NAME}*\n\n"
        md += "---\n\n"
        
        # Overall stats
        total = len(critiques)
        passed = sum(1 for c in critiques if c.get("overall_assessment") == "pass")
        needs_rev = sum(1 for c in critiques if c.get("overall_assessment") == "needs_revision")
        rejected = sum(1 for c in critiques if c.get("overall_assessment") == "reject")
        
        md += "## סיכום כללי\n\n"
        md += f"- **סה\"כ פרקים**: {total}\n"
        md += f"- ✅ עברו: {passed}\n"
        md += f"- ⚠️ דורשים תיקון: {needs_rev}\n"
        md += f"- ❌ נדחו: {rejected}\n\n"
        
        # Issue breakdown
        all_issues = []
        for c in critiques:
            for issue in c.get("issues", []):
                issue["chapter_id"] = c.get("chapter_id")
                all_issues.append(issue)
        
        critical = [i for i in all_issues if i.get("severity") == "critical"]
        major = [i for i in all_issues if i.get("severity") == "major"]
        minor = [i for i in all_issues if i.get("severity") == "minor"]
        
        md += "## התפלגות בעיות\n\n"
        md += f"- 🔴 קריטיות: {len(critical)}\n"
        md += f"- 🟠 משמעותיות: {len(major)}\n"
        md += f"- 🟢 קלות: {len(minor)}\n\n"
        
        # Critical issues list
        if critical:
            md += "## ⚠️ בעיות קריטיות לתיקון מיידי\n\n"
            for issue in critical:
                chap = issue.get("chapter_id", "?")
                dim = issue.get("dimension", "?")
                prob = issue.get("problem", "?")
                md += f"- **פרק {chap}** [{dim}]: {prob}\n"
            md += "\n"
        
        # Per-chapter summary
        md += "## פירוט לפי פרק\n\n"
        
        for critique in critiques:
            chap = critique.get("chapter_id", "?")
            assessment = critique.get("overall_assessment", "?")
            summary = critique.get("critique_summary", "")
            issues = critique.get("issues", [])
            strengths = critique.get("strengths", [])
            
            emoji = "✅" if assessment == "pass" else "⚠️" if assessment == "needs_revision" else "❌"
            
            md += f"### {emoji} פרק {chap}\n\n"
            md += f"**הערכה**: {assessment}\n\n"
            
            if summary:
                md += f"**סיכום**: {summary}\n\n"
            
            if strengths:
                md += "**נקודות חוזק**:\n"
                for s in strengths[:3]:
                    md += f"- {s}\n"
                md += "\n"
            
            if issues:
                md += f"**בעיות** ({len(issues)}):\n"
                for issue in issues[:5]:
                    sev = issue.get("severity", "?")
                    dim = issue.get("dimension", "?")
                    prob = issue.get("problem", "?")[:100]
                    md += f"- [{sev}] {dim}: {prob}\n"
                md += "\n"
        
        md += "---\n\n"
        md += "*הערה: יש לתקן את כל הבעיות הקריטיות לפני פרסום.*\n"
        
        return md
