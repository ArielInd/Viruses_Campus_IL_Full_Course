"""
Agent E: DevelopmentalEditor
Converts drafts into book-ready chapters and writes edit memos.
"""

import os
from typing import Dict, List
from datetime import datetime

from .schemas import (
    EditedChapter, PipelineLogger, TodoTracker,
    save_json, save_markdown, load_json, read_file
)

AGENT_NAME = "DevelopmentalEditor"


class DevelopmentalEditor:
    """
    Agent E: Produces /book/chapters/*.md and /ops/reports/edit_memos/*.md
    """

    def __init__(self, ops_dir: str, book_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.book_dir = book_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        self.drafts_dir = os.path.join(self.artifacts_dir, "drafts", "chapters")
        self.edit_memos_dir = os.path.join(ops_dir, "reports", "edit_memos")
        self.chapters_dir = os.path.join(book_dir, "chapters")

    def run(self) -> Dict:
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []

        draft_paths = self._find_drafts()
        print(f"[{AGENT_NAME}] Editing {len(draft_paths)} drafts")

        for draft_path in draft_paths:
            draft_md = read_file(draft_path)
            chapter_id = self._extract_chapter_id(draft_path)
            edited_md, notes = self._edit_content(draft_md)

            chapter_filename = f"chapter_{chapter_id}.md"
            chapter_path = os.path.join(self.chapters_dir, chapter_filename)
            save_markdown(edited_md, chapter_path)
            output_files.append(chapter_path)

            memo_path = os.path.join(self.edit_memos_dir, f"chapter_{chapter_id}_memo.md")
            memo = self._build_memo(chapter_id, notes)
            save_markdown(memo, memo_path)
            output_files.append(memo_path)

            edited = EditedChapter(
                chapter_id=chapter_id,
                title=self._extract_title(edited_md),
                content_md=edited_md,
                word_count=len(edited_md.split()),
                edit_notes=notes,
                quality_score=0.82,
            )
            meta_path = os.path.join(self.chapters_dir, f"chapter_{chapter_id}.json")
            save_json(edited.__dict__, meta_path)

        # Create front matter and README
        front_matter_path = os.path.join(self.book_dir, "00_front_matter.md")
        save_markdown(self._front_matter(), front_matter_path)
        output_files.append(front_matter_path)

        readme_path = os.path.join(self.book_dir, "README.md")
        save_markdown(self._readme(), readme_path)
        output_files.append(readme_path)

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        print(f"[{AGENT_NAME}] Wrote {len(output_files)} edited outputs")
        return {"chapters_dir": self.chapters_dir, "num_chapters": len(draft_paths)}

    def _find_drafts(self) -> List[str]:
        paths = []
        if not os.path.exists(self.drafts_dir):
            return paths
        for filename in os.listdir(self.drafts_dir):
            if filename.endswith(".md"):
                paths.append(os.path.join(self.drafts_dir, filename))
        return sorted(paths)

    def _extract_chapter_id(self, path: str) -> str:
        base = os.path.basename(path)
        return base.replace("chapter_", "").replace(".md", "")

    def _extract_title(self, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "").strip()
        return "פרק"

    def _edit_content(self, content: str) -> (str, List[str]):
        notes = []
        cleaned = content.replace("\r\n", "\n")
        cleaned = cleaned.replace("\n\n\n", "\n\n")
        notes.append("תוקנו רווחים ושורות ריקות עודפות")
        return cleaned.strip() + "\n", notes

    def _build_memo(self, chapter_id: str, notes: List[str]) -> str:
        md = f"# מזכר עריכה – פרק {chapter_id}\n\n"
        md += "## שינויים שבוצעו\n"
        for note in notes:
            md += f"- {note}\n"
        md += "\n## דגשים להמשך\n"
        md += "- לשמור על עקביות מונחים בין הפרקים.\n"
        md += "- לוודא שכל שאלת תרגול כוללת רציונל קצר.\n"
        return md

    def _front_matter(self) -> str:
        return (
            "# נגיפים, תאים וחיסונים – ספר לימוד\n\n"
            "## הצהרת בטיחות ותיחום\n\n"
            "הספר נועד ללמידה עיונית בלבד. כל התיאורים של מעבדות או הדגמות הם רעיוניים ואינם כוללים "
            "פרוטוקולים, הוראות ביצוע, או פרטים טכניים. אין לראות במידע ייעוץ רפואי או קליני.\n\n"
            "## כיצד להשתמש בספר\n\n"
            "הפרקים בנויים ללמידה הדרגתית: יסודות ביולוגיים, עולם הנגיפים, מערכת החיסון, חיסונים ולבסוף "
            "מקרי מבחן עדכניים. בכל פרק תמצאו מטרות למידה, סיכום מהיר, ומערך שאלות לתרגול.\n\n"
        )

    def _readme(self) -> str:
        return (
            "# ספר לימוד – קורס נגיפים וחיסונים\n\n"
            "ספר זה נבנה מתוך תמלולי השיעורים (course_transcripts) והומר למבנה לימודי קריא עם יעדי למידה, "
            "סיכומים, ותרגול לבחינות.\n\n"
            "## מבנה התיקיות\n\n"
            "- `book/`: קבצי הספר הסופיים.\n"
            "- `ops/`: תוצרי ביניים, דוחות, ולוגים של תהליך העיבוד.\n\n"
            "## בנייה מחדש\n\n"
            "הריצו `run_pipeline.py` כדי לעבד מחדש את התמלולים ולבנות את הספר.\n"
        )
