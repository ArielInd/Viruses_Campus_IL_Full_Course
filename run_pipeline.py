#!/usr/bin/env python3
"""
Main pipeline runner for the Hebrew virology study ebook.
Executes all agents in sequence and produces the final book.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents import (
    PipelineLogger, TodoTracker,
    CorpusLibrarian,
    CurriculumArchitect,
    ChapterBriefBuilder,
    DraftWriter,
    DevelopmentalEditor,
    AssessmentDesigner,
    TerminologyConsistencyKeeper,
    CopyeditorProofreader,
    SafetyScopeReviewer,
    save_markdown
)

# Configuration
TRANSCRIPTS_DIR = PROJECT_ROOT / "course_transcripts"
BOOK_DIR = PROJECT_ROOT / "book"
OPS_DIR = PROJECT_ROOT / "ops"

# Ensure directories exist
BOOK_DIR.mkdir(exist_ok=True)
(BOOK_DIR / "chapters").mkdir(exist_ok=True)
OPS_DIR.mkdir(exist_ok=True)
(OPS_DIR / "logs").mkdir(exist_ok=True)
(OPS_DIR / "artifacts").mkdir(exist_ok=True)
(OPS_DIR / "artifacts" / "file_notes").mkdir(exist_ok=True)
(OPS_DIR / "artifacts" / "chapter_briefs").mkdir(exist_ok=True)
(OPS_DIR / "artifacts" / "drafts" / "chapters").mkdir(parents=True, exist_ok=True)
(OPS_DIR / "reports").mkdir(exist_ok=True)
(OPS_DIR / "reports" / "edit_memos").mkdir(exist_ok=True)


def create_front_matter(book_dir: Path):
    """Create front matter if not exists."""
    front_matter_path = book_dir / "00_front_matter.md"
    
    content = """# נגיפים, תאים וחיסונים
## ספר לימוד מקיף לקורס Campus IL

---

### עמוד השער

**כותרת:** נגיפים – מביולוגיה מולקולרית למגפות

**מבוסס על:** קורס "וירוסים, איך מנצחים אותם?" מאת פרופ' יונתן גרשוני

**עריכה והפקה:** מערכת אוטומטית רב-סוכנית

**שפה:** עברית

---

### הודעת אחריות (Disclaimer)

> ⚠️ **חשוב לקרוא**
>
> ספר זה הוא חומר לימודי בלבד. אין להסתמך עליו לצורכי אבחון או טיפול רפואי.
>
> הדגמות מעבדה המופיעות בספר מוצגות **ברמה קונספטואלית בלבד** ואינן כוללות פרוטוקולים מעשיים.
> הספר אינו מספק הוראות לייצור, בידוד, או טיפוח של פתוגנים.
>
> לכל שאלה רפואית יש לפנות לרופא מוסמך.

---

### כיצד להשתמש בספר זה

1. **קריאה ראשונית**: עברו על כל פרק בסדר, תוך התמקדות במטרות הלמידה.
2. **מונחי מפתח**: השתמשו במילון בסוף הספר להבנת מושגים חדשים.
3. **שאלות לתרגול**: פתרו את השאלות בסוף כל פרק לבדיקה עצמית.
4. **חזרה לבחינה**: עברו על נספח "מדריך למבחן" לסיכום ממוקד.

**סמלים בספר:**

| סמל | משמעות |
|-----|---------|
| 📚 | מושג מפתח |
| ⚗️ | הדגמת מעבדה (קונספטואלית) |
| 🎓 | נקודת מבט של מומחה |
| ⚠️ | טעות נפוצה |
| 💡 | טיפ ללמידה |

---

### תוכן עניינים

1. **פרק 1**: מבוא – תאים הם יחידות החיים
2. **פרק 2**: מולקולות המקרו – מ-DNA לחלבונים
3. **פרק 3**: נגיפים – מבנה, סיווג ושכפול
4. **פרק 4**: מחלות נגיפיות בהיסטוריה
5. **פרק 5**: מערכת החיסון המולדת
6. **פרק 6**: מערכת החיסון הנרכשת
7. **פרק 7**: חיסונים – עקרונות ויישומים
8. **פרק 8**: נגיפי הקורונה ומגפת COVID-19

**נספחים:**
- נספח א': מילון מושגים
- נספח ב': מדריך למבחן
- נספח ג': בנק שאלות

---

