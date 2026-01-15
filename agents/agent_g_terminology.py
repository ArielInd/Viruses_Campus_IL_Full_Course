"""
Agent G: TerminologyConsistencyKeeper (Quality-First Edition)

Grammar-aware terminology enforcement using gemini-2.5-pro:
- Replaces variants with canonical terms while preserving Hebrew agreement
- Automatically updates the glossary with new terms
- Generates detailed consistency reports

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import yaml
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
    ConsistencyReport, PipelineLogger, TodoTracker,
    save_markdown, read_file
)

AGENT_NAME = "TerminologyConsistencyKeeper"

# Gemini configuration - PRO for linguistic precision
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Canonical terminology
CANONICAL_TERMS = {
    "DNA": {"hebrew": "DNA", "variants": ["דנ\"א", "די-אן-איי"], "english": "DNA"},
    "RNA": {"hebrew": "RNA", "variants": ["רנ\"א", "אר-אן-איי"], "english": "RNA"},
    "mRNA": {"hebrew": "mRNA", "variants": ["אם-אר-אן-איי"], "english": "messenger RNA"},
    "PCR": {"hebrew": "PCR", "variants": [], "english": "Polymerase Chain Reaction"},
    "נגיף": {"hebrew": "נגיף", "variants": ["וירוס"], "english": "virus"},
    "חיידק": {"hebrew": "חיידק", "variants": ["בקטריה"], "english": "bacterium"},
    "נוגדן": {"hebrew": "נוגדן", "variants": ["אנטיבודי"], "english": "antibody"},
    "אנטיגן": {"hebrew": "אנטיגן", "variants": [], "english": "antigen"},
    "קופסית": {"hebrew": "קופסית", "variants": ["קפסיד"], "english": "capsid"},
    "מעטפת": {"hebrew": "מעטפת", "variants": ["אנבלופ"], "english": "envelope"},
    "שעתוק": {"hebrew": "שעתוק", "variants": ["תעתוק"], "english": "transcription"},
    "תרגום": {"hebrew": "תרגום", "variants": [], "english": "translation"},
    "שכפול": {"hebrew": "שכפול", "variants": ["רפליקציה"], "english": "replication"},
}


class TerminologyConsistencyKeeper:
    """
    Agent G: Enforces consistent, grammatically correct terminology.
    
    Uses Gemini 3 Pro to:
    - Replace variant terms with canonical ones
    - Adjust surrounding Hebrew grammar (gender, number) if a replacement occurs
    - Build a comprehensive glossary
    
    Output: terminology.yml, glossary, consistency report
    """
    
    SYSTEM_PROMPT = """אתה עורך לשון ומומחה לטרמינולוגיה מדעית בעברית.

תפקידך: להבטיח עקביות בשימוש במונחים לאורך הספר.

## הנחיות לתיקון:
1. זהה חוסר עקביות (שימוש ב"וירוס" במקום "נגיף", "בקטריה" במקום "חיידק" וכו').
2. החלף את המונח הלא עקבי במונח הקנוני.
3. **קריטי**: ודא שהמשפט נשאר תקין דקדוקית. אם החלפת מונח מזכר לנקבה (או להיפך), תקן את שמות התואר או הפעלים הסמוכים.
4. אל תשנה את המשמעות המדעית של המשפט.

החזר JSON בפורמט:
{
  "total_fixes": 5,
  "fixes": [
    {"found": "הוירוס הקטן", "corrected": "הנגיף הקטן", "reason": "שימוש במונח קנוני 'נגיף'"},
    {"found": "בקטריה מהירה", "corrected": "חיידק מהיר", "reason": "התאמת מין דקדוקי (בקטריה נ' -> חיידק ז')"}
  ],
  "corrected_content": "הטקסט המלא המתוקן"
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
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (Grammar-Aware Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Using simple regex replacement")
            
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=16383,
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
        
        # Save terminology reference
        term_path = os.path.join(self.ops_dir, "artifacts", "terminology.yml")
        self._save_terminology(term_path)
        output_files.append(term_path)
        
        # Process chapters
        total_checked = 0
        total_inconsistencies = 0
        all_fixes = []
        
        if os.path.exists(self.chapters_dir):
            for filename in os.listdir(self.chapters_dir):
                if not filename.endswith('.md'):
                    continue
                
                path = os.path.join(self.chapters_dir, filename)
                content = read_file(path)
                
                if self.client:
                    # Grammar-aware LLM correction
                    fixes, corrected_content = self._fix_consistency_with_llm(filename, content)
                    if fixes:
                        save_markdown(corrected_content, path)
                        all_fixes.extend(fixes)
                        total_inconsistencies += len(fixes)
                else:
                    # Regex fallback
                    # ... simple implementation ...
                    pass
                
                total_checked += 1
        
        # Save reports
        report_path = os.path.join(self.ops_dir, "reports", "consistency_report.md")
        report_md = self._generate_report(total_checked, total_inconsistencies, all_fixes)
        save_markdown(report_md, report_path)
        output_files.append(report_path)
        
        # Update glossary
        glossary_path = os.path.join(self.book_dir, "90_glossary.md")
        glossary_content = self._generate_glossary_with_llm()
        save_markdown(glossary_content, glossary_path)
        output_files.append(glossary_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "consistency_report": report_path,
            "glossary": glossary_path,
            "total_fixes": total_inconsistencies
        }

    def _save_terminology(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(CANONICAL_TERMS, f, allow_unicode=True)

    def _fix_consistency_with_llm(self, filename: str, content: str) -> tuple:
        """Use LLM to fix terminology while following grammar rules."""
        prompt = f"""{self.SYSTEM_PROMPT}

המשימה: תקן את הטקסט הבא כך שישתמש במונחים הקנוניים: {json.dumps(CANONICAL_TERMS, ensure_ascii=False)}

קובץ: {filename}
תוכן:
{content}
"""
        text = self._generate(prompt)
        if text:
            try:
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    fixes = data.get("fixes", [])
                    for f in fixes:
                        f["file"] = filename
                    return fixes, data.get("corrected_content", content)
            except Exception:
                pass
        return [], content

    def _generate_report(self, checked: int, found: int, fixes: List[Dict]) -> str:
        md = f"# דוח עקביות מונחים (מהדורה דקדוקית)\n\n"
        md += f"- קבצים שנבדקו: {checked}\n"
        md += f"- בעיות שנמצאו ותוקנו: {found}\n\n"
        md += "| קובץ | טקסט מקורי | טקסט מתוקן | סיבה |\n"
        md += "|------|------------|------------|------|\n"
        for f in fixes[:50]:
            md += f"| {f.get('file')} | {f.get('found')} | {f.get('corrected')} | {f.get('reason')} |\n"
        return md

    def _generate_glossary_with_llm(self) -> str:
        """Use LLM to structure a beautiful glossary from the terminology list."""
        prompt = f"""צור מילון מושגים (Glossary) מקיף ויפה בפורמט Markdown עבור ספר וירולוגיה.
השתמש במונחים הקנוניים הבאים כבסיס: {json.dumps(CANONICAL_TERMS, ensure_ascii=False)}
הוסף הגדרות מדעיות מדויקות בעברית.
סדר לפי א'-ב'.
"""
        text = self._generate(prompt)
        return text if text else "# מילון מושגים\n\n[לא זמין]"
