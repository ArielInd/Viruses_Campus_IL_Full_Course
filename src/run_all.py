#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from pathlib import Path

# Steps configuration
STEPS = [
    {"name": "Step 2: Ingest", "script": "src/ingest.py", "args": []},
    {"name": "Step 3: Extract", "script": "src/extract.py", "args": []},
    {"name": "Step 4: Plan", "script": "src/plan.py", "args": []},
    {"name": "Step 6: Write Chapters", "script": "src/write_book.py", "args": []},
    {"name": "Step 8: Consistency", "script": "src/consistency.py", "args": []},
    {"name": "Step 9: Extras", "script": "src/assemble_extras.py", "args": []},
    {"name": "Step 7: Verify", "script": "src/verify.py", "args": []},
    {"name": "Step 10: Build PDF", "script": "book/build_pdf.sh", "args": []},
]

LOG_FILE = Path("ops/logs/pipeline.jsonl")

def log_event(event_type, details):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        import json
        f.write(json.dumps({
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }) + "\n")

def run_step(step):
    print(f"\n[RUNNER] Starting {step['name']}...")
    log_event("step_start", {"step": step['name']})
    
    start_time = time.time()
    
    cmd = [step['script']] + step['args']
    
    # Handle permissions - ensure executable or use interpreter
    if step['script'].endswith('.py'):
        cmd = [sys.executable, step['script']] + step['args']
    elif step['script'].endswith('.sh'):
        cmd = ["bash", step['script']] + step['args']
        
    try:
        # Pass through environment variables
        env = os.environ.copy()
        
        result = subprocess.run(
            cmd,
            env=env,
            check=True,
            text=True
        )
        
        duration = time.time() - start_time
        print(f"[RUNNER] Finished {step['name']} in {duration:.2f}s")
        log_event("step_success", {"step": step['name'], "duration": duration})
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[RUNNER] Step {step['name']} failed with code {e.returncode}")
        log_event("step_failed", {"step": step['name'], "code": e.returncode})
        # Determine if we should stop. For rigorous pipeline, yes.
        # But extraction might be partial.
        if step['name'] == "Step 3: Extract":
            print("[RUNNER] Extraction might be partial or failed. Checking chunks...")
            # We allow proceeding if some claims exist
            if Path("ops/artifacts/claims.jsonl").exists():
                 print("[RUNNER] Continuing with available claims.")
                 return True
        return False

def main():
    print("=== Evidence-First Virology Ebook Pipeline ===")
    
    # Check env
    if "GEMINI_API_KEY" not in os.environ:
        print("Warning: GEMINI_API_KEY not found in environment.")
        # Attempt to load from .env? (handled by scripts usually)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    for step in STEPS:
        success = run_step(step)
        if not success:
            print("[RUNNER] Pipeline halted due to failure.")
            sys.exit(1)
            
    print("\n=== Pipeline Complete ===")
    
    # Final Summary
    if Path("book/build/book.pdf").exists():
        print("PDF created: book/build/book.pdf")
    else:
        print("PDF creation skipped/failed.")

if __name__ == "__main__":
    main()
