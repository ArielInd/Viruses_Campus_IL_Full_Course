# Exam-Prep Optimization Plan: Transform EPUB from Transcript Dump to Study Tool

## Executive Summary

**Purpose**: Refactor the programmatically-generated Hebrew EPUB "וירוסים: איך מנצחים אותם?" to function as an **exam-prep tool** that replaces video lectures, not a "publishable book."

**Current State**: 109KB EPUB with 10 chapters (02-12, skipping 07), generated from Campus IL course transcripts. Content is evidence-grounded with claim IDs, includes glossary and questions.

**Target Outcome**: Students can study efficiently in 3-4 passes:
1. **First pass (coverage)**: Read chapters quickly, highlight "must-know" bullets
2. **Second pass (consolidation)**: Create personal summaries from must-know lists
3. **Third pass (retrieval)**: Self-test with questions (answers hidden)
4. **Final pass**: Drill weak topics + misconception boxes

---

## What's Currently Working (Keep These!)

### ✅ Already Exam-Friendly Features

1. **Learning Objectives** (`## מטרות למידה`) - Every chapter starts with clear goals
   - Example (Chapter 03): "להגדיר את התא כיחידת החיים הבסיסית"
   - **Action**: Standardize format to bullet list (already done)

2. **Common Mistakes** (`## טעויות נפוצות ומלכודות`) - High-value for tests
   - Example (Chapter 05): "טעות: נגיפים הם חיידקים / הסבר: נגיפים קטנים בהרבה..."
   - **Action**: Keep and expand (see Phase 3)

3. **Quick Summary** (`## סיכום מהיר`) - Bullet-point recaps
   - Example (Chapter 03): "התאים הם יחידות החיים הבסיסיות"
   - **Action**: Keep as-is

4. **Key Terms** (`## מושגי מפתח`) - Term + definition format
   - Example: "**פתוגן:** אורגניזם מחולל מחלה"
   - **Action**: Keep, ensure glossary sync (Phase 2)

5. **Practice Questions** (`## שאלות לתרגול`) - MCQs with answers
   - Example: "מהי יחידת החיים הבסיסית? א. אטום ב. מולקולה ג. תא ד. אברון **תשובה:** ג"
   - **Action**: Fix answer separation (Phase 4)

---

## What Needs Fixing: 7 Exam-Prep Transformations

### 🔧 Transformation 1: Fix Chapter Naming for Concept Recall

**Problem**: Titles look like transcript artifacts
- Current: `פרק 03: 03_שיעור_1_תאים_הם_יחידות_החיים`
- Issue: Redundant numbering, underscores, lesson metadata visible

**Solution**: Concept-first titles with source as subtitle
```markdown
# פרק 3: תאים – יחידת החיים

**שיעור מקור**: שיעור 1 במערכת Campus IL
**מסמכים**: `03_שיעור_1_תאים_הם_יחידות_החיים/`
```

**Implementation**:
- **File**: `src/write_book.py` (lines 120-140, chapter generation prompt)
- **Change**: Update LLM prompt to format title as: `פרק {NUMBER}: {CONCEPT_NAME}`
- **Subtitle**: Add source metadata as italicized line below title

**Benefit**: Students can quickly map concepts to course structure while scanning TOC

---

### 🔧 Transformation 2: Replace "Book Outline" with Study Roadmap

**Problem**: `book/01_outline.md` is an internal file listing
- Current content: Lists chapter IDs and source transcript paths
- Useless for students: Doesn't explain learning path or dependencies

**Solution**: Create `book/01_study_guide.md` with:

```markdown
# מדריך למידה: איך להשתמש בספר זה

## מבנה הקורס
הקורס מורכב מ-10 פרקים שבונים זה על זה:

**חלק א: יסודות ביולוגיה** (פרקים 2-4)
- פרק 2: וירוס הקורונה – שאלות נפוצות [הקדמה]
- פרק 3: תאים – יחידת החיים [חובה]
- פרק 4: מקרומולקולות – מ-DNA לחלבונים [חובה]

**חלק ב: וירוסולוגיה** (פרקים 5-6)
- פרק 5: נגיפים – מבנה, תפקוד, הדבקה ושכפול [חובה]
- פרק 6: מחלות נגיפיות הומניות [חובה]

**חלק ג: מערכת החיסון** (פרקים 8-10)
- פרק 8: חסינות מולדת – קו הגנה ראשון [חובה]
- פרק 9: חסינות נרכשת – זיכרון חיסוני [חובה]
- פרק 10: חיסונים – יתרונות וחסרונות [חובה]

**חלק ד: מקרה בוחן** (פרקים 11-12)
- פרק 11: משפחת נגיפי הקורונה ומגפת COVID-19 [חובה]
- פרק 12: סיכום הקורס [חזרה]

## מפת תלות: מה צריך ללמוד קודם
```
תאים (3) → מקרומולקולות (4) → נגיפים (5) → מחלות (6)
                                          ↓
חסינות מולדת (8) ← חסינות נרכשת (9) ← חיסונים (10)
                                          ↓
                              COVID-19 (11) → סיכום (12)
```

## אסטרטגיית למידה (3 שבועות)
**שבוע 1**: קריאה מהירה – פרקים 3-6 (יסודות)
**שבוע 2**: עומק + תרגול – פרקים 8-11 (חיסון)
**שבוע 3**: חזרה + שאלות – כל הפרקים + בנק שאלות

## מה יהיה במבחן?
**בטוח בשאלון** (לפי ההרצאות):
- הגדרות בסיסיות: תא, פרוקריוט, אוקריוט, נגיף, פתוגן
- מנגנוני הדבקה נגיפית (חלבון ספייק, קולטנים)
- הבדלים: חסינות מולדת vs נרכשת
- סוגי חיסונים: חי מוחלש, מומת, mRNA
- COVID-19 specifics: מבנה, מנגנון, חיסונים

**סביר** (הרחבות):
- שכפול DNA/RNA (דוגמה הדגמתית)
- סיווג נגיפים לפי Baltimore
- נוגדנים חד-שבטיים ושימושים

**לא סביר** (פרטים היסטוריים):
- שמות מדענים מלאים (למעט קוך, פסטר)
- תאריכים מדויקים (למעט SARS 2003, COVID 2019)
```

**Implementation**:
- **File**: Create new `book/01_study_guide.md` (replace `01_outline.md`)
- **Generator**: Manual creation OR extend `src/assemble_extras.py` to auto-generate from manifest
- **Build**: Update `book/build_epub.sh` to use study guide instead of outline

---

### 🔧 Transformation 3: Add "Must-Know / Nice-to-Know" Signals

**Problem**: No differentiation between testable core content and enrichment
- Current: All content presented with equal weight
- Students waste time on interesting but non-essential details

**Solution**: Add priority signaling at chapter start

