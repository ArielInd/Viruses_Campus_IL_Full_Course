import json
from pathlib import Path
import pytest
from src.generate_manifest import generate_book_manifest

def test_generate_book_manifest_structure(tmp_path):
    # Mock scan data
    scan_data = [
        {'filename': '01_intro.txt', 'parent_dir': '03_שיעור_1', 'path': 'path/to/01_intro.txt'},
        {'filename': '01_dna.txt', 'parent_dir': '04_שיעור_2', 'path': 'path/to/01_dna.txt'}
    ]
    
    manifest = generate_book_manifest(scan_data)
    
    assert 'title' in manifest
    assert 'chapters' in manifest
    assert len(manifest['chapters']) >= 2
    
    # Check chapter 1
    chap1 = next(c for c in manifest['chapters'] if '1' in c['id'])
    assert len(chap1['sources']) == 1
    assert chap1['sources'][0]['filename'] == '01_intro.txt'

def test_generate_manifest_file_creation(tmp_path):
    # Test writing to file
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    
    scan_data = []
    from src.generate_manifest import save_manifest
    save_manifest(book_dir, {'title': 'Test Book'})
    
    assert (book_dir / "manifest.json").exists()
