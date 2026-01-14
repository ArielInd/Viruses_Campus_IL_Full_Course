"""
Unit tests for Agent A (CorpusLibrarian).
"""

import os
import pytest
import tempfile
import shutil
import json
from agents.agent_a_corpus_librarian import CorpusLibrarian
from agents.schemas import PipelineLogger, TodoTracker


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    transcripts_dir = tempfile.mkdtemp()
    ops_dir = tempfile.mkdtemp()
    yield transcripts_dir, ops_dir
    shutil.rmtree(transcripts_dir)
    shutil.rmtree(ops_dir)


@pytest.fixture
def sample_transcript(temp_dirs):
    """Create a sample transcript file."""
    transcripts_dir, _ = temp_dirs

    # Create a lesson directory
    lesson_dir = os.path.join(transcripts_dir, "03_שיעור_1")
    os.makedirs(lesson_dir)

    # Create sample transcript
    content = """
מבוא לקורס

נושא: תאים הם יחידות החיים

מהו תא? תא הוא יחידת הבסיס של כל היצורים החיים.

דוגמה: תאי דם אדומים נושאים חמצן.

תהליך שכפול DNA הוא תהליך מרכזי בחיים.
"""

    file_path = os.path.join(lesson_dir, "01_1.0_מבוא_לקורס.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path


@pytest.fixture
def corpus_librarian(temp_dirs):
    """Create CorpusLibrarian instance."""
    transcripts_dir, ops_dir = temp_dirs
    logger = PipelineLogger(os.path.join(ops_dir, "pipeline.jsonl"))
    todos = TodoTracker(os.path.join(ops_dir, "todos.md"))

    return CorpusLibrarian(transcripts_dir, ops_dir, logger, todos)


class TestCorpusLibrarian:
    """Test suite for CorpusLibrarian."""

    def test_initialization(self, corpus_librarian):
        """Test that agent initializes correctly."""
        assert corpus_librarian.transcripts_dir is not None
        assert corpus_librarian.ops_dir is not None
        assert corpus_librarian.artifacts_dir is not None

    def test_find_transcripts(self, corpus_librarian, sample_transcript):
        """Test finding transcript files."""
        files = corpus_librarian._find_transcripts()
        assert len(files) > 0
        assert any(f.endswith('.txt') for f in files)

    def test_parse_filename(self, corpus_librarian):
        """Test filename parsing for lesson/unit numbers."""
        filename = "01_1.0_מבוא_לקורס.txt"
        lesson, unit = corpus_librarian._parse_filename(filename)
        assert lesson == "1"
        assert unit == "1.0"

    def test_extract_title(self, corpus_librarian):
        """Test title extraction from filename."""
        filename = "01_1.0_מבוא_לקורס.txt"
        title = corpus_librarian._extract_title(filename)
        assert "מבוא לקורס" in title
        assert "01_1.0_" not in title

    def test_extract_topics(self, corpus_librarian):
        """Test topic extraction from content."""
        content = """
נושא: תאים הם יחידות החיים
נלמד על מבנה התא
בפרק זה נבחן את DNA
"""
        topics = corpus_librarian._extract_topics(content)
        assert len(topics) > 0

    def test_extract_definitions(self, corpus_librarian):
        """Test definition extraction."""
        content = """
תא - יחידת הבסיס של החיים.
DNA - חומר גנטי המכיל את המידע.
מהו רבוזום? רבוזום הוא מבנה המייצר חלבונים.
"""
        definitions = corpus_librarian._extract_definitions(content)
        assert len(definitions) > 0

    def test_extract_mechanisms(self, corpus_librarian):
        """Test mechanism extraction."""
        content = """
תהליך שכפול ה-DNA מתרחש בשלבים.
תהליך תרגום מתבצע בריבוזום.
הידבקות הנגיף לתא היא שלב ראשון.
"""
        mechanisms = corpus_librarian._extract_mechanisms(content)
        assert len(mechanisms) > 0

    def test_extract_examples(self, corpus_librarian):
        """Test example extraction."""
        content = """
לדוגמה: תאי דם אדומים.
למשל, נגיף השפעת.
כמו חיידקי E. coli.
"""
        examples = corpus_librarian._extract_examples(content)
        assert len(examples) >= 2

    def test_extract_expert_name(self, corpus_librarian):
        """Test expert name extraction from interview files."""
        filename = "06_3.5_ראיון_עם_פרופסור_דיוויד_בולטימור.txt"
        expert = corpus_librarian._extract_expert_name(filename)
        assert "דיוויד בולטימור" in expert

    def test_find_implied_figures(self, corpus_librarian):
        """Test finding references to figures."""
        content = """
כפי שניתן לראות בתרשים, המבנה הוא כפול.
באיור 1 מוצג המבנה.
"""
        figures = corpus_librarian._find_implied_figures(content)
        assert len(figures) > 0

    def test_process_file(self, corpus_librarian, sample_transcript):
        """Test processing a single file."""
        note = corpus_librarian._process_file(sample_transcript)

        assert note.filename is not None
        assert note.lesson_number is not None
        assert note.word_count > 0
        assert isinstance(note.main_topics, list)
        assert isinstance(note.key_definitions, list)

    def test_run_creates_artifacts(self, corpus_librarian, sample_transcript):
        """Test that run() creates expected artifacts."""
        result = corpus_librarian.run()

        assert result['total_files'] > 0
        assert os.path.exists(result['corpus_index'])
        assert os.path.exists(result['concepts_map'])
        assert os.path.isdir(result['file_notes_dir'])

    def test_corpus_index_structure(self, corpus_librarian, sample_transcript):
        """Test that corpus index has correct structure."""
        result = corpus_librarian.run()

        with open(result['corpus_index'], 'r', encoding='utf-8') as f:
            index = json.load(f)

        assert 'total_files' in index
        assert 'total_words' in index
        assert 'lessons' in index
        assert isinstance(index['lessons'], dict)

    def test_concepts_map_generated(self, corpus_librarian, sample_transcript):
        """Test that concepts map is generated."""
        result = corpus_librarian.run()

        with open(result['concepts_map'], 'r', encoding='utf-8') as f:
            content = f.read()

        assert len(content) > 0
        assert "מפת מושגים" in content or "שיעור" in content

    def test_hebrew_encoding(self, corpus_librarian, temp_dirs):
        """Test handling of Hebrew text encoding."""
        transcripts_dir, _ = temp_dirs

        # Create file with Hebrew content
        lesson_dir = os.path.join(transcripts_dir, "test_lesson")
        os.makedirs(lesson_dir)

        hebrew_content = "תאים הם יחידות החיים. DNA הוא חומר גנטי."
        file_path = os.path.join(lesson_dir, "01_test.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(hebrew_content)

        note = corpus_librarian._process_file(file_path)
        assert note.word_count > 0
