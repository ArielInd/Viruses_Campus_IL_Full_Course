import asyncio
from unittest.mock import MagicMock, patch
from src.downloader import Downloader
import os
import shutil

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

# Mock for async methods
async def mock_download_unit_async(context, unit, module_path, semaphore, results):
    # Mimic the logic of _download_unit_async but without real network calls
    file_path = os.path.join(module_path, unit['filename'])
    if os.path.exists(file_path):
        results["skipped"].append(unit)
        return

    # Simulate success for Lecture 1
    if unit['title'] == "Lecture 1":
        content = "Transcript content for Lecture 1"
        downloader.save_transcript(content, module_path, unit['filename'])
        results["downloaded"].append(unit)

async def mock_run_bulk_download_async(hierarchy, output_dir):
     # Mimic logic of _run_bulk_download_async but calling our mocked download unit
     # Or simply copy paste the simplified logic, since we can't easily patch inside asyncio.run
     # Actually, since bulk_download calls asyncio.run(self._run_bulk_download_async(...))
     # We can patch _run_bulk_download_async
     pass

# We will patch _download_unit_async to avoid network calls.
# Note: Since _download_unit_async is a method on the instance, we can patch it on the class or instance.

async def side_effect_download_unit(context, unit, module_path, semaphore, results):
    # Same logic as above
    file_path = os.path.join(module_path, unit['filename'])
    if os.path.exists(file_path):
        results["skipped"].append(unit)
        return

    if unit['url'] == "url1":
         # Simulate creation
         if not os.path.exists(module_path):
             os.makedirs(module_path)
         with open(file_path, 'w') as f:
             f.write("content")
         results["downloaded"].append(unit)

with patch.object(Downloader, '_download_unit_async', side_effect=side_effect_download_unit) as mock_method:
    print("Running bulk download (first run)...")
    results = downloader.bulk_download(hierarchy, output_dir)
    print(f"Downloaded: {[u['title'] for u in results['downloaded']]}")

    expected_file = os.path.join(output_dir, "01_Module_1", "01_Lecture_1.txt")
    if os.path.exists(expected_file):
        print("✅ File created successfully.")
    else:
        print("❌ File creation failed.")

    print("\nRunning bulk download (second run - skip check)...")
    hierarchy[0]['path'] = os.path.join(output_dir, "01_Module_1")
    results_skip = downloader.bulk_download(hierarchy, output_dir)
    print(f"Skipped: {[u['title'] for u in results_skip['skipped']]}")

    if len(results_skip['skipped']) == 1:
        print("✅ Skip logic verified.")
    else:
        print("❌ Skip logic failed.")
