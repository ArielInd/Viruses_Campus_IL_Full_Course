"""
Shared schemas and utilities for the multi-agent ebook pipeline.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os

# =============================================================================
# DATA SCHEMAS
# =============================================================================

@dataclass
class FileNote:
    """Notes extracted from a single transcript file."""
    filename: str
    path: str
    lesson_number: str
    unit_number: str
    title: str
    word_count: int
    main_topics: List[str]
    key_definitions: List[Dict[str, str]]  # {"term": ..., "definition": ...}
    mechanisms: List[str]
    examples: List[str]
    expert_interview: Optional[str] = None
    lab_demo: Optional[str] = None
    implied_figures: List[str] = field(default_factory=list)
    todos: List[str] = field(default_factory=list)

@dataclass
class CorpusIndex:
    """Index of all transcript files with metadata."""
    total_files: int
    total_words: int
    lessons: Dict[str, List[str]]  # lesson_id -> [file_paths]
    file_notes_dir: str
    concepts_map_path: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ChapterPlan:
    """Plan for a single chapter."""
    chapter_id: str
    hebrew_title: str
    english_title: str
    source_files: List[str]
    learning_objectives: List[str]
    must_include_definitions: List[str]
    required_tables: List[str]
    expert_box: Optional[str]
    lab_box: Optional[str]
    misconceptions_to_address: List[str]
    question_targets: List[str]

@dataclass
class ChapterBrief:
    """Detailed brief for writing a chapter."""
    chapter_id: str
    title: str
    objectives: List[str]
    roadmap: str
    content_sections: List[Dict[str, Any]]
    definitions_to_bold: List[str]
    tables_to_create: List[Dict[str, Any]]
    expert_perspective: Optional[Dict[str, str]]
    lab_demo_conceptual: Optional[Dict[str, str]]
    common_mistakes: List[str]
    key_terms: List[Dict[str, str]]
    mcq_targets: List[str]
    short_answer_targets: List[str]
    thinking_question_target: str

@dataclass
class DraftChapter:
    """A draft chapter before editing."""
    chapter_id: str
    title: str
    content_md: str
    word_count: int
    has_objectives: bool
    has_roadmap: bool
    has_summary: bool
    has_key_terms: bool
    has_questions: bool
    todos: List[str]

@dataclass
class EditedChapter:
    """Final edited chapter."""
    chapter_id: str
    title: str
    content_md: str
    word_count: int
    edit_notes: List[str]
    quality_score: float  # 0-1

@dataclass
class ConsistencyReport:
    """Report on terminology consistency."""
    total_terms_checked: int
    inconsistencies_found: int
    fixes_applied: List[Dict[str, str]]
    warnings: List[str]

@dataclass 
class SafetyReport:
    """Report on safety review."""
    chapter_id: str
    passed: bool
    issues_found: List[str]
    remediations_applied: List[str]

@dataclass
class LogEvent:
    """Structured log event for JSONL logging."""
    agent_name: str
    event_type: str  # "start", "end", "warning", "error"
    timestamp: str
    input_files: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    message: str = ""
    duration_seconds: float = 0.0

# =============================================================================
# UTILITIES
# =============================================================================

class PipelineLogger:
    """Structured JSONL logger for the pipeline."""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        if os.path.dirname(log_path):
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        # Ensure file exists
        if not os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                pass
    
    def log(self, event: LogEvent):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
    
    def log_start(self, agent_name: str, input_files: List[str] = None):
        event = LogEvent(
            agent_name=agent_name,
            event_type="start",
            timestamp=datetime.now().isoformat(),
            input_files=input_files or [],
            message=f"Agent {agent_name} starting"
        )
        self.log(event)
        return datetime.now()
    
    def log_end(self, agent_name: str, start_time: datetime, 
                output_files: List[str] = None, warnings: List[str] = None,
                errors: List[str] = None):
        duration = (datetime.now() - start_time).total_seconds()
        event = LogEvent(
            agent_name=agent_name,
            event_type="end",
            timestamp=datetime.now().isoformat(),
            output_files=output_files or [],
            warnings=warnings or [],
            errors=errors or [],
            duration_seconds=duration,
            message=f"Agent {agent_name} completed in {duration:.2f}s"
        )
        self.log(event)


class TodoTracker:
    """Tracks TODO items across the pipeline."""
    
    def __init__(self, todo_path: str):
        self.todo_path = todo_path
        self.todos: List[Dict[str, str]] = []
        os.makedirs(os.path.dirname(todo_path), exist_ok=True)
    
    def add(self, agent: str, context: str, description: str):
        self.todos.append({
            "agent": agent,
            "context": context,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def save(self):
        with open(self.todo_path, 'w', encoding='utf-8') as f:
            f.write("# TODO Items from Pipeline\n\n")
            for todo in self.todos:
                f.write(f"## [{todo['agent']}] {todo['context']}\n")
                f.write(f"- {todo['description']}\n")
                f.write(f"- *Recorded: {todo['timestamp']}*\n\n")


def save_json(data: Any, path: str):
    """Save data to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        if hasattr(data, '__dataclass_fields__'):
            json.dump(asdict(data), f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str) -> Dict:
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_markdown(content: str, path: str):
    """Save markdown content to file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_file(path: str) -> str:
    """Read text file with fallback encodings."""
    for encoding in ['utf-8', 'utf-16', 'windows-1255', 'iso-8859-8']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {path}")
