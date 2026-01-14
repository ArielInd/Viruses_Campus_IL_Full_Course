"""
Agent A: CorpusLibrarian
Reads all transcripts and produces structured notes, corpus index, and concepts map.
"""

import os
import re
from typing import List, Dict, Tuple

from .schemas import (
    FileNote, CorpusIndex, PipelineLogger, TodoTracker,
    save_json, save_markdown, read_file
)

AGENT_NAME = "CorpusLibrarian"

# Canonical transcript ordering from user request
CANONICAL_ORDER = [
    "01_וירוס_הקורונה.txt",
    "01_1.0_מבוא_לקורס.txt",
    "02_1.1_מהם_החיים_החיים_הם_קצת_יותר_מאשר_רק_לחיות.txt",
    "03_1.2_יחידות_מדידה_במדע.txt",
    "04_1.3_תאים_הם_יחידת_החיים.txt",
    "05_1.4_הרכב_החומרים.txt",
    "06_1.5_מים.txt",
    "07_1.6_סוכרים_ורב-סוכרים.txt",
    "08_1.7_הדגמת_מעבדה_–_צביעת_תאים.txt",
    "09_1.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_2.1_הדגמת_מעבדה_–_ההשפעה_של_סבון_על_חיידקים.txt",
    "03_2.2_מבנה_כללי_של_פולימרים_ליניאריים.txt",
    "04_2.3_DNA_–_הרכב_כימי_–_חוקי_שרגף_(Chargaff).txt",
    "05_2.4_DNA_–_מבנה_–_הסליל_הכפול.txt",
    "06_2.5_DNA_–_שכפול.txt",
    "07_2.6_ראיון_עם_פרופסור_דיוויד_בולטימור_(David_Baltimore)_הדוֹגמה_המרכזית.txt",
    "08_2.7_חלבונים.txt",
    "09_2.8_הקוד_הגנטי.txt",
    "10_2.9_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_3.1_מחלות_לא_מדבקות.txt",
    "03_3.2_מחלות_מדבקות_-_העיקרים_של_קוך_(Koch's_Postulates).txt",
    "04_3.3_הדגמת_מעבדה_–_גידול_תרביות_חיידקים.txt",
    "05_3.4_נגיפים_מגיעים_בכל_הצורות_והגדלים.txt",
    "06_3.5_ראיון_עם_פרופסור_דיוויד_בולטימור_(Baltimore_David)_–_סיווג_של_נגיפים.txt",
    "07_3.6_תרביות_תאים_וחקר_הנגיפים.txt",
    "08_3.7_תהליך_השכפול_של_הנגיפים.txt",
    "09_3.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_4.1_דרכי_העברה_של_נגיפים.txt",
    "03_4.2_נגיף_האבעבועות_השחורות.txt",
    "04_4.3_נגיף_הקדחת_הצהובה.txt",
    "05_4.4_נגיף_האבולה_–_קדחת_דימומית.txt",
    "06_4.5_ראיון_עם_פרופסור_אריקה_אולמן_ספיר_(Erica_Ollmann_Saphire)_אבולה.txt",
    "07_4.6_נגיף_השפעת.txt",
    "08_4.7_נגיף_הפוליו.txt",
    "09_4.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_5.1_האנטומיה_והתאים_של_מערכת_החיסון.txt",
    "03_5.2_העור_-_קו_ההגנה_הראשון.txt",
    "04_5.3_מקרופאגים_וזיהוי_פתוגנים.txt",
    "05_5.4_ראיון_עם_פרופסור_ברוס_בויטלר_(Bruce_Beutler)_–_TLRs.txt",
    "06_5.5_מערכת_החיסון_המולדת_ודלקת.txt",
    "07_5.6_המיקרוביום_–_הרוב_שחיי_בתוכנו.txt",
    "08_5.7_מערכת_החיסון_המולדת_מול_הנרכשת.txt",
    "09_5.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_6.1_תאי_B_–_מבנה_ותפקוד_הנוגדנים.txt",
    "03_6.2_כיצד_נוגדנים_מנטרלים_נגיפים.txt",
    "04_6.3_תאי_T_ומערכת_ה-MHC.txt",
    "05_6.4_נלחמים_בתולעים_ואלרגיות.txt",
    "06_6.5_כשל_חיסוני_–_תת_תזונה,_SCID_והכשל_החיסוני_הנרכש_(AIDS).txt",
    "07_6.6_ראיון_עם_פרופסור_רוברט_גאלו_(Robert_C._Gallo)_–_בדיקת_דם_ל-AIDS.txt",
    "08_6.7_ELISA_–_כיצד_בדיקות_דם_עובדות.txt",
    "09_6.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "02_7.1_חיסונים_–_עקרונות_בסיסיים.txt",
    "03_7.2_חיסוני_פוליו_ואבעבועות_שחורות.txt",
    "04_7.3_חיסוני_תת-יחידה.txt",
    "05_7.4_נגיפים_שלא_נשמעים_לכללים.txt",
    "06_7.5_ראיון_עם_פרופסור_פיטר_פאלזה_(Peter_Palese)_–_חיסון_השפעת.txt",
    "07_7.6_אז_איפה_המלכוד_מה_הסיכון.txt",
    "08_7.7_כמה_רעילים_הם_החיסונים.txt",
    "09_7.8_לוח_זמני_החיסונים_(השנתיים_הראשונות_של_החיים).txt",
    "10_7.9_דעת_מומחים_על_חשיבות_חיסונים.txt",
    "11_7.10_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "01_8.0_מבוא.txt",
    "02_8.1_משפחת_נגיפי_הקורונה.txt",
    "03_8.2_נגיפי_קורונה_שמדביקים_בעלי_חיים.txt",
    "04_8.3_נגיפי_קורונה_שמדביקים_בני_אדם.txt",
    "05_8.4_בדיקות_דיאגנוסטית.txt",
    "06_8.5_היבט_קליני_על_מחלת_הקורונה.txt",
    "07_8.6_מהפכת_החיסונים.txt",
    "08_8.7_מגפת_נגיף_הקורונה_2019.txt",
    "09_8.8_סיכום_–_רעיונות_מרכזיים_ומפות_מושגים.txt",
    "11_אחרית_דבר_–_השערות.txt",
    "01_דברי_סיום.txt",
]


class CorpusLibrarian:
    """
    Agent A: Reads all transcripts and produces:
    - /ops/artifacts/corpus_index.json
    - /ops/artifacts/file_notes/*.json
    - /ops/artifacts/concepts_map.md
    """
    
    def __init__(self, transcripts_dir: str, ops_dir: str, 
                 logger: PipelineLogger, todos: TodoTracker):
        self.transcripts_dir = transcripts_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        self.file_notes_dir = os.path.join(self.artifacts_dir, "file_notes")
        
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Find all transcript files
        transcript_files = self._find_transcripts()
        print(f"[{AGENT_NAME}] Found {len(transcript_files)} transcript files")
        
        # Process each file
        file_notes = []
        lessons = {}
        total_words = 0
        
        for path in transcript_files:
            try:
                note = self._process_file(path)
                file_notes.append(note)
                total_words += note.word_count
                
                # Group by lesson
                lesson_key = note.lesson_number
                if lesson_key not in lessons:
                    lessons[lesson_key] = []
                lessons[lesson_key].append(path)
                
                # Save individual note
                note_path = os.path.join(
                    self.file_notes_dir, 
                    f"{os.path.basename(path).replace('.txt', '.json')}"
                )
                save_json(note, note_path)
                output_files.append(note_path)
                
            except Exception as e:
                warnings.append(f"Error processing {path}: {str(e)}")
                self.todos.add(AGENT_NAME, path, f"Failed to process: {str(e)}")
        
        # Create corpus index
        corpus_index = CorpusIndex(
            total_files=len(file_notes),
            total_words=total_words,
            lessons=lessons,
            file_notes_dir=self.file_notes_dir,
            concepts_map_path=os.path.join(self.artifacts_dir, "concepts_map.md")
        )
        
        index_path = os.path.join(self.artifacts_dir, "corpus_index.json")
        save_json(corpus_index, index_path)
        output_files.append(index_path)
        
        # Generate concepts map
        concepts_map = self._generate_concepts_map(file_notes)
        concepts_path = os.path.join(self.artifacts_dir, "concepts_map.md")
        save_markdown(concepts_map, concepts_path)
        output_files.append(concepts_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Processed {len(file_notes)} files, {total_words} total words")
        
        return {
            "corpus_index": index_path,
            "concepts_map": concepts_path,
            "file_notes_dir": self.file_notes_dir,
            "total_files": len(file_notes),
            "total_words": total_words
        }
    
    def _find_transcripts(self) -> List[str]:
        """Find all transcript files in order."""
        all_files = []
        for root, dirs, files in os.walk(self.transcripts_dir):
            for f in files:
                if f.endswith('.txt') and not f.startswith('.'):
                    all_files.append(os.path.join(root, f))
        
        # Sort by canonical order if possible, otherwise by path
        def sort_key(path):
            basename = os.path.basename(path)
            try:
                return CANONICAL_ORDER.index(basename)
            except ValueError:
                # Not in canonical order, sort alphabetically at end
                return len(CANONICAL_ORDER) + ord(basename[0])
        
        return sorted(all_files, key=sort_key)
    
    def _process_file(self, path: str) -> FileNote:
        """Process a single transcript file."""
        content = read_file(path)
        filename = os.path.basename(path)
        
        # Extract lesson and unit numbers from filename
        lesson_num, unit_num = self._parse_filename(filename)
        
        # Extract title (cleaned from filename)
        title = self._extract_title(filename)
        
        # Count words
        word_count = len(content.split())
        
        # Extract key information
        main_topics = self._extract_topics(content)
        key_definitions = self._extract_definitions(content)
        mechanisms = self._extract_mechanisms(content)
        examples = self._extract_examples(content)
        
        # Check for special content
        expert_interview = None
        if "ראיון" in filename or "פרופסור" in filename:
            expert_interview = self._extract_expert_name(filename)
        
        lab_demo = None
        if "הדגמת מעבדה" in filename or "מעבדה" in filename:
            lab_demo = title
        
        # Find implied figures/diagrams
        implied_figures = self._find_implied_figures(content)
        
        return FileNote(
            filename=filename,
            path=path,
            lesson_number=lesson_num,
            unit_number=unit_num,
            title=title,
            word_count=word_count,
            main_topics=main_topics,
            key_definitions=key_definitions,
            mechanisms=mechanisms,
            examples=examples,
            expert_interview=expert_interview,
            lab_demo=lab_demo,
            implied_figures=implied_figures
        )
    
    def _parse_filename(self, filename: str) -> Tuple[str, str]:
        """Extract lesson and unit numbers from filename."""
        # Pattern: XX_Y.Z_title.txt where Y is lesson and Z is unit
        match = re.match(r'(\d+)_(\d+)\.(\d+)', filename)
        if match:
            return match.group(2), f"{match.group(2)}.{match.group(3)}"
        
        # Fallback pattern: XX_Y.Z without prefix number
        match = re.match(r'(\d+)\.(\d+)', filename)
        if match:
            return match.group(1), f"{match.group(1)}.{match.group(2)}"
        
        # Special cases (intro, epilogue)
        if "מבוא" in filename or "קורונה" in filename:
            return "0", "0.0"
        if "סיום" in filename or "אחרית" in filename:
            return "9", "9.0"
        
        return "unknown", "unknown"
    
    def _extract_title(self, filename: str) -> str:
        """Extract clean title from filename."""
        # Remove extension
        title = filename.replace('.txt', '')
        
        # Remove leading numbers and underscores
        title = re.sub(r'^\d+_\d+\.\d+_', '', title)
        title = re.sub(r'^\d+_', '', title)
        
        # Replace underscores with spaces
        title = title.replace('_', ' ')
        
        return title.strip()
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content."""
        topics = []
        
        # Look for Hebrew topic patterns
        patterns = [
            r'נושא[ים]?\s*[:-]\s*(.+?)(?:\n|$)',
            r'נלמד\s+(?:על\s+)?(.+?)(?:\n|$)',
            r'בפרק\s+זה\s+(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            topics.extend(matches[:5])  # Limit per pattern
        
        # Also extract from structure
        lines = content.split('\n')
        for line in lines[:50]:  # Look in first 50 lines
            if line.strip().startswith('•') or line.strip().startswith('-'):
                topic = line.strip().lstrip('•-').strip()
                if len(topic) > 5 and len(topic) < 100:
                    topics.append(topic)
        
        return list(set(topics))[:10]
    
    def _extract_definitions(self, content: str) -> List[Dict[str, str]]:
        """Extract key definitions from content."""
        definitions = []
        
        # Pattern: term - definition or term: definition
        patterns = [
            r'([א-ת\w-]+)\s*[-–:]\s*([^.\n]+\.)',
            r'מהו\s+(.+?)\?\s*(.+?\.)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for term, defn in matches[:10]:
                if len(term) > 2 and len(defn) > 10:
                    definitions.append({"term": term.strip(), "definition": defn.strip()})
        
        return definitions[:15]
    
    def _extract_mechanisms(self, content: str) -> List[str]:
        """Extract biological mechanisms mentioned."""
        mechanisms = []
        
        keywords = [
            'שכפול', 'תרגום', 'שעתוק', 'הידבקות', 'חדירה',
            'היצמדות', 'הרכבה', 'יציאה', 'פגוציטוזיס',
            'דלקת', 'נטרול', 'אופסוניזציה'
        ]
        
        for keyword in keywords:
            if keyword in content:
                # Extract surrounding context
                idx = content.find(keyword)
                start = max(0, idx - 50)
                end = min(len(content), idx + 100)
                context = content[start:end].replace('\n', ' ').strip()
                mechanisms.append(context)
        
        return list(set(mechanisms))[:10]
    
    def _extract_examples(self, content: str) -> List[str]:
        """Extract concrete examples from content."""
        examples = []
        
        patterns = [
            r'לדוגמ[הא]\s*[,:]?\s*(.+?)(?:\.|$)',
            r'למשל\s*[,:]?\s*(.+?)(?:\.|$)',
            r'כמו\s+(.+?)(?:\.|,|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            examples.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return list(set(examples))[:10]
    
    def _extract_expert_name(self, filename: str) -> str:
        """Extract expert name from interview filename."""
        # Handle both spaces and underscores after "פרופסור"
        # Capture everything until a parenthesis or the file extension
        match = re.search(r'פרופסור[\s_]+([^.(]+)', filename)
        if match:
            name = match.group(1).replace('.txt', '').strip().replace('_', ' ')
            return name
        return "Unknown Expert"
    
    def _find_implied_figures(self, content: str) -> List[str]:
        """Find references to figures or diagrams."""
        implied = []
        
        patterns = [
            r'כפי שניתן לראות',
            r'בתרשים',
            r'באיור',
            r'בדיאגרמה',
            r'המבנה נראה',
            r'הצורה של',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                idx = content.find(re.search(pattern, content).group())
                context = content[max(0, idx-20):min(len(content), idx+80)]
                implied.append(context.replace('\n', ' ').strip())
        
        return implied[:5]
    
    def _generate_concepts_map(self, file_notes: List[FileNote]) -> str:
        """Generate a concepts map markdown document."""
        md = "# מפת מושגים - קורס נגיפים וחיסונים\n\n"
        md += f"*נוצר אוטומטית על ידי {AGENT_NAME}*\n\n"
        md += "---\n\n"
        
        # Group by lesson
        lessons = {}
        for note in file_notes:
            lesson = note.lesson_number
            if lesson not in lessons:
                lessons[lesson] = []
            lessons[lesson].append(note)
        
        for lesson_num in sorted(lessons.keys()):
            notes = lessons[lesson_num]
            md += f"## שיעור {lesson_num}\n\n"
            
            for note in notes:
                md += f"### {note.title}\n"
                md += f"- מספר מילים: {note.word_count}\n"
                
                if note.main_topics:
                    md += f"- נושאים: {', '.join(note.main_topics[:5])}\n"
                
                if note.expert_interview:
                    md += f"- ראיון מומחה: {note.expert_interview}\n"
                
                if note.lab_demo:
                    md += f"- הדגמת מעבדה: {note.lab_demo}\n"
                
                md += "\n"
        
        return md
