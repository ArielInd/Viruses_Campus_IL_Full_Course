import os
import json

# The canonical ordered list from the prompt
EXPECTED_FILES = [
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
    "01_דברי_סיום.txt"
]

ROOT_DIR = "course_transcripts"
MANIFEST_PATH = "book/manifest.json"

def generate_manifest():
    file_map = {}
    
    # 1. Walk the directory and map basenames to full paths
    print(f"Scanning {ROOT_DIR}...")
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            file_map[file] = os.path.abspath(os.path.join(root, file))
    
    manifest = []
    
    # 2. Build the manifest ensuring order
    missing = []
    
    # Unit logic (simple heuristic based on filename digits, e.g. "1.2" -> Unit 1)
    
    for idx, expected_name in enumerate(EXPECTED_FILES, 1):
        if expected_name in file_map:
            # Infer unit from filename (e.g., "05_1.4_..." -> Unit 1)
            # Find the pattern X.Y 
            import re
            match = re.search(r'_(\d)\.(\d+)_', expected_name)
            if match:
                unit = int(match.group(1))
            else:
                # Special cases
                if "8.0" in expected_name: unit = 8 # handle 8.0 special case if regex fails
                elif "וירוס_הקורונה" in expected_name: unit = 1
                elif "אחרית_דבר" in expected_name: unit = 9 
                elif "דברי_סיום" in expected_name: unit = 9
                else: unit = 0 # Front matter or unknown
                
            manifest_item = {
                "order": idx,
                "filename": expected_name,
                "path": file_map[expected_name],
                "inferred_unit": unit
            }
            manifest.append(manifest_item)
        else:
            print(f"WARNING: File not found: {expected_name}")
            missing.append(expected_name)
            
    # 3. Write manifest
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump({"files": manifest, "missing": missing}, f, indent=2, ensure_ascii=False)
        
    print(f"Manifest written to {MANIFEST_PATH}")
    print(f"Found {len(manifest)}/{len(EXPECTED_FILES)} files.")

if __name__ == "__main__":
    generate_manifest()
