"""
Agent I: SafetyScopeReviewer
Scans outputs for procedural lab content and remediates.
"""

import os
import re
from typing import Dict, List
from datetime import datetime

from .schemas import PipelineLogger, TodoTracker, save_markdown, read_file

AGENT_NAME = "SafetyScopeReviewer"


class SafetyScopeReviewer:
    """
    Agent I: Produces /ops/reports/safety_review.md
    """

    def __init__(self, book_dir: str, ops_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.report_path = os.path.join(ops_dir, "reports", "safety_review.md")

    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []

        reports = []
        for path in self._iter_chapters():
            content = read_file(path)
            cleaned, issues, remediations = self._sanitize(content)
            if cleaned != content:
                save_markdown(cleaned, path)
            reports.append({
                "chapter": os.path.basename(path),
                "passed": len(issues) == 0,
                "issues": issues,
                "remediations": remediations,
            })

        report_md = self._build_report(reports)
        save_markdown(report_md, self.report_path)
        output_files.append(self.report_path)

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        print(f"[{AGENT_NAME}] Safety review completed")
        return {"safety_report": self.report_path}

    def _iter_chapters(self) -> List[str]:
        if not os.path.exists(self.chapters_dir):
            return []
        return [os.path.join(self.chapters_dir, f)
                for f in sorted(os.listdir(self.chapters_dir))
                if f.endswith(".md")]

    def _sanitize(self, content: str) -> (str, List[str], List[str]):
        issues = []
        remediations = []
        risky_patterns = [
            r"שלב", r"פרוטוקול", r"דגירה", r"חמם", r"הוסף", r"הזרק",
            r"מ\"ל", r"מ\"ג", r"טמפרטורה", r"דקות", r"שעות",
            r"RPM", r"צנטריפוג", r"תרבית", r"גידול", r"מדידה",
        ]
        sentences = re.split(r"(?<=[\.\!\?])\s+", content)
        cleaned_sentences = []
        for sentence in sentences:
            if any(re.search(pat, sentence) for pat in risky_patterns):
                issues.append(sentence.strip())
                remediations.append("הוסרה התייחסות פרוצדורלית לטובת ניסוח רעיוני")
                cleaned_sentences.append("הדיון נשאר רעיוני ומתמקד בעקרונות המדעיים בלבד.")
            else:
                cleaned_sentences.append(sentence)
        cleaned = " ".join(cleaned_sentences)
        return cleaned, issues, remediations

    def _build_report(self, reports: List[Dict]) -> str:
        md = "# דוח בטיחות והיקף\n\n"
        for report in reports:
            status = "עבר" if report["passed"] else "נדרש תיקון"
            md += f"## {report['chapter']} – {status}\n\n"
            if report["issues"]:
                md += "**בעיות שאותרו:**\n"
                for issue in report["issues"][:5]:
                    md += f"- {issue}\n"
                md += "\n**תיקונים שבוצעו:**\n"
                for fix in report["remediations"][:5]:
                    md += f"- {fix}\n"
            else:
                md += "לא נמצאו תכנים פרוצדורליים.\n"
            md += "\n"
        return md
