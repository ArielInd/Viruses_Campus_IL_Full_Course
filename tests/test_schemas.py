"""
Unit tests for shared schemas and utilities.
"""

import os
import pytest
import tempfile
import shutil
import json
from agents.schemas import (
    FileNote, CorpusIndex, ChapterPlan, ChapterBrief, PipelineLogger, TodoTracker, LogEvent,
    save_json, load_json, save_markdown, read_file
)
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


class TestDataclasses:
    """Test dataclass schemas."""

    def test_file_note_creation(self):
        """Test FileNote dataclass."""
        note = FileNote(
            filename="test.txt",
            path="/path/to/test.txt",
            lesson_number="1",
            unit_number="1.0",
            title="Test Lesson",
            word_count=100,
            main_topics=["Topic 1", "Topic 2"],
            key_definitions=[{"term": "DNA", "definition": "Genetic material"}],
            mechanisms=["Replication"],
            examples=["E. coli"],
            expert_interview="Prof. Smith",
            lab_demo="Lab test"
        )

        assert note.filename == "test.txt"
        assert note.word_count == 100
        assert len(note.main_topics) == 2
        assert note.expert_interview == "Prof. Smith"

    def test_corpus_index_creation(self):
        """Test CorpusIndex dataclass."""
        index = CorpusIndex(
            total_files=73,
            total_words=43000,
            lessons={"1": ["/path/file1.txt"], "2": ["/path/file2.txt"]},
            file_notes_dir="/path/to/notes",
            concepts_map_path="/path/to/map.md"
        )

        assert index.total_files == 73
        assert "1" in index.lessons
        assert index.created_at is not None

    def test_chapter_plan_creation(self):
        """Test ChapterPlan dataclass."""
        plan = ChapterPlan(
            chapter_id="01",
            hebrew_title="פרק ראשון",
            english_title="Chapter One",
            source_files=["/path/file1.txt"],
            learning_objectives=["Objective 1", "Objective 2"],
            must_include_definitions=["DNA", "RNA"],
            required_tables=["Table 1"],
            expert_box="Prof. Smith",
            lab_box="Lab Demo",
            misconceptions_to_address=["Misconception 1"],
            question_targets=["Target 1"]
        )

        assert plan.chapter_id == "01"
        assert len(plan.learning_objectives) == 2
        assert "DNA" in plan.must_include_definitions

    def test_chapter_brief_creation(self):
        """Test ChapterBrief dataclass."""
        brief = ChapterBrief(
            chapter_id="01",
            title="Test Chapter",
            objectives=["Obj1"],
            roadmap="Test roadmap",
            content_sections=[{"heading": "Section 1", "key_points": ["Point 1"]}],
            definitions_to_bold=["Term1"],
            tables_to_create=[{"name": "Table1", "columns": ["A", "B"], "purpose": "Compare"}],
            expert_perspective={"expert_name": "Smith", "topic": "DNA"},
            lab_demo_conceptual={"demo_title": "Lab1", "conceptual_focus": "Focus"},
            common_mistakes=["Mistake1"],
            key_terms=[{"hebrew": "תא", "english": "Cell"}],
            mcq_targets=["MCQ1"],
            short_answer_targets=["SA1"],
            thinking_question_target="Think Q1"
        )

        assert brief.chapter_id == "01"
        assert len(brief.objectives) == 1
        assert brief.expert_perspective["expert_name"] == "Smith"


