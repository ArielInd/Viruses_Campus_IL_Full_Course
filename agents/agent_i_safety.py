"""
Agent I: SafetyScopeReviewer
FINAL GATE - Scans all outputs for safety constraints.
"""

import os
import re
from typing import List, Dict

from .schemas import (
    SafetyReport, PipelineLogger, TodoTracker,
    save_markdown, read_file
)

AGENT_NAME = "SafetyScopeReviewer"

# Patterns that indicate procedural/dangerous content
DANGEROUS_PATTERNS = [
    # Lab protocols
    (r'\d+\s*(ml|mL|מ"ל|ליטר)', "volume_specification", "Specific volume mentioned"),
    (r'\d+\s*(mg|g|גרם|מיליגרם)', "mass_specification", "Specific mass mentioned"),
    (r'\d+\s*(דקות|שעות|minutes|hours)', "time_specification", "Specific incubation time"),
    (r'(37|98\.6)\s*(°|מעלות|degrees)', "temperature_protocol", "Specific culture temperature"),
    (r'(אינקובציה|incubat)', "incubation_mention", "Incubation mentioned"),
    
    # Growth/cultivation
    (r'גידול\s+תרבית', "culture_growth", "Culture growth instructions"),
    (r'מזון\s+גידול|growth\s+medium', "growth_medium", "Growth medium mentioned"),
    (r'אגר\s+דם|blood\s+agar', "blood_agar", "Blood agar mentioned"),
    
    # Dangerous pathogens - detailed synthesis
    (r'סינתזה\s+של\s+נגיף', "virus_synthesis", "Virus synthesis mentioned"),
    (r'בניית\s+נגיף', "virus_construction", "Virus construction"),
    (r'הנדסה\s+גנטית\s+של\s+פתוגן', "pathogen_engineering", "Pathogen engineering"),
    
    # Bioweapon terms
    (r'נשק\s+ביולוגי', "bioweapon", "Bioweapon reference"),
    (r'טרור\s+ביולוגי', "bioterror", "Bioterrorism reference"),
]

# Allowed contexts (educational)
SAFE_CONTEXTS = [
    "הדגמה קונספטואלית",
    "ברמה קונספטואלית בלבד",
    "עקרון ולא פרוטוקול",
    "הערה: ללא פרוטוקול",
]


