"""
Unit tests for VersionManager.
"""

import os
import pytest
import tempfile
import shutil
from agents.version_manager import VersionManager, VersionMetadata


@pytest.fixture
def temp_ops_dir():
    """Create a temporary ops directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def version_manager(temp_ops_dir):
    """Create a VersionManager instance for testing."""
    return VersionManager(temp_ops_dir)


class TestVersionManager:
    """Test suite for VersionManager."""

    def test_initialization(self, version_manager):
        """Test that VersionManager initializes correctly."""
        assert os.path.exists(version_manager.versions_dir)
        assert os.path.exists(version_manager.chapters_dir)
        assert os.path.exists(version_manager.diffs_dir)

    def test_save_version(self, version_manager):
        """Test saving a version."""
        content = "# Chapter 1\n\nThis is test content."
        version_id = version_manager.save_version(
            chapter_id="01",
            content=content,
            agent="TestAgent",
            message="Initial test version"
        )

        assert version_id == "v001"
        assert os.path.exists(version_manager.metadata_path)

    def test_get_version(self, version_manager):
        """Test retrieving a version."""
        content = "# Chapter 1\n\nThis is test content."
        version_id = version_manager.save_version(
            chapter_id="01",
            content=content,
            agent="TestAgent",
            message="Initial test version"
        )

        retrieved = version_manager.get_version("01", version_id)
        assert retrieved == content

    def test_multiple_versions(self, version_manager):
        """Test saving multiple versions of same chapter."""
        v1 = version_manager.save_version(
            "01", "Version 1 content", "Agent1", "First version"
        )
        v2 = version_manager.save_version(
            "01", "Version 2 content", "Agent2", "Second version"
        )
        v3 = version_manager.save_version(
            "01", "Version 3 content", "Agent3", "Third version"
        )

        assert v1 == "v001"
        assert v2 == "v002"
        assert v3 == "v003"

    def test_get_latest_version(self, version_manager):
        """Test getting the latest version."""
        version_manager.save_version("01", "V1", "Agent1", "First")
        version_manager.save_version("01", "V2", "Agent2", "Second")
        version_manager.save_version("01", "V3", "Agent3", "Third")

        version_id, content = version_manager.get_latest_version("01")
        assert version_id == "v003"
        assert content == "V3"

    def test_get_chapter_versions(self, version_manager):
        """Test getting all versions for a chapter."""
        version_manager.save_version("01", "V1", "Agent1", "First")
        version_manager.save_version("01", "V2", "Agent2", "Second")
        version_manager.save_version("02", "Other chapter", "Agent1", "Other")

        versions = version_manager.get_chapter_versions("01")
        assert len(versions) == 2
        assert versions[0].version_id == "v001"
        assert versions[1].version_id == "v002"

    def test_version_metadata(self, version_manager):
        """Test that version metadata is correct."""
        version_manager.save_version(
            chapter_id="01",
            content="Test content with multiple words here",
            agent="TestAgent",
            message="Test message",
            tags=["draft", "test"]
        )

        versions = version_manager.get_chapter_versions("01")
        assert len(versions) == 1

        v = versions[0]
        assert v.chapter_id == "01"
        assert v.agent == "TestAgent"
        assert v.message == "Test message"
        assert v.word_count == 6
        assert "draft" in v.tags
        assert "test" in v.tags
        assert v.parent_version is None

    def test_parent_version_tracking(self, version_manager):
        """Test that parent versions are tracked correctly."""
        version_manager.save_version("01", "V1", "Agent1", "First")
        version_manager.save_version("01", "V2", "Agent2", "Second")

        versions = version_manager.get_chapter_versions("01")
        assert versions[0].parent_version is None
        assert versions[1].parent_version == "v001"

    def test_diff_generation(self, version_manager):
        """Test that diffs are generated between versions."""
        content1 = "# Chapter 1\n\nOriginal content."
        content2 = "# Chapter 1\n\nModified content."

        version_manager.save_version("01", content1, "Agent1", "First")
        version_manager.save_version("01", content2, "Agent2", "Second")

        diff = version_manager.get_diff("01", "v001", "v002")
        assert diff is not None
        assert "-Original content." in diff
        assert "+Modified content." in diff

    def test_tag_version(self, version_manager):
        """Test adding tags to versions."""
        version_manager.save_version("01", "Content", "Agent1", "First")
        version_manager.tag_version("01", "v001", "approved")

        versions = version_manager.get_chapter_versions("01")
        assert "approved" in versions[0].tags

    def test_history_report(self, version_manager):
        """Test generating history report."""
        version_manager.save_version("01", "V1", "Agent1", "First version")
        version_manager.save_version("01", "V2", "Agent2", "Second version")

        report = version_manager.generate_history_report("01")
        assert "Chapter 01" in report
        assert "v001" in report
        assert "v002" in report
        assert "Agent1" in report
        assert "Agent2" in report

    def test_multiple_chapters(self, version_manager):
        """Test managing versions for multiple chapters."""
        version_manager.save_version("01", "Chapter 1 V1", "Agent1", "C1V1")
        version_manager.save_version("02", "Chapter 2 V1", "Agent1", "C2V1")
        version_manager.save_version("01", "Chapter 1 V2", "Agent2", "C1V2")

        c1_versions = version_manager.get_chapter_versions("01")
        c2_versions = version_manager.get_chapter_versions("02")

        assert len(c1_versions) == 2
        assert len(c2_versions) == 1

    def test_get_all_versions(self, version_manager):
        """Test getting all versions across all chapters."""
        version_manager.save_version("01", "C1V1", "Agent1", "Msg1")
        version_manager.save_version("02", "C2V1", "Agent1", "Msg2")
        version_manager.save_version("01", "C1V2", "Agent2", "Msg3")

        all_versions = version_manager.get_all_versions()
        assert len(all_versions) == 3

    def test_nonexistent_version(self, version_manager):
        """Test retrieving nonexistent version returns None."""
        content = version_manager.get_version("99", "v999")
        assert content is None

    def test_empty_chapter_versions(self, version_manager):
        """Test getting versions for chapter with no versions."""
        versions = version_manager.get_chapter_versions("99")
        assert versions == []

    def test_content_hash(self, version_manager):
        """Test that content hashes are generated."""
        version_manager.save_version("01", "Content", "Agent1", "First")
        versions = version_manager.get_chapter_versions("01")

        assert versions[0].content_hash is not None
        assert len(versions[0].content_hash) == 16

    def test_hebrew_content(self, version_manager):
        """Test that Hebrew content is handled correctly."""
        hebrew_content = """# פרק 1: תאים

תאים הם יחידות החיים הבסיסיות.
"""
        version_id = version_manager.save_version(
            "01", hebrew_content, "TestAgent", "Hebrew content test"
        )

        retrieved = version_manager.get_version("01", version_id)
        assert retrieved == hebrew_content
        assert "תאים" in retrieved