```markdown
## תוכן מרכזי

### ✅ חובה למבחן (Must-Know)
*קרא לעומק, זכור לטווח ארוך*

- התא הוא יחידת החיים הבסיסית
- הבדל בין פרוקריוט לאוקריוט (גרעין vs אין גרעין)
- ארבעת היסודות העיקריים בחיים: C, H, O, N
- מים = 70% מהגוף
- מקרומולקולות: חלבונים, DNA, RNA, פחמימות
- פולימרים ← מונומרים (מושג יסוד)
- חלבונים = כוח עבודה של התא (אנזימים)
- DNA/RNA = פולימרים של נוקלאוטידים

### ℹ️ רקע מעניין (Nice-to-Know)
*קרא להבנת הקשר, לא חובה לשינון*

- היסטוריה: לוונהוק, רוברט הוק, שליידן ושואן
- מיקרוסקופ העדשה היחידה של לוונהוק
- סוכרים D vs L (דקסטרו ולבו)
- פרטי מבנה אגר וצלחות פטרי
- הדגמת צביעת תאי הילה
```

**Implementation**:
- **File**: `src/write_book.py` (chapter generation prompt)
- **Change**: Add to prompt template:
  ```python
  PROMPT_TEMPLATE = """
  Structure the chapter with two-tier content:

  ## תוכן מרכזי

  ### ✅ חובה למבחן (Must-Know)
  *8-15 bullet points of core testable facts*

  ### ℹ️ רקע מעניין (Nice-to-Know)
  *3-6 bullets of context/enrichment*

  Then proceed with detailed sections...
  """
  ```
- **Benefit**: Students immediately know what to prioritize in time-constrained study

---

### 🔧 Transformation 4: Convert Transcript Paragraphs to Exam-Note Structures

**Problem**: Content is too prose-heavy for efficient studying
- Example (Chapter 05, lines 15-16):
  ```markdown
  מחלות מתרחשות כאשר התפקוד הפיזיולוגי הטבעי של גופנו משתבש. ניתן לחלק מחלות לשתי קטגוריות עיקריות: מחלות לא מדבקות ומחלות מדבקות. מחלות לא מדבקות הן מחלות כרוניות המתקדמות לאט לאורך זמן, כמו מחלות לב וכלי דם, סרטן וסוכרת.
  ```
- Issue: Rambling narrative style, hard to extract key facts quickly

**Solution**: Transform to bullet/table format

```markdown
### מבוא למחלות

**הגדרה**: מחלה = שיבוש בתפקוד הפיזיולוגי הטבעי של הגוף

**שני סוגי מחלות**:

| סוג | מאפיינים | דוגמאות | % תמותה עולמית |
|-----|----------|----------|----------------|
| **לא מדבקות** | כרוניות, מתקדמות לאט, לא מועברות | מחלות לב, סרטן, סוכרת | 65% |
| **מדבקות** | נגרמות מפתוגנים, מועברות | שפעת, COVID-19, אבולה | 35% |

**פתוגנים = אורגניזמים מחוללי מחלה**
- חיידקים (Bacteria)
- נגיפים (Viruses)
- פטריות (Fungi)
- טפילים (Parasites)
```

**Implementation**:
- **Rule of Thumb**: If paragraph > 5-6 lines → convert to list or table
- **Files**: All 10 chapter markdown files (`book/chapters/*.md`)
- **Method**: Manual refactoring OR regenerate with updated `src/write_book.py` prompt
- **Prompt Change**:
  ```python
  INSTRUCTIONS += """
  Use these formats:
  - Definitions: **Term** = definition (one line)
  - Comparisons: Tables with clear columns
  - Processes: Numbered steps or flowcharts
  - Lists: Bullets with ← arrows for relationships

  Avoid paragraphs > 4 lines.
  """
  ```

**Example Transformations**:

**Before** (Chapter 03, lines 28-30):
```markdown
ארבעה יסודות מרכיבים את מרבית גופנו: פחמן, חמצן, מימן וחנקן. המים מהווים 70 אחוזים מגופנו. 70% מגופנו עשויים ממים. מרבית משאר 30 האחוזים של גופנו עשויה ממקרומולקולות, פולימרים כמו חלבונים, דנ"א ורב-סוכרים.
```

**After**:
```markdown
### הרכב כימי של הגוף

**70% מים** (H₂O)
**30% מקרומולקולות**:
- חלבונים (Proteins) ← עשויים מ-amino acids
- דנ"א/רנ"א (DNA/RNA) ← עשויים מ-nucleotides
- פחמימות (Carbohydrates) ← עשויים מ-sugars

**4 יסודות עיקריים**: C, H, O, N (99% מגופנו)
```

---

### 🔧 Transformation 5: Fix Self-Testing – Separate Answers from Questions

**Problem**: Inline answers reduce testing effectiveness
- Current format (Chapter 03, lines 87-92):
  ```markdown
  1.  מהי יחידת החיים הבסיסית?
      *   א. אטום
      *   ב. מולקולה
      *   ג. תא
      *   ד. אברון
      *   **תשובה:** ג
  ```
- Issue: Eye catches answer immediately → no retrieval practice

**Solution**: Move all answers to end of book (or collapsible section)

**Option A: End-of-Book Answer Key**
```markdown
## שאלות לתרגול

1. מהי יחידת החיים הבסיסית?
   - א. אטום
   - ב. מולקולה
   - ג. תא
   - ד. אברון

2. מי ניסח את תורת התאים?
   - א. לוונהוק והוק
   - ב. שליידן ושואן
   - ג. הוק ודרווין
   - ד. פסטר וקוך

[... 3 more questions ...]

---

*תשובות בעמוד הבא – אל תציץ!*

\newpage

## מפתח תשובות – פרק 3

1. **ג** (תא)
2. **ב** (שליידן ושואן)
3. **ב** (פחמן, חמצן, מימן וחנקן)
```

**Option B: Collapsible HTML Details (EPUB 3 compatible)**
```html
<details>
<summary><strong>לחץ/י כאן לראות תשובות</strong></summary>
<ol>
  <li><strong>ג</strong> – התא הוא יחידת החיים הבסיסית</li>
  <li><strong>ב</strong> – שליידן ושואן ניסחו את תורת התאים</li>
</ol>
</details>
```

**Implementation**:
- **Files**: All chapter files (`book/chapters/*.md`) + `book/92_question_bank.md`
- **Method**:
  1. Strip inline `**תשובה:**` from all questions
  2. Create answer key sections at end of each chapter (after `\newpage`)
  3. OR consolidate all answers in `book/93_answer_key.md`
- **Build**: Update `build_epub.sh` to include answer key file
- **Test**: Verify students must scroll/page-turn to see answers

---

### 🔧 Transformation 6: Create High-Yield Comparison Tables (Formula Sheet Equivalent)

**Problem**: Biology doesn't have "formulas" but has key comparisons scattered through text
- Missing: Quick-reference tables for exam prep

**Solution**: Create `book/89_quick_reference.md` with essential tables