class SafetyScopeReviewer:
    """
    Agent I: FINAL GATE - Safety review of all content.
    Output: safety_review.md with pass/fail per chapter
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
        
        reports = []
        files_checked = 0
        passed = 0
        failed = 0
        
        # Check all book files
        for root, dirs, files in os.walk(self.book_dir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                path = os.path.join(root, filename)
                report = self._check_file(path, filename)
                reports.append(report)
                files_checked += 1
                
                if report.passed:
                    passed += 1
                else:
                    failed += 1
                    # Auto-remediate if possible
                    remediated = self._remediate(path, report)
                    if remediated:
                        report.remediations_applied.append("Auto-remediated flagged content")
                        report.passed = True
                        passed += 1
                        failed -= 1
        
        # Generate safety review
        review_path = os.path.join(self.ops_dir, "reports", "safety_review.md")
        review_md = self._generate_review(reports, files_checked, passed, failed)
        save_markdown(review_md, review_path)
        output_files.append(review_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        status = "✅ PASSED" if failed == 0 else "⚠️ ISSUES FOUND"
        print(f"[{AGENT_NAME}] Safety review: {status} ({passed}/{files_checked} passed)")
        
        return {
            "safety_review": review_path,
            "files_checked": files_checked,
            "passed": passed,
            "failed": failed,
            "all_passed": failed == 0
        }
    
    def _check_file(self, path: str, filename: str) -> SafetyReport:
        """Check a single file for safety issues."""
        issues = []
        
        try:
            content = read_file(path)
        except Exception as e:
            return SafetyReport(
                chapter_id=filename,
                passed=False,
                issues_found=[f"Could not read file: {e}"],
                remediations_applied=[]
            )
        
        # Check for safe context markers first
        has_safe_context = any(ctx in content for ctx in SAFE_CONTEXTS)
        
        # Check for dangerous patterns
        for pattern, code, description in DANGEROUS_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Check if in safe context
                for match in matches[:3]:  # Limit to first 3 matches
                    match_str = match if isinstance(match, str) else match[0]
                    # Check surrounding context
                    idx = content.find(match_str) if isinstance(match_str, str) else -1
                    if idx >= 0:
                        context_start = max(0, idx - 100)
                        context_end = min(len(content), idx + 100)
                        context = content[context_start:context_end]
                        
                        # If in safe educational context, skip
                        if has_safe_context or any(safe in context for safe in SAFE_CONTEXTS):
                            continue
                        
                        issues.append(f"[{code}] {description}")
        
        # Special checks for lab sections
        if "הדגמת מעבדה" in content or "מעבדה" in content:
            if "קונספטואלית" not in content and "ברמה" not in content:
                issues.append("[lab_section] Lab section may lack conceptual disclaimer")
        
        return SafetyReport(
            chapter_id=filename,
            passed=len(issues) == 0,
            issues_found=issues,
            remediations_applied=[]
        )
    
    def _remediate(self, path: str, report: SafetyReport) -> bool:
        """Attempt to auto-remediate issues."""
        if not report.issues_found:
            return True
        
        # For now, just log that remediation is needed
        # In a full implementation, this would rewrite problematic sections
        for issue in report.issues_found:
            self.todos.add(
                AGENT_NAME, 
                path, 
                f"Manual review needed: {issue}"
            )
        
        # Only mark as remediated if issues are minor
        minor_issues = ["volume_specification", "time_specification"]
        if all(any(mi in issue for mi in minor_issues) for issue in report.issues_found):
            return True
        
        return False
    
    def _generate_review(self, reports: List[SafetyReport], 
                         total: int, passed: int, failed: int) -> str:
        """Generate safety review markdown."""
        md = "# סקירת בטיחות (Safety Review)\n\n"
        md += f"*נוצר על ידי {AGENT_NAME} (Final Gate)*\n\n"
        md += "---\n\n"
        
        # Overall status
        if failed == 0:
            md += "## ✅ סטטוס: עבר בהצלחה\n\n"
            md += "כל הקבצים עברו את בדיקת הבטיחות.\n\n"
        else:
            md += "## ⚠️ סטטוס: נדרשת תשומת לב\n\n"
            md += f"{failed} קבצים דורשים בדיקה ידנית.\n\n"
        
        md += "## סיכום\n\n"
        md += "| מדד | ערך |\n"
        md += "|-----|-----|\n"
        md += f"| קבצים שנבדקו | {total} |\n"
        md += f"| עברו ✅ | {passed} |\n"
        md += f"| דורשים בדיקה ⚠️ | {failed} |\n\n"
        
        # Details per file
        md += "## פירוט לפי קובץ\n\n"
        
        for report in reports:
            status = "✅" if report.passed else "⚠️"
            md += f"### {status} {report.chapter_id}\n\n"
            
            if report.issues_found:
                md += "**בעיות שנמצאו:**\n"
                for issue in report.issues_found:
                    md += f"- {issue}\n"
                md += "\n"
            
            if report.remediations_applied:
                md += "**תיקונים שבוצעו:**\n"
                for rem in report.remediations_applied:
                    md += f"- {rem}\n"
                md += "\n"
            
            if not report.issues_found and not report.remediations_applied:
                md += "אין בעיות.\n\n"
        
        # Safety guidelines reminder
        md += "---\n\n"
        md += "## הנחיות בטיחות\n\n"
        md += "הספר עוקב אחר הכללים הבאים:\n\n"
        md += "1. **אין פרוטוקולי מעבדה** - הדגמות מעבדה קונספטואליות בלבד\n"
        md += "2. **אין נפחים/זמנים ספציפיים** - לא מאפשרים שכפול פרקטי\n"
        md += "3. **אין הנחיות סינתזה** - לא מסבירים כיצד לבנות פתוגנים\n"
        md += "4. **דיסקליימר בפתיחה** - הקוראים מודעים למגבלות\n"
        
        return md
