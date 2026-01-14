#!/usr/bin/env python3
"""
Complete Pipeline Runner - Actually runs all agents end-to-end

This script runs the ACTUAL multi-agent pipeline, not a demo.
"""

import os
import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.pipeline_context import PipelineContext
from agents.schemas import PipelineLogger, TodoTracker

# Import actual agents
from agents.agent_a_corpus_librarian import CorpusLibrarian
from agents.agent_b_curriculum_architect import CurriculumArchitect
from agents.agent_c_brief_builder import ChapterBriefBuilder
from agents.agent_d_draft_writer import DraftWriter


def main():
    """Run the complete pipeline."""

    print("="*70)
    print("COMPLETE PIPELINE EXECUTION - ALL AGENTS")
    print("="*70)
    print()

    # Setup
    BASE_DIR = Path(__file__).parent
    OPS_DIR = BASE_DIR / "ops"
    TRANSCRIPTS_DIR = BASE_DIR / "course_transcripts"
    BOOK_DIR = BASE_DIR / "book"

    # Create directories
    OPS_DIR.mkdir(exist_ok=True)
    (OPS_DIR / "artifacts").mkdir(exist_ok=True)
    (OPS_DIR / "reports").mkdir(exist_ok=True)

    # Initialize shared context
    print("[Setup] Initializing pipeline context...")
    context = PipelineContext(
        ops_dir=str(OPS_DIR),
        transcripts_dir=str(TRANSCRIPTS_DIR)
    )

    # Initialize logger and todos
    logger = PipelineLogger(str(OPS_DIR / "pipeline.jsonl"))
    todos = TodoTracker(str(OPS_DIR / "todos.md"))

    pipeline_start = time.time()

    # ========================================================================
    # AGENT A: CORPUS LIBRARIAN
    # ========================================================================

    print("\n" + "="*70)
    print("AGENT A: CORPUS LIBRARIAN")
    print("="*70)

    agent_a = CorpusLibrarian(
        transcripts_dir=str(TRANSCRIPTS_DIR),
        ops_dir=str(OPS_DIR),
        logger=logger,
        todos=todos
    )

    start = time.time()
    result_a = agent_a.run()
    duration_a = time.time() - start

    print(f"\n✅ Agent A completed in {duration_a:.2f}s")
    print(f"   - Files analyzed: {result_a['total_files']}")
    print(f"   - Total words: {result_a['total_words']}")

    # Invalidate context cache to reload fresh data
    context.invalidate_cache()

    # ========================================================================
    # AGENT B: CURRICULUM ARCHITECT
    # ========================================================================

    print("\n" + "="*70)
    print("AGENT B: CURRICULUM ARCHITECT")
    print("="*70)

    agent_b = CurriculumArchitect(
        ops_dir=str(OPS_DIR),
        book_dir=str(BOOK_DIR),
        logger=logger,
        todos=todos
    )

    start = time.time()
    result_b = agent_b.run()
    duration_b = time.time() - start

    print(f"\n✅ Agent B completed in {duration_b:.2f}s")
    print(f"   - Chapters planned: {result_b['num_chapters']}")

    # Invalidate context cache
    context.invalidate_cache()

    # ========================================================================
    # AGENT C: CHAPTER BRIEF BUILDER (PARALLEL)
    # ========================================================================

    print("\n" + "="*70)
    print("AGENT C: CHAPTER BRIEF BUILDER (Parallel)")
    print("="*70)

    agent_c = ChapterBriefBuilder(
        ops_dir=str(OPS_DIR),
        logger=logger,
        todos=todos
    )

    start = time.time()
    result_c = agent_c.run()
    duration_c = time.time() - start

    print(f"\n✅ Agent C completed in {duration_c:.2f}s")
    print(f"   - Briefs created: {result_c['num_briefs']}")

    # Invalidate context cache
    context.invalidate_cache()

    # ========================================================================
    # AGENT D: DRAFT WRITER (WITH LLM)
    # ========================================================================

    print("\n" + "="*70)
    print("AGENT D: DRAFT WRITER (LLM-Powered)")
    print("="*70)
    print("⚠️  Note: This will use Gemini API and take several minutes")
    print()

    agent_d = DraftWriter(
        transcripts_dir=str(TRANSCRIPTS_DIR),
        ops_dir=str(OPS_DIR),
        logger=logger,
        todos=todos
    )

    start = time.time()
    result_d = agent_d.run()
    duration_d = time.time() - start

    print(f"\n✅ Agent D completed in {duration_d:.2f}s")
    print(f"   - Drafts generated: {result_d.get('num_drafts', 'N/A')}")

    # ========================================================================
    # SUMMARY
    # ========================================================================

    total_duration = time.time() - pipeline_start

    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print()
    print(f"Total execution time: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
    print()
    print("Stage breakdown:")
    print(f"  Agent A (Corpus):      {duration_a:.2f}s")
    print(f"  Agent B (Curriculum):  {duration_b:.2f}s")
    print(f"  Agent C (Briefs):      {duration_c:.2f}s")
    print(f"  Agent D (Drafts):      {duration_d:.2f}s")
    print()
    print("Artifacts created:")
    print(f"  - Corpus index:    {OPS_DIR}/artifacts/corpus_index.json")
    print(f"  - Chapter plan:    {OPS_DIR}/artifacts/chapter_plan.json")
    print(f"  - Chapter briefs:  {OPS_DIR}/artifacts/chapter_briefs/")
    print(f"  - Draft chapters:  {OPS_DIR}/artifacts/drafts/chapters/")
    print(f"  - Logs:            {OPS_DIR}/pipeline.jsonl")
    print(f"  - TODOs:           {OPS_DIR}/todos.md")
    print()

    # Save TODOs
    todos.save()

    print("✅ All agents executed successfully!")
    print()
    print("Next steps:")
    print("  1. Review drafts in: ops/artifacts/drafts/chapters/")
    print("  2. Run remaining agents (E-I) for full ebook")
    print("  3. Convert to PDF using: python3 convert_to_pdf.py")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
