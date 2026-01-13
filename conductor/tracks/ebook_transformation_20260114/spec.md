# Specification: Hebrew Virology Study Ebook Transformation

## 1. Overview
This track involves transforming a collection of 72 Hebrew lecture transcripts from the "Viruses" Campus IL course into a structured, cohesive, reading-first study ebook. The primary goal is to provide students with a textbook-like resource optimized for comprehension and exam preparation.

## 2. Functional Requirements

### 2.1 Content Transformation
- **Original Prose:** Rewrite and synthesize raw transcript text into original, textbook-like prose. Avoid verbatim transcript conversion.
- **Organization:** Group content based on the original course "Lesson" structure (Lesson 1-8).
- **Study Supports:** Each chapter must include learning objectives, roadmaps, quick summaries, key terms, and practice questions.
- **Expert Interviews:** Summarize interviews with experts as "Expert Perspective" sidebars.
- **Lab Demonstrations:** Summarize lab demonstrations conceptually in sidebars. **Strictly avoid step-by-step protocols or actionable recipes.**

### 2.2 Structure & Artifacts
- **Book Directory:** Create a `/book` directory to house all artifacts.
- **Manifest:** `manifest.json` mapping sources to chapters with metadata.
- **Front Matter:** `00_front_matter.md` containing title, disclaimer, study guide, and table of contents.
- **Outline:** `01_outline.md` justifying the chapter grouping and structure.
- **Chapters:** Individual Markdown files in `chapters/` following a strict template.
- **Glossary:** `90_glossary.md` with Hebrew definitions and English terms in parentheses.
- **Exam Review:** `91_exam_review.md` with high-yield concept maps and "most-tested" topics.
- **Question Bank:** `92_question_bank.md` consolidating all MCQ and short-answer questions.
- **README:** `README.md` explaining the organization and build process.

### 2.3 Style & Tone
- **Language:** Hebrew, using standard scientific acronyms (DNA/RNA).
- **Terminology:** Bilingual emphasis—include the English term in parentheses for technical terms throughout.
- **Tone:** Educational, direct, and non-chatty.
- **Formatting:** Use short paragraphs, frequent headings, and tables for comparisons.

## 3. Non-Functional Requirements
- **Safety:** Ensure no harmful instructions for culturing pathogens are included.
- **Medical Advice:** Include a disclaimer that the content is for educational purposes only.
- **Consistency:** Maintain uniform terminology and units across all chapters.

## 4. Acceptance Criteria
- [ ] A cohesive ebook is generated in the `/book` directory.
- [ ] All 72 transcripts are processed and synthesized.
- [ ] The chapter structure follows the original Lesson grouping.
- [ ] No step-by-step lab protocols are present.
- [ ] Every chapter includes the required study support elements (objectives, questions, etc.).
- [ ] The Glossary and Question Bank are fully populated and consistent with chapter content.

## 5. Out of Scope
- Detailed wet-lab protocols.
- Verbatim transcript conversion.
- External research beyond the provided transcripts.