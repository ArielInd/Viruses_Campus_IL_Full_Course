"""
Agent F: AssessmentDesigner
Ensures exam scaffolding exists and creates consolidated question bank.
"""

import os
import re
from typing import List, Dict
from datetime import datetime

from .schemas import (
    PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "AssessmentDesigner"


class AssessmentDesigner:
    """
    Agent F: Produces question bank and exam review materials.
    Output: /book/92_question_bank.md, /book/91_exam_review.md
    """
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Load chapter plan for structure
        plan_path = os.path.join(self.ops_dir, "artifacts", "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        # Collect questions from chapters
        all_questions = []
        for plan in chapter_plans:
            chapter_id = plan["chapter_id"]
            questions = self._extract_questions_from_chapter(chapter_id)
            all_questions.extend(questions)
        
        print(f"[{AGENT_NAME}] Collected {len(all_questions)} questions from chapters")
        
        # Generate question bank
        question_bank = self._generate_question_bank(all_questions, chapter_plans)
        qb_path = os.path.join(self.book_dir, "92_question_bank.md")
        save_markdown(question_bank, qb_path)
        output_files.append(qb_path)
        
        # Generate exam review
        exam_review = self._generate_exam_review(chapter_plans)
        er_path = os.path.join(self.book_dir, "91_exam_review.md")
        save_markdown(exam_review, er_path)
        output_files.append(er_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Created question bank and exam review")
        
        return {
            "question_bank": qb_path,
            "exam_review": er_path,
            "total_questions": len(all_questions)
        }
    
    def _extract_questions_from_chapter(self, chapter_id: str) -> List[Dict]:
        """Extract questions from a chapter file."""
        questions = []
        
        # Try to find the chapter file
        possible_names = [
            f"{chapter_id}_chapter.md",
            f"0{chapter_id}_chapter.md" if len(chapter_id) == 1 else f"{chapter_id}_chapter.md",
        ]
        
        # Also check existing chapter names
        if os.path.exists(self.chapters_dir):
            for fname in os.listdir(self.chapters_dir):
                if fname.startswith(chapter_id) or fname.startswith(f"0{chapter_id}"):
                    possible_names.append(fname)
        
        for name in possible_names:
            path = os.path.join(self.chapters_dir, name)
            if os.path.exists(path):
                content = read_file(path)
                
                # Extract MCQ questions
                mcq_pattern = r'\*\*(\d+)\.\*\*\s*(.+?)\n\s*א\.\s*(.+?)\n\s*ב\.\s*(.+?)\n\s*ג\.\s*(.+?)\n\s*ד\.\s*(.+?)\n'
                mcq_matches = re.findall(mcq_pattern, content, re.MULTILINE | re.DOTALL)
                
                for match in mcq_matches:
                    questions.append({
                        "chapter": chapter_id,
                        "type": "mcq",
                        "question": match[1].strip(),
                        "options": [m.strip() for m in match[2:6]],
                    })
                
                break
        
        return questions
    
    def _generate_question_bank(self, questions: List[Dict], plans: List[Dict]) -> str:
        """Generate consolidated question bank."""
        md = "# נספח ג': בנק שאלות לתרגול חזרה\n\n"
        md += "*שאלות אלו נאספו מכל פרקי הספר לחזרה מרוכזת לפני הבחינה.*\n\n"
        md += "---\n\n"
        
        # Group by chapter
        md += "## חלק א': שאלות רב-ברירה (MCQ)\n\n"
        
        for plan in plans:
            chapter_id = plan["chapter_id"]
            title = plan["hebrew_title"]
            
            md += f"### פרק {chapter_id}: {title}\n\n"
            
            chapter_questions = [q for q in questions if q.get("chapter") == chapter_id]
            
            if chapter_questions:
                for i, q in enumerate(chapter_questions, 1):
                    md += f"**{i}.** {q.get('question', '[שאלה]')}\n"
                    for j, opt in enumerate(q.get('options', []), 0):
                        letters = ['א', 'ב', 'ג', 'ד']
                        if j < len(letters):
                            md += f"   {letters[j]}. {opt}\n"
                    md += "\n"
            else:
                # Generate placeholder questions for chapters without extracted MCQs
                md += self._generate_chapter_mcqs(chapter_id, plan.get("question_targets", []))
            
            md += "\n"
        
        # Open-ended questions section
        md += "---\n\n"
        md += "## חלק ב': שאלות פתוחות\n\n"
        
        for plan in plans:
            chapter_id = plan["chapter_id"]
            title = plan["hebrew_title"]
            
            md += f"### פרק {chapter_id}: {title}\n\n"
            md += self._generate_open_questions(chapter_id)
            md += "\n"
        
        return md
    
    def _generate_chapter_mcqs(self, chapter_id: str, targets: List[str]) -> str:
        """Generate placeholder MCQs for a chapter."""
        mcqs = {
            "01": [
                ("איזה אברון אחראי על הפקת האנרגיה בתא?", ["גרעין", "ליזוזום", "מיטוכונדריה", "גולג'י"], "ג"),
                ("לפי חוקי שרגף, אם ב-DNA יש 20% אדנין (A), כמה תימין (T) יש?", ["20%", "30%", "40%", "0%"], "א"),
            ],
            "02": [
                ("איזה תהליך משחרר מולקולת מים?", ["הידרוליזה", "תרגום", "דחיסה (קונדנסציה)", "שעתוק"], "ג"),
                ("כמה קשרי מימן יש בזוג הבסיסים G-C?", ["1", "2", "3", "4"], "ג"),
            ],
            "03": [
                ("מה נכון לגבי כל הנגיפים?", ["יש להם מעטפת שומנית", "הם מכילים DNA ו-RNA", "הם טפילים מוחלטים", "ניתן להרגם עם פניצילין"], "ג"),
            ],
            "04": [
                ("איזו חיה נחשבת ל\"כלי ערבוב\" שבו נוצרים נגיפי שפעת חדשים?", ["עטלף", "חזיר", "יתוש", "עכבר"], "ב"),
            ],
            "05": [
                ("מה תפקידם של קולטני TLR?", ["לייצר אנרגיה", "לשכפל DNA נגיפי", "לזהות תבניות זרות (PAMPs)", "להעביר חמצן"], "ג"),
            ],
            "06": [
                ("איזה נוגדן הוא הראשון להופיע בתגובה לזיהום חדש?", ["IgG", "IgA", "IgM", "IgE"], "ג"),
            ],
            "07": [
                ("מדוע יש צורך בחיסון שפעת חדש בכל שנה?", ["החיסון מתפרק", "חברות רוצות להרוויח", "הנגיף עובר שינויים (Drift)", "החיסון גורם למחלה"], "ג"),
            ],
            "08": [
                ("במה שונה הגנום של הקורונה מהשפעת?", ["לקורונה DNA", "לקורונה מנגנון הגהה", "קורונה קטן יותר", "אין הבדל"], "ב"),
            ],
        }
        
        md = ""
        for i, (q, opts, ans) in enumerate(mcqs.get(chapter_id, [])[:3], 1):
            md += f"**{i}.** {q}\n"
            for j, opt in enumerate(opts):
                letters = ['א', 'ב', 'ג', 'ד']
                md += f"   {letters[j]}. {opt}\n"
            md += f"   *(תשובה: {ans})*\n\n"
        
        return md
    
    def _generate_open_questions(self, chapter_id: str) -> str:
        """Generate open-ended questions for a chapter."""
        questions = {
            "01": "הסבר מדוע ארבעה יסודות בלבד (C, O, H, N) מרכיבים כמעט את כל גופנו.",
            "02": "מהי \"הדוגמה המרכזית\" ומדוע שעתוק לאחור שינה את הבנתנו?",
            "03": "ציין שני הבדלים מרכזיים בין נגיף לתא חי.",
            "04": "הסבר כיצד יתוש מעביר נגיף מאדם לאדם.",
            "05": "מהו ההבדל העיקרי בין חסינות מולדת לנרכשת?",
            "06": "הסבר את \"היפותזת ההיגיינה\" בהקשר של אלרגיות.",
            "07": "מהם היתרונות והחסרונות של חיסון חי-מוחלש?",
            "08": "כיצד עובד חיסון ה-mRNA?",
        }
        
        q = questions.get(chapter_id, "שאלה פתוחה")
        return f"**שאלה:** {q}\n\n*תשובה לדוגמה: [ראה בפרק]*\n\n"
    
    def _generate_exam_review(self, plans: List[Dict]) -> str:
        """Generate high-yield exam review."""
        md = "# נספח ב': מדריך למידה וסיכום למבחן\n\n"
        md += "סיכום מרוכז של הנקודות החשובות ביותר (\"High Yield\") לבחינה.\n\n"
        md += "---\n\n"
        
        # High-yield summaries by topic area
        sections = [
            ("1. המדרג הביולוגי (פרקים 1-2)", [
                "**תא**: יחידת החיים הבסיסית.",
                "**CHON**: פחמן, מימן, חמצן, חנקן - 4 היסודות העיקריים.",
                "**DNA**: סליל כפול (Chargaff: A=T, C=G).",
                "**הדוגמה המרכזית**: DNA → RNA → Protein.",
            ]),
            ("2. וירולוגיה בסיסית (פרק 3)", [
                "**נגיף**: טפיל מוחלט (Obligate Parasite).",
                "**מבנה**: גנום (DNA או RNA) + קופסית. לחלקם יש מעטפת.",
                "**מחזור חיים**: היצמדות → חדירה → שכפול → הרכבה → יציאה.",
            ]),
            ("3. מחלות נגיפיות (פרק 4)", [
                "**אבעבועות שחורות**: DNA, הוכחדה.",
                "**פוליו**: RNA ערום, פה-צואה, שיתוק.",
                "**שפעת**: RNA, 8 מקטעים, Drift/Shift.",
                "**אבולה**: RNA, זואונוזה, קדחת דימומית.",
            ]),
            ("4. אימונולוגיה (פרקים 5-6)", [
                "**מולדת**: מהירה, לא ספציפית, ללא זיכרון (מקרופאגים, TLR).",
                "**נרכשת**: איטית, ספציפית, **זיכרון** (תאי B ו-T).",
                "**IgM**: ראשוני. **IgG**: עיקרי. **IgA**: ריריות. **IgE**: אלרגיה.",
            ]),
            ("5. חיסונים (פרקים 7-8)", [
                "**חי-מוחלש**: תגובה חזקה, אסור למדוכאי חיסון.",
                "**מומת/תת-יחידה**: בטוח, דורש דחף.",
                "**mRNA**: הוראות לייצור חלבון בגוף.",
                "**חסינות העדר**: הגנה קהילתית.",
            ]),
        ]
        
        for title, points in sections:
            md += f"## {title}\n\n"
            for point in points:
                md += f"* {point}\n"
            md += "\n"
        
        # Common pitfalls
        md += "---\n\n"
        md += "## מלכודות נפוצות במבחן\n\n"
        pitfalls = [
            "**אנטיביוטיקה** הורגת חיידקים, **לא** נגיפים.",
            "**נוגדנים** הם החייל שלנו (צורת Y). **אנטיגן** הוא חלק של האויב.",
            "נגיף מכיל DNA **או** RNA, לא את שניהם.",
            "**MHC** נמצא על תאי הגוף שלנו, לא על הנגיף.",
        ]
        for pitfall in pitfalls:
            md += f"1. {pitfall}\n"
        
        return md
