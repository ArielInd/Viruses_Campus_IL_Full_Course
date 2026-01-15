#!/usr/bin/env python3
"""
Unified Production Pipeline for Hebrew Virology Ebook

QUALITY-FIRST EDITION (Round 2):
- All primary agents use gemini-2.5-pro for deep reasoning
- Agent D uses 3-wave iterative writing
- Agent J provides adversarial critique before editing
- Agent H uses LLM-powered proofreading
- Agent E performs active rewriting
- Agent K extracts visual context from transcripts
- Agent L ensures cross-chapter narrative flow
- Final cover generation based on actual content

Orchestrates the full multi-agent workflow (Agents A-L) and 
generates final EPUB and PDF books.
"""

import os
import asyncio
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for agent imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google import genai
    print(f"[Diagnostics] google-genai SDK available")
except ImportError:
    print("[Diagnostics] google-genai NOT FOUND")

print(f"[Diagnostics] GEMINI_API_KEY set: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")

from agents.pipeline_context import PipelineContext
from agents.pipeline_orchestrator import PipelineOrchestrator, AgentStage, AgentTask
from agents.schemas import PipelineLogger, TodoTracker

# Import Real Agents (A-L)
from agents.agent_a_corpus_librarian import CorpusLibrarian
from agents.agent_b_curriculum_architect import CurriculumArchitect
from agents.agent_c_brief_builder import ChapterBriefBuilder
from agents.agent_d_draft_writer import DraftWriter
from agents.agent_e_dev_editor import DevelopmentalEditor
from agents.agent_f_assessment import AssessmentDesigner
from agents.agent_g_terminology import TerminologyConsistencyKeeper
from agents.agent_h_proofreader import CopyeditorProofreader
from agents.agent_i_safety import SafetyScopeReviewer
from agents.agent_j_critic import AdversarialCritic
from agents.agent_k_visuals import VisualChronicler
from agents.agent_l_narrative import PedagogicalBridge
from agents.agent_m_verifier import SourceVerifier  # NEW: Anti-Hallucination

