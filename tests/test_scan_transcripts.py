import os
import shutil
import tempfile
from pathlib import Path
import pytest
from src.scan_transcripts import scan_directory, analyze_file_content

@pytest.fixture
def mock_transcripts_dir():
    # Create a temporary directory structure mimicking the real one
    with tempfile.TemporaryDirectory() as tmpdirname:
        base_dir = Path(tmpdirname)
        
        # Create lesson directories
        lesson1 = base_dir / "03_שיעור_1"
        lesson1.mkdir()
        (lesson1 / "01_intro.txt").write_text("Introduction to cells.\nMain claim: Cells are the unit of life.")
        (lesson1 / "02_water.txt").write_text("Water is essential.\nDefinition: H2O.")
        
        lesson2 = base_dir / "04_שיעור_2"
        lesson2.mkdir()
        (lesson2 / "01_dna.txt").write_text("DNA structure.\nMechanism: Replication.")
        
        yield base_dir

def test_scan_directory_finds_all_txt_files(mock_transcripts_dir):
    results = scan_directory(mock_transcripts_dir)
    assert len(results) == 3
    
    filenames = [r['filename'] for r in results]
    assert "01_intro.txt" in filenames
    assert "02_water.txt" in filenames
    assert "01_dna.txt" in filenames

def test_analyze_file_content_extracts_basics():
    content = "Introduction to cells.\nMain claim: Cells are the unit of life."
    metadata = analyze_file_content(content)
    assert isinstance(metadata, dict)
    assert 'summary' in metadata
    # For now, we expect a simple extraction or just the content being processed
    assert "Cells" in metadata['summary'] or "Introduction" in metadata['summary']
