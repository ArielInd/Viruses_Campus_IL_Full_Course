"""
Agent C: ChapterBriefBuilder
Produces detailed briefs for each chapter to guide writing.
"""

import os
import json
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .schemas import (
    ChapterBrief, PipelineLogger, TodoTracker,
    save_json, save_markdown, load_json
)

AGENT_NAME = "ChapterBriefBuilder"


class ChapterBriefBuilder:
    """
    Agent C: Produces one brief per chapter at /ops/artifacts/chapter_briefs/*.md
    Each brief includes objectives, definitions, tables, misconceptions, and question targets.
    """
    
    def __init__(self, ops_dir: str, logger: PipelineLogger, todos: TodoTracker):
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        self.briefs_dir = os.path.join(self.artifacts_dir, "chapter_briefs")
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        errors = []
        output_files = []

        try:
            # Load chapter plan
            plan_path = os.path.join(self.artifacts_dir, "chapter_plan.json")
            if not os.path.exists(plan_path):
                error_msg = f"Chapter plan not found at {plan_path}"
                errors.append(error_msg)
                self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
                raise FileNotFoundError(error_msg)

            try:
                chapter_plans = load_json(plan_path)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in chapter plan: {str(e)}"
                errors.append(error_msg)
                self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
                raise ValueError(error_msg)

            # Load file notes for content details
            file_notes = self._load_file_notes()

            print(f"[{AGENT_NAME}] Creating briefs for {len(chapter_plans)} chapters (parallel processing)")

            # Process chapter briefs in parallel
            with ThreadPoolExecutor(max_workers=min(len(chapter_plans), 4)) as executor:
                # Submit all tasks
                future_to_plan = {
                    executor.submit(self._process_single_brief, plan, file_notes): plan
                    for plan in chapter_plans
                }

                # Collect results as they complete
                for future in as_completed(future_to_plan):
                    plan = future_to_plan[future]
                    chapter_id = plan.get('chapter_id', 'unknown')
                    try:
                        brief_files = future.result()
                        output_files.extend(brief_files)
                        print(f"[{AGENT_NAME}] ✓ Completed brief for chapter {chapter_id}")
                    except Exception as e:
                        error_msg = f"Failed to create brief for chapter {chapter_id}: {str(e)}"
                        warnings.append(error_msg)
                        self.todos.add(AGENT_NAME, f"Chapter {chapter_id}", error_msg)
                        print(f"[{AGENT_NAME}] ✗ Warning: {error_msg}")

        except Exception as e:
            error_msg = f"Critical error in {AGENT_NAME}: {str(e)}"
            errors.append(error_msg)
            self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)
            raise

        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, errors)

        print(f"[{AGENT_NAME}] Created {len(output_files)} chapter briefs")

        return {
            "briefs_dir": self.briefs_dir,
            "num_briefs": len(chapter_plans)
        }
    
    def _process_single_brief(self, plan: Dict, file_notes: Dict) -> List[str]:
        """Process a single chapter brief and return list of output files."""
        chapter_id = plan.get('chapter_id', 'unknown')
        output_files = []

        # Create brief
        brief = self._create_brief(plan, file_notes)

        # Save as markdown
        brief_path = os.path.join(
            self.briefs_dir,
            f"chapter_{chapter_id}_brief.md"
        )
        brief_md = self._brief_to_markdown(brief)
        save_markdown(brief_md, brief_path)
        output_files.append(brief_path)

        # Also save as JSON for programmatic access
        json_path = os.path.join(
            self.briefs_dir,
            f"chapter_{chapter_id}_brief.json"
        )
        save_json(brief.__dict__, json_path)
        output_files.append(json_path)

        return output_files

    def _load_file_notes(self) -> Dict[str, Dict]:
        """Load file notes indexed by path."""
        notes = {}
        notes_dir = os.path.join(self.artifacts_dir, "file_notes")

        if os.path.exists(notes_dir):
            for filename in os.listdir(notes_dir):
                if filename.endswith('.json'):
                    path = os.path.join(notes_dir, filename)
                    note = load_json(path)
                    notes[note.get("path", "")] = note

        return notes
    
    def _create_brief(self, plan: Dict, file_notes: Dict) -> ChapterBrief:
        """Create a detailed brief for a chapter."""
        chapter_id = plan["chapter_id"]
        
        # Collect content from source files
        definitions = []
        topics = []
        expert_content = None
        lab_content = None
        
        for source_path in plan.get("source_files", []):
            note = file_notes.get(source_path, {})
            
            for defn in note.get("key_definitions", []):
                definitions.append(defn)
            
            topics.extend(note.get("main_topics", []))
            
            if note.get("expert_interview"):
                expert_content = {
                    "expert_name": note["expert_interview"],
                    "topic": note.get("title", ""),
                    "source": source_path
                }
            
            if note.get("lab_demo"):
                lab_content = {
                    "demo_title": note["lab_demo"],
                    "conceptual_focus": "עקרון ומסקנות, לא פרוטוקול",
                    "source": source_path
                }
        
        # Generate content sections
        content_sections = self._generate_content_sections(chapter_id, topics)
        
        # Generate tables needed
        tables = self._generate_tables_spec(chapter_id, plan.get("required_tables", []))
        
        # Key terms with English
        key_terms = self._generate_key_terms(chapter_id, definitions)
        
        return ChapterBrief(
            chapter_id=chapter_id,
            title=plan["hebrew_title"],
            objectives=plan.get("learning_objectives", []),
            roadmap=self._generate_roadmap(chapter_id, plan["hebrew_title"]),
            content_sections=content_sections,
            definitions_to_bold=plan.get("must_include_definitions", []),
            tables_to_create=tables,
            expert_perspective=expert_content,
            lab_demo_conceptual=lab_content,
            common_mistakes=plan.get("misconceptions_to_address", []),
            key_terms=key_terms,
            mcq_targets=plan.get("question_targets", [])[:6],
            short_answer_targets=plan.get("question_targets", [])[:3],
            thinking_question_target=self._get_thinking_question(chapter_id)
        )
    
    def _generate_roadmap(self, chapter_id: str, title: str) -> str:
        """Generate roadmap text for a chapter."""
        roadmaps = {
            "01": "פרק זה מניח את היסודות לכל הקורס. נתחיל בשאלה הפילוסופית \"מהם חיים?\", נעבור לכימיה בסיסית של החומר החי, ונסיים בהיכרות עם התא – יחידת הבסיס של כל הדברים החיים.",
            "02": "פרק זה עוסק במולקולות הגדולות של החיים – DNA, RNA, וחלבונים. נתחיל בהבנת מבנה ה-DNA ונסיים בתהליך תרגום המידע הגנטי לחלבונים.",
            "03": "בפרק זה נבחן מה קורה כשהבריאות מתערערת. נתחיל בסקירת סוגי המחלות וכיצד המדע מזהה את הגורמים להן, ונעבור להכיר את הנגיפים – הטפילים המושלמים.",
            "04": "נצא למסע בהיסטוריה האנושית ונבחן את הנגיפים ששינו את פני העולם – מהאבעבועות השחורות שהכריעו אימפריות ועד לשפעת שממשיכה לאיים עלינו.",
            "05": "נכיר את קו ההגנה הראשון והמהיר של הגוף – החסינות המולדת. נראה כיצד העור והריריות משמשים כחומות, וכיצד הגוף מגייס \"חיילים\" לאתר הפציעה.",
            "06": "נלמד על יחידת הקומנדו של הגוף – החסינות הנרכשת. נבין כיצד תאי B ו-T מפתחים נשק מדויק נגד פתוגנים ספציפיים וכיצד הם \"זוכרים\" אותם לעשרות שנים.",
            "07": "חיסונים הם ההישג הגדול ביותר של הרפואה הציבורית. נלמד כיצד הם עובדים, אילו סוגים קיימים, ונתמודד מדעית עם החששות והשמועות הנפוצות.",
            "08": "נשתמש בכל הכלים שרכשנו במהלך הספר – מבנה הנגיף, מנגנוני הדבקה וכלי החיסון – כדי לנתח את המגפה ששינתה את חיינו.",
        }
        return roadmaps.get(chapter_id, f"פרק זה עוסק ב{title}.")
    
    def _generate_content_sections(self, chapter_id: str, topics: List[str]) -> List[Dict]:
        """Generate content section specifications."""
        sections_map = {
            "01": [
                {"heading": "מהם החיים?", "key_points": ["מטרה, מבנה, תפקוד"]},
                {"heading": "יחידות מידה במדע", "key_points": ["מטר, סלזיוס, אטומים"]},
                {"heading": "התאים – יחידות החיים", "key_points": ["ליווינהוק, דוקטרינת התא"]},
                {"heading": "הרכב כימי של החיים", "key_points": ["CHON, כימיה אורגנית"]},
                {"heading": "מים – המולקולה המיוחדת", "key_points": ["קוטביות, קשרי מימן"]},
                {"heading": "סוכרים ורב-סוכרים", "key_points": ["גלוקוז, עמילן, גליקוגן"]},
                {"heading": "מבנה התא האאוקריוטי", "key_points": ["אברונים"]},
            ],
            "02": [
                {"heading": "פילמור – בניית שרשראות גדולות", "key_points": ["דחיסה, הידרוליזה"]},
                {"heading": "DNA – המולקולה הגנטית", "key_points": ["ניסוי גריפית', נוקלאוטידים"]},
                {"heading": "חוקי שרגף", "key_points": ["A=T, G=C"]},
                {"heading": "הסליל הכפול", "key_points": ["ווטסון וקריק, פרנקלין"]},
                {"heading": "שכפול ה-DNA", "key_points": ["סמי-קונסרבטיבי"]},
                {"heading": "הדוגמה המרכזית", "key_points": ["DNA→RNA→חלבון"]},
                {"heading": "חלבונים", "key_points": ["חומצות אמינו, קשר פפטידי"]},
                {"heading": "הקוד הגנטי", "key_points": ["קודונים, ריבוזום"]},
            ],
            "03": [
                {"heading": "מחלות: מדבקות מול לא מדבקות", "key_points": ["פתוגנים"]},
                {"heading": "העיקרים של קוך", "key_points": ["4 כללים"]},
                {"heading": "עולם הנגיפים", "key_points": ["גנום, קופסית, מעטפת"]},
                {"heading": "מיון בולטימור", "key_points": ["6 קבוצות, mRNA"]},
                {"heading": "תרביות תאים", "key_points": ["HeLa, CPE"]},
                {"heading": "מחזור החיים הנגיפי", "key_points": ["היצמדות→יציאה"]},
            ],
            "04": [
                {"heading": "דרכי העברה של נגיפים", "key_points": ["אוויר, מגע, וקטורים"]},
                {"heading": "אבעבועות שחורות", "key_points": ["Variola, הכחדה"]},
                {"heading": "קדחת צהובה", "key_points": ["יתושים, לואיזיאנה"]},
                {"heading": "אבולה", "key_points": ["קדחת דימומית, עטלפים"]},
                {"heading": "שפעת", "key_points": ["8 מקטעים, H/N"]},
                {"heading": "פוליו", "key_points": ["פה-צואה, שיתוק"]},
            ],
            "05": [
                {"heading": "מערכת החיסון: הצבא שבתוכנו", "key_points": ["לויקוציטים"]},
                {"heading": "מחסומים פיזיים וכימיים", "key_points": ["עור, ריריות, ליזוזים"]},
                {"heading": "זיהוי האויב: PAMPs ו-PRRs", "key_points": ["TLRs"]},
                {"heading": "דלקת", "key_points": ["ציטוקינים, נויטרופילים"]},
                {"heading": "המיקרוביום", "key_points": ["חיידקים ידידותיים"]},
                {"heading": "חסינות מולדת מול נרכשת", "key_points": ["מהירות vs זיכרון"]},
            ],
            "06": [
                {"heading": "חסינות נרכשת: דיוק וזיכרון", "key_points": ["אנטיגנים, אפיטופ"]},
                {"heading": "תאי B ונוגדנים", "key_points": ["IgM, IgG, IgA, IgE"]},
                {"heading": "תאי T ומערכת ה-MHC", "key_points": ["הצגת אנטיגנים"]},
                {"heading": "אלרגיות", "key_points": ["היסטמין, אנפילקסיס"]},
                {"heading": "כשל חיסוני", "key_points": ["תת-תזונה, SCID, HIV"]},
                {"heading": "ELISA", "key_points": ["בדיקות דם"]},
            ],
            "07": [
                {"heading": "עקרון הפעולה של חיסונים", "key_points": ["זיכרון חיסוני"]},
                {"heading": "היסטוריה: ג'נר והאבעבועות", "key_points": ["Vacca"]},
                {"heading": "סוגי חיסונים", "key_points": ["חי-מוחלש, מומת, תת-יחידה"]},
                {"heading": "נגיפים סרבנים", "key_points": ["HIV, שפעת"]},
                {"heading": "בטיחות ומיתוסים", "key_points": ["אוטיזם, תימרוסל"]},
                {"heading": "חסינות העדר", "key_points": ["הגנה קהילתית"]},
            ],
            "08": [
                {"heading": "משפחת Coronaviridae", "key_points": ["ספייק, RNA+, הגהה"]},
                {"heading": "היסטוריה: SARS ו-MERS", "key_points": ["זואונוזה"]},
                {"heading": "אבחון", "key_points": ["PCR, אנטיגן, סרולוגיה"]},
                {"heading": "חיסוני mRNA", "key_points": ["ננו-חלקיקים"]},
                {"heading": "עתיד המגפות", "key_points": ["זליגה טבעית"]},
            ],
        }
        return sections_map.get(chapter_id, [])
    
    def _generate_tables_spec(self, chapter_id: str, table_names: List[str]) -> List[Dict]:
        """Generate table specifications."""
        tables = []
        for name in table_names:
            tables.append({
                "name": name,
                "columns": ["תכונה", "A", "B"],
                "purpose": f"השוואה: {name}"
            })
        return tables
    
    def _generate_key_terms(self, chapter_id: str, definitions: List[Dict]) -> List[Dict]:
        """Generate key terms list."""
        # Add standard terms per chapter
        standard_terms = {
            "01": [
                {"hebrew": "תא", "english": "Cell"},
                {"hebrew": "אאוקריוט", "english": "Eukaryote"},
                {"hebrew": "פרוקריוט", "english": "Prokaryote"},
                {"hebrew": "קשר מימן", "english": "Hydrogen bond"},
            ],
            "02": [
                {"hebrew": "נוקלאוטיד", "english": "Nucleotide"},
                {"hebrew": "שעתוק", "english": "Transcription"},
                {"hebrew": "תרגום", "english": "Translation"},
                {"hebrew": "קודון", "english": "Codon"},
            ],
            "03": [
                {"hebrew": "קופסית", "english": "Capsid"},
                {"hebrew": "פתוגן", "english": "Pathogen"},
                {"hebrew": "פלאק", "english": "Plaque"},
            ],
            "04": [
                {"hebrew": "וקטור", "english": "Vector"},
                {"hebrew": "זואונוזה", "english": "Zoonosis"},
            ],
            "05": [
                {"hebrew": "מקרופאג", "english": "Macrophage"},
                {"hebrew": "ציטוקין", "english": "Cytokine"},
                {"hebrew": "דלקת", "english": "Inflammation"},
            ],
            "06": [
                {"hebrew": "נוגדן", "english": "Antibody"},
                {"hebrew": "אנטיגן", "english": "Antigen"},
            ],
            "07": [
                {"hebrew": "חיסון", "english": "Vaccine"},
                {"hebrew": "חסינות העדר", "english": "Herd immunity"},
            ],
            "08": [
                {"hebrew": "ספייק", "english": "Spike protein"},
                {"hebrew": "PCR", "english": "PCR"},
            ],
        }
        return standard_terms.get(chapter_id, [])
    
    def _get_thinking_question(self, chapter_id: str) -> str:
        """Get the thinking question target for a chapter."""
        questions = {
            "01": "האם נגיפים עונים על הקריטריונים לחיים?",
            "02": "מדוע רטרו-וירוסים שינו את הבנת הביולוגיה?",
            "03": "מדוע קולטנים קובעים את טווח המאכסנים?",
            "04": "כיצד ידע על דרכי העברה מסייע במניעת מגפה?",
            "05": "מדוע הגוף זקוק גם לחסינות מולדת וגם לנרכשת?",
            "06": "מדוע בדיקת ELISA שלילית אחרי הדבקה ב-HIV?",
            "07": "מדוע קשה לפתח חיסון ל-HIV?",
            "08": "מדוע נגיפים מעטלפים קטלניים לבני אדם?",
        }
        return questions.get(chapter_id, "שאלה לחשיבה")
    
    def _brief_to_markdown(self, brief: ChapterBrief) -> str:
        """Convert brief to markdown format."""
        md = f"# בריף לפרק {brief.chapter_id}: {brief.title}\n\n"
        md += f"*נוצר אוטומטית על ידי {AGENT_NAME}*\n\n"
        md += "---\n\n"
        
        md += "## מטרות למידה\n\n"
        for obj in brief.objectives:
            md += f"- {obj}\n"
        md += "\n"
        
        md += "## מפת דרכים\n\n"
        md += f"{brief.roadmap}\n\n"
        
        md += "## מתווה התוכן\n\n"
        for section in brief.content_sections:
            md += f"### {section['heading']}\n"
            for point in section.get('key_points', []):
                md += f"- {point}\n"
            md += "\n"
        
        if brief.definitions_to_bold:
            md += "## מונחים להדגשה (bold בהופעה ראשונה)\n\n"
            for term in brief.definitions_to_bold[:15]:
                md += f"- {term}\n"
            md += "\n"
        
        if brief.tables_to_create:
            md += "## טבלאות נדרשות\n\n"
            for table in brief.tables_to_create:
                md += f"- {table['name']}\n"
            md += "\n"
        
        if brief.expert_perspective:
            md += "## תיבת מומחה\n\n"
            md += f"- מומחה: {brief.expert_perspective.get('expert_name', 'N/A')}\n"
            md += f"- נושא: {brief.expert_perspective.get('topic', 'N/A')}\n\n"
        
        if brief.lab_demo_conceptual:
            md += "## הדגמת מעבדה (קונספטואלית בלבד!)\n\n"
            md += f"- כותרת: {brief.lab_demo_conceptual.get('demo_title', 'N/A')}\n"
            md += "- **הערה: ללא פרוטוקול מעשי!**\n\n"
        
        md += "## טעויות נפוצות לכסות\n\n"
        for mistake in brief.common_mistakes:
            md += f"- {mistake}\n"
        md += "\n"
        
        md += "## יעדי שאלות\n\n"
        md += f"**MCQ:** {', '.join(brief.mcq_targets)}\n\n"
        md += f"**שאלות קצרות:** {', '.join(brief.short_answer_targets)}\n\n"
        md += f"**שאלת חשיבה:** {brief.thinking_question_target}\n\n"
        
        md += "## מונחי מפתח\n\n"
        for term in brief.key_terms:
            md += f"- {term['hebrew']} ({term['english']})\n"
        
        return md
