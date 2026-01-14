import json
from pathlib import Path

def generate_book_manifest(scan_data):
    """
    Generates the book manifest structure from scan results.
    """
    manifest = {
        "title": "Viruses: From Molecular Biology to Pandemics",
        "language": "he",
        "chapters": []
    }
    
    # Group by parent directory
    grouped = {}
    for item in scan_data:
        parent = item.get('parent_dir', 'Unknown')
        if parent not in grouped:
            grouped[parent] = []
        grouped[parent].append(item)
    
    # Sort groups by name (assuming numbered folders like 03_..., 04_...)
    sorted_groups = sorted(grouped.keys())
    
    chapter_map = {
        '03_שיעור_1': {'id': '01', 'title': 'Introduction & The Cell'},
        '04_שיעור_2': {'id': '02', 'title': 'Macromolecules & DNA'},
        '05_שיעור_3': {'id': '03', 'title': 'Viruses: Structure & Function'},
        '06_שיעור_4': {'id': '04', 'title': 'Human Viral Diseases'},
        '08_שיעור_5': {'id': '05', 'title': 'Innate Immunity'},
        '09_שיעור_6': {'id': '06', 'title': 'Adaptive Immunity'},
        '10_שיעור_7': {'id': '07', 'title': 'Vaccines'},
        '11_שיעור_8': {'id': '08', 'title': 'Coronaviruses & COVID-19'}
    }
    
    for group_name in sorted_groups:
        # Check if it maps to a chapter
        # Basic matching: check if group_name starts with known prefix or is in map
        chap_info = None
        for key in chapter_map:
            if key in group_name:
                chap_info = chapter_map[key]
                break
        
        if chap_info:
            chapter = {
                "id": chap_info['id'],
                "title": chap_info['title'],
                "directory": group_name,
                "sources": sorted(grouped[group_name], key=lambda x: x['filename'])
            }
            manifest['chapters'].append(chapter)
        else:
            # Handle unmapped (Intro, etc.) - maybe add as special sections later
            pass
            
    return manifest

def save_manifest(book_dir, manifest):
    path = Path(book_dir) / "manifest.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    from src.scan_transcripts import scan_directory
    scan_data = scan_directory("course_transcripts")
    manifest = generate_book_manifest(scan_data)
    save_manifest("book", manifest)
    print("Manifest generated.")
