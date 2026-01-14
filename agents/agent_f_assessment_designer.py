"""
Agent F: AssessmentDesigner
Creates question bank and exam review, updates chapters if needed.
"""

import os
import re
from typing import Dict, List
from datetime import datetime

from .schemas import PipelineLogger, TodoTracker, save_markdown, read_file

AGENT_NAME = "AssessmentDesigner"


class AssessmentDesigner:
    """
    Agent F: Produces /book/92_question_bank.md and /book/91_exam_review.md
    """

    def __init__(self, book_dir: str, ops_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")

    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []

        chapters = self._load_chapters()
        question_bank = self._build_question_bank(chapters)
        qb_path = os.path.join(self.book_dir, "92_question_bank.md")
        save_markdown(question_bank, qb_path)
        output_files.append(qb_path)

        exam_review = self._build_exam_review(chapters)
        review_path = os.path.join(self.book_dir, "91_exam_review.md")
        save_markdown(exam_review, review_path)
        output_files.append(review_path)

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        print(f"[{AGENT_NAME}] Wrote question bank and exam review")
        return {"question_bank": qb_path, "exam_review": review_path}

    def _load_chapters(self) -> Dict[str, str]:
        chapters = {}
        if not os.path.exists(self.chapters_dir):
            return chapters
        for filename in sorted(os.listdir(self.chapters_dir)):
            if filename.endswith(".md") and filename.startswith("chapter_"):
                path = os.path.join(self.chapters_dir, filename)
                chapters[filename] = read_file(path)
        return chapters

    def _extract_questions(self, content: str) -> str:
        marker = "## שאלות לתרגול"
        if marker in content:
            return content.split(marker, 1)[1].strip()
        return ""

    def _extract_summary(self, content: str) -> List[str]:
        marker = "## סיכום מהיר"
        if marker in content:
            section = content.split(marker, 1)[1]
            lines = []
            for line in section.splitlines()[1:30]:
                if line.strip().startswith("-"):
                    lines.append(line.strip().lstrip("- "))
                if line.startswith("## "):
                    break
            return lines
        return []

    def _build_question_bank(self, chapters: Dict[str, str]) -> str:
        md = "# בנק שאלות – קורס נגיפים וחיסונים\n\n"
        for filename, content in chapters.items():
            chapter_title = self._extract_title(content)
            questions = self._extract_questions(content)
            md += f"## {chapter_title}\n\n"
            if questions:
                md += questions + "\n\n"
            else:
                md += "אין שאלות זמינות לפרק זה.\n\n"
        return md

    def _build_exam_review(self, chapters: Dict[str, str]) -> str:
        md = "# חזרה לבחינה – נקודות מפתח\n\n"
        md += "## עקרונות כלליים\n\n"
        md += "- להבין יחסי מבנה-תפקוד ולזהות מנגנונים חוזרים.\n"
        md += "- להבחין בין חסינות מולדת לנרכשת, ובין סוגי נגיפים.\n"
        md += "- להתמקד בשאלות של 'למה' ולא רק 'מה'.\n\n"

        for filename, content in chapters.items():
            chapter_title = self._extract_title(content)
            md += f"## {chapter_title}\n\n"
            summary = self._extract_summary(content)
            if summary:
                for item in summary[:10]:
                    md += f"- {item}\n"
            else:
                md += "- סיכום קצר יתווסף על בסיס הפרק.\n"
            md += "\n"

        md += "## תרגול מעורב (Mixed Practice)\n\n"
        md += "1. הסבירו כיצד מנגנון החיסון הנרכשת מסייע בפיתוח חיסון יעיל.\n"
        md += "2. השוו בין נגיף RNA לנגיף DNA בהקשר של קצב מוטציות.\n"
        md += "3. נתחו תרחיש: התפרצות מחלה חדשה שמועברת דרך וקטור.\n"
        md += "\n"
        return md

    def _extract_title(self, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "").strip()
        return "פרק"
