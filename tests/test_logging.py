import logging
from src.downloader import Downloader

def test_logging_bulk_download(caplog, mocker):
    """Verify that progress is logged during bulk download."""
    downloader = Downloader(username="user", password="pass")
    hierarchy = [
        {
            "index": 1,
            "title": "Module 1",
            "units": [
                {"index": 1, "title": "Unit 1", "url": "url1", "filename": "01_Unit_1.txt"}
            ]
        }
    ]
    
    # Mock download_transcript to return something
    mocker.patch.object(Downloader, "download_transcript", return_value="content")
    mocker.patch.object(Downloader, "save_transcript")
    mocker.patch("os.path.exists", return_value=False)
    
    with caplog.at_level(logging.INFO):
        downloader.bulk_download(hierarchy, "output")
        
    assert "Downloading: 01_Unit_1.txt" in caplog.text
    assert "Successfully downloaded: Unit 1" in caplog.text

def test_logging_bulk_download_failed(caplog, mocker):
    """Verify that failure is logged during bulk download."""
    downloader = Downloader(username="user", password="pass")
    hierarchy = [
        {
            "index": 1,
            "title": "Module 1",
            "units": [
                {"index": 1, "title": "Unit 1", "url": "url1", "filename": "01_Unit_1.txt"}
            ]
        }
    ]
    
    # Mock download_transcript to return None
    mocker.patch.object(Downloader, "download_transcript", return_value=None)
    mocker.patch("os.path.exists", return_value=False)
    
    with caplog.at_level(logging.ERROR):
        downloader.bulk_download(hierarchy, "output")
        
    assert "Failed to download: Unit 1" in caplog.text