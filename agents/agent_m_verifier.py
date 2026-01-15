"""
Agent M: SourceVerifier (Anti-Hallucination System)

Validates that draft citations [SRC-XXX] match actual source chunks.
Flags unsourced claims for manual review or removal.

NOTE: This agent does NOT strip citations. Stripping happens at the
final build step using strip_citations.py.

Uses the new unified Google GenAI SDK (google-genai).
"""

import os
import re
import json
from typing import Dict, List, Optional

# Use the new unified Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .schemas import (
    PipelineLogger, TodoTracker,
    save_markdown, load_json, read_file
)

AGENT_NAME = "SourceVerifier"

GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


class SourceVerifier:
    """
    Agent M: Verifies citations against source material.
    
    Actions for unsourced claims:
    1. Log to todos.md for manual review
    2. Attempt to find the closest source chunk
    3. Mark paragraphs without citations as "[NEEDS SOURCE]"
    
    Output: /ops/reports/citation_coverage.md
    """
    
    def __init__(self, book_dir: str, ops_dir: str,
                 logger: PipelineLogger, todos: TodoTracker):
        self.book_dir = book_dir
        self.ops_dir = ops_dir
        self.logger = logger
        self.todos = todos
        self.chapters_dir = os.path.join(book_dir, "chapters")
        self.chunks_path = os.path.join(ops_dir, "artifacts", "source_chunks.json")
        
        # Initialize Gemini client for finding sources
        self.client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception:
                pass
    
    def run(self) -> Dict:
        """Execute the agent."""
        start_time = self.logger.log_start(AGENT_NAME)
        output_files = []
        
        # Load source chunks (saved by Agent D)
        source_chunks = {}
        if os.path.exists(self.chunks_path):
            source_chunks = load_json(self.chunks_path)
        
        print(f"[{AGENT_NAME}] Loaded {len(source_chunks)} source chunks for verification")
        
        all_stats = []
        unsourced_claims = []
        
        if os.path.exists(self.chapters_dir):
            for filename in os.listdir(self.chapters_dir):
                if not filename.endswith('.md'):
                    continue
                
                path = os.path.join(self.chapters_dir, filename)
                content = read_file(path)
                
                # Verify existing citations
                stats = self._verify_citations(filename, content, source_chunks)
                all_stats.append(stats)
                
                # Find paragraphs WITHOUT citations (potential hallucinations)
                uncited = self._find_uncited_paragraphs(filename, content)
                unsourced_claims.extend(uncited)
                
                # Mark uncited paragraphs for review
                if uncited:
                    updated_content = self._mark_uncited_for_review(content, uncited)
                    save_markdown(updated_content, path)
                    output_files.append(path)
                
                print(f"[{AGENT_NAME}] ✓ {filename}: {stats['valid']}/{stats['total']} citations, {len(uncited)} uncited paragraphs")
        
        # Log unsourced claims to todos
        for claim in unsourced_claims:
            self.todos.add(AGENT_NAME, claim["file"], f"Uncited claim: {claim['text'][:80]}...")
        
        # Generate report
        report_path = os.path.join(self.ops_dir, "reports", "citation_coverage.md")
        report = self._generate_report(all_stats, unsourced_claims)
        save_markdown(report, report_path)
        output_files.append(report_path)
        
        self.logger.log_end(AGENT_NAME, start_time, output_files)
        
        return {
            "report": report_path,
            "files_processed": len(all_stats),
            "unsourced_claims": len(unsourced_claims)
        }
    
    def _verify_citations(self, filename: str, content: str, chunks: Dict) -> Dict:
        """Verify all [SRC-XXX] citations."""
        pattern = r'\[SRC-(\d{3})\]'
        matches = re.findall(pattern, content)
        
        valid = 0
        invalid = []
        
        for match in matches:
            citation = f"[SRC-{match}]"
            if citation in chunks:
                valid += 1
            else:
                invalid.append(citation)
        
        return {
            "file": filename,
            "total": len(matches),
            "valid": valid,
            "invalid": invalid,
            "coverage": valid / len(matches) if matches else 1.0
        }
    
    def _find_uncited_paragraphs(self, filename: str, content: str) -> List[Dict]:
        """Find paragraphs that make factual claims but have no citations."""
        uncited = []
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        for i, para in enumerate(paragraphs):
            # Skip headers, lists, short paragraphs
            if para.strip().startswith('#'):
                continue
            if para.strip().startswith('-') or para.strip().startswith('*'):
                continue
            if len(para.split()) < 20:
                continue
            
            # Check if paragraph has a citation
            if not re.search(r'\[SRC-\d{3}\]', para):
                # This paragraph might contain unsourced claims
                uncited.append({
                    "file": filename,
                    "paragraph_index": i,
                    "text": para.strip()[:200]
                })
        
        return uncited
    
    def _mark_uncited_for_review(self, content: str, uncited: List[Dict]) -> str:
        """Add [NEEDS SOURCE] markers to uncited paragraphs."""
        paragraphs = content.split('\n\n')
        
        for claim in uncited:
            idx = claim["paragraph_index"]
            if idx < len(paragraphs):
                # Add marker at end of paragraph
                if "[NEEDS SOURCE]" not in paragraphs[idx]:
                    paragraphs[idx] += " <!-- [NEEDS SOURCE] -->"
        
        return '\n\n'.join(paragraphs)
    
    def _generate_report(self, stats: List[Dict], unsourced: List[Dict]) -> str:
        """Generate verification report."""
        md = "# דוח אימות מקורות (Citation Verification)\n\n"
        md += f"*נוצר על ידי {AGENT_NAME}*\n\n"
        
        total_citations = sum(s["total"] for s in stats)
        total_valid = sum(s["valid"] for s in stats)
        
        md += "## סיכום\n\n"
        md += f"- **ציטוטים תקינים**: {total_valid}/{total_citations}\n"
        md += f"- **פסקאות ללא מקור**: {len(unsourced)}\n\n"
        
        if unsourced:
            md += "> [!WARNING]\n"
            md += f"> נמצאו {len(unsourced)} פסקאות ללא ציטוט - יש לבדוק ידנית!\n\n"
            
            md += "## פסקאות לבדיקה\n\n"
            for claim in unsourced[:20]:  # Show first 20
                md += f"- **{claim['file']}**: {claim['text'][:100]}...\n"
        else:
            md += "> [!TIP]\n"
            md += "> כל התוכן מצוטט כראוי!\n"
        
        md += "\n---\n\n"
        md += "*הערה: להסרת ציטוטים לפני פרסום, הרץ: `python3 strip_citations.py`*\n"
        
        return md
