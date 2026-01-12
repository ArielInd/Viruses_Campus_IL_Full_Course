import os
import shutil
from src.downloader import Downloader

results = {
    "downloaded": [
        {"title": "Intro", "filename": "01_Intro.txt"},
        {"title": "Basics", "filename": "02_Basics.txt"}
    ],
    "skipped": [
        {"title": "Setup", "filename": "00_Setup.txt"}
    ],
    "failed": [
        {"title": "Advanced Theory"}
    ]
}

output_dir = "test_summary_output"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

downloader = Downloader("user", "pass")
report_path = downloader.generate_summary_report(results, output_dir)

print(f"Checking summary report at '{report_path}':")
with open(report_path, "r", encoding="utf-8") as f:
    print(f.read())

if os.path.exists(report_path):
    print("✅ Summary report generated successfully.")
else:
    print("❌ Summary report generation failed.")