*בהצלחה בלמידה!*
"""
    
    save_markdown(content, str(front_matter_path))
    return front_matter_path


def print_banner():
    """Print startup banner."""
    print("\n" + "=" * 60)
    print("  📚 Hebrew Virology Ebook Pipeline")
    print("  Multi-Agent System for Study Material Generation")
    print("=" * 60 + "\n")


def print_summary(results: dict, start_time: datetime):
    """Print final summary."""
    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("  📊 Pipeline Summary")
    print("=" * 60)
    
    print(f"\n⏱️  Total time: {duration:.1f} seconds")
    print(f"\n📁 Files processed:")
    print(f"   - Transcripts: {results.get('corpus', {}).get('total_files', 'N/A')}")
    print(f"   - Chapters created: {results.get('editor', {}).get('num_chapters', 'N/A')}")
    
    print(f"\n✅ Quality checks:")
    print(f"   - Terminology issues: {results.get('terminology', {}).get('inconsistencies', 'N/A')}")
    print(f"   - Proofreading issues: {results.get('proofreader', {}).get('issues_found', 'N/A')}")
    
    safety = results.get('safety', {})
    if safety.get('all_passed', False):
        print(f"   - Safety review: ✅ PASSED")
    else:
        print(f"   - Safety review: ⚠️ {safety.get('failed', 0)} files need review")
    
    print(f"\n📂 Output locations:")
    print(f"   - Book: {BOOK_DIR}")
    print(f"   - Logs: {OPS_DIR / 'logs'}")
    print(f"   - Reports: {OPS_DIR / 'reports'}")
    
    # Highest yield chapters (based on word count)
    print(f"\n📈 Ready for review!")
    print("=" * 60 + "\n")


def run_pipeline():
    """Execute the full pipeline."""
    print_banner()
    start_time = datetime.now()
    results = {}
    
    # Initialize logging
    log_path = str(OPS_DIR / "logs" / "pipeline.jsonl")
    logger = PipelineLogger(log_path)
    
    # Initialize TODO tracker
    todos_path = str(OPS_DIR / "reports" / "todos.md")
    todos = TodoTracker(todos_path)
    
    print(f"📝 Pipeline log: {log_path}")
    print(f"📋 TODOs: {todos_path}\n")
    
    agents = [
        ("A", "CorpusLibrarian", lambda: CorpusLibrarian(
            str(TRANSCRIPTS_DIR), str(OPS_DIR), logger, todos
        )),
        ("B", "CurriculumArchitect", lambda: CurriculumArchitect(
            str(OPS_DIR), str(BOOK_DIR), logger, todos
        )),
        ("C", "ChapterBriefBuilder", lambda: ChapterBriefBuilder(
            str(OPS_DIR), logger, todos
        )),
        ("D", "DraftWriter", lambda: DraftWriter(
            str(TRANSCRIPTS_DIR), str(OPS_DIR), logger, todos
        )),
        ("E", "DevelopmentalEditor", lambda: DevelopmentalEditor(
            str(OPS_DIR), str(BOOK_DIR), logger, todos
        )),
        ("F", "AssessmentDesigner", lambda: AssessmentDesigner(
            str(BOOK_DIR), str(OPS_DIR), logger, todos
        )),
        ("G", "TerminologyKeeper", lambda: TerminologyConsistencyKeeper(
            str(BOOK_DIR), str(OPS_DIR), logger, todos
        )),
        ("H", "Proofreader", lambda: CopyeditorProofreader(
            str(BOOK_DIR), str(OPS_DIR), logger, todos
        )),
        ("I", "SafetyReviewer", lambda: SafetyScopeReviewer(
            str(BOOK_DIR), str(OPS_DIR), logger, todos
        )),
    ]
    
    # Create front matter
    print("📄 Creating front matter...")
    create_front_matter(BOOK_DIR)
    
    # Run each agent
    for agent_id, agent_name, agent_factory in agents:
        print(f"\n{'─' * 50}")
        print(f"🤖 Agent {agent_id}: {agent_name}")
        print('─' * 50)
        
        try:
            agent = agent_factory()
            result = agent.run()
            
            # Store result
            result_key = agent_name.lower().replace("keeper", "").replace("reviewer", "")
            results[result_key] = result
            
        except Exception as e:
            print(f"❌ Error in {agent_name}: {e}")
            import traceback
            traceback.print_exc()
            
            # Log error but continue
            todos.add(agent_name, "pipeline", f"Agent failed: {e}")
    
    # Save TODOs
    todos.save()
    
    # Print summary
    print_summary(results, start_time)
    
    # Save results
    results_path = OPS_DIR / "reports" / "pipeline_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        # Convert Path objects to strings for JSON serialization
        serializable = {}
        for k, v in results.items():
            if isinstance(v, dict):
                serializable[k] = {
                    str(kk): str(vv) if isinstance(vv, Path) else vv 
                    for kk, vv in v.items()
                }
            else:
                serializable[k] = str(v) if isinstance(v, Path) else v
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    run_pipeline()
