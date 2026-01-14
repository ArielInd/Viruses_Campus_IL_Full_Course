"""
Agent H: CopyeditorProofreader
Final language and typography pass.
"""

import os
import re
from typing import Dict, List
from datetime import datetime

from .schemas import PipelineLogger, TodoTracker, save_markdown, read_file

AGENT_NAME = "CopyeditorProofreader"


class CopyeditorProofreader:
    """
    Agent H: Produces /ops/reports/proof_log.md
    """

    def __init__(self, book_dir: str, ops_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.proof_log_path = os.path.join(ops_dir, "reports", "proof_log.md")

    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []

        changes = []
        for path in self._iter_files():
            content = read_file(path)
            updated, file_changes = self._proofread(content)
            if updated != content:
                save_markdown(updated, path)
            if file_changes:
                changes.append(f"{os.path.basename(path)}: {', '.join(file_changes)}")

        log = self._build_log(changes)
        save_markdown(log, self.proof_log_path)
        output_files.append(self.proof_log_path)

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        print(f"[{AGENT_NAME}] Proofreading complete")
        return {"proof_log": self.proof_log_path}

    def _iter_files(self) -> List[str]:
        paths = []
        if os.path.exists(self.chapters_dir):
            for filename in sorted(os.listdir(self.chapters_dir)):
                if filename.endswith(".md"):
                    paths.append(os.path.join(self.chapters_dir, filename))
        front_matter = os.path.join(self.book_dir, "00_front_matter.md")
        if os.path.exists(front_matter):
            paths.append(front_matter)
        return paths

    def _proofread(self, content: str) -> (str, List[str]):
        changes = []
        updated = content
        updated = re.sub(r"[ \t]+\n", "\n", updated)
        if updated != content:
            changes.append("ניקוי רווחים בסוף שורה")
        updated2 = re.sub(r"\n{3,}", "\n\n", updated)
        if updated2 != updated:
            changes.append("איחוד שורות ריקות")
        return updated2, changes

    def _build_log(self, changes: List[str]) -> str:
        md = "# דוח הגהה\n\n"
        if changes:
            md += "## שינויים\n\n"
            for change in changes:
                md += f"- {change}\n"
        else:
            md += "לא נדרשו שינויים.\n"
        return md
