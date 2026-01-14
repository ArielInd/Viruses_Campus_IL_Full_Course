"""
Agent H: CopyeditorProofreader
Final language and typography pass.
"""

import os
import re
from typing import List, Dict

from .schemas import (
    PipelineLogger, TodoTracker,
    save_markdown, read_file
)

AGENT_NAME = "CopyeditorProofreader"


class CopyeditorProofreader:
    """
    Agent H: Final polish on all book files.
    Output: proof_log.md with issues found
    """
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        issues = []
        files_checked = 0
        
        # Check all markdown files
        for root, dirs, files in os.walk(self.book_dir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                path = os.path.join(root, filename)
                file_issues = self._check_file(path)
                issues.extend(file_issues)
                files_checked += 1
        
        # Save proof log
        log_path = os.path.join(self.ops_dir, "reports", "proof_log.md")
        log_md = self._generate_log(issues, files_checked)
        save_markdown(log_md, log_path)
        output_files.append(log_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Checked {files_checked} files, found {len(issues)} issues")
        
        return {
            "proof_log": log_path,
            "files_checked": files_checked,
            "issues_found": len(issues)
        }
    
    def _check_file(self, path: str) -> List[Dict]:
        """Check a single file for issues."""
        issues = []
        filename = os.path.basename(path)
        
        try:
            content = read_file(path)
        except Exception as e:
            return [{"file": filename, "type": "read_error", "message": str(e)}]
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for double spaces
            if '  ' in line and not line.strip().startswith('```'):
                issues.append({
                    "file": filename,
                    "line": i,
                    "type": "double_space",
                    "message": "Double space found"
                })
            
            # Check for unfinished placeholders
            if '[' in line and ']' in line:
                placeholder_match = re.search(r'\[([^\]]{0,50})\]', line)
                if placeholder_match:
                    text = placeholder_match.group(1)
                    if text.startswith('תוכן') or text.startswith('הסבר') or text.startswith('שאלה'):
                        issues.append({
                            "file": filename,
                            "line": i,
                            "type": "placeholder",
                            "message": f"Placeholder found: [{text[:30]}...]"
                        })
            
            # Check for lecture-style language
            lecture_phrases = ["בשקף", "ראינו", "הראיתי", "בואו נראה"]
            for phrase in lecture_phrases:
                if phrase in line:
                    issues.append({
                        "file": filename,
                        "line": i,
                        "type": "lecture_style",
                        "message": f"Lecture phrase: '{phrase}'"
                    })
            
            # Check heading structure
            if line.startswith('#'):
                heading_level = len(line.split()[0]) if line.split() else 0
                if heading_level > 4:
                    issues.append({
                        "file": filename,
                        "line": i,
                        "type": "heading_depth",
                        "message": "Heading too deep (>4 levels)"
                    })
        
        return issues
    
    def _generate_log(self, issues: List[Dict], files_checked: int) -> str:
        """Generate proof log markdown."""
        md = "# יומן הגהה (Proofreading Log)\n\n"
        md += f"*נוצר על ידי {AGENT_NAME}*\n\n"
        md += "---\n\n"
        
        md += "## סיכום\n\n"
        md += f"- קבצים שנבדקו: {files_checked}\n"
        md += f"- בעיות שנמצאו: {len(issues)}\n\n"
        
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
                for issue in file_issues:
                    line = issue.get("line", "?")
                    itype = issue.get("type", "unknown")
                    msg = issue.get("message", "")
                    md += f"- שורה {line}: [{itype}] {msg}\n"
                md += "\n"
        else:
            md += "## תוצאה\n\n✅ לא נמצאו בעיות הגהה!\n\n"
        
        md += "---\n\n"
        md += "## סוגי בעיות\n\n"
        md += "| סוג | הסבר |\n"
        md += "|-----|------|\n"
        md += "| `double_space` | רווח כפול |\n"
        md += "| `placeholder` | טקסט זמני שלא הושלם |\n"
        md += "| `lecture_style` | ניסוח הרצאה במקום ספר |\n"
        md += "| `heading_depth` | כותרת עמוקה מדי |\n"
        
        return md