async def run_production():
    """Run the complete production pipeline."""
    
    print("\n" + "="*70)
    print("🚀 HEBREW VIROLOGY EBOOK - PRODUCTION PIPELINE (QUALITY-FIRST)")
    print("="*70 + "\n")

    # 1. Setup
    BASE_DIR = Path(__file__).parent
    OPS_DIR = BASE_DIR / "ops"
    TRANSCRIPTS_DIR = BASE_DIR / "course_transcripts"
    BOOK_DIR = BASE_DIR / "book"

    for d in [OPS_DIR / "artifacts", OPS_DIR / "reports", BOOK_DIR / "chapters"]:
        d.mkdir(parents=True, exist_ok=True)

    context = PipelineContext(
        ops_dir=str(OPS_DIR),
        transcripts_dir=str(TRANSCRIPTS_DIR),
        book_dir=str(BOOK_DIR)
    )
    logger = PipelineLogger(str(OPS_DIR / "pipeline.jsonl"))
    todos = TodoTracker(str(OPS_DIR / "todos.md"))
    orchestrator = PipelineOrchestrator(context, logger, todos)

    # 2. Sequential Agents (A & B)
    print("[Production] Starting base analysis...")
    
    async def run_a(ctx):
        agent = CorpusLibrarian(str(TRANSCRIPTS_DIR), str(OPS_DIR), logger, todos)
        return agent.run()
    
    await orchestrator.run_stage(AgentStage.CORPUS_ANALYSIS, [
        AgentTask("CorpusLibrarian", AgentStage.CORPUS_ANALYSIS, function=run_a)
    ])

    async def run_b(ctx):
        agent = CurriculumArchitect(str(OPS_DIR), str(BOOK_DIR), logger, todos)
        return agent.run()
    
    await orchestrator.run_stage(AgentStage.CURRICULUM_DESIGN, [
        AgentTask("CurriculumArchitect", AgentStage.CURRICULUM_DESIGN, function=run_b)
    ])

    # 3. Core Generation (C, D, J, E)
    print("[Production] Generating core content...")
    
    async def run_c(ctx):
        agent = ChapterBriefBuilder(str(OPS_DIR), logger, todos)
        return agent.run()
    
    await orchestrator.run_stage(AgentStage.BRIEF_GENERATION, [
        AgentTask("BriefBuilder", AgentStage.BRIEF_GENERATION, function=run_c)
    ])

    async def run_d(ctx):
        agent = DraftWriter(str(TRANSCRIPTS_DIR), str(OPS_DIR), logger, todos)
        return await agent.run()
    
    await orchestrator.run_stage(AgentStage.DRAFT_WRITING, [
        AgentTask("DraftWriter", AgentStage.DRAFT_WRITING, function=run_d)
    ])

    async def run_j(ctx):
        agent = AdversarialCritic(str(OPS_DIR), str(BOOK_DIR), logger, todos)
        return agent.run()
    
    await orchestrator.run_stage(AgentStage.VALIDATION, [
        AgentTask("AdversarialCritic", AgentStage.VALIDATION, function=run_j)
    ])

    async def run_e(ctx):
        agent = DevelopmentalEditor(str(OPS_DIR), str(BOOK_DIR), logger, todos)
        return agent.run()
    
    await orchestrator.run_stage(AgentStage.EDITING, [
        AgentTask("DevelopmentalEditor", AgentStage.EDITING, function=run_e)
    ])

    # 4. Pedagogical & Visual Enhancement (K, L)
    print("\n[Production] Starting Pedagogical & Visual Enhancement (Round 2)...")
    
    async def run_k(ctx):
        agent = VisualChronicler(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()
    
    async def run_l(ctx):
        agent = PedagogicalBridge(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()

    await orchestrator.run_stage(AgentStage.VALIDATION, [
        AgentTask("VisualChronicler", AgentStage.VALIDATION, function=run_k, parallelizable=True),
        AgentTask("PedagogicalBridge", AgentStage.VALIDATION, function=run_l, parallelizable=True)
    ])

    # 5. Global Refinement (F, G, H, I)
    print("\n[Production] Starting final refinements...")

    async def run_f(ctx):
        agent = AssessmentDesigner(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()
    
    async def run_g(ctx):
        agent = TerminologyConsistencyKeeper(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()

    async def run_h(ctx):
        agent = CopyeditorProofreader(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()

    async def run_i(ctx):
        agent = SafetyScopeReviewer(str(BOOK_DIR), str(OPS_DIR), logger, todos)
        return agent.run()

    validation_tasks = [
        AgentTask("AssessmentDesigner", AgentStage.VALIDATION, function=run_f, parallelizable=True),
        AgentTask("TerminologyKeeper", AgentStage.VALIDATION, function=run_g, parallelizable=True),
        AgentTask("Proofreader", AgentStage.VALIDATION, function=run_h, parallelizable=True),
        AgentTask("SafetyReviewer", AgentStage.VALIDATION, function=run_i, parallelizable=True)
    ]
    
    await orchestrator.run_stage(AgentStage.VALIDATION, validation_tasks)

    # 6. Book Build (EPUB & PDF)
    print("\n" + "="*70)
    print("📚 BUILDING FINAL BOOK ARTIFACTS")
    print("="*70 + "\n")

    build_script = BOOK_DIR / "build_all.sh"
    if build_script.exists():
        print(f"[Build] Executing {build_script}...")
        try:
            os.chmod(build_script, 0o755)
            result = subprocess.run([str(build_script)], check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed:\n{e.stderr}")
            todos.add("BuildSystem", "build_all.sh", f"Build failed with error: {e.stderr}")
    else:
        print("⚠️  build_all.sh not found in book/ directory.")

    # 7. Final Aesthetic Touch: Cover Generation (Last Step)
    print("\n[Production] Generating final book cover based on content...")
    try:
        from llm_utils import generate_cover_from_book
        chapters_dir = BOOK_DIR / "chapters"
        full_text = ""
        # Collect top context for cover
        chapter_files = sorted(list(chapters_dir.glob("*.md")))
        for f in chapter_files[:3]:
            full_text += f.read_text()[:2000]
        
        generate_cover_from_book(full_text, str(BOOK_DIR / "cover.png"))
        print("✅ Final book cover generated.")
    except Exception as e:
        print(f"⚠️ Cover generation failed: {e}")

    # 8. Conclusion
    print("\n" + "="*70)
    print("✅ PRODUCTION COMPLETE")
    print("="*70)
    
    report = orchestrator.generate_performance_report()
    print(report)
    
    todos.save()
    print("\n📂 Results preserved in:")
    print(f"- Book:  {BOOK_DIR}/build/")
    print(f"- Logs:  {OPS_DIR}/pipeline.jsonl")
    print(f"- TODOs: {OPS_DIR}/todos.md")

if __name__ == "__main__":
    try:
        asyncio.run(run_production())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nPipeline Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
