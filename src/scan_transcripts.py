import os
from pathlib import Path

def scan_directory(root_path):
    """
    Recursively scans the directory for .txt files.
    Returns a list of dictionaries containing filename, full path, and extracted metadata.
    """
    root = Path(root_path)
    results = []
    
    # Sort to ensure consistent order (though os.walk order isn't guaranteed, we sort after)
    for path in sorted(root.rglob('*.txt')):
        content = path.read_text(encoding='utf-8', errors='replace')
        metadata = analyze_file_content(content)
        
        results.append({
            'filename': path.name,
            'path': str(path),
            'parent_dir': path.parent.name,
            'metadata': metadata
        })
        
    return results

def analyze_file_content(content):
    """
    Analyzes the content of a transcript file to extract key info.
    For now, returns a simple summary (first non-empty line).
    """
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    summary = lines[0] if lines else "No content"
    
    return {
        'summary': summary,
        'length': len(content)
    }

if __name__ == "__main__":
    # Example usage (can be run directly to test on real data)
    import json
    real_path = "course_transcripts"
    if os.path.exists(real_path):
        data = scan_directory(real_path)
        print(json.dumps(data[:3], indent=2, ensure_ascii=False))
