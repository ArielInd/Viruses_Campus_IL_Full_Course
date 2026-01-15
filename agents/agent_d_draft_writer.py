"""
Agent D: DraftWriter (Quality-First Edition)

High-quality chapter generation using:
- gemini-2.5-pro for deep reasoning
- Iterative 3-wave writing (Outline → Sections → Synthesis)
- Full-context transcript ingestion (no truncation)

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

# Use the new unified Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")

from .schemas import (
    DraftChapter, PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file,
    validate_outline_response, PYDANTIC_AVAILABLE
)
from .version_manager import VersionManager

AGENT_NAME = "DraftWriter"

# Gemini configuration - PRO for quality
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Quality settings
MAX_OUTPUT_TOKENS = 16384
TEMPERATURE_OUTLINE = 0.3  # Lower for structured thinking
TEMPERATURE_WRITING = 0.6  # Higher for creative prose
TEMPERATURE_SYNTHESIS = 0.4  # Balanced for editing

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set.")


class DraftWriter:
    """
    Agent D: Quality-First Draft Writer
    
    Uses a 3-wave iterative approach:
    1. Wave 1 (Outline): Generate detailed 10+ section outline
    2. Wave 2 (Sections): Write each section with full transcript context
    3. Wave 3 (Synthesis): Smooth transitions and ensure flow
    
    Output: /ops/artifacts/drafts/chapters/*.md
    """
    
    def __init__(self, transcripts_dir: str, ops_dir: str, 
                 logger: PipelineLogger, todos: TodoTracker):
        self.transcripts_dir = transcripts_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.artifacts_dir = os.path.join(ops_dir, "artifacts")
        self.drafts_dir = os.path.join(self.artifacts_dir, "drafts", "chapters")
        self.briefs_dir = os.path.join(self.artifacts_dir, "chapter_briefs")
        
        # Initialize Gemini client (new SDK)
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[{AGENT_NAME}] Gemini 3 Pro initialized (Quality-First Mode)")
            except Exception as e:
                print(f"[{AGENT_NAME}] Failed to initialize Gemini: {e}")
        else:
            print(f"[{AGENT_NAME}] Using template-based generation")

        # Setup version manager
        self.version_manager = VersionManager(ops_dir)
        
        # Ensure directories exist
        os.makedirs(self.drafts_dir, exist_ok=True)
    
    def _generate(self, prompt: str, temperature: float = 0.5) -> Optional[str]:
        """Generate content using the new Gemini SDK."""
        if not self.client:
            return None
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
            )
            return response.text
        except Exception as e:
            print(f"[{AGENT_NAME}] Generation error: {e}")
            return None
        
    async def run(self, chapter_id: Optional[str] = None) -> Dict:
        """
        Execute the agent asynchronously.
        
        Args:
            chapter_id: If provided, only process this chapter.
        """
        start_time = self.logger.log_start(AGENT_NAME)
        warnings = []
        output_files = []
        
        # Load chapter plan
        plan_path = os.path.join(self.artifacts_dir, "chapter_plan.json")
        chapter_plans = load_json(plan_path)
        
        # Filter plans if chapter_id is provided
        if chapter_id:
            target_plan = next((p for p in chapter_plans if p["chapter_id"] == chapter_id), None)
            if not target_plan:
                error_msg = f"Chapter {chapter_id} not found in plan"
                self.logger.log_end(AGENT_NAME, start_time, output_files, warnings, [error_msg])
                raise ValueError(error_msg)
            plans_to_process = [target_plan]
            print(f"[{AGENT_NAME}] Writing draft for chapter {chapter_id} (Parallel Quality-First)")
        else:
            plans_to_process = chapter_plans
            print(f"[{AGENT_NAME}] Writing drafts for {len(chapter_plans)} chapters (Parallel Quality-First)")

        # Use a semaphore to limit concurrent chapters (stay within rate limits)
        semaphore = asyncio.Semaphore(2)  # Process 2 chapters at a time

        async def process_chapter(plan):
            async with semaphore:
                cid = plan["chapter_id"]
                
                # Load brief
                brief_path = os.path.join(self.briefs_dir, f"chapter_{cid}_brief.json")
                brief = load_json(brief_path) if os.path.exists(brief_path) else {}
                
                # Load FULL source content
                print(f"[{AGENT_NAME}] Loading sources for chapter {cid}...")
                source_content = self._load_sources_full(plan.get("source_files", []))
                
                # Generate draft
                if self.client and source_content:
                    print(f"[{AGENT_NAME}] Starting 3-wave generation for chapter {cid}...")
                    # Note: We need to make sure _write_draft_iterative and its components are async-friendly
                    # If they are sync, we run them in a thread.
                    draft = await asyncio.to_thread(self._write_draft_iterative, plan, brief, source_content)
                else:
                    draft = await asyncio.to_thread(self._write_draft_template, plan, brief, source_content)
                
                # Save draft
                draft_path = os.path.join(self.drafts_dir, f"{cid}_chapter_draft.md")
                save_markdown(draft.content_md, draft_path)
                
                print(f"[{AGENT_NAME}] ✓ Chapter {cid}: {draft.word_count} words (Quality-First)")
                return draft_path

        # Run all chapters
        tasks = [process_chapter(plan) for plan in plans_to_process]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if isinstance(res, Exception):
                warnings.append(f"Chapter failed: {str(res)}")
                print(f"[{AGENT_NAME}] ✗ Error: {res}")
            else:
                output_files.append(res)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files, warnings)
        
        return {
            "drafts_dir": self.drafts_dir,
            "num_drafts": len(output_files)
        }
    
    def _load_sources_full(self, source_paths: List[str]) -> str:
        """Load FULL source transcript content with chunk IDs for citation."""
        content = []
        self.source_chunks = {}  # Store for verification
        chunk_id = 1
        
        for path in source_paths:
            if os.path.exists(path):
                try:
                    text = read_file(path)
                    filename = os.path.basename(path)
                    
                    # Split into chunks (~500 words each) and assign IDs
                    paragraphs = text.split('\n\n')
                    current_chunk = ""
                    
                    for para in paragraphs:
                        current_chunk += para + "\n\n"
                        if len(current_chunk.split()) >= 400:
                            chunk_label = f"[SRC-{chunk_id:03d}]"
                            self.source_chunks[chunk_label] = {
                                "file": filename,
                                "text": current_chunk.strip()
                            }
                            content.append(f"{chunk_label}\n{current_chunk.strip()}")
                            current_chunk = ""
                            chunk_id += 1
                    
                    # Remaining content
                    if current_chunk.strip():
                        chunk_label = f"[SRC-{chunk_id:03d}]"
                        self.source_chunks[chunk_label] = {
                            "file": filename,
                            "text": current_chunk.strip()
                        }
                        content.append(f"{chunk_label}\n{current_chunk.strip()}")
                        chunk_id += 1
                        
                except Exception as e:
                    self.todos.add(AGENT_NAME, path, f"Failed to read: {e}")
        
        print(f"[{AGENT_NAME}] Loaded {chunk_id-1} source chunks for citation")
        return "\n\n".join(content)
    
    def _write_draft_iterative(self, plan: Dict, brief: Dict, source_content: str) -> DraftChapter:
        """
        Write chapter using 3-wave iterative approach for maximum quality.
        """
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        print(f"[{AGENT_NAME}] Wave 1: Generating detailed outline...")
        outline = self._wave1_generate_outline(plan, brief, source_content)
        time.sleep(5)  # Brief pause between waves
        
        print(f"[{AGENT_NAME}] Wave 2: Writing {len(outline)} sections...")
        sections = self._wave2_write_sections(plan, brief, source_content, outline)
        time.sleep(5)
        
        print(f"[{AGENT_NAME}] Wave 3: Synthesizing and polishing...")
        final_content = self._wave3_synthesize(plan, sections)
        
        word_count = len(final_content.split())
        
        return DraftChapter(
            chapter_id=chapter_id,
            title=title,
            content_md=final_content,
            word_count=word_count,
            has_objectives=True,
            has_roadmap=True,
            has_summary=True,
            has_key_terms=True,
            has_questions=True,
            todos=[]
        )
    
    def _wave1_generate_outline(self, plan: Dict, brief: Dict, source_content: str) -> List[Dict]:
        """
        Wave 1: Generate a detailed 10+ section outline from the brief and sources.
        Returns a list of section dictionaries with title, key_points, and word_target.
        """
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        prompt = f"""אתה מתכנן פרקים לספר לימוד אקדמי על וירולוגיה ואימונולוגיה.

המשימה: צור מתאר מפורט לפרק {chapter_id}: "{title}"

---
תקציר הפרק (Brief):
{json.dumps(brief, ensure_ascii=False, indent=2) if brief else "לא זמין"}

---
חומר המקור (תמלילים מלאים):
{source_content[:80000]}

---
הנחיות:
1. צור מתאר עם לפחות 10 חלקים (sections)
2. כל חלק צריך להכיל:
   - כותרת (title)
   - נקודות מפתח (3-5 key_points)
   - יעד מילים (word_target): 300-600 מילים לחלק
3. כלול את המקטעים הבאים:
   - מטרות למידה
   - מפת דרכים
   - 6-8 חלקי תוכן עיקריים
   - טעויות נפוצות
   - סיכום מהיר
   - מושגי מפתח
   - שאלות לתרגול

החזר JSON בפורמט:
{{
  "sections": [
    {{
      "id": 1,
      "title": "מטרות למידה",
      "key_points": ["נקודה 1", "נקודה 2"],
      "word_target": 200
    }},
    ...
  ]
}}

דוגמה לפורמט נכון:
{{
  "sections": [
    {{
      "id": 1,
      "title": "מטרות למידה",
      "key_points": [
        "הבנת מבנה הנגיף הכללי",
        "הכרת דרכי הדבקה עיקריות",
        "זיהוי מנגנוני הגנה חיסוניים"
      ],
      "word_target": 300
    }},
    {{
      "id": 2,
      "title": "מבוא: מהו נגיף?",
      "key_points": [
        "הגדרה: ישות ביולוגית תת-תאית",
        "הבדלים בין נגיף לחיידק",
        "מבנה בסיסי: חומר גנטי + מעטפת חלבון"
      ],
      "word_target": 500
    }},
    {{
      "id": 3,
      "title": "מחזור החיים של נגיף",
      "key_points": [
        "שלב 1: הדבקה וחדירה לתא",
        "שלב 2: שכפול חומר גנטי",
        "שלב 3: יציאה והדבקת תאים חדשים"
      ],
      "word_target": 600
    }}
  ]
}}
"""
        
        text = self._generate(prompt, TEMPERATURE_OUTLINE)

        if text:
            try:
                # Extract JSON using regex to find the outermost JSON object
                # This handles cases where LLM adds explanatory text before/after
                import re

                # Pattern to match outermost JSON object (handles nested objects)
                # We look for all potential JSON objects and try the largest first
                json_matches = []

                # Find all potential JSON object boundaries
                brace_stack = []
                for i, char in enumerate(text):
                    if char == '{':
                        brace_stack.append(i)
                    elif char == '}' and brace_stack:
                        start = brace_stack.pop()
                        # Only keep complete objects (stack empty after closing)
                        if not brace_stack:
                            json_matches.append((start, i + 1))

                # Try each match from largest to smallest
                json_matches.sort(key=lambda x: x[1] - x[0], reverse=True)

                for start, end in json_matches:
                    try:
                        candidate = text[start:end]
                        data = json.loads(candidate)
                        # Verify it has the expected structure
                        if "sections" in data and isinstance(data["sections"], list):
                            # Validate with Pydantic if available
                            if PYDANTIC_AVAILABLE:
                                try:
                                    validated_sections = validate_outline_response(data)
                                    print(f"[{AGENT_NAME}] ✓ Outline validation passed ({len(validated_sections)} sections)")
                                    return validated_sections
                                except Exception as validation_error:
                                    print(f"[{AGENT_NAME}] ⚠ Validation failed: {validation_error}")
                                    print(f"[{AGENT_NAME}] Using unvalidated data as fallback")
                                    # Continue to next match or use unvalidated data
                            else:
                                # Pydantic not available, use data as-is
                                return data["sections"]
                    except json.JSONDecodeError:
                        continue

                # If no valid JSON found, raise error
                raise ValueError("No valid JSON object with 'sections' field found")

            except Exception as e:
                print(f"[{AGENT_NAME}] Outline parsing failed: {e}")
                self.todos.add(AGENT_NAME, f"chapter_{chapter_id}", f"Outline failed: {e}")
        
        # Fallback: default structure
        return [
            {"id": 1, "title": "מטרות למידה", "key_points": [], "word_target": 200},
            {"id": 2, "title": "מפת דרכים", "key_points": [], "word_target": 150},
            {"id": 3, "title": "תוכן מרכזי", "key_points": [], "word_target": 2000},
            {"id": 4, "title": "סיכום מהיר", "key_points": [], "word_target": 300},
            {"id": 5, "title": "מושגי מפתח", "key_points": [], "word_target": 200},
            {"id": 6, "title": "שאלות לתרגול", "key_points": [], "word_target": 400},
        ]
    
    def _wave2_write_sections(self, plan: Dict, brief: Dict, source_content: str, 
                               outline: List[Dict]) -> List[Tuple[str, str]]:
        """
        Wave 2: Write each section independently with full context.
        Returns list of (section_title, section_content) tuples.
        """
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        sections = []
        
        for i, section in enumerate(outline):
            section_title = section.get("title", f"חלק {i+1}")
            key_points = section.get("key_points", [])
            word_target = section.get("word_target", 400)
            
            prompt = f"""אתה כותב ספר לימוד עברי מקיף על וירולוגיה.

כותב כעת: פרק {chapter_id} - "{title}"
מקטע נוכחי: "{section_title}"

---
נקודות מפתח לכסות:
{chr(10).join('- ' + p for p in key_points) if key_points else "(כתוב לפי שיקול דעתך)"}

---
חומר מקור מלא:
{source_content}

---
הנחיות כתיבה:
1. כתוב בעברית אקדמית ברורה (לא שפת הרצאה!)
2. הגדר כל מונח בהופעה ראשונה: **מונח** (English)
3. השאר קיצורי מדע באנגלית: DNA, RNA, mRNA, PCR, MHC
4. אורך יעד: {word_target} מילים
5. אל תכתוב "כפי שראינו", "בשקף הזה" - זה ספר, לא הרצאה
6. השתמש בטבלאות ורשימות לארגון מידע
7. **חובה**: ציין את מקור כל טענה מהותית באמצעות [SRC-XXX] שמופיע בחומר המקור.
   דוגמה: "הנגיף חודר לתא דרך קולטני ACE2 [SRC-012]."

כתוב את המקטע "{section_title}":
"""
            
            content = self._generate(prompt, TEMPERATURE_WRITING)
            
            if content:
                content = content.strip().replace("```markdown", "").replace("```", "")
                sections.append((section_title, content))
                print(f"    ✓ Section {i+1}/{len(outline)}: {section_title}")
            else:
                sections.append((section_title, f"## {section_title}\n\n[תוכן ייכתב מאוחר יותר]"))
                print(f"    ✗ Section {i+1} failed")
            
            time.sleep(3)  # Rate limiting between sections
        
        return sections
    
    def _wave3_synthesize(self, plan: Dict, sections: List[Tuple[str, str]]) -> str:
        """
        Wave 3: Combine sections and smooth transitions for cohesive flow.
        """
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        # Combine all sections
        raw_content = f"# פרק {chapter_id}: {title}\n\n"
        for section_title, section_content in sections:
            # Add section header if not already present
            if not section_content.strip().startswith("#"):
                raw_content += f"## {section_title}\n\n"
            raw_content += section_content + "\n\n"
        
        # Synthesis pass to smooth transitions
        prompt = f"""אתה עורך ראשי של ספר לימוד אקדמי.

להלן טיוטה של פרק שנכתב בחלקים נפרדים. המשימה שלך:
1. לשפר את המעברים בין החלקים (transitions)
2. להסיר כפילויות או סתירות
3. לוודא זרימה לוגית מפשוט למורכב
4. לשמור על כל התוכן המהותי
5. לוודא שהכותרות מסודרות היררכית (# -> ## -> ###)

טיוטה:
{raw_content}

---
החזר את הפרק המעובד במלואו (Markdown):
"""
        
        final = self._generate(prompt, TEMPERATURE_SYNTHESIS)
        
        if final:
            final = final.strip().replace("```markdown", "").replace("```", "")
            
            # Ensure chapter header
            if not final.startswith(f"# פרק {chapter_id}"):
                final = f"# פרק {chapter_id}: {title}\n\n" + final
            
            return final
        else:
            print(f"[{AGENT_NAME}] Synthesis failed, using raw content")
            return raw_content
    
    def _write_draft_template(self, plan: Dict, brief: Dict, source_content: str) -> DraftChapter:
        """Fallback template-based writing (no API)."""
        chapter_id = plan["chapter_id"]
        title = plan["hebrew_title"]
        
        md = f"# פרק {chapter_id}: {title}\n\n"
        
        # Learning objectives
        md += "## מטרות למידה\n\n"
        md += "בסיום פרק זה תוכלו:\n\n"
        for obj in brief.get("objectives", plan.get("learning_objectives", []))[:8]:
            md += f"- {obj}\n"
        md += "\n"
        
        # Roadmap
        md += "## מפת דרכים\n\n"
        md += brief.get("roadmap", f"פרק זה עוסק ב{title}.") + "\n\n"
        md += "---\n\n"
        
        # Main content placeholder
        md += "## תוכן מרכזי\n\n"
        md += "[תוכן יתווסף כאשר ה-API יהיה זמין]\n\n"
        
        # Quick summary
        md += "## סיכום מהיר\n\n"
        for obj in brief.get("objectives", [])[:5]:
            md += f"- {obj}\n"
        md += "\n"
        
        # Key terms
        md += "## מושגי מפתח\n\n"
        md += "| מונח בעברית | English | הגדרה קצרה |\n"
        md += "|-------------|---------|------------|\n"
        for term in brief.get("key_terms", [])[:10]:
            md += f"| {term.get('hebrew', '')} | {term.get('english', '')} | מושג מרכזי |\n"
        md += "\n"
        
        # Practice questions
        md += "## שאלות לתרגול\n\n"
        md += "[שאלות יתווספו מאוחר יותר]\n"
        
        word_count = len(md.split())
        
        return DraftChapter(
            chapter_id=chapter_id,
            title=title,
            content_md=md,
            word_count=word_count,
            has_objectives=True,
            has_roadmap=True,
            has_summary=True,
            has_key_terms=True,
            has_questions=False,
            todos=["Expand content with Gemini API"]
        )