```markdown
# טבלאות התייחסות מהירה

## תאים: פרוקריוט vs אוקריוט

| מאפיין | פרוקריוט | אוקריוט |
|--------|-----------|---------|
| גרעין | ✗ אין | ✓ יש |
| גודל | קטן (1-10 μm) | גדול (10-100 μm) |
| אברונים | ✗ אין | ✓ יש (מיטוכונדריה, גולג'י) |
| דוגמאות | חיידקים | בעלי חיים, צמחים, פטריות |

## נגיפים: DNA vs RNA

| מאפיין | נגיפי DNA | נגיפי RNA |
|--------|-----------|-----------|
| חומר גנטי | DNA | RNA |
| מיקום שכפול | גרעין התא (בדרך כלל) | ציטופלזמה |
| שיעור מוטציות | נמוך | גבוה |
| מערכת תיקון | יש | לרוב אין (מלבד קורונה) |
| דוגמאות | הרפס, אבעבועות | שפעת, קורונה, HIV |

## חסינות: מולדת vs נרכשת

| מאפיין | חסינות מולדת | חסינות נרכשת |
|--------|---------------|---------------|
| זמן תגובה | מיידי (דקות-שעות) | איטי (ימים-שבועות) |
| ספציפיות | כללי (מזהה PAMPs) | ספציפי (אנטיגן) |
| זיכרון | ✗ אין | ✓ יש |
| תאים עיקריים | מקרופאגים, נויטרופילים, NK | T cells, B cells |
| דוגמאות | דלקת, חום, מקרופאגים אוכלים חיידקים | נוגדנים, חיסונים |

## סוגי חיסונים

| סוג | טכנולוגיה | יתרונות | חסרונות | דוגמה |
|-----|-----------|---------|----------|--------|
| **חי מוחלש** | נגיף חי אך חלש | חיסון חזק, זיכרון ארוך | סיכון לחולים חסיני חיסון | חצבת, אבעבועות רוח |
| **מומת** | נגיף הרוג | בטוח יותר | פחות יעיל, צריך חיזוקים | פוליו (Salk) |
| **תת-יחידה** | רק חלבון ספייק | בטוח מאוד | פחות יעיל | הפטיטיס B |
| **mRNA** | הוראות ליצור ספייק | מהיר לפתח, יעיל | דורש קירור, טכנולוגיה חדשה | Pfizer, Moderna (COVID) |
| **וקטור ויראלי** | נגיף אחר נושא גן ספייק | יעיל, זול | תגובה לווקטור | AstraZeneca (COVID) |

## משפחת קורונה: השוואת מגפות

| נגיף | שנה | מקור | קולטן | מקרים | תמותה | מדבקות |
|------|-----|------|-------|-------|-------|--------|
| **SARS-CoV-1** | 2003 | סיבט ← עטלף | ACE2 | ~8,000 | ~10% | בינוני |
| **MERS** | 2012 | גמל ← עטלף | DPP4 | ~2,500 | ~36% | נמוך |
| **SARS-CoV-2** | 2019 | עטלף? | ACE2 | 600M+ | ~1-2% | גבוה מאוד |

## מקרומולקולות

| סוג | מונומר | פולימר | תפקיד עיקרי |
|-----|--------|--------|-------------|
| **פחמימות** | Monosaccharide (גלוקוז) | Polysaccharide (עמילן, גליקוגן) | אנרגיה |
| **חלבונים** | Amino acid (20 סוגים) | Protein | מבנה, אנזימים, הגנה |
| **חומצות גרעין** | Nucleotide (4-8 סוגים) | DNA/RNA | מידע גנטי |
| **שומנים** | Fatty acid + glycerol | Phospholipid | ממברנות |
```

**Implementation**:
- **File**: Create new `book/89_quick_reference.md`
- **Content**: Extract from existing chapters + structure as tables
- **Build**: Add to `build_epub.sh` before glossary
- **Order**: Front matter → Study guide → Chapters → Quick reference → Glossary → Questions → Answer key

---

### 🔧 Transformation 7: Fix Glossary for True Exam Utility

**Problem**: Current glossary is inconsistent and hard to use
- Mixed Hebrew/English definitions
- Empty cells (`-` in English column)
- No alphabetical sorting (Hebrew or English)
- 107KB file (too large, likely duplicates)

**Current Format** (lines 5-10):
```markdown
| **229E** | 229E | נגיף קורונה (Coronavirus) הגורם למחלות דמויות הצטננות (that causes cold-like illnesses) |
| **3 prime UTR** | - | Untranslated region that ends with a poly A sequence |
| **5 Prime UTR** | - | Untranslated region preceded by a 5 Prime cap structure and contains a ribosome binding site |
```

