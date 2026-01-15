"""
Agent H: CopyeditorProofreader (Quality-First Edition)

LLM-powered linguistic analysis using gemini-2.5-pro:
- Academic register enforcement
- Hebrew morphological correctness
- Spoken-artifact removal
- Deep grammatical analysis

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
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
    save_markdown, read_file
)

AGENT_NAME = "CopyeditorProofreader"

# Gemini configuration - PRO for quality
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class CopyeditorProofreader:
    """
    Agent H: LLM-Powered Proofreader
    
    Uses Gemini 3 Pro to perform deep linguistic analysis:
    - Academic register (formal vs. colloquial)
    - Hebrew morphological correctness
    - Spoken-artifact detection and removal
    - Terminology consistency
    
    Output: Corrected chapters + proof_log.md with detailed feedback
    """
    
    SYSTEM_PROMPT = """אתה עורך לשון בכיר (Senior Copy Editor) לספרי לימוד אקדמיים בעברית.

תפקידך: לבדוק ולתקן את הטקסט לפי הקריטריונים הבאים:

## 1. רישום אקדמי (Academic Register)
- הסר ניסוחי הרצאה: "כפי שראינו", "בשקף הזה", "היי", "בואו נראה"
- החלף בניסוחי ספר: "כפי שיוסבר בהמשך", "איור X מציג", "ניתן לראות כי"
- הימנע מפניות ישירות לקורא ("אתם", "תבחינו")

## 2. דקדוק עברי (Hebrew Grammar)
- בדוק התאמה במין ומספר בין נושא לפועל
- וודא שימוש נכון בסמיכות
- תקן שגיאות כתיב נפוצות

## 3. עקביות טרמינולוגית
- מונחים מדעיים נשארים באנגלית: DNA, RNA, mRNA, PCR, MHC, ELISA
- הגדרות בפורמט: **מונח בעברית** (English Term)
- אותו מונח = אותו תרגום בכל הטקסט

## 4. מבנה ועיצוב
- כותרות: # (פרק) → ## (תת-פרק) → ### (נושא)
- רשימות: תבליטים עם מקף (-)
- טבלאות: פורמט Markdown תקין

## פלט נדרש
החזר JSON בפורמט:
{
  "issues": [
    {
      "line": 12,
      "type": "lecture_style|grammar|terminology|structure",
      "severity": "minor|moderate|major",
      "original": "הטקסט המקורי",
      "corrected": "הטקסט המתוקן",
      "explanation": "הסבר קצר"
    }
  ],
  "summary": {
    "total_issues": 5,
    "critical_issues": 1,
    "recommendation": "אישור|דורש תיקון"
  },
  "corrected_content": "הטקסט המלא אחרי תיקונים"
}
"""
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        
        # Initialize Gemini client (new SDK)
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (LLM-Powered Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Using regex-based fallback")
    
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Low for precise editing
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
        all_issues = []
        files_checked = 0
        files_corrected = 0
        
        # Process all markdown files
        for root, dirs, files in os.walk(self.book_dir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                path = os.path.join(root, filename)
                
                if self.client:
                    # LLM-powered proofreading
                    issues, corrected = self._proofread_with_llm(path)
                    if corrected:
                        files_corrected += 1
                else:
                    # Regex fallback
                    issues = self._proofread_regex(path)
                    corrected = False
                
                all_issues.extend(issues)
                files_checked += 1
        
        # Save proof log
        log_path = os.path.join(self.ops_dir, "reports", "proof_log.md")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_md = self._generate_log(all_issues, files_checked, files_corrected)
        save_markdown(log_md, log_path)
        output_files.append(log_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Checked {files_checked} files, found {len(all_issues)} issues, corrected {files_corrected}")
        
        return {
            "proof_log": log_path,
            "files_checked": files_checked,
            "files_corrected": files_corrected,
            "issues_found": len(all_issues)
        }
    
    def _proofread_with_llm(self, path: str) -> tuple:
        """
        LLM-powered proofreading with automatic correction.
        Returns (issues_list, was_corrected).
        """
        import json
        import time
        
        filename = os.path.basename(path)
        issues = []
        
        try:
            content = read_file(path)
        except Exception as e:
            return [{"file": filename, "type": "read_error", "message": str(e)}], False
        
        # Skip very short files
        if len(content) < 100:
            return [], False
        
        prompt = f"""{self.SYSTEM_PROMPT}

---
קובץ: {filename}

