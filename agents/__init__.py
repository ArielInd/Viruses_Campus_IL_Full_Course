"""
Multi-agent pipeline for creating a Hebrew virology study ebook.
"""

from .schemas import (
    FileNote, CorpusIndex, ChapterPlan, ChapterBrief,
    DraftChapter, EditedChapter, ConsistencyReport, SafetyReport,
    LogEvent, PipelineLogger, TodoTracker,
    save_json, load_json, save_markdown, read_file
)

from .agent_a_corpus_librarian import CorpusLibrarian
from .agent_b_curriculum_architect import CurriculumArchitect
from .agent_c_brief_builder import ChapterBriefBuilder
from .agent_d_draft_writer import DraftWriter
from .agent_e_dev_editor import DevelopmentalEditor
from .agent_f_assessment import AssessmentDesigner
from .agent_g_terminology import TerminologyConsistencyKeeper
from .agent_h_proofreader import CopyeditorProofreader
from .agent_i_safety import SafetyScopeReviewer

__all__ = [
    # Schemas
    'FileNote', 'CorpusIndex', 'ChapterPlan', 'ChapterBrief',
    'DraftChapter', 'EditedChapter', 'ConsistencyReport', 'SafetyReport',
    'LogEvent', 'PipelineLogger', 'TodoTracker',
    'save_json', 'load_json', 'save_markdown', 'read_file',
    # Agents
    'CorpusLibrarian',
    'CurriculumArchitect', 
    'ChapterBriefBuilder',
    'DraftWriter',
    'DevelopmentalEditor',
    'AssessmentDesigner',
    'TerminologyConsistencyKeeper',
    'CopyeditorProofreader',
    'SafetyScopeReviewer',
]
