"""
Agent G: TerminologyConsistencyKeeper
Enforces consistent terminology, builds glossary and consistency report.
"""

import os
import re
from typing import Dict, List, Tuple
from datetime import datetime

from .schemas import PipelineLogger, TodoTracker, save_markdown, read_file

AGENT_NAME = "TerminologyConsistencyKeeper"


class TerminologyConsistencyKeeper:
    """
    Agent G: Produces terminology.yml, glossary, and consistency report.
    """

    def __init__(self, book_dir: str, ops_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.terminology_path = os.path.join(ops_dir, "artifacts", "terminology.yml")
        self.glossary_path = os.path.join(book_dir, "90_glossary.md")
        self.report_path = os.path.join(ops_dir, "reports", "consistency_report.md")

    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []

        chapters = self._load_chapters()
        term_map, fixes = self._normalize_terms(chapters)

        terminology_yaml = self._build_terminology_yaml(term_map)
        save_markdown(terminology_yaml, self.terminology_path)
        output_files.append(self.terminology_path)

        glossary = self._build_glossary(term_map)
        save_markdown(glossary, self.glossary_path)
        output_files.append(self.glossary_path)

        report = self._build_report(fixes)
        save_markdown(report, self.report_path)
        output_files.append(self.report_path)

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        print(f"[{AGENT_NAME}] Glossary and terminology report written")
        return {"glossary": self.glossary_path, "terminology": self.terminology_path}

    def _load_chapters(self) -> Dict[str, str]:
        chapters = {}
        if not os.path.exists(self.chapters_dir):
            return chapters
        for filename in sorted(os.listdir(self.chapters_dir)):
            if filename.endswith(".md") and filename.startswith("chapter_"):
                path = os.path.join(self.chapters_dir, filename)
                chapters[path] = read_file(path)
        return chapters

    def _normalize_terms(self, chapters: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        replacements = {
            "דנא": "DNA",
            "דנ\"א": "DNA",
            "רנא": "RNA",
            "רנ\"א": "RNA",
            "איליזה": "ELISA",
            "טיאלר": "TLR",
            "אמ-הי-סי": "MHC",
        }
        fixes = []
        term_map = {}

        for path, content in chapters.items():
            updated = content
            for old, new in replacements.items():
                if old in updated:
                    updated = updated.replace(old, new)
                    fixes.append(f"{os.path.basename(path)}: {old} -> {new}")
            if updated != content:
                save_markdown(updated, path)

            # Extract key terms section
            term_map.update(self._extract_key_terms(updated))

        return term_map, fixes

    def _extract_key_terms(self, content: str) -> Dict[str, str]:
        terms = {}
        marker = "## מושגי מפתח"
        if marker not in content:
            return terms
        section = content.split(marker, 1)[1]
        for line in section.splitlines()[1:40]:
            if line.startswith("## "):
                break
            if line.strip().startswith("-"):
                entry = line.strip().lstrip("- ")
                if "(" in entry and entry.endswith(")"):
                    hebrew, english = entry.rsplit("(", 1)
                    terms[hebrew.strip()] = english.strip(") ")
                else:
                    terms[entry.strip()] = ""
        return terms

    def _build_terminology_yaml(self, term_map: Dict[str, str]) -> str:
        lines = ["# Canonical terminology", "terms:"]
        for hebrew, english in sorted(term_map.items()):
            if english:
                lines.append(f"  - hebrew: '{hebrew}'")
                lines.append(f"    english: '{english}'")
            else:
                lines.append(f"  - hebrew: '{hebrew}'")
                lines.append("    english: ''")
        return "\n".join(lines) + "\n"

    def _build_glossary(self, term_map: Dict[str, str]) -> str:
        md = "# מילון מונחים\n\n"
        for hebrew, english in sorted(term_map.items()):
            if english:
                md += f"- **{hebrew}** ({english}): הגדרה תמציתית בעברית.\n"
            else:
                md += f"- **{hebrew}**: הגדרה תמציתית בעברית.\n"
        return md

    def _build_report(self, fixes: List[str]) -> str:
        md = "# דוח עקביות מונחים\n\n"
        if fixes:
            md += "## תיקונים שבוצעו\n\n"
            for fix in fixes:
                md += f"- {fix}\n"
        else:
            md += "לא נמצאו אי-עקביות מובהקות.\n"
        return md
