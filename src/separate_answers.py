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
        print(f"⚠️  No questions found in {chapter_path.name}")
        return content

    questions_section = match.group(1)

    # Extract answers - handle multiple formats:
    # Format 1: **תשובה:** ב
    # Format 2: תשובה: (ב)
    # Format 3: תשובה נכונה: (ב)
    # Format 4: תשובה: ב (no parentheses)
    answer_patterns = [
        r'(\d+)\.\s*(.*?)\*\*תשובה:\*\*\s*([א-ת]|[a-d])',       # Format 1
        r'(\d+)\.\s*(.*?)תשובה:\s*\(([א-ת]|[a-d])\)',           # Format 2
        r'(\d+)\.\s*(.*?)תשובה נכונה:\s*\(([א-ת]|[a-d])\)',    # Format 3
        r'(\d+)\.\s*(.*?)תשובה:\s*([א-ת])\s*$',                 # Format 4 (Hebrew, end of line)
        r'(\d+)\.\s*(.*?)תשובה:\s*([a-d])\s*$',                 # Format 4 (English, end of line)
    ]

    answers = []
    for pattern in answer_patterns:
        if not answers:  # Only try next pattern if no matches yet
            for ans_match in re.finditer(pattern, questions_section, re.DOTALL | re.MULTILINE):
                q_num = ans_match.group(1)
                answer = ans_match.group(3)
                answers.append(f"{q_num}. **{answer}**")

    if not answers:
        print(f"⚠️  No answers found in {chapter_path.name} (different format?)")
        return content

    # Remove inline answers - all formats
    questions_clean = re.sub(r'\s*\*\*תשובה:\*\*\s*[א-ת]', '', questions_section)
    questions_clean = re.sub(r'\s*\*\*תשובה:\*\*\s*[a-d]', '', questions_clean)
    questions_clean = re.sub(r'\s*תשובה:\s*\([א-ת]\)', '', questions_clean)
    questions_clean = re.sub(r'\s*תשובה:\s*\([a-d]\)', '', questions_clean)
    questions_clean = re.sub(r'\s*תשובה נכונה:\s*\([א-ת]\)', '', questions_clean)
    questions_clean = re.sub(r'\s*תשובה נכונה:\s*\([a-d]\)', '', questions_clean)
    questions_clean = re.sub(r'\s*תשובה:\s*[א-ת]\s*$', '', questions_clean, flags=re.MULTILINE)
    questions_clean = re.sub(r'\s*תשובה:\s*[a-d]\s*$', '', questions_clean, flags=re.MULTILINE)

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
    new_content = re.sub(
        questions_pattern,
        f"## שאלות לתרגול\n{new_questions_section}",
        content,
        flags=re.DOTALL
    )

    return new_content


if __name__ == "__main__":
    chapters_dir = Path("book/chapters")

    if not chapters_dir.exists():
        print(f"❌ Directory not found: {chapters_dir}")
        print("   Run this script from the project root directory")
        exit(1)

    chapter_files = sorted(chapters_dir.glob("*.md"))

    if not chapter_files:
        print(f"❌ No markdown files found in {chapters_dir}")
        exit(1)

    print(f"📚 Processing {len(chapter_files)} chapters...\n")

    processed = 0
    skipped = 0

    for chapter_file in chapter_files:
        print(f"Processing {chapter_file.name}...", end=" ")

        original_content = chapter_file.read_text(encoding='utf-8')
        new_content = separate_answers_in_chapter(chapter_file)

        if new_content != original_content:
            chapter_file.write_text(new_content, encoding='utf-8')
            print("✅ Updated")
            processed += 1
        else:
            print("⏭️  Skipped (no changes)")
            skipped += 1

    print(f"\n{'='*50}")
    print(f"✅ Complete: {processed} chapters updated, {skipped} skipped")
    print(f"{'='*50}\n")
