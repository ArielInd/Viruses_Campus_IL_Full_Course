import pytest
import os
from unittest.mock import MagicMock, patch
from src.downloader import Downloader

@pytest.fixture
def temp_output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return str(d)

def test_download_transcript_success(mocker):
    """Verify that transcript is downloaded correctly."""
    downloader = Downloader(username="user", password="pass")
    mock_page = MagicMock()
    downloader.page = mock_page
    
    # Mock finding a transcript link
    mock_link = MagicMock()
    mock_link.get_attribute.return_value = "https://example.com/transcript.txt"
    mock_page.query_selector.return_value = mock_link
    
    with patch.object(Downloader, '_download_file_from_url', return_value="Transcript content"):
        content = downloader.download_transcript("https://campus.gov.il/unit/1")
        assert content == "Transcript content"
        mock_page.goto.assert_called_with("https://campus.gov.il/unit/1")

def test_download_transcript_not_found(mocker):
    """Verify handling when no transcript link is found."""
    downloader = Downloader(username="user", password="pass")
    mock_page = MagicMock()
    downloader.page = mock_page
    
    mock_page.query_selector.return_value = None
    
    content = downloader.download_transcript("https://campus.gov.il/unit/1")
    assert content is None

def test_save_transcript(temp_output_dir):
    """Verify that transcript is saved correctly to disk."""
    downloader = Downloader(username="user", password="pass")
    content = "Hello, this is a transcript."
    filename = "01_Test.txt"
    
    file_path = downloader.save_transcript(content, temp_output_dir, filename)
    
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content