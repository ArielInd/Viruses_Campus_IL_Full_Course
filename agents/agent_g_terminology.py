"""
Agent G: TerminologyConsistencyKeeper
Enforces consistent Hebrew terminology and acronyms.
"""

import os
import yaml
from typing import Dict

from .schemas import (
    ConsistencyReport, PipelineLogger, TodoTracker,
    save_markdown, read_file
)

AGENT_NAME = "TerminologyConsistencyKeeper"

# Canonical terminology
CANONICAL_TERMS = {
    # Scientific terms
    "DNA": {"hebrew": "DNA", "variants": ["דנ\"א", "די-אן-איי"], "english": "DNA"},
    "RNA": {"hebrew": "RNA", "variants": ["רנ\"א", "אר-אן-איי"], "english": "RNA"},
    "mRNA": {"hebrew": "mRNA", "variants": ["אם-אר-אן-איי"], "english": "messenger RNA"},
    "PCR": {"hebrew": "PCR", "variants": [], "english": "Polymerase Chain Reaction"},
    "ELISA": {"hebrew": "ELISA", "variants": [], "english": "Enzyme-Linked Immunosorbent Assay"},
    "MHC": {"hebrew": "MHC", "variants": [], "english": "Major Histocompatibility Complex"},
    "TLR": {"hebrew": "TLR", "variants": [], "english": "Toll-Like Receptor"},
    
    # Hebrew terms
    "נגיף": {"hebrew": "נגיף", "variants": ["וירוס"], "english": "virus"},
    "חיידק": {"hebrew": "חיידק", "variants": ["בקטריה"], "english": "bacterium"},
    "נוגדן": {"hebrew": "נוגדן", "variants": ["אנטיבודי"], "english": "antibody"},
    "אנטיגן": {"hebrew": "אנטיגן", "variants": [], "english": "antigen"},
    "קופסית": {"hebrew": "קופסית", "variants": ["קפסיד"], "english": "capsid"},
    "מעטפת": {"hebrew": "מעטפת", "variants": ["אנבלופ"], "english": "envelope"},
    "שעתוק": {"hebrew": "שעתוק", "variants": ["תעתוק"], "english": "transcription"},
    "תרגום": {"hebrew": "תרגום", "variants": [], "english": "translation"},
    "שכפול": {"hebrew": "שכפול", "variants": ["רפליקציה"], "english": "replication"},
}


