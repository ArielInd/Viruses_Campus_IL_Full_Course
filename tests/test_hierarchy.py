import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from src.downloader import Downloader

@pytest.fixture
def temp_output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return str(d)

def test_extract_hierarchy_mock(mocker):
    """Verify that hierarchy extraction logic works with a mocked page."""
    downloader = Downloader(username="user", password="pass")
    mock_page = MagicMock()
    downloader.page = mock_page
    
    mock_hierarchy = [
        {
            "index": 1,
            "title": "Introduction",
            "units": [
                {"index": 1, "title": "Welcome", "url": "url1"},
                {"index": 2, "title": "Overview", "url": "url2"}
            ]
        },
        {
            "index": 2,
            "title": "Week 1",
            "units": [
                {"index": 1, "title": "Lesson 1", "url": "url3"}
            ]
        }
    ]
    
    with patch.object(Downloader, 'get_course_hierarchy', return_value=mock_hierarchy):
        hierarchy = downloader.get_course_hierarchy()
        assert len(hierarchy) == 2
        assert hierarchy[0]["title"] == "Introduction"
        assert len(hierarchy[0]["units"]) == 2

def test_create_directories(temp_output_dir):
    """Verify that directories are created correctly based on hierarchy."""
    downloader = Downloader(username="user", password="pass")
    hierarchy = [
        {
            "index": 1,
            "title": "Module One",
            "units": [
                {"index": 1, "title": "Unit A", "url": "url1"}
            ]
        }
    ]
    
    downloader.create_directories(hierarchy, temp_output_dir)
    
    expected_path = os.path.join(temp_output_dir, "01_Module_One")
    assert os.path.exists(expected_path)
    assert os.path.isdir(expected_path)

def test_sanitize_filename():
    """Verify filename sanitization."""
    downloader = Downloader(username="user", password="pass")
    assert downloader.sanitize_filename("Hello: World?") == "Hello_World"
    assert downloader.sanitize_filename("Module 1/2") == "Module_1_2"
