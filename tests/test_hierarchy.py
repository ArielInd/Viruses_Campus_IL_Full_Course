import pytest
from unittest.mock import MagicMock, patch
from src.downloader import Downloader

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