class TerminologyConsistencyKeeper:
    """
    Agent G: Enforces consistent terminology across the book.
    Output: terminology.yml, glossary, consistency report
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
        
        # Save terminology reference
        term_path = os.path.join(self.ops_dir, "artifacts", "terminology.yml")
        self._save_terminology(term_path)
        output_files.append(term_path)
        
        # Scan all chapters for inconsistencies
        report = self._check_consistency()
        
        # Save consistency report
        report_path = os.path.join(self.ops_dir, "reports", "consistency_report.md")
        report_md = self._generate_report(report)
        save_markdown(report_md, report_path)
        output_files.append(report_path)
        
        # Generate/update glossary
        glossary = self._generate_glossary()
        glossary_path = os.path.join(self.book_dir, "90_glossary.md")
        save_markdown(glossary, glossary_path)
        output_files.append(glossary_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        print(f"[{AGENT_NAME}] Checked {report.total_terms_checked} terms, found {report.inconsistencies_found} issues")
        
        return {
            "terminology_file": term_path,
            "consistency_report": report_path,
            "glossary": glossary_path,
            "inconsistencies": report.inconsistencies_found
        }
    
    def _save_terminology(self, path: str):
        """Save terminology reference as YAML."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        term_dict = {}
        for key, data in CANONICAL_TERMS.items():
            term_dict[key] = {
                "canonical": data["hebrew"],
                "variants": data["variants"],
                "english": data["english"]
            }
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(term_dict, f, allow_unicode=True, default_flow_style=False)
    
    def _check_consistency(self) -> ConsistencyReport:
        """Check all chapters for terminology consistency."""
        total_checked = 0
        inconsistencies = 0
        fixes = []
        warns = []
        
        if not os.path.exists(self.chapters_dir):
            return ConsistencyReport(0, 0, [], ["Chapters directory not found"])
        
        for filename in os.listdir(self.chapters_dir):
            if not filename.endswith('.md'):
                continue
            
            path = os.path.join(self.chapters_dir, filename)
            content = read_file(path)
            
            for key, data in CANONICAL_TERMS.items():
                canonical = data["hebrew"]
                variants = data["variants"]
                
                # Check for variant usage
                for variant in variants:
                    if variant in content:
                        inconsistencies += 1
                        fixes.append({
                            "file": filename,
                            "found": variant,
                            "should_be": canonical
                        })
                
                total_checked += 1
        
        return ConsistencyReport(
            total_terms_checked=total_checked,
            inconsistencies_found=inconsistencies,
            fixes_applied=fixes,
            warnings=warns
        )
    
    def _generate_report(self, report: ConsistencyReport) -> str:
        """Generate consistency report markdown."""
        md = "# דוח עקביות מונחים\n\n"
        md += f"*נוצר על ידי {AGENT_NAME}*\n\n"
        md += "---\n\n"
        
        md += "## סיכום\n\n"
        md += f"- מונחים שנבדקו: {report.total_terms_checked}\n"
        md += f"- חוסר עקביות שנמצא: {report.inconsistencies_found}\n\n"
        
        if report.fixes_applied:
            md += "## בעיות שנמצאו\n\n"
            md += "| קובץ | נמצא | צריך להיות |\n"
            md += "|------|------|------------|\n"
            for fix in report.fixes_applied:
                md += f"| {fix['file']} | {fix['found']} | {fix['should_be']} |\n"
            md += "\n"
        else:
            md += "## תוצאה\n\n✅ לא נמצאו בעיות עקביות!\n\n"
        
        if report.warnings:
            md += "## אזהרות\n\n"
            for warn in report.warnings:
                md += f"- {warn}\n"
        
        return md
    
    def _generate_glossary(self) -> str:
        """Generate comprehensive glossary."""
        md = "# נספח א': מילון מושגים (Glossary)\n\n"
        md += "*מונחים חשובים מהקורס, מסודרים לפי אלפבית עברי.*\n\n"
        md += "---\n\n"
        
        # Comprehensive glossary entries
        glossary_entries = {
            "א": [
                ("אבולה (Ebola)", "נגיף ממשפחת ה-Filoviruses הגורם לקדחת דימומית קשה."),
                ("אבעבועות שחורות (Smallpox)", "מחלה קטלנית שהוכחדה עולמית בזכות חיסונים."),
                ("אדג'ובנט (Adjuvant)", "חומר המוסף לחיסון כדי להגביר את התגובה החיסונית."),
                ("אופסוניזציה (Opsonization)", "ציפוי פתוגן בנוגדנים לסימון לבליעה."),
                ("אימונוגלובולין (Immunoglobulin)", "שם נרדף לנוגדן, חלבון בצורת Y."),
                ("אלרגיה (Allergy)", "תגובת יתר של מערכת החיסון לחומר לא מזיק."),
                ("אנטיגן (Antigen)", "כל חומר המעורר תגובה חיסונית."),
            ],
            "ד": [
                ("דוגמה מרכזית (Central Dogma)", "זרימת מידע: DNA → RNA → חלבון."),
                ("דלקת (Inflammation)", "תגובה מקומית לזיהום: אודם, חום, נפיחות, כאב."),
                ("דנטורציה (Denaturation)", "הרס המבנה המרחבי של חלבון."),
            ],
            "ה": [
                ("הידרופובי (Hydrophobic)", "פחד מים, לא מסיס במים."),
                ("הידרופילי (Hydrophilic)", "אוהב מים, מסיס במים."),
                ("העברה זואונוטית (Zoonosis)", "מעבר מחלה מבעל חיים לאדם."),
            ],
            "ז": [
                ("זיכרון חיסוני (Immune Memory)", "יכולת לזכור פתוגן ולהגיב מהר בחשיפה חוזרת."),
            ],
            "ח": [
                ("חומצת אמינו (Amino Acid)", "אבן הבניין של חלבונים, 20 סוגים."),
                ("חסינות העדר (Herd Immunity)", "הגנה קהילתית כשרוב מחוסנים."),
            ],
            "ט": [
                ("טפיל מוחלט (Obligate Parasite)", "אורגניזם שחייב מארח להתרבות (כמו נגיף)."),
            ],
            "כ": [
                ("כימוקין (Chemokine)", "ציטוקין המושך תאי חיסון לאתר הזיהום."),
            ],
            "ל": [
                ("ליזוזים (Lysozyme)", "אנזים בדמעות ורוק המפרק חיידקים."),
                ("לימפוציט (Lymphocyte)", "תא דם לבן (B או T)."),
            ],
            "מ": [
                ("מגפה (Pandemic)", "התפרצות מחלה עולמית."),
                ("מיטוכונדריה (Mitochondria)", "אברון להפקת אנרגיה."),
                ("מיקרוביום (Microbiome)", "החיידקים הטבעיים בגופנו."),
                ("מעטפת ויראלית (Viral Envelope)", "קרום שומני המקיף חלק מהנגיפים."),
                ("מקרופאג (Macrophage)", "תא בולען גדול של החסינות המולדת."),
            ],
            "נ": [
                ("נוגדן (Antibody)", "חלבון בצורת Y המנטרל פתוגנים."),
                ("נויטרופיל (Neutrophil)", "תא דם לבן, קו הגנה ראשון."),
            ],
            "ס": [
                ("סיווג בולטימור (Baltimore Classification)", "מיון נגיפים לפי יצירת mRNA."),
            ],
            "פ": [
                ("פוליו (Polio)", "נגיף הגורם לשיתוק, מועבר פה-צואה."),
                ("פולימר (Polymer)", "מולקולה מיחידות חוזרות (מונומרים)."),
                ("פתוגן (Pathogen)", "גורם מחלה."),
            ],
            "צ": [
                ("ציטוקין (Cytokine)", "חלבון לתקשורת בין תאי חיסון."),
            ],
            "ק": [
                ("קודון (Codon)", "3 נוקלאוטידים = חומצת אמינו אחת."),
                ("קולטן (Receptor)", "חלבון על התא שהנגיף נקשר אליו."),
                ("קופסית (Capsid)", "המעטפת החלבונית של הנגיף."),
            ],
            "ר": [
                ("ריבוזום (Ribosome)", "מכונת התרגום, מייצרת חלבונים."),
            ],
            "ש": [
                ("שעתוק (Transcription)", "DNA → RNA."),
                ("שפעת (Influenza)", "נגיף RNA עטוף עם גנום מחולק."),
            ],
            "ת": [
                ("תאי B (B Cells)", "לימפוציטים המייצרים נוגדנים."),
                ("תאי T (T Cells)", "לימפוציטים ההורגים תאים נגועים."),
                ("תרגום (Translation)", "RNA → חלבון."),
            ],
        }
        
        for letter, entries in glossary_entries.items():
            md += f"## {letter}\n\n"
            for term, defn in entries:
                md += f"* **{term}**: {defn}\n"
            md += "\n"
        
        # Add acronyms section
        md += "## קיצורים נפוצים\n\n"
        acronyms = [
            ("ACE2", "קולטן הכניסה של SARS-CoV-2"),
            ("DNA", "חומצה דאוקסיריבונוקלאית, החומר התורשתי"),
            ("ELISA", "בדיקה לזיהוי נוגדנים/אנטיגנים"),
            ("MHC", "מולקולה להצגת פפטידים על פני התא"),
            ("mRNA", "RNA שליח"),
            ("PCR", "שכפול מהיר של DNA/RNA לאבחון"),
            ("RNA", "חומצת גרעין חד-גדילית"),
        ]
        
        for abbr, meaning in acronyms:
            md += f"* **{abbr}**: {meaning}\n"
        
        return md
