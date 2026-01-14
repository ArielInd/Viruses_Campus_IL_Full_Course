#!/usr/bin/env python3
import json
import glob
from pathlib import Path

CHAPTERS_DIR = Path("book/chapters")
CLAIMS_FILE = Path("ops/artifacts/claims.jsonl")
TRACEABILITY_FILE = Path("ops/artifacts/traceability.json")
REPORT_FILE = Path("ops/reports/verification_report.md")

def main():
    report = "# Verification Report\n\n"
    
    # 1. Check Claims
    claim_count = 0
    if CLAIMS_FILE.exists():
        with open(CLAIMS_FILE, 'r', encoding='utf-8') as f:
            claim_count = sum(1 for _ in f)
    report += f"- **Total Claims Extracted:** {claim_count}\n"
    
    # 2. Check Traceability
    traceability = {}
    if TRACEABILITY_FILE.exists():
        with open(TRACEABILITY_FILE, 'r', encoding='utf-8') as f:
            traceability = json.load(f)
    report += f"- **Chapters Generated:** {len(traceability)}\n\n"
    
    # 3. Chapter Analysis
    report += "## Chapter Traceability\n\n"
    chapters = sorted(list(CHAPTERS_DIR.glob("*.md")))
    
    total_issues = 0
    
    for chap in chapters:
        chap_id = chap.stem.split('_')[0]
        report += f"### {chap.name}\n"
        
        # Check size
        size = chap.stat().st_size
        report += f"- Size: {size} bytes\n"
        
        # Check traceability entry
        if chap_id in traceability:
            claims_used = len(traceability[chap_id].get("claims_used", []))
            report += f"- Claims Cited: {claims_used}\n"
            transcripts = len(traceability[chap_id].get("transcripts", []))
            report += f"- Source Transcripts: {transcripts}\n"
        else:
            report += "- ⚠️ **No traceability record found.**\n"
            total_issues += 1
            
        report += "\n"
        
    report += "---\n"
    if total_issues == 0 and len(chapters) > 0:
        report += "**Status: ✅ VERIFIED**\n"
    else:
        report += f"**Status: ⚠️ ISSUES FOUND ({total_issues})**\n"
        
    # Write report
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Wrote verification report to {REPORT_FILE}")

if __name__ == "__main__":
    main()
