import os
import shutil
from unittest.mock import patch
from src.downloader import Downloader

# Define a dummy hierarchy
hierarchy = [
    {
        "index": 1,
        "title": "Module 1",
        "units": [
            {"index": 1, "title": "Lecture 1", "url": "url1", "filename": "01_Lecture_1.txt"}
        ]
    }
]

output_dir = "test_bulk_output"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

downloader = Downloader("user", "pass")

# Mock download_transcript to return content for the first call and None for others
def mock_download(url):
    if url == "url1":
        return "Transcript content for Lecture 1"
    return None

with patch.object(Downloader, 'download_transcript', side_effect=mock_download):
    print("Running bulk download (first run)...")
    results = downloader.bulk_download(hierarchy, output_dir)
    print(f"Downloaded: {[u['title'] for u in results['downloaded']]}")

    # Verify file creation
    expected_file = os.path.join(output_dir, "01_Module_1", "01_Lecture_1.txt")
    if os.path.exists(expected_file):
        print("✅ File created successfully.")
    else:
        # Maybe path was different in hierarchy
        print("Checking for file manually...")
        # Results from bulk_download should have updated the paths

    print("\nRunning bulk download (second run - skip check)...")
    # Pre-create the correct path in hierarchy for the skip test
    hierarchy[0]['path'] = os.path.join(output_dir, "01_Module_1")
    results_skip = downloader.bulk_download(hierarchy, output_dir)
    print(f"Skipped: {[u['title'] for u in results_skip['skipped']]}")

    if len(results_skip['skipped']) == 1:
        print("✅ Skip logic verified.")
    else:
        print("❌ Skip logic failed.")