תוכן לבדיקה:
{content}
"""
        
        text = self._generate(prompt)
        
        if text:
            try:
                # Extract JSON
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    
                    # Extract issues
                    for issue in data.get("issues", []):
                        issue["file"] = filename
                        issues.append(issue)
                    
                    # Apply corrections if available
                    corrected_content = data.get("corrected_content", "")
                    if corrected_content and len(corrected_content) > len(content) * 0.5:
                        # Save corrected version
                        save_markdown(corrected_content, path)
                        print(f"    ✓ Corrected: {filename}")
                        time.sleep(2)
                        return issues, True
            except Exception as e:
                print(f"    ✗ JSON parsing error for {filename}: {e}")
        
        time.sleep(2)
        return issues, False
    
    def _proofread_regex(self, path: str) -> List[Dict]:
        """Fallback regex-based proofreading."""
        import re
        
        issues = []
        filename = os.path.basename(path)
        
        try:
            content = read_file(path)
        except Exception as e:
            return [{"file": filename, "type": "read_error", "message": str(e)}]
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Double spaces
            if '  ' in line and not line.strip().startswith('```'):
                issues.append({
                    "file": filename,
                    "line": i,
                    "type": "structure",
                    "severity": "minor",
                    "message": "רווח כפול"
                })
            
            # Lecture-style language
            lecture_phrases = ["בשקף", "ראינו", "הראיתי", "בואו נראה", "כפי שאמרתי", "היי"]
            for phrase in lecture_phrases:
                if phrase in line:
                    issues.append({
                        "file": filename,
                        "line": i,
                        "type": "lecture_style",
                        "severity": "moderate",
                        "message": f"ניסוח הרצאה: '{phrase}'"
                    })
            
            # Placeholder detection
            if re.search(r'\[תוכן\s*[^\]]*\]|\[הסבר\s*[^\]]*\]', line):
                issues.append({
                    "file": filename,
                    "line": i,
                    "type": "structure",
                    "severity": "major",
                    "message": "טקסט זמני שלא הושלם"
                })
        
        return issues
    
    def _generate_log(self, issues: List[Dict], files_checked: int, files_corrected: int) -> str:
        """Generate comprehensive proof log."""
        md = "# יומן הגהה (Proofreading Log)\n\n"
        md += f"*נוצר על ידי {AGENT_NAME} (LLM-Powered)*\n\n"
        md += "---\n\n"
        
        md += "## סיכום\n\n"
        md += f"- קבצים שנבדקו: {files_checked}\n"
        md += f"- קבצים שתוקנו: {files_corrected}\n"
        md += f"- בעיות שנמצאו: {len(issues)}\n\n"
        
        # Severity breakdown
        major = sum(1 for i in issues if i.get("severity") == "major")
        moderate = sum(1 for i in issues if i.get("severity") == "moderate")
        minor = sum(1 for i in issues if i.get("severity") == "minor")
        
        md += "### חומרה\n\n"
        md += f"- 🔴 חמורות (major): {major}\n"
        md += f"- 🟡 בינוניות (moderate): {moderate}\n"
        md += f"- 🟢 קלות (minor): {minor}\n\n"
        
        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                fname = issue.get("file", "unknown")
                if fname not in by_file:
                    by_file[fname] = []
                by_file[fname].append(issue)
            
            md += "## בעיות לפי קובץ\n\n"
            
            for fname, file_issues in by_file.items():
                md += f"### {fname}\n\n"
                md += "| שורה | סוג | חומרה | הודעה |\n"
                md += "|------|-----|-------|-------|\n"
                for issue in file_issues[:20]:  # Limit to 20 per file
                    line = issue.get("line", "?")
                    itype = issue.get("type", "unknown")
                    severity = issue.get("severity", "?")
                    msg = issue.get("message", issue.get("explanation", ""))[:50]
                    md += f"| {line} | {itype} | {severity} | {msg} |\n"
                md += "\n"
        else:
            md += "## תוצאה\n\n✅ לא נמצאו בעיות הגהה!\n\n"
        
        md += "---\n\n"
        md += "## מקרא סוגי בעיות\n\n"
        md += "| סוג | הסבר |\n"
        md += "|-----|------|\n"
        md += "| `lecture_style` | ניסוח הרצאה שצריך להפוך לניסוח ספר |\n"
        md += "| `grammar` | שגיאת דקדוק עברי |\n"
        md += "| `terminology` | חוסר עקביות במונחים |\n"
        md += "| `structure` | בעיית מבנה או עיצוב |\n"
        
        return md
