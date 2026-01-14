#!/usr/bin/env python3
"""
Optimized Multi-Agent Pipeline Runner

This script demonstrates the improved pipeline architecture with:
- Shared PipelineContext for cached data access
- Concurrent execution of independent agents
- Performance metrics and tracking
- Multi-provider LLM support
"""

import asyncio
import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.pipeline_context import PipelineContext
from agents.pipeline_orchestrator import PipelineOrchestrator, AgentStage, AgentTask
from agents.schemas import PipelineLogger, TodoTracker
from agents.llm_client import get_llm_client

# Import agents (you'll need to adapt these imports based on actual agent implementations)
# from agents.agent_a_corpus_librarian import CorpusLibrarian
# from agents.agent_b_curriculum_architect import CurriculumArchitect
# ... etc


async def run_optimized_pipeline():
    """
    Run the complete ebook generation pipeline with optimizations.
    """

    # =========================================================================
    # SETUP
    # =========================================================================

    print("="*70)
    print("HEBREW VIROLOGY EBOOK - OPTIMIZED PIPELINE")
    print("="*70)
    print()

    # Directories
    BASE_DIR = Path(__file__).parent
    OPS_DIR = BASE_DIR / "ops"
    TRANSCRIPTS_DIR = BASE_DIR / "course_transcripts"
    BOOK_DIR = BASE_DIR / "book"

    # Ensure directories exist
    OPS_DIR.mkdir(exist_ok=True)
    (OPS_DIR / "artifacts").mkdir(exist_ok=True)
    (OPS_DIR / "reports").mkdir(exist_ok=True)
    BOOK_DIR.mkdir(exist_ok=True)

    # Initialize shared context (loads data once, caches for all agents)
    print("[Setup] Initializing shared pipeline context...")
    context = PipelineContext(
        ops_dir=str(OPS_DIR),
        transcripts_dir=str(TRANSCRIPTS_DIR),
        book_dir=str(BOOK_DIR)
    )

    # Initialize logger and TODO tracker
    logger = PipelineLogger(str(OPS_DIR / "pipeline.jsonl"))
    todos = TodoTracker(str(OPS_DIR / "todos.md"))

    # Initialize LLM client (supports Gemini + OpenRouter)
    print("[Setup] Initializing LLM client...")
    llm_client = get_llm_client()

    # Initialize orchestrator
    orchestrator = PipelineOrchestrator(
        context=context,
        logger=logger,
        todos=todos,
        max_parallel_agents=4
    )

    print("[Setup] Configuration complete!\n")
    print(f"Context stats: {context.get_cache_stats()}\n")

    # =========================================================================
    # STAGE 1: CORPUS ANALYSIS (Sequential)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 1: CORPUS ANALYSIS")
    print("="*70 + "\n")

    # Note: You'll need to adapt this based on your actual agent implementations
    # Example placeholder:

    async def corpus_analysis_task(ctx: PipelineContext):
        """Analyze all transcripts and generate file notes."""
        # from agents.agent_a_corpus_librarian import CorpusLibrarian
        # agent = CorpusLibrarian(ctx, logger, todos)
        # return agent.run()

        print("[CorpusLibrarian] Analyzing transcripts...")
        await asyncio.sleep(2)  # Simulate work
        print("[CorpusLibrarian] ✓ Generated file notes for 103 files")
        return {"status": "complete", "files": 103}

    stage1_tasks = [
        AgentTask(
            agent_name="CorpusLibrarian",
            stage=AgentStage.CORPUS_ANALYSIS,
            function=corpus_analysis_task,
            parallelizable=False
        )
    ]

    stage1_results = await orchestrator.run_stage(AgentStage.CORPUS_ANALYSIS, stage1_tasks)

    # =========================================================================
    # STAGE 2: CURRICULUM DESIGN (Sequential)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 2: CURRICULUM DESIGN")
    print("="*70 + "\n")

    async def curriculum_design_task(ctx: PipelineContext):
        """Design chapter structure and learning objectives."""
        # Uses cached file_notes from context (no redundant loading!)
        file_notes = ctx.get_file_notes()
        print(f"[CurriculumArchitect] Using {len(file_notes)} cached file notes")
        await asyncio.sleep(1)
        print("[CurriculumArchitect] ✓ Generated plan for 8 chapters")
        return {"status": "complete", "chapters": 8}

    stage2_tasks = [
        AgentTask(
            agent_name="CurriculumArchitect",
            stage=AgentStage.CURRICULUM_DESIGN,
            function=curriculum_design_task,
            parallelizable=False
        )
    ]

    stage2_results = await orchestrator.run_stage(AgentStage.CURRICULUM_DESIGN, stage2_tasks)

    # =========================================================================
    # STAGE 3: BRIEF GENERATION (Parallel)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 3: BRIEF GENERATION (Parallel)")
    print("="*70 + "\n")

    async def brief_generation_task(ctx: PipelineContext):
        """Generate chapter briefs in parallel."""
        chapter_plan = ctx.get_chapter_plan()
        print(f"[BriefBuilder] Generating briefs for {len(chapter_plan)} chapters (parallel)...")

        # Simulate parallel brief generation
        async def generate_brief(chapter_id):
            await asyncio.sleep(0.5)
            print(f"[BriefBuilder] ✓ Brief for chapter {chapter_id}")

        await asyncio.gather(*[generate_brief(f"{i:02d}") for i in range(1, 9)])
        return {"status": "complete", "briefs": 8}

    stage3_tasks = [
        AgentTask(
            agent_name="BriefBuilder",
            stage=AgentStage.BRIEF_GENERATION,
            function=brief_generation_task,
            parallelizable=True
        )
    ]

    stage3_results = await orchestrator.run_stage(AgentStage.BRIEF_GENERATION, stage3_tasks)

    # =========================================================================
    # STAGE 4: DRAFT WRITING (Parallel with Rate Limiting)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 4: DRAFT WRITING (Async with Rate Limiting)")
    print("="*70 + "\n")

    async def draft_writing_task(ctx: PipelineContext):
        """Generate chapter drafts using LLM (async with rate limiting)."""
        briefs = ctx.get_all_chapter_briefs()
        print(f"[DraftWriter] Writing drafts for {len(briefs)} chapters...")

        async def write_chapter_draft(chapter_id):
            # Simulate LLM API call with automatic rate limiting
            prompt = f"Write chapter {chapter_id} about virology in Hebrew"
            # response = await llm_client.generate_async(prompt)
            await asyncio.sleep(1)  # Simulate API call
            print(f"[DraftWriter] ✓ Draft for chapter {chapter_id}")

        # All 8 chapters processed concurrently with built-in rate limiting
        await asyncio.gather(*[write_chapter_draft(f"{i:02d}") for i in range(1, 9)])
        return {"status": "complete", "drafts": 8}

    stage4_tasks = [
        AgentTask(
            agent_name="DraftWriter",
            stage=AgentStage.DRAFT_WRITING,
            function=draft_writing_task,
            parallelizable=True
        )
    ]

    stage4_results = await orchestrator.run_stage(AgentStage.DRAFT_WRITING, stage4_tasks)

    # =========================================================================
    # STAGE 5: EDITING (Parallel)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 5: DEVELOPMENTAL EDITING (Parallel)")
    print("="*70 + "\n")

    async def editing_task(ctx: PipelineContext):
        """Edit chapter drafts in parallel."""
        print("[DevelopmentalEditor] Editing 8 chapters...")

        async def edit_chapter(chapter_id):
            await asyncio.sleep(0.3)
            print(f"[DevelopmentalEditor] ✓ Edited chapter {chapter_id}")

        await asyncio.gather(*[edit_chapter(f"{i:02d}") for i in range(1, 9)])
        return {"status": "complete", "edited": 8}

    stage5_tasks = [
        AgentTask(
            agent_name="DevelopmentalEditor",
            stage=AgentStage.EDITING,
            function=editing_task,
            parallelizable=True
        )
    ]

    stage5_results = await orchestrator.run_stage(AgentStage.EDITING, stage5_tasks)

    # =========================================================================
    # STAGE 6: VALIDATION (3 Agents in Parallel!)
    # =========================================================================

    print("\n" + "="*70)
    print("STAGE 6: VALIDATION (3 Agents Concurrent)")
    print("="*70 + "\n")

    async def terminology_task(ctx: PipelineContext):
        """Check terminology consistency."""
        print("[TerminologyKeeper] Checking term consistency...")
        await asyncio.sleep(1.5)
        print("[TerminologyKeeper] ✓ Validated 40 terms across 8 chapters")
        return {"status": "complete", "terms": 40}

    async def proofreading_task(ctx: PipelineContext):
        """Proofread all content."""
        print("[Proofreader] Scanning for errors...")
        await asyncio.sleep(2.0)
        print("[Proofreader] ✓ Checked 8 chapters")
        return {"status": "complete", "issues": 3}

    async def safety_task(ctx: PipelineContext):
        """Safety review for dangerous content."""
        # Uses compiled regex patterns from context (cached!)
        patterns = ctx.get_compiled_patterns({
            "pip_install": r"pip install",
            "sudo_rm": r"sudo rm -rf",
            "unsafe_lab": r"Step-by-step.*protocol"
        })

        print(f"[SafetyReviewer] Scanning with {len(patterns)} pre-compiled patterns...")
        await asyncio.sleep(3.0)
        print("[SafetyReviewer] ✓ Safety review complete - no issues found")
        return {"status": "complete", "safe": True}

    # All three run concurrently!
    stage6_tasks = [
        AgentTask("TerminologyKeeper", AgentStage.VALIDATION, function=terminology_task, parallelizable=True),
        AgentTask("Proofreader", AgentStage.VALIDATION, function=proofreading_task, parallelizable=True),
        AgentTask("SafetyReviewer", AgentStage.VALIDATION, function=safety_task, parallelizable=True),
    ]

    stage6_results = await orchestrator.run_stage(AgentStage.VALIDATION, stage6_tasks)

    # =========================================================================
    # FINALIZATION
    # =========================================================================

    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70 + "\n")

    # Generate performance report
    report = orchestrator.generate_performance_report()
    print(report)

    # Save metrics
    metrics_path = OPS_DIR / "performance_metrics.json"
    orchestrator.save_performance_metrics(str(metrics_path))
    print(f"\n📊 Performance metrics saved to: {metrics_path}")

    # Save TODO items
    todos.save()
    print(f"📝 TODO items saved to: {OPS_DIR / 'todos.md'}")

    # Show cache statistics
    print("\n💾 Cache statistics:")
    print(context)

    return orchestrator


def main():
    """Entry point."""
    try:
        # Run async pipeline
        orchestrator = asyncio.run(run_optimized_pipeline())

        print("\n✅ Pipeline completed successfully!")
        print("\nNext steps:")
        print("1. Review generated book in: book/chapters/")
        print("2. Check performance metrics: ops/performance_metrics.json")
        print("3. Review TODOs: ops/todos.md")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return 130

    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
