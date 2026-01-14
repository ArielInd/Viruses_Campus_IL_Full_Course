"""
Agent B: CurriculumArchitect
Uses corpus index and notes to produce outline, manifest, and chapter plan.
"""

import os
from typing import List, Dict
from datetime import datetime

from .schemas import (
    ChapterPlan, PipelineLogger, TodoTracker,
    save_json, save_markdown, load_json
)

AGENT_NAME = "CurriculumArchitect"

# Chapter structure mapping lessons to chapters
CHAPTER_STRUCTURE = [
    {
        "chapter_id": "01",
        "hebrew_title": "מבוא – תאים הם יחידות החיים",
        "english_title": "Introduction – Cells Are the Units of Life",
        "lessons": ["0", "1"],
        "source_pattern": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"],
    },
    {
        "chapter_id": "02", 
        "hebrew_title": "מולקולות המקרו – מ-DNA לחלבונים",
        "english_title": "Macromolecules – From DNA to Proteins",
        "lessons": ["2"],
        "source_pattern": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9"],
    },
    {
        "chapter_id": "03",
        "hebrew_title": "נגיפים – מבנה, סיווג ושכפול", 
        "english_title": "Viruses – Structure, Classification and Replication",
        "lessons": ["3"],
        "source_pattern": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"],
    },
    {
        "chapter_id": "04",
        "hebrew_title": "מחלות נגיפיות בהיסטוריה",
        "english_title": "Viral Diseases in History",
        "lessons": ["4"],
        "source_pattern": ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8"],
    },
    {
        "chapter_id": "05",
        "hebrew_title": "מערכת החיסון המולדת",
        "english_title": "Innate Immunity",
        "lessons": ["5"],
        "source_pattern": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8"],
    },
    {
        "chapter_id": "06",
        "hebrew_title": "מערכת החיסון הנרכשת",
        "english_title": "Adaptive Immunity",
        "lessons": ["6"],
        "source_pattern": ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8"],
    },
    {
        "chapter_id": "07",
        "hebrew_title": "חיסונים – עקרונות ויישומים",
        "english_title": "Vaccines – Principles and Applications",
        "lessons": ["7"],
        "source_pattern": ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9", "7.10"],
    },
    {
        "chapter_id": "08",
        "hebrew_title": "נגיפי הקורונה ומגפת COVID-19",
        "english_title": "Coronaviruses and the COVID-19 Pandemic",
        "lessons": ["8", "9"],
        "source_pattern": ["8.0", "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "אחרית", "סיום"],
    },
]


class CurriculumArchitect:
    """
    Agent B: Produces outline, manifest, and chapter plan.
    """
    
    def __init__(self, ops_dir: str, book_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.book_dir = book_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        errors = []
        output_files = []

        try:
            # Load corpus index
            corpus_index_path = os.path.join(self.artifacts_dir, "corpus_index.json")
            if not os.path.exists(corpus_index_path):
                error_msg = f"Corpus index not found at {corpus_index_path}"
                errors.append(error_msg)
                self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
                raise FileNotFoundError(error_msg)

            corpus_index = load_json(corpus_index_path)

            # Load all file notes
            file_notes = self._load_file_notes()
            print(f"[{AGENT_NAME}] Loaded {len(file_notes)} file notes")

            if not file_notes:
                warning = "No file notes found - chapter plans may be incomplete"
                warnings.append(warning)
                print(f"[{AGENT_NAME}] Warning: {warning}")

            # Create chapter plans
            chapter_plans = []
            for chapter_config in CHAPTER_STRUCTURE:
                try:
                    plan = self._create_chapter_plan(chapter_config, file_notes)
                    chapter_plans.append(plan)
                except Exception as e:
                    error_msg = f"Failed to create plan for chapter {chapter_config.get('chapter_id')}: {str(e)}"
                    warnings.append(error_msg)
                    self.todos.add(AGENT_NAME, f"Chapter {chapter_config.get('chapter_id')}", error_msg)
                    print(f"[{AGENT_NAME}] Warning: {error_msg}")

            if not chapter_plans:
                error_msg = "No chapter plans created - critical failure"
                errors.append(error_msg)
                self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
                raise RuntimeError(error_msg)

            # Save chapter plan
            plan_path = os.path.join(self.artifacts_dir, "chapter_plan.json")
            try:
                save_json([p.__dict__ for p in chapter_plans], plan_path)
                output_files.append(plan_path)
            except Exception as e:
                error_msg = f"Failed to save chapter plan: {str(e)}"
                errors.append(error_msg)
                raise RuntimeError(error_msg)

            # Generate manifest.json
            manifest = self._generate_manifest(chapter_plans, file_notes)
            manifest_path = os.path.join(self.book_dir, "manifest.json")
            try:
                save_json(manifest, manifest_path)
            except Exception as e:
                error_msg = f"Failed to save manifest: {str(e)}"
                errors.append(error_msg)
                raise RuntimeError(error_msg)
            output_files.append(manifest_path)

            # Generate outline.md (Hebrew)
            outline = self._generate_outline(chapter_plans)
            outline_path = os.path.join(self.book_dir, "01_outline.md")
            try:
                save_markdown(outline, outline_path)
                output_files.append(outline_path)
            except Exception as e:
                error_msg = f"Failed to save outline: {str(e)}"
                warnings.append(error_msg)
                print(f"[{AGENT_NAME}] Warning: {error_msg}")

        except Exception as e:
            error_msg = f"Critical error in {AGENT_NAME}: {str(e)}"
            errors.append(error_msg)
            self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
            raise

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)

        print(f"[{AGENT_NAME}] Created {len(chapter_plans)} chapter plans")

        return {
            "chapter_plan": plan_path,
            "manifest": manifest_path,
            "outline": outline_path,
            "num_chapters": len(chapter_plans)
        }
    
    def _load_file_notes(self) -> List[Dict]:
        """Load all file notes from artifacts."""
        notes = []
        notes_dir = os.path.join(self.artifacts_dir, "file_notes")
        
        if os.path.exists(notes_dir):
            for filename in os.listdir(notes_dir):
                if filename.endswith('.json'):
                    path = os.path.join(notes_dir, filename)
                    notes.append(load_json(path))
        
        return notes
    
    def _create_chapter_plan(self, config: Dict, file_notes: List[Dict]) -> ChapterPlan:
        """Create a chapter plan from config and notes."""
        # Find matching source files
        source_files = []
        expert_box = None
        lab_box = None
        definitions = []
        topics = []
        
        for note in file_notes:
            unit = note.get("unit_number", "")
            for pattern in config["source_pattern"]:
                if unit.startswith(pattern) or pattern in note.get("filename", ""):
                    source_files.append(note["path"])
                    
                    # Collect expert interviews
                    if note.get("expert_interview"):
                        expert_box = note["expert_interview"]
                    
                    # Collect lab demos
                    if note.get("lab_demo"):
                        lab_box = note["lab_demo"]
                    
                    # Collect definitions
                    for defn in note.get("key_definitions", []):
                        definitions.append(defn.get("term", ""))
                    
                    # Collect topics
                    topics.extend(note.get("main_topics", []))
                    break
        
        # Generate learning objectives based on chapter
        objectives = self._generate_objectives(config["chapter_id"], topics)
        
        # Common misconceptions per chapter
        misconceptions = self._get_misconceptions(config["chapter_id"])
        
        # Question targets
        question_targets = self._get_question_targets(config["chapter_id"])
        
        return ChapterPlan(
            chapter_id=config["chapter_id"],
            hebrew_title=config["hebrew_title"],
            english_title=config["english_title"],
            source_files=source_files,
            learning_objectives=objectives,
            must_include_definitions=list(set(definitions))[:20],
            required_tables=self._get_required_tables(config["chapter_id"]),
            expert_box=expert_box,
            lab_box=lab_box,
            misconceptions_to_address=misconceptions,
            question_targets=question_targets
        )
    
    def _generate_objectives(self, chapter_id: str, topics: List[str]) -> List[str]:
        """Generate learning objectives for a chapter."""
        objectives_map = {
            "01": [
                "להגדיר את מאפייני החיים ולהבדיל בין חי לדומם",
                "לתאר את יחידות המידה הרלוונטיות למדע החיים",
                "להסביר את ההבדל בין תאים פרוקריוטיים לאאוקריוטיים",
                "לפרט את הרכב היסודות הכימיים של היצורים החיים",
                "לתאר את תכונות המים וחשיבותם לחיים",
                "להסביר את מבנה הסוכרים והרב-סוכרים",
                "לזהות את האברונים העיקריים בתא האאוקריוטי",
            ],
            "02": [
                "להסביר את תהליך הדחיסה (קונדנסציה) והידרוליזה בפילמור",
                "לתאר את מבנה הנוקלאוטידים והרכב ה-DNA",
                "לפרט את חוקי שרגף ומשמעותם",
                "לתאר את מבנה הסליל הכפול",
                "להסביר את מנגנון שכפול ה-DNA",
                "להגדיר את הדוגמה המרכזית (Central Dogma)",
                "לתאר את מבנה החלבונים וסוגי חומצות האמינו",
                "להסביר את הקוד הגנטי ואת תפקיד הריבוזומים",
            ],
            "03": [
                "להבחין בין מחלות מדבקות ללא מדבקות",
                "להבין את העיקרים של קוך לזיהוי פתוגנים",
                "להגדיר מהו נגיף ומאפייניו כטפיל מוחלט",
                "לתאר את מבנה הנגיף: גנום, קופסית ומעטפת",
                "להסביר את שיטת סיווג בולטימור",
                "לתאר את שלבי מחזור החיים הנגיפי",
            ],
            "04": [
                "להכיר את דרכי ההעברה העיקריות של נגיפים",
                "ללמוד על נגיף האבעבועות השחורות והשפעתו ההיסטורית",
                "להבין את הקשר בין וקטורים (יתושים) להעברת מחלות",
                "לתאר את מאפייני נגיף האבולה ומקורו",
                "להסביר את הגנום המחולק של נגיף השפעת",
                "להכיר את נגיף הפוליו ודרכי מניעתו",
            ],
            "05": [
                "להבין את מבנה מערכת החיסון ותאי הדם הלבנים",
                "לתאר את המחסומים הפיזיים והכימיים של הגוף",
                "להסביר כיצד מזהים פתוגנים באמצעות PAMPs ו-PRRs",
                "לתאר את תהליך הדלקת ותסמיניה",
                "להבין את תפקיד המיקרוביום",
                "להבחין בין חסינות מולדת לנרכשת",
            ],
            "06": [
                "להבין את הספציפיות והזיכרון של החסינות הנרכשת",
                "לתאר את מבנה הנוגדנים וסוגי ה-Ig השונים",
                "להסביר כיצד תאי T מזהים תאים נגועים דרך MHC",
                "להבין את הקשר בין אלרגיות ל-IgE",
                "לתאר את הגורמים לכשל חיסוני",
                "להסביר את מנגנון הפעולה של HIV",
                "להבין את עקרון בדיקת ELISA",
            ],
            "07": [
                "להסביר את עקרון הפעולה של חיסונים",
                "להבחין בין חיסון חי-מוחלש, מומת ותת-יחידה",
                "להבין מדוע קשה לפתח חיסון ל-HIV ושפעת",
                "להפריך מיתוסים בנוגע לבטיחות חיסונים",
                "להסביר את מושג חסינות העדר",
            ],
            "08": [
                "לתאר את מאפייני משפחת נגיפי הקורונה",
                "להשוות בין SARS, MERS ו-COVID-19",
                "להבחין בין סוגי בדיקות האבחון",
                "להסביר את מנגנון חיסוני ה-mRNA",
                "להבין את מקור הנגיפים הזואונוטי",
            ],
        }
        
        return objectives_map.get(chapter_id, ["להבין את נושאי הפרק"])
    
    def _get_misconceptions(self, chapter_id: str) -> List[str]:
        """Get common misconceptions for a chapter."""
        misconceptions_map = {
            "01": [
                "רוברט הוק גילה שהתאים חיים",
                "בלבול בין פרוקריוטים לאאוקריוטים",
                "המים חסרי משמעות כי הם רק ממס",
            ],
            "02": [
                "DNA ו-RNA זהים פרט לאות אחת",
                "השכפול מדויק ב-100%",
                "לכל חומצת אמינו קודון אחד",
            ],
            "03": [
                "לתאים יש קולטנים שתפקידם להכניס נגיפים",
                "כל הנגיפים הורגים את התא מיד",
            ],
            "04": [
                "נגיפים יכולים לחיות זמן רב מחוץ לגוף",
                "אנטיביוטיקה עוזרת נגד נגיפים",
            ],
            "05": [
                "דלקת היא תמיד דבר רע",
                "החסינות המולדת ספציפית",
            ],
            "06": [
                "נוגדנים יכולים להיכנס לתוך תאים",
                "כל הנוגדנים זהים",
            ],
            "07": [
                "חיסונים גורמים לאוטיזם",
                "חיסונים מכילים כמויות מסוכנות של כספית",
            ],
            "08": [
                "קורונה הוא נגיף חדש לחלוטין",
                "בדיקת PCR יכולה לזהות נגיף גם אחרי שהדבקה עברה",
            ],
        }
        return misconceptions_map.get(chapter_id, [])
    
    def _get_question_targets(self, chapter_id: str) -> List[str]:
        """Get question targets for assessments."""
        targets_map = {
            "01": ["דוקטרינת התא", "הבדל פרוקריוט/אאוקריוט", "קשר מימן", "פולימר/מונומר"],
            "02": ["חוקי שרגף", "הדוגמה המרכזית", "קודון", "קשר פפטידי"],
            "03": ["עיקרי קוך", "סיווג בולטימור", "מחזור נגיפי", "CPE"],
            "04": ["דרכי העברה", "זואונוזה", "שינוי אנטיגני בשפעת"],
            "05": ["PAMPs/PRRs", "דלקת", "מיקרוביום"],
            "06": ["IgM vs IgG", "MHC", "HIV", "ELISA"],
            "07": ["סוגי חיסונים", "חסינות עדר", "בטיחות"],
            "08": ["PCR vs אנטיגן", "mRNA vaccine", "ACE2"],
        }
        return targets_map.get(chapter_id, [])
    
    def _get_required_tables(self, chapter_id: str) -> List[str]:
        """Get required tables for a chapter."""
        tables_map = {
            "01": ["פרוקריוטים vs אאוקריוטים", "יסודות כימיים", "רב-סוכרים"],
            "02": ["בסיסים חנקניים", "תהליכי הדוגמה המרכזית", "סוגי חומצות אמינו"],
            "03": ["סיווג בולטימור", "שלבי מחזור נגיפי"],
            "04": ["נגיפים והמאפיינים שלהם", "דרכי העברה"],
            "05": ["חסינות מולדת vs נרכשת", "תאי מערכת החיסון"],
            "06": ["סוגי נוגדנים (Ig)", "הבדל תאי B ו-T"],
            "07": ["סוגי חיסונים", "יתרונות וחסרונות"],
            "08": ["השוואת קורונה וירוסים", "סוגי בדיקות"],
        }
        return tables_map.get(chapter_id, [])
    
    def _generate_manifest(self, chapter_plans: List[ChapterPlan], file_notes: List[Dict]) -> Dict:
        """Generate manifest.json."""
        manifest = {
            "title": "נגיפים, תאים וחיסונים",
            "title_en": "Viruses: From Molecular Biology to Pandemics",
            "language": "he",
            "created_at": datetime.now().isoformat(),
            "chapters": []
        }
        
        for plan in chapter_plans:
            chapter_entry = {
                "id": plan.chapter_id,
                "title": plan.hebrew_title,
                "title_en": plan.english_title,
                "sources": plan.source_files,
                "objectives_count": len(plan.learning_objectives),
                "has_expert_box": plan.expert_box is not None,
                "has_lab_demo": plan.lab_box is not None,
            }
            manifest["chapters"].append(chapter_entry)
        
        return manifest
    
    def _generate_outline(self, chapter_plans: List[ChapterPlan]) -> str:
        """Generate Hebrew outline document."""
        md = "# מתווה הספר: נגיפים – מביולוגיה מולקולרית למגפות\n\n"
        md += "## רציונל\n\n"
        md += "ספר זה הופך את ההרצאות לספר לימוד קוהרנטי. המבנה עוקב אחר התקדמות הקורס "
        md += "המקורי בן 8 השיעורים, כשהוא בונה באופן הגיוני מיסודות מולקולריים דרך מבנה נגיפי, "
        md += "מחלות ספציפיות, מערכת החיסון, חיסונים, ולבסוף מחקר המקרה הרלוונטי של COVID-19.\n\n"
        md += "---\n\n"
        md += "## מבנה הפרקים\n\n"
        
        for plan in chapter_plans:
            md += f"### פרק {plan.chapter_id}: {plan.hebrew_title}\n\n"
            md += f"*({plan.english_title})*\n\n"
            
            md += "**מטרות למידה מרכזיות:**\n"
            for obj in plan.learning_objectives[:5]:
                md += f"- {obj}\n"
            md += "\n"
            
            if plan.expert_box:
                md += f"**תיבת מומחה:** ראיון עם {plan.expert_box}\n\n"
            
            if plan.lab_box:
                md += f"**הדגמת מעבדה:** {plan.lab_box}\n\n"
            
            md += "---\n\n"
        
        md += "## נספחים\n\n"
        md += "- **מילון מונחים:** הגדרות מונחים מרכזיים (עברית/אנגלית)\n"
        md += "- **חזרה לבחינה:** סיכומים בנקודות, טעויות נפוצות\n"
        md += "- **בנק שאלות:** שאלות תרגול מכל הפרקים\n"
        
        return md
