#!/usr/bin/env python3
"""Separate inline answers from questions in all chapters"""

import re
from pathlib import Path

def separate_answers_in_chapter(chapter_path):
    """Separate answers from questions and create answer key at end"""
    content = chapter_path.read_text(encoding='utf-8')

    # Find all question section headers
    section_pattern = r'##\s*שאלות לתרגול'
    section_matches = list(re.finditer(section_pattern, content))

    if not section_matches:
        print(f"  No questions section in {chapter_path.name}")
        return content

    # Use the last occurrence (skip duplicate header)
    last_section_start = section_matches[-1].start()

    # Get everything from last "## שאלות לתרגול" to end of file
    questions_and_answers = content[last_section_start:]
    before_questions = content[:last_section_start]

    # Find all answers with pattern **תשובה:** [X]
    answer_pattern = r'\*\*תשובה:\*\*\s*\[([א-ת]|[a-dA-D])\](?:\s*\n\*\([^\)]+\)\*)?'
    answers = []

    for match in re.finditer(answer_pattern, questions_and_answers):
        answers.append(match.group(1))

    if not answers:
        print(f"  No answers found in {chapter_path.name}")
        return content

    print(f"  Found {len(answers)} answers")

    # Remove all answer lines from questions section
    questions_clean = re.sub(answer_pattern, '', questions_and_answers)

    # Clean up excessive blank lines
    questions_clean = re.sub(r'\n\s*\n\s*\n+', '\n\n', questions_clean)

    # Build answer key
    answer_key = "\n\n---\n\n*תשובות בעמוד הבא – נסו לענות בעצמכם קודם!*\n\n\\newpage\n\n## מפתח תשובות\n\n"
    for i, answer in enumerate(answers, 1):
        answer_key += f"{i}. **{answer}**\n"
    answer_key += "\n"

    # Reconstruct document
    new_content = before_questions + questions_clean.strip() + answer_key

    return new_content

if __name__ == "__main__":
    chapters_dir = Path("book/chapters")

    for chapter_file in sorted(chapters_dir.glob("*.md")):
        print(f"Processing {chapter_file.name}...")
        new_content = separate_answers_in_chapter(chapter_file)
        chapter_file.write_text(new_content, encoding='utf-8')
        print("  ✓ Completed\n")

    print("✅ All chapters processed!")