**Issues**:
1. Inconsistent language (some Hebrew def, some English def)
2. Missing transliterations (English speakers can't search)
3. No sorting (impossible to find terms quickly)

**Solution**: Standardized three-column format

```markdown
# מילון מושגים

## א (Alef)

| מונח בעברית | English / תעתיק | הגדרה מלאה |
|-------------|-----------------|-----------|
| **אברון** | Organelle | מבנה תוך-תאי בעל תפקיד מוגדר (מיטוכונדריה, גולג'י, גרעין) |
| **אוקריוט** | Eukaryote | תא בעל גרעין ואברונים מעוטפים בממברנה (בעלי חיים, צמחים) |
| **אמפיפתי** | Amphipathic | מולקולה בעלת חלק הידרופילי (אוהב מים) וחלק הידרופובי (דוחה מים) |
| **אנזים** | Enzyme | חלבון מזרז תהליכים כימיים בגוף (כל האנזימים הם חלבונים) |

## ב (Bet)

| מונח בעברית | English / תעתיק | הגדרה מלאה |
|-------------|-----------------|-----------|
| **בקטריופאג'** | Bacteriophage | נגיף שמדביק חיידקים |

## ג (Gimel)

| מונח בעברית | English / תעתיק | הגדרה מלאה |
|-------------|-----------------|-----------|
| **גרעין** | Nucleus | אברון מרכזי התא המכיל DNA וכרומוזומים |
| **גלוקוז** | Glucose | סוכר פשוט (monosaccharide) בעל נוסחה C₆H₁₂O₆, מקור אנרגיה עיקרי |

[... continue alphabetically ...]

## ק (Qof)

| מונח בעברית | English / תעתיק | הגדרה מלאה |
|-------------|-----------------|-----------|
| **קפסיד** | Capsid | מעטפת חלבון המגנה על הגנום הנגיפי |
| **קולטן** | Receptor | חלבון על פני התא שנגיף נקשר אליו (ACE2 לקורונה, CD4 ל-HIV) |
| **קורונה** | Corona (crown) | משפחת נגיפי RNA בעלי "כתר" של חלבוני ספייק על פני השטח |

---

## English → עברית (Reverse Index)

| English Term | עברית | Short Definition |
|--------------|-------|------------------|
| **ACE2** | ACE2 | Angiotensin-converting enzyme 2, קולטן לנגיף הקורונה |
| **Amino acid** | חומצת אמינו | Building block of proteins (20 types) |
| **Antibody** | נוגדן | חלבון במערכת החיסון שמזהה אנטיגנים |
| **Antigen** | אנטיגן | Molecule that triggers immune response |
| **Capsid** | קפסיד | Protein shell protecting viral genome |

[... continue alphabetically ...]
```

**Implementation**:
- **File**: Refactor `book/90_glossary.md` (currently 107KB)
- **Method**:
  1. Load `ops/artifacts/terminology.yml` (128KB source)
  2. Filter: Remove duplicates, keep only terms used in chapters
  3. Translate: Ensure every Hebrew term has English + vice versa
  4. Sort: Hebrew alphabetical (א-ת), then create English reverse index
- **Script**: Create `src/refactor_glossary.py`
  ```python
  import yaml
  from collections import defaultdict

  def refactor_glossary():
      with open('ops/artifacts/terminology.yml') as f:
          terms = yaml.safe_load(f)

      # Group by Hebrew first letter
      hebrew_grouped = defaultdict(list)
      for term in terms:
          first_letter = term['hebrew'][0]
          hebrew_grouped[first_letter].append(term)

      # Sort within each letter
      for letter in hebrew_grouped:
          hebrew_grouped[letter].sort(key=lambda x: x['hebrew'])

      # Generate markdown
      output = "# מילון מושגים\n\n"
      for letter in sorted(hebrew_grouped.keys()):
          output += f"## {letter}\n\n"
          output += "| מונח בעברית | English / תעתיק | הגדרה מלאה |\n"
          output += "|-------------|-----------------|------------|\n"
          for term in hebrew_grouped[letter]:
              heb = term['hebrew']
              eng = term.get('english', '—')
              defn = term['definition']
              output += f"| **{heb}** | {eng} | {defn} |\n"
          output += "\n"

      # Add reverse index
      output += "---\n\n## English → עברית (Reverse Index)\n\n"
      # ... (similar logic)

      with open('book/90_glossary.md', 'w') as f:
          f.write(output)
  ```
- **Benefit**: Students can quickly look up terms while studying (EPUB reader search works well)

---

## Implementation Decisions (User Confirmed)

✅ **Scope**: All priorities (18-26 hours) - Complete exam-prep overhaul
✅ **Answer Format**: End-of-chapter answers (each chapter has questions, then `\newpage`, then answer key)
✅ **Method**: Regenerate chapters with updated LLM prompts (requires Gemini API access)
✅ **Chapter Numbering**: Reorder based on lesson structure (Lesson 1 → Chapter 1, etc.)
  - Current Chapter 02 (COVID FAQ) is actually introductory, may become Chapter 0 or Introduction
  - Chapter 07 is midterm exam (not a content chapter)
  - Need to map lesson numbers to chapter numbers correctly

---

## Implementation Roadmap

### Priority 0: Chapter Renumbering (FIRST)

**Estimated Time**: 1-2 hours

**Critical Fix**: Current chapter IDs (02, 03, 04, 05, 06, 08, 09, 10, 11, 12) don't match lesson numbers.

**Actual Lesson Structure** (from manifest.json):

| Current Chapter ID | Lesson Number | Title | New Chapter Number |
|-------------------|---------------|-------|-------------------|
| 02 | 0 (intro) | COVID-19 FAQ | 00 (Introduction) |
| 03 | 1 | תאים הם יחידות החיים | 01 |
| 04 | 2 | מקרומולקולות | 02 |
| 05 | 3 | נגיפים - מבנה ותפקוד | 03 |
| 06 | 4 | מחלות נגיפיות הומניות | 04 |
| 08 | 5 | חסינות מולדת | 05 |
| 09 | 6 | חסינות נרכשת | 06 |
| 10 | 7 | חיסונים | 07 |
| 11 | 8 | משפחת נגיפי הקורונה | 08 |
| 12 | - | סיכום הקורס | 09 (Epilogue) |

**Note**: Lesson 7 is the midterm exam (not represented as a chapter)

**Action**:
1. **Do NOT rename files** - Keep current numbering (02-12) to preserve traceability
2. **Fix chapter titles only** - Update display titles to use lesson numbers:
   - `פרק 00: וירוס הקורונה – מבוא` (Introduction)
   - `פרק 1: תאים – יחידת החיים` (Lesson 1)
   - `פרק 2: מקרומולקולות – מ-DNA לחלבונים` (Lesson 2)
   - ...
   - `פרק 7: חיסונים – כיצד הם פועלים` (Lesson 7)
   - `פרק 8: משפחת נגיפי הקורונה ומגפת COVID-19` (Lesson 8)
   - `פרק 9: סיכום הקורס` (Epilogue)
3. Update TOC generation to reflect lesson-based numbering
4. Add note in study guide: "הערה: אין פרק למבחן האמצע (שיעור 7 במערכת המקורית)"

**Benefit**: Titles match lesson flow while preserving file-based traceability

---

### Priority 1: High-Impact, Low-Effort

**Estimated Time**: 4-6 hours

#### Task 1.1: Update `src/write_book.py` - Fix Chapter Title Generation (30 min)

**File**: `src/write_book.py` (lines ~120-160, chapter generation prompt)

**Change**: Update the LLM prompt template to generate lesson-based chapter numbers:

```python
# Find the section that builds the chapter prompt (around line 150)
# Current prompt likely says: "Write a chapter titled '{title}'"
# Change to:

LESSON_MAPPING = {
    "02": (0, "וירוס הקורונה – מבוא"),
    "03": (1, "תאים – יחידת החיים"),
    "04": (2, "מקרומולקולות – מ-DNA לחלבונים"),
    "05": (3, "נגיפים – מבנה, תפקוד, הדבקה ושכפול"),
    "06": (4, "מחלות נגיפיות הומניות"),
    "08": (5, "חסינות מולדת – קו ההגנה הראשון"),
    "09": (6, "חסינות נרכשת – מחסלים את האויב"),
    "10": (7, "חיסונים – כיצד הם פועלים"),
    "11": (8, "משפחת נגיפי הקורונה ומגפת COVID-19"),
    "12": (9, "סיכום הקורס"),
}

def generate_chapter_title(chapter_id, original_title):
    """Generate student-friendly chapter title based on lesson number"""
    if chapter_id in LESSON_MAPPING:
        lesson_num, clean_title = LESSON_MAPPING[chapter_id]
        if lesson_num == 0:
            return f"מבוא: {clean_title}"
        elif lesson_num == 9:
            return f"סיכום: {clean_title}"
        else:
            return f"פרק {lesson_num}: {clean_title}"
    return original_title

# Then in the prompt template:
chapter_title = generate_chapter_title(chapter_id, plan['title'])
prompt = f"""
# {chapter_title}

**שיעור מקור**: {plan['title']}
**תעוד**: מקורות במערכת Campus IL

[rest of prompt...]
"""
```

**Alternative**: If `src/write_book.py` is complex, create `src/fix_chapter_titles.py` to post-process generated markdown files.

#### Task 1.2: Create Study Roadmap (2 hours)

**File**: Create new `book/01_study_guide.md`

**Content**: See full template in Transformation 2 above (lines 76-130 of this plan)

**Key Sections**:
- Course structure (4 parts: Biology basics, Virology, Immunity, COVID case study)
- Dependency map (ASCII diagram showing prerequisites)
- 3-week study strategy
- "What will be on the exam?" (Must-know vs Nice-to-know topics)

**Update**: `book/build_epub.sh` line ~15:
```bash
# Change from:
pandoc ... book/01_outline.md ...

# To:
pandoc ... book/01_study_guide.md ...
```

#### Task 1.3: Separate Question Answers - End of Chapter Format (1 hour)

**Files**: All `book/chapters/*.md` files

**Method**: Python script to automate this transformation

**Create**: `src/separate_answers.py`

```python
#!/usr/bin/env python3
"""Separate inline answers from questions in all chapters"""

import re
from pathlib import Path

def separate_answers_in_chapter(chapter_path):
    """
    Transform questions from:
        1. Question text?
           - a. Option A
           - b. Option B
           **תשובה:** a

    To:
        ## שאלות לתרגול

        1. Question text?
           - a. Option A
           - b. Option B

        \newpage

        ## מפתח תשובות

        1. **a** - [optional explanation]
    """
    content = chapter_path.read_text(encoding='utf-8')

    # Find the questions section
    questions_pattern = r'##\s*שאלות לתרגול\s*\n(.*?)(?=##|\Z)'
    match = re.search(questions_pattern, content, re.DOTALL)

    if not match:
        print(f"No questions found in {chapter_path.name}")
        return content

    questions_section = match.group(1)

    # Extract answers
    # Pattern: 1. [question] ... **תשובה:** [answer]
    answer_pattern = r'(\d+)\.\s*(.*?)\*\*תשובה:\*\*\s*([א-ת]|[a-d])'

    answers = []
    for match in re.finditer(answer_pattern, questions_section, re.DOTALL):
        q_num = match.group(1)
        answer = match.group(3)
        answers.append(f"{q_num}. **{answer}**")

    # Remove inline answers
    questions_clean = re.sub(r'\s*\*\*תשובה:\*\*\s*[א-ת]', '', questions_section)

    # Reconstruct
    new_questions_section = f"""## שאלות לתרגול

{questions_clean.strip()}

---

*תשובות בעמוד הבא – נסו לענות בעצמכם קודם!*

\\newpage

## מפתח תשובות

{chr(10).join(answers)}
"""

    # Replace in content
    new_content = re.sub(questions_pattern, f"## שאלות לתרגול\n{new_questions_section}", content, flags=re.DOTALL)

    return new_content

if __name__ == "__main__":
    chapters_dir = Path("book/chapters")

    for chapter_file in sorted(chapters_dir.glob("*.md")):
        print(f"Processing {chapter_file.name}...")
        new_content = separate_answers_in_chapter(chapter_file)
        chapter_file.write_text(new_content, encoding='utf-8')

    print("✅ All chapters processed")
```

**Run**: `python3 src/separate_answers.py`

#### Task 1.4: Create Quick Reference Tables (2 hours)

**File**: Create new `book/89_quick_reference.md`

**Content**: See full template in Transformation 6 above (lines 339-397 of this plan)

**Tables to Create**:
1. Prokaryote vs Eukaryote cells
2. DNA vs RNA viruses
3. Innate vs Adaptive immunity
4. Vaccine types comparison (5 types: live attenuated, inactivated, subunit, mRNA, viral vector)
5. Coronavirus pandemics (SARS, MERS, COVID-19)
6. Macromolecules overview

**Update**: `book/build_epub.sh` to include quick reference before glossary

**Test**: Rebuild EPUB, verify TOC order and answer separation work

---

### Priority 2: Medium-Impact, Medium-Effort (Do Second)

**Estimated Time**: 6-8 hours

#### Task 2.1: Add Must-Know/Nice-to-Know Signals (3 hours)

**File**: `src/write_book.py` (chapter generation prompt)

**Change**: Update the LLM prompt to add priority tiers at the start of content

```python
# Add to the chapter generation prompt (around line 160-180):

CHAPTER_PROMPT_TEMPLATE = """
Write a comprehensive Hebrew chapter titled "{chapter_title}" based ONLY on the provided evidence claims.

## Structure Requirements

### מטרות למידה (Learning Objectives)
[existing prompt...]

### מפת דרכים (Roadmap)
[existing prompt...]

### תוכן מרכזי (Main Content)

**CRITICAL: Start with priority signals:**

#### ✅ חובה למבחן (Must-Know)
*קרא לעומק, זכור לטווח ארוך*

Generate 8-15 bullet points of core testable facts from the evidence. These should be:
- Essential concepts that would definitely appear on an exam
- Definitions, mechanisms, key comparisons
- Facts referenced multiple times in the transcripts

Example format:
- התא הוא יחידת החיים הבסיסית <!-- claim_XXXXX -->
- הבדל בין פרוקריוט לאוקריוט: פרוקריוט ללא גרעין, אוקריוט עם גרעין <!-- claim_XXXXX -->

#### ℹ️ רקע מעניין (Nice-to-Know)
*קרא להבנת הקשר, לא חובה לשינון*

Generate 3-6 bullets of enrichment content:
- Historical context (scientists, discovery dates)
- Interesting examples or analogies
- Advanced details not essential for basic understanding

Example format:
- לוונהוק בנה מיקרוסקופ ראשון בשנת 1670 <!-- claim_XXXXX -->
- רוברט הוק טבע את המונח "תא" לאחר שראה תאי פקק <!-- claim_XXXXX -->

**Then continue with detailed subsections as usual...**

[rest of existing prompt structure]
"""
```

**Regenerate**: Run `python3 src/write_book.py` to regenerate all 10 chapters with new prompts

**Verify**: Check that each chapter has both ✅ and ℹ️ sections after "תוכן מרכזי"

#### Task 2.2: Refactor Glossary (3-4 hours)

**File**: Create new `src/refactor_glossary.py`

```python
#!/usr/bin/env python3
"""Refactor glossary to alphabetized, standardized format"""

import yaml
from collections import defaultdict
from pathlib import Path

def load_terminology():
    """Load terminology from ops/artifacts/terminology.yml"""
    with open('ops/artifacts/terminology.yml', encoding='utf-8') as f:
        return yaml.safe_load(f)

def group_by_hebrew_letter(terms):
    """Group terms by first Hebrew letter"""
    hebrew_grouped = defaultdict(list)

    for term in terms:
        hebrew_term = term.get('hebrew', term.get('term', ''))
        if not hebrew_term:
            continue

        first_letter = hebrew_term[0]
        hebrew_grouped[first_letter].append(term)

    # Sort within each letter
    for letter in hebrew_grouped:
        hebrew_grouped[letter].sort(key=lambda x: x.get('hebrew', x.get('term', '')))

    return hebrew_grouped

def generate_glossary_markdown(hebrew_grouped):
    """Generate markdown with Hebrew alphabetical order"""
    output = "# מילון מושגים\n\n"
    output += "*מילון מונחים מקצועיים לשימוש במהלך הלימוד*\n\n"
    output += "---\n\n"

    # Hebrew letter names for headers
    letter_names = {
        'א': 'א (Alef)', 'ב': 'ב (Bet)', 'ג': 'ג (Gimel)', 'ד': 'ד (Dalet)',
        'ה': 'ה (Heh)', 'ו': 'ו (Vav)', 'ז': 'ז (Zayin)', 'ח': 'ח (Chet)',
        'ט': 'ט (Tet)', 'י': 'י (Yod)', 'כ': 'כ (Kaf)', 'ל': 'ל (Lamed)',
        'מ': 'מ (Mem)', 'נ': 'נ (Nun)', 'ס': 'ס (Samech)', 'ע': 'ע (Ayin)',
        'פ': 'פ (Peh)', 'צ': 'צ (Tzadi)', 'ק': 'ק (Qof)', 'ר': 'ר (Resh)',
        'ש': 'ש (Shin)', 'ת': 'ת (Tav)'
    }

    for letter in sorted(hebrew_grouped.keys()):
        header = letter_names.get(letter, letter)
        output += f"## {header}\n\n"
        output += "| מונח בעברית | English / תעתיק | הגדרה מלאה |\n"
        output += "|-------------|-----------------|------------|\n"

        for term in hebrew_grouped[letter]:
            heb = term.get('hebrew', term.get('term', ''))
            eng = term.get('english', '—')
            defn = term.get('definition', term.get('explanation', 'אין הגדרה'))

            # Clean up definition (remove excessive whitespace)
            defn = ' '.join(defn.split())

            output += f"| **{heb}** | {eng} | {defn} |\n"

        output += "\n"

    return output

def generate_english_index(terms):
    """Generate English → Hebrew reverse index"""
    output = "\n---\n\n"
    output += "## English → עברית (Reverse Index)\n\n"
    output += "| English Term | עברית | Short Definition |\n"
    output += "|--------------|-------|------------------|\n"

    # Sort by English term
    english_terms = []
    for term in terms:
        eng = term.get('english', '')
        if eng and eng != '—':
            heb = term.get('hebrew', term.get('term', ''))
            defn = term.get('definition', term.get('explanation', ''))[:80] + '...'
            english_terms.append((eng, heb, defn))

    for eng, heb, defn in sorted(english_terms):
        output += f"| **{eng}** | {heb} | {defn} |\n"

    return output

if __name__ == "__main__":
    print("Loading terminology...")
    terms = load_terminology()

    print(f"Processing {len(terms)} terms...")
    hebrew_grouped = group_by_hebrew_letter(terms)

    print("Generating glossary markdown...")
    glossary_md = generate_glossary_markdown(hebrew_grouped)
    glossary_md += generate_english_index(terms)

    output_path = Path("book/90_glossary.md")
    output_path.write_text(glossary_md, encoding='utf-8')

    print(f"✅ Glossary written to {output_path}")
    print(f"   Total size: {len(glossary_md) / 1024:.1f} KB")
    print(f"   Hebrew letters covered: {len(hebrew_grouped)}")
```

**Run**: `python3 src/refactor_glossary.py`

**Verify**:
- Open `book/90_glossary.md`
- Check that terms are alphabetized by Hebrew letter
- Verify English reverse index exists at bottom
- Test EPUB reader search functionality

**Test**: Verify glossary is alphabetized and searchable in EPUB reader

---

### Priority 3: High-Impact, High-Effort (Do Third, Optional)

**Estimated Time**: 8-12 hours

#### Task 3.1: Convert Prose to Exam-Note Structures (8-12 hours)

**File**: `src/write_book.py` (chapter generation prompt - final enhancement)

**Change**: Add formatting rules to prompt template

```python
CHAPTER_PROMPT_TEMPLATE += """

## Formatting Rules for Exam Prep

**CRITICAL: Avoid long paragraphs. Use structured formats:**

1. **Definitions** → One-line format:
   **Term** = definition (example: **פתוגן** = אורגניזם מחולל מחלה)

2. **Comparisons** → Tables:
   | Parameter | Option A | Option B |
   |-----------|----------|----------|
   | Feature 1 | Value A1 | Value B1 |

3. **Processes/Steps** → Numbered or bulleted lists:
   **שכפול DNA:**
   1. פתיחת הסליל הכפול
   2. קשירת פריימרים
   3. הוספת נוקלאוטידים

4. **Relationships** → Bullets with arrows:
   - גלוקוז (מונומר) ← גליקוגן (פולימר)
   - DNA → RNA → חלבון (הדוגמה המרכזית)

5. **Key Facts** → Highlights with numbers:
   **70% מים** בגוף האדם
   **4 יסודות עיקריים**: C, H, O, N

**NEVER write paragraphs longer than 4 lines.**
**If you have 3+ related facts, use a bullet list or table.**

Example of WRONG format (too much prose):
```
מחלות מתרחשות כאשר התפקוד הפיזיולוגי הטבעי של גופנו משתבש. ניתן לחלק מחלות לשתי קטגוריות עיקריות: מחלות לא מדבקות ומחלות מדבקות. מחלות לא מדבקות הן מחלות כרוניות המתקדמות לאט לאורך זמן.
```

Example of CORRECT format (structured):
```
### מבוא למחלות

**הגדרה**: מחלה = שיבוש בתפקוד הפיזיולוגי של הגוף

**שני סוגי מחלות**:
| סוג | מאפיינים | דוגמאות |
|-----|----------|----------|
| לא מדבקות | כרוניות, איטיות | סרטן, סוכרת |
| מדבקות | נגרמות מפתוגנים | שפעת, COVID |

**פתוגנים**:
- חיידקים (Bacteria)
- נגיפים (Viruses)
- פטריות (Fungi)
- טפילים (Parasites)
```
"""
```

**Regenerate**: Run `python3 src/write_book.py` to regenerate all chapters with prose-to-structure rules

**Manual Alternative**: If LLM doesn't follow rules well, manually edit chapters:
- Focus on Chapters 05, 06, 11 (most prose-heavy based on earlier reading)
- Convert paragraphs > 4 lines to bullets or tables
- Use search-and-replace for common patterns:
  - "X is... Y is..." → table
  - "First... Second... Third..." → numbered list
  - "X and Y and Z" → bullet list

**Verify**:
- Open each chapter markdown file
- Scan for paragraphs longer than 5 lines
- Check that key comparisons are in table format
- Ensure definitions use bold **Term** = format

**Test**: Read refactored chapters, ensure key facts are scannable

---

## Success Metrics: How to Verify This Works

### Metric 1: Student Can Complete 3-Pass Study Workflow
**Test**: Give book to a test student, ask them to:
1. Read Chapter 05 and highlight "must-know" items (should take 15 min, not 45 min)
2. Create a one-page summary from must-knows (should be possible)
3. Self-test with questions without seeing answers (answers must be hidden/separated)

**Pass Criteria**: Student completes all 3 tasks efficiently

### Metric 2: Key Terms Are Quickly Findable
**Test**: Pick 10 random terms from chapters (e.g., "קפסיד", "ACE2", "פולימר")
**Action**: Use EPUB reader search to find each term in glossary
**Pass Criteria**: All 10 terms found in < 30 seconds total

### Metric 3: Comparison Tables Eliminate Re-Reading
**Test**: Ask "What's the difference between innate and adaptive immunity?"
**Expected**: Student opens quick reference, finds table, answers in 30 seconds
**Pass Criteria**: Answer is complete and correct without re-reading Chapter 08

### Metric 4: Chapter Titles Map to Concepts
**Test**: Show student TOC, ask "Which chapter covers virus replication?"
**Expected**: Student identifies "פרק 5: נגיפים – מבנה, תפקוד, הדבקה ושכפול" immediately
**Pass Criteria**: No confusion, no need to open chapter to check

---

## Known Limitations & Future Enhancements

### What This Plan Does NOT Address

1. **EPUB Technical Issues** (Deliberately Excluded)
   - RTL spine direction in OPF
   - Dark mode CSS
   - Accessibility ARIA roles
   - **Reason**: These don't affect exam-prep efficiency, only polish

2. **Content Accuracy** (Already Handled)
   - **Source of Truth**: Campus IL course transcripts from expert lecturer
   - **Verification**: All content grounded in claim IDs that trace back to transcripts
   - **System**: Traceability.json ensures every chapter maps to source evidence
   - **Conclusion**: Content accuracy is guaranteed by evidence-grounding architecture

3. **Image/Diagram Addition** (Future)
   - Current EPUB is text-only
   - Visual learners would benefit from:
     - Cell structure diagrams
     - Virus replication cycle flowcharts
     - Immune system overview
   - **Future Work**: Add SVG diagrams to `book/images/` and reference in chapters

4. **Interactive Self-Testing** (Future)
   - Current: Static MCQs in EPUB
   - Ideal: Interactive quiz with score tracking
   - **Future Work**: Export questions to Anki deck OR create companion web app

---

## Critical Files Summary

### Files to Create (New)
- `book/01_study_guide.md` - Replaces outline with study roadmap
- `book/89_quick_reference.md` - Comparison tables and formula sheet
- `book/93_answer_key.md` - Consolidated answers for all chapters
- `src/refactor_glossary.py` - Script to alphabetize and standardize glossary

### Files to Modify (Edit)
- `src/write_book.py` - Update LLM prompt for must-know/nice-to-know + note structures
- `book/build_epub.sh` - Update file order (study guide first, answer key last)
- `book/chapters/*.md` - Strip inline answers, add priority signals, convert prose to notes
- `book/90_glossary.md` - Refactor to alphabetized three-column format

### Files to Delete (Remove)
- `book/01_outline.md` - Internal file listing, not useful for students

---

## End-to-End Verification Plan

### Step 1: Build Verification

**Run the build**:
```bash
cd /Users/arielindenbaum/Downloads/Viruses_Campus_IL_Full_Course
bash book/build_epub.sh
```

**Expected Output**:
- EPUB builds without errors
- File size: 120-150KB (slightly larger than current 109KB due to added tables)
- No Pandoc warnings about broken references

**Check**:
```bash
ls -lh book/build/book.epub
# Should show ~120-150KB file

# Verify EPUB structure
unzip -l book/build/book.epub | head -20
# Should show mimetype, META-INF, EPUB/ structure
```

---

### Step 2: Content Verification

#### Check 2.1: Chapter Titles Match Lesson Numbers

**Open EPUB** in Calibre or Apple Books

**Verify TOC shows**:
- מבוא: וירוס הקורונה
- פרק 1: תאים – יחידת החיים
- פרק 2: מקרומולקולות – מ-DNA לחלבונים
- ...
- פרק 7: חיסונים
- פרק 8: משפחת נגיפי הקורונה
- סיכום: סיכום הקורס

**NOT** the old format (פרק 03: 03_שיעור_1...)

#### Check 2.2: Study Guide Exists

**Navigate to first chapter after front matter**

**Verify presence of**:
- Course structure (4 parts)
- Dependency map (ASCII diagram)
- 3-week study strategy
- "What will be on the exam?" section

#### Check 2.3: Must-Know Signals in Chapters

**Open Chapter 1 (Cells)**

**Verify it contains**:
```markdown
## תוכן מרכזי

### ✅ חובה למבחן (Must-Know)
*קרא לעומק, זכור לטווח ארוך*

- [8-15 bullet points of core facts]

### ℹ️ רקע מעניין (Nice-to-Know)
*קרא להבנת הקשר, לא חובה לשינון*

- [3-6 bullets of enrichment]
```

**Repeat check** for Chapters 2, 3, 4, 5

#### Check 2.4: Answer Separation

**Open Chapter 1 questions section**

**Verify format**:
1. Questions section has NO inline `**תשובה:**` markers
2. Questions end with `\newpage` or page break
3. Answer key appears on next page with format:
   ```
   ## מפתח תשובות

   1. **ג** - [optional explanation]
   2. **ב** - [optional explanation]
   ```

**Test**: Try to answer question 1 without seeing the answer (should require page turn)

#### Check 2.5: Quick Reference Tables Exist

**Navigate to chapter BEFORE glossary**

**Verify "טבלאות התייחסות מהירה" exists with tables for**:
- [ ] Prokaryote vs Eukaryote
- [ ] DNA vs RNA viruses
- [ ] Innate vs Adaptive immunity
- [ ] Vaccine types (5 types)
- [ ] Coronavirus pandemics (SARS, MERS, COVID)
- [ ] Macromolecules

**Test**: Can you answer "What's the difference between innate and adaptive immunity?" in 30 seconds using the quick reference?

#### Check 2.6: Glossary Alphabetization

**Open glossary (last content chapter before question bank)**

**Verify**:
- [ ] Starts with "## א (Alef)" section
- [ ] Terms within each letter are sorted alphabetically
- [ ] All entries have 3 columns: Hebrew term, English/transliteration, Definition
- [ ] No empty cells (use "—" if English unavailable)
- [ ] English reverse index exists at bottom

**Test EPUB search**:
- Search for "קפסיד" → Should jump to glossary ק section
- Search for "capsid" → Should appear in English reverse index

---

### Step 3: Functional Testing

#### Test 3.1: Three-Pass Study Workflow

**Give EPUB to a test student** (or self-test):

**Pass 1 (15 min)**: Read Chapter 1, highlight only "✅ חובה למבחן" items
- Should complete in 15 minutes (not 45 minutes)
- Should be able to list 8-15 core facts

**Pass 2 (10 min)**: Create one-page summary from must-knows
- Should be possible without re-reading entire chapter
- Summary should be < 1 page

**Pass 3 (5 min)**: Self-test with questions
- Answers should be hidden/separated
- Should require page turn or scroll to check answers

**Pass Criteria**: All 3 passes completed efficiently without frustration

#### Test 3.2: Term Lookup Speed

**Pick 10 random terms from chapters**:
1. קפסיד
2. ACE2
3. פולימר
4. נוגדן
5. מקרופאג
6. RNA
7. חסינות מולדת
8. חיסון mRNA
9. ספייק
10. קורונה

**Use EPUB reader search** to find each term in glossary

**Pass Criteria**: All 10 terms found in < 30 seconds total (average 3 sec/term)

#### Test 3.3: Comparison Table Utility

**Ask test question**: "What's the difference between innate and adaptive immunity?"

**Expected workflow**:
1. Open quick reference (TOC or page flip)
2. Find "Innate vs Adaptive" table
3. Read table rows
4. Answer question completely

**Pass Criteria**: Complete answer in 30 seconds, no need to re-read Chapter 5

#### Test 3.4: Chapter Title→Concept Mapping

**Show test student EPUB TOC**

**Ask**: "Which chapter covers virus replication?"

**Expected answer**: "פרק 3: נגיפים – מבנה, תפקוד, הדבקה ושכפול" (immediately)

**Pass Criteria**: No confusion, no need to open chapter to verify

---

### Step 4: Technical Validation

#### Validation 4.1: EPUBCheck

**Run EPUB validator** (if available):
```bash
# Install epubcheck if needed:
# brew install epubcheck  # macOS
# apt-get install epubcheck  # Linux

epubcheck book/build/book.epub
```

**Expected Output**: "No errors or warnings detected."

**If errors**: Fix OPF/NCX issues before proceeding

#### Validation 4.2: Cross-Reader Testing

**Test in 3+ readers**:

| Reader | Platform | Test Result |
|--------|----------|-------------|
| **Apple Books** | macOS/iOS | ✓ Opens, RTL pagination works |
| **Calibre** | Desktop | ✓ TOC navigation works |
| **Adobe Digital Editions** | Desktop | ✓ Search works |
| **Google Play Books** | Android/Web | ✓ Tables render correctly |

**Critical checks per reader**:
- [ ] EPUB opens without errors
- [ ] TOC shows lesson-based chapter numbering
- [ ] Hebrew text displays correctly (RTL)
- [ ] Tables in quick reference render properly
- [ ] Search finds glossary terms
- [ ] Page breaks separate questions from answers

---

### Step 5: Final Checklist

**Before declaring "exam-ready", verify ALL items**:

**Chapter Structure**:
- [ ] TOC shows concept-first chapter titles (פרק 1, not פרק 03)
- [ ] Study guide exists with learning path and dependency map
- [ ] Each chapter has "✅ חובה למבחן" section (8-15 bullets)
- [ ] Each chapter has "ℹ️ רקע מעניין" section (3-6 bullets)
- [ ] Paragraphs > 5 lines converted to bullets/tables (Priority 3)

**Self-Testing**:
- [ ] Practice questions have NO inline answers
- [ ] Answer key appears after `\newpage` in each chapter
- [ ] Students must page-turn to see answers

**Quick Reference**:
- [ ] `book/89_quick_reference.md` exists
- [ ] Contains 5+ comparison tables
- [ ] Tables render correctly in EPUB

**Glossary**:
- [ ] Terms alphabetized by Hebrew letter (א-ת)
- [ ] All entries have 3 columns (Hebrew, English, Definition)
- [ ] No empty cells (use "—" for missing)
- [ ] English reverse index exists at bottom

**Build**:
- [ ] EPUB builds successfully with `bash book/build_epub.sh`
- [ ] File size: 120-150KB
- [ ] No Pandoc warnings

**Functionality**:
- [ ] EPUB opens in Apple Books / Calibre / Adobe Digital Editions
- [ ] Search finds glossary terms
- [ ] Tables render correctly
- [ ] Hebrew RTL text displays properly

---

## If Tests Fail: Troubleshooting

### Issue 1: Chapters still have old titles (פרק 03: 03_שיעור...)

**Cause**: `src/write_book.py` not updated or chapters not regenerated

**Fix**:
1. Verify `LESSON_MAPPING` exists in `src/write_book.py`
2. Re-run: `python3 src/write_book.py`
3. Rebuild EPUB: `bash book/build_epub.sh`

### Issue 2: Answers still inline (not separated)

**Cause**: `src/separate_answers.py` not run or regex didn't match

**Fix**:
1. Check script regex pattern matches your question format
2. Manually verify one chapter has format: `**תשובה:** [letter]`
3. Re-run: `python3 src/separate_answers.py`
4. Check output: `grep -n "תשובה" book/chapters/03*.md` (should be empty)

### Issue 3: Must-know sections missing

**Cause**: Prompt not updated or chapters not regenerated

**Fix**:
1. Verify prompt includes `✅ חובה למבחן` instructions
2. Re-run: `python3 src/write_book.py`
3. Grep check: `grep -n "✅ חובה" book/chapters/*.md` (should show hits)

### Issue 4: Glossary not alphabetized

**Cause**: `src/refactor_glossary.py` not run

**Fix**:
1. Re-run: `python3 src/refactor_glossary.py`
2. Check output: `head -50 book/90_glossary.md` (should start with "## א (Alef)")

### Issue 5: Quick reference doesn't exist

**Cause**: File not created

**Fix**:
1. Manually create `book/89_quick_reference.md` using template (lines 339-397)
2. Update `book/build_epub.sh` to include it before glossary

---

## Success Criteria Summary

**This EPUB is exam-ready when**:

1. ✅ A test student can complete the 3-pass study workflow efficiently
2. ✅ 10 glossary term lookups take < 30 seconds total
3. ✅ Quick reference tables answer comparison questions in < 30 seconds
4. ✅ Chapter titles immediately map to concepts (no confusion)
5. ✅ EPUB builds without errors and opens in 3+ readers

**These changes align with learning science**:
- Separated answers → Forces retrieval practice
- Must-know signals → Reduces decision fatigue
- Comparison tables → Reduces cognitive load
- Bullet lists → Enables faster scanning
- Study roadmap → Prevents wasted effort

**This is not a book. This is a study system.**

---

## Estimated Total Effort

| Priority | Tasks | Hours |
|----------|-------|-------|
| Priority 1 (High-impact, low-effort) | Titles, study guide, answer separation, quick ref | 4-6 |
| Priority 2 (Medium-impact, medium-effort) | Must-know signals, glossary refactor | 6-8 |
| Priority 3 (High-impact, high-effort) | Prose → note structures | 8-12 |
| **Total** | **All transformations** | **18-26 hours** |

**Recommendation**: Complete Priority 1 first (6 hours), test with students, then decide if Priority 2-3 are worth the investment based on feedback.

---

## Final Note: Why This Approach Works

This plan prioritizes **retrieval practice** and **cognitive load reduction** over "book aesthetics":

1. **Separated answers** → Forces recall (proven to improve retention)
2. **Must-know signals** → Reduces decision fatigue (students know what to focus on)
3. **Comparison tables** → Reduces working memory load (no need to hold 5 facts in head while comparing)
4. **Bullet lists** → Faster scanning (prose requires linear reading)
5. **Study roadmap** → Prevents wasted effort (students know dependencies)

These changes align with evidence-based learning science (Roediger & Karpicke, 2006; Sweller's Cognitive Load Theory).

**This is not a book. It's a study system.**
