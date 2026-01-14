#!/usr/bin/env python3
import re
from pathlib import Path

BOOK_DIR = Path("book")
CHAPTERS_DIR = BOOK_DIR / "chapters"
FRONT_MATTER_FILE = BOOK_DIR / "00_front_matter.md"
QUESTION_BANK_FILE = BOOK_DIR / "92_question_bank.md"
EXAM_REVIEW_FILE = BOOK_DIR / "91_exam_review.md"

def generate_front_matter():
    content = """# וירוסים: איך מנצחים אותם?

**מדריך למידה מקיף**

---

### הקדמה
ספר זה מבוסס על סדרת ההרצאות "וירוסים: איך מנצחים אותם?" (Campus IL).
התוכן נכתב באמצעות בינה מלאכותית על בסיס תמלילי ההרצאות בלבד.

### הסרת אחריות (Disclaimer)
המידע בספר זה מיועד למטרות לימוד והשכלה בלבד.
**אין לראות במידע זה ייעוץ רפואי.**
בכל עניין רפואי יש לפנות לרופא או גורם מטפל מוסמך.
הדגמות המעבדה המופיעות בספר הן קונספטואליות בלבד ואינן מהוות פרוטוקול לביצוע מעשי.

---

### תוכן העניינים
*(נוצר אוטומטית בעת בניית PDF)*

\\newpage
"""
    with open(FRONT_MATTER_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Wrote {FRONT_MATTER_FILE}")

def aggregate_questions():
    """Extract questions from chapters and create a question bank."""
    if not CHAPTERS_DIR.exists():
        print("Chapters directory not found.")
        return

    files = sorted(list(CHAPTERS_DIR.glob("*.md")))
    all_questions = []

    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            text = fh.read()
        
        # Regex to find "## שאלות לתרגול" and content until next ## or EOF
        match = re.search(r"## שאלות לתרגול\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        if match:
            questions = match.group(1).strip()
            chapter_title = " ".join(f.stem.split("_")[1:])
            all_questions.append(f"## שאלות מתוך {chapter_title}\n\n{questions}\n")
            
    with open(QUESTION_BANK_FILE, 'w', encoding='utf-8') as f:
        f.write("# בנק שאלות (Question Bank)\n\n")
        f.write("ריכוז שאלות התרגול מכל פרקי הספר.\n\n")
        for q in all_questions:
            f.write(q + "\n---\n\n")
            
    print(f"Wrote {QUESTION_BANK_FILE}")

def main():
    generate_front_matter()
    aggregate_questions()
    # Exam review could be generated similarly or using claims
    with open(EXAM_REVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write("# חזרה למבחן (Exam Review)\n\n*(תוכן זה נוצר אוטומטית)*\n")
    print(f"Wrote stub for {EXAM_REVIEW_FILE}")

if __name__ == "__main__":
    main()
