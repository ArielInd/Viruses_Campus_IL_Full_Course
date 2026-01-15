"""
Multi-agent pipeline for creating a Hebrew virology study ebook.

Quality-First Edition: All agents upgraded to gemini-2.5-pro with deep analysis.
"""

from .schemas import (
    FileNote, CorpusIndex, ChapterPlan, ChapterBrief,
    DraftChapter, EditedChapter, ConsistencyReport, SafetyReport,
    LogEvent, PipelineLogger, TodoTracker,
    save_json, load_json, save_markdown, read_file
)

from .base_agent import BaseAgent

from .agent_a_corpus_librarian import CorpusLibrarian
from .agent_b_curriculum_architect import CurriculumArchitect
from .agent_c_brief_builder import ChapterBriefBuilder
from .agent_d_draft_writer import DraftWriter
from .agent_e_dev_editor import DevelopmentalEditor
from .agent_f_assessment import AssessmentDesigner
from .agent_g_terminology import TerminologyConsistencyKeeper
from .agent_h_proofreader import CopyeditorProofreader
from .agent_i_safety import SafetyScopeReviewer
from .agent_j_critic import AdversarialCritic
from .agent_k_visuals import VisualChronicler      # NEW: Round 2
from .agent_l_narrative import PedagogicalBridge    # NEW: Round 2
from .agent_m_verifier import SourceVerifier      # NEW: Anti-Hallucination

__all__ = [
    # Schemas
    'FileNote', 'CorpusIndex', 'ChapterPlan', 'ChapterBrief',
    'DraftChapter', 'EditedChapter', 'ConsistencyReport', 'SafetyReport',
    'LogEvent', 'PipelineLogger', 'TodoTracker',
    'save_json', 'load_json', 'save_markdown', 'read_file',
    # Base Agent
    'BaseAgent',
    # Agents (A-L)
    'CorpusLibrarian',        # A: Corpus analysis
    'CurriculumArchitect',    # B: Curriculum design
    'ChapterBriefBuilder',    # C: Brief generation
    'DraftWriter',            # D: Iterative writing (3-wave)
    'DevelopmentalEditor',    # E: Active editing
    'AssessmentDesigner',     # F: LLM assessment
    'TerminologyConsistencyKeeper',  # G: Grammar-aware term consistency
    'CopyeditorProofreader',  # H: LLM proofreading
    'SafetyScopeReviewer',    # I: High-rigor safety review
    'AdversarialCritic',      # J: Adversarial critique
    'VisualChronicler',       # K: Visual insights (multimodal)
    'PedagogicalBridge',      # L: Narrative continuity
    'SourceVerifier',         # M: Citation verification & stripping
]
