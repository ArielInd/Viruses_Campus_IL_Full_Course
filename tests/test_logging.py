import logging
import os
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

def test_generate_summary_report(tmp_path):
    """Verify that summary.txt is generated correctly."""
    downloader = Downloader(username="user", password="pass")
    output_dir = str(tmp_path)
    results = {
        "downloaded": [{"title": "Unit 1", "filename": "01_Unit_1.txt"}],
        "skipped": [{"title": "Unit 2", "filename": "02_Unit_2.txt"}],
        "failed": [{"title": "Unit 3", "filename": "03_Unit_3.txt"}]
    }
    
    report_path = downloader.generate_summary_report(results, output_dir)
    
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Downloaded: 1" in content
        assert "Skipped: 1" in content
        assert "Failed: 1" in content
        assert "Unit 1" in content
        assert "Unit 2" in content
        assert "Unit 3" in content
