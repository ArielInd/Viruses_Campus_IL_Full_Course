import os
import shutil
from src.downloader import Downloader

hierarchy = [
    {
        "index": 1,
        "title": "Module 1: Getting Started",
        "units": [
            {"index": 1, "title": "Introduction Video", "url": "url1"},
            {"index": 2, "title": "Course Syllabus", "url": "url2"}
        ]
    },
    {
        "index": 2,
        "title": "Module 2: The Virus Structure",
        "units": [
            {"index": 1, "title": "What is a Virus?", "url": "url3"}
        ]
    }
]

output_dir = "test_course_output"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

downloader = Downloader("user", "pass")
downloader.create_directories(hierarchy, output_dir)

print(f"Checking directory structure in '{output_dir}':")
for root, dirs, files in os.walk(output_dir):
    print(f"Folder: {root}")

# Check specifically for a module folder
if os.path.exists(os.path.join(output_dir, "01_Module_1_Getting_Started")):
    print("✅ Module directory created and sanitized correctly.")
else:
    print("❌ Directory creation or sanitization failed.")
