"""
Agent E: DevelopmentalEditor
Converts drafts into book-grade chapters by leveraging existing high-quality content.
"""

import os
from typing import Dict

from .schemas import (
    EditedChapter, PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "DevelopmentalEditor"

# Map of existing chapters to use (already high quality)
EXISTING_CHAPTERS = {
    "01": "01_introduction_cells.md",
    "02": "02_macromolecules.md",
    "03": "03_chapter_viruses_intro.md",
    "04": "04_chapter_human_diseases.md",
    "05": "05_chapter_innate_immunity.md",
    "06": "06_chapter_adaptive_immunity.md",
    "07": "07_chapter_vaccines.md",
    "08": "08_chapter_coronavirus.md",
}


class DevelopmentalEditor:
    """
    Agent E: Converts drafts into book-grade chapters.
    Uses existing high-quality chapters where available.
    Output: /book/chapters/*.md and edit memos in /ops/reports/edit_memos/
    """
    
    def __init__(self, ops_dir: str, book_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.book_dir = book_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.memos_dir = os.path.join(ops_dir, "reports", "edit_memos")
        self.drafts_dir = os.path.join(ops_dir, "artifacts", "drafts", "chapters")
        
        os.makedirs(self.chapters_dir, exist_ok=True)
        os.makedirs(self.memos_dir, exist_ok=True)
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Load chapter plan
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        print(f"[{AGENT_NAME}] Processing {len(chapter_plans)} chapters")
        
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            
            # Check if high-quality existing chapter exists
            existing_file = EXISTING_CHAPTERS.get(chapter_id)
            existing_path = os.path.join(self.chapters_dir, existing_file) if existing_file else None
            
            if existing_path and os.path.exists(existing_path):
                # Use existing chapter, just validate and enhance
                result = self._enhance_existing(chapter_id, existing_path, plan)
                output_files.append(existing_path)
                
                # Write memo
                memo = self._generate_memo(chapter_id, "enhanced_existing", result)
            else:
                # Use draft and develop it
                draft_path = os.path.join(self.drafts_dir, f"{chapter_id}_chapter_draft.md")
                if os.path.exists(draft_path):
                    result = self._develop_draft(chapter_id, draft_path, plan)
                    output_path = os.path.join(self.chapters_dir, f"{chapter_id}_chapter.md")
                    save_markdown(result.content_md, output_path)
                    output_files.append(output_path)
                    memo = self._generate_memo(chapter_id, "developed_draft", result)
                else:
                    warnings.append(f"No draft found for chapter {chapter_id}")
                    continue
            
            # Save memo
            memo_path = os.path.join(self.memos_dir, f"chapter_{chapter_id}_memo.md")
            save_markdown(memo, memo_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Processed {len(output_files)} chapters")
        
        return {
            "chapters_dir": self.chapters_dir,
            "memos_dir": self.memos_dir,
            "num_chapters": len(output_files)
        }
    
    def _enhance_existing(self, chapter_id: str, path: str, plan: Dict) -> EditedChapter:
        """Enhance an existing high-quality chapter."""
        content = read_file(path)
        
        # Validate required sections
        edit_notes = []
        
        required_sections = [
            ("מטרות למידה", "## מטרות למידה"),
            ("מפת דרכים", "## מפת דרכים"),
            ("סיכום מהיר", "## סיכום מהיר"),
            ("מושגי מפתח", "## מושגי מפתח"),
            ("שאלות לתרגול", "## שאלות לתרגול"),
        ]
        
        for name, marker in required_sections:
            if marker not in content:
                edit_notes.append(f"Missing: {name}")
                self.todos.add(AGENT_NAME, path, f"Add {name} section")
        
        # Check for misconceptions section
        if "טעויות נפוצות" not in content:
            edit_notes.append("Consider adding טעויות נפוצות section")
        
        word_count = len(content.split())
        quality_score = 1.0 - (len(edit_notes) * 0.1)  # Deduct for missing sections
        
        return EditedChapter(
            chapter_id=chapter_id,
            title=plan["hebrew_title"],
            content_md=content,
            word_count=word_count,
            edit_notes=edit_notes,
            quality_score=max(0.5, quality_score)
        )
    
    def _develop_draft(self, chapter_id: str, path: str, plan: Dict) -> EditedChapter:
        """Develop a draft into a fully edited chapter."""
        content = read_file(path)
        
        edit_notes = ["Developed from draft"]
        
        # Apply standard improvements
        content = self._apply_style_improvements(content)
        
        word_count = len(content.split())
        
        return EditedChapter(
            chapter_id=chapter_id,
            title=plan["hebrew_title"],
            content_md=content,
            word_count=word_count,
            edit_notes=edit_notes,
            quality_score=0.7  # Drafts start at lower quality
        )
    
    def _apply_style_improvements(self, content: str) -> str:
        """Apply style improvements to content."""
        # Remove lecture-style phrases
        lecture_phrases = [
            "כפי שראינו בשקף",
            "בשקף הזה",
            "כפי שאמרתי",
            "בואו נראה",
            "שלום לכולם",
            "היי",
        ]
        
        for phrase in lecture_phrases:
            content = content.replace(phrase, "")
        
        return content
    
    def _generate_memo(self, chapter_id: str, action: str, result: EditedChapter) -> str:
        """Generate an edit memo."""
        md = f"# Edit Memo: Chapter {chapter_id}\n\n"
        md += f"**Title:** {result.title}\n\n"
        md += f"**Action:** {action}\n\n"
        md += f"**Word Count:** {result.word_count}\n\n"
        md += f"**Quality Score:** {result.quality_score:.2f}\n\n"
        
        md += "## Edit Notes\n\n"
        for note in result.edit_notes:
            md += f"- {note}\n"
        
        md += f"\n*Generated by {AGENT_NAME}*\n"
        
        return md