class TestPipelineLogger:
    """Test PipelineLogger."""

    def test_logger_initialization(self, temp_dir):
        """Test logger creates file."""
        log_path = os.path.join(temp_dir, "test.jsonl")
        logger = PipelineLogger(log_path)
        assert os.path.exists(log_path)

    def test_log_event(self, temp_dir):
        """Test logging an event."""
        log_path = os.path.join(temp_dir, "test.jsonl")
        logger = PipelineLogger(log_path)

        event = LogEvent(
            agent_name="TestAgent",
            event_type="start",
            timestamp=datetime.now().isoformat(),
            message="Test message"
        )

        logger.log(event)

        with open(log_path, 'r') as f:
            line = f.readline()
            data = json.loads(line)
            assert data['agent_name'] == "TestAgent"
            assert data['event_type'] == "start"

    def test_log_start(self, temp_dir):
        """Test log_start method."""
        log_path = os.path.join(temp_dir, "test.jsonl")
        logger = PipelineLogger(log_path)

        start_time = logger.log_start("TestAgent", ["input1.txt"])

        assert start_time is not None
        assert isinstance(start_time, datetime)

    def test_log_end(self, temp_dir):
        """Test log_end method."""
        log_path = os.path.join(temp_dir, "test.jsonl")
        logger = PipelineLogger(log_path)

        start_time = logger.log_start("TestAgent")
        logger.log_end("TestAgent", start_time, ["output1.txt"], ["warning1"], [])

        with open(log_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2  # start and end events

            end_data = json.loads(lines[1])
            assert end_data['event_type'] == "end"
            assert end_data['duration_seconds'] >= 0


class TestTodoTracker:
    """Test TodoTracker."""

    def test_todo_initialization(self, temp_dir):
        """Test TodoTracker initialization."""
        todo_path = os.path.join(temp_dir, "todos.md")
        tracker = TodoTracker(todo_path)
        assert tracker.todo_path == todo_path

    def test_add_todo(self, temp_dir):
        """Test adding a TODO item."""
        todo_path = os.path.join(temp_dir, "todos.md")
        tracker = TodoTracker(todo_path)

        tracker.add("AgentA", "Chapter 01", "Fix this issue")
        assert len(tracker.todos) == 1
        assert tracker.todos[0]['agent'] == "AgentA"

    def test_save_todos(self, temp_dir):
        """Test saving TODOs to file."""
        todo_path = os.path.join(temp_dir, "todos.md")
        tracker = TodoTracker(todo_path)

        tracker.add("AgentA", "Context1", "Description1")
        tracker.add("AgentB", "Context2", "Description2")
        tracker.save()

        assert os.path.exists(todo_path)

        with open(todo_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "AgentA" in content
            assert "AgentB" in content
            assert "Description1" in content


class TestUtilityFunctions:
    """Test utility functions."""

    def test_save_and_load_json(self, temp_dir):
        """Test JSON save/load functions."""
        file_path = os.path.join(temp_dir, "test.json")
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        save_json(data, file_path)
        assert os.path.exists(file_path)

        loaded = load_json(file_path)
        assert loaded == data

    def test_save_json_with_dataclass(self, temp_dir):
        """Test saving dataclass as JSON."""
        file_path = os.path.join(temp_dir, "test.json")

        note = FileNote(
            filename="test.txt",
            path="/path",
            lesson_number="1",
            unit_number="1.0",
            title="Test",
            word_count=100,
            main_topics=[],
            key_definitions=[],
            mechanisms=[],
            examples=[]
        )

        save_json(note, file_path)
        loaded = load_json(file_path)

        assert loaded['filename'] == "test.txt"
        assert loaded['word_count'] == 100

    def test_save_markdown(self, temp_dir):
        """Test saving markdown content."""
        file_path = os.path.join(temp_dir, "test.md")
        content = "# Test Heading\n\nTest content."

        save_markdown(content, file_path)
        assert os.path.exists(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            loaded = f.read()
            assert loaded == content

    def test_read_file_utf8(self, temp_dir):
        """Test reading UTF-8 file."""
        file_path = os.path.join(temp_dir, "test.txt")
        content = "Test content with Hebrew: תאים"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        loaded = read_file(file_path)
        assert loaded == content
        assert "תאים" in loaded

    def test_read_file_encoding_fallback(self, temp_dir):
        """Test read_file with different encodings."""
        file_path = os.path.join(temp_dir, "test.txt")

        # Write as UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hebrew text: תאים")

        # Should successfully read
        content = read_file(file_path)
        assert "תאים" in content

    def test_save_json_hebrew_content(self, temp_dir):
        """Test saving JSON with Hebrew content."""
        file_path = os.path.join(temp_dir, "test.json")
        data = {
            "title": "פרק ראשון",
            "description": "תיאור בעברית"
        }

        save_json(data, file_path)
        loaded = load_json(file_path)

        assert loaded['title'] == "פרק ראשון"
        assert loaded['description'] == "תיאור בעברית"
