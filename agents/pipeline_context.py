"""
Pipeline Context Manager: Shared state and caching for the multi-agent pipeline.
Eliminates redundant file loading and provides efficient data access.
"""

import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from functools import lru_cache
import json


@dataclass
class PipelineContext:
    """
    Shared context for all agents in the pipeline.
    Loads common data once and provides cached access.

    Usage:
        context = PipelineContext(ops_dir="/path/to/ops")
        file_notes = context.get_file_notes()  # Cached after first call
        chapter_plan = context.get_chapter_plan()  # Cached
    """

    ops_dir: str
    transcripts_dir: Optional[str] = None
    _file_notes_cache: Optional[Dict[str, Dict]] = field(default=None, init=False, repr=False)
    _corpus_index_cache: Optional[Dict] = field(default=None, init=False, repr=False)
    _chapter_plan_cache: Optional[List[Dict]] = field(default=None, init=False, repr=False)
    _chapter_briefs_cache: Dict[str, Dict] = field(default_factory=dict, init=False, repr=False)
    _compiled_patterns_cache: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        """Initialize context."""
        self.artifacts_dir = os.path.join(self.ops_dir, "artifacts")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.artifacts_dir, exist_ok=True)
        os.makedirs(os.path.join(self.artifacts_dir, "file_notes"), exist_ok=True)
        os.makedirs(os.path.join(self.artifacts_dir, "chapter_briefs"), exist_ok=True)

    def get_file_notes(self, force_reload: bool = False) -> Dict[str, Dict]:
        """
        Get all file notes, cached after first load.

        Args:
            force_reload: If True, bypass cache and reload from disk

        Returns:
            Dictionary mapping file paths to note data
        """
        if self._file_notes_cache is not None and not force_reload:
            return self._file_notes_cache

        notes = {}
        notes_dir = os.path.join(self.artifacts_dir, "file_notes")

        if os.path.exists(notes_dir):
            # Batch load all JSON files
            json_files = [f for f in os.listdir(notes_dir) if f.endswith('.json')]

            for filename in json_files:
                path = os.path.join(notes_dir, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        note = json.load(f)
                        notes[note.get("path", "")] = note
                except Exception as e:
                    print(f"[PipelineContext] Warning: Failed to load {filename}: {e}")

        self._file_notes_cache = notes
        print(f"[PipelineContext] Loaded {len(notes)} file notes (cached)")

        return notes

    def get_corpus_index(self, force_reload: bool = False) -> Dict:
        """
        Get corpus index, cached after first load.

        Args:
            force_reload: If True, bypass cache and reload from disk

        Returns:
            Corpus index dictionary
        """
        if self._corpus_index_cache is not None and not force_reload:
            return self._corpus_index_cache

        index_path = os.path.join(self.artifacts_dir, "corpus_index.json")

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Corpus index not found: {index_path}")

        with open(index_path, 'r', encoding='utf-8') as f:
            self._corpus_index_cache = json.load(f)

        print(f"[PipelineContext] Loaded corpus index (cached)")

        return self._corpus_index_cache

    def get_chapter_plan(self, force_reload: bool = False) -> List[Dict]:
        """
        Get chapter plan, cached after first load.

        Args:
            force_reload: If True, bypass cache and reload from disk

        Returns:
            List of chapter plan dictionaries
        """
        if self._chapter_plan_cache is not None and not force_reload:
            return self._chapter_plan_cache

        plan_path = os.path.join(self.artifacts_dir, "chapter_plan.json")

        if not os.path.exists(plan_path):
            raise FileNotFoundError(f"Chapter plan not found: {plan_path}")

        with open(plan_path, 'r', encoding='utf-8') as f:
            self._chapter_plan_cache = json.load(f)

        print(f"[PipelineContext] Loaded chapter plan ({len(self._chapter_plan_cache)} chapters, cached)")

        return self._chapter_plan_cache

    def get_chapter_brief(self, chapter_id: str, force_reload: bool = False) -> Optional[Dict]:
        """
        Get a specific chapter brief, cached.

        Args:
            chapter_id: Chapter identifier (e.g., "01")
            force_reload: If True, bypass cache

        Returns:
            Chapter brief dictionary or None if not found
        """
        if chapter_id in self._chapter_briefs_cache and not force_reload:
            return self._chapter_briefs_cache[chapter_id]

        brief_path = os.path.join(
            self.artifacts_dir,
            "chapter_briefs",
            f"chapter_{chapter_id}_brief.json"
        )

        if not os.path.exists(brief_path):
            return None

        with open(brief_path, 'r', encoding='utf-8') as f:
            brief = json.load(f)
            self._chapter_briefs_cache[chapter_id] = brief

        return brief

    def get_all_chapter_briefs(self, force_reload: bool = False) -> Dict[str, Dict]:
        """
        Get all chapter briefs, cached.

        Returns:
            Dictionary mapping chapter IDs to brief data
        """
        briefs_dir = os.path.join(self.artifacts_dir, "chapter_briefs")

        if not os.path.exists(briefs_dir):
            return {}

        # Load all briefs
        json_files = [f for f in os.listdir(briefs_dir) if f.endswith('_brief.json')]

        for filename in json_files:
            # Extract chapter ID from filename (e.g., "chapter_01_brief.json" -> "01")
            chapter_id = filename.split('_')[1]

            if chapter_id not in self._chapter_briefs_cache or force_reload:
                self.get_chapter_brief(chapter_id, force_reload)

        return self._chapter_briefs_cache

    def get_compiled_pattern(self, pattern_name: str, pattern: str, flags: int = 0):
        """
        Get a compiled regex pattern, cached.

        Args:
            pattern_name: Unique name for this pattern
            pattern: Regex pattern string
            flags: Regex flags (e.g., re.IGNORECASE)

        Returns:
            Compiled regex pattern object
        """
        cache_key = f"{pattern_name}_{flags}"

        if cache_key not in self._compiled_patterns_cache:
            self._compiled_patterns_cache[cache_key] = re.compile(pattern, flags)

        return self._compiled_patterns_cache[cache_key]

    def get_compiled_patterns(self, patterns: Dict[str, str], flags: int = 0) -> Dict[str, Any]:
        """
        Get multiple compiled patterns at once.

        Args:
            patterns: Dictionary mapping pattern names to pattern strings
            flags: Regex flags to apply to all

        Returns:
            Dictionary mapping pattern names to compiled patterns
        """
        return {
            name: self.get_compiled_pattern(name, pattern, flags)
            for name, pattern in patterns.items()
        }

    def save_artifact(self, filename: str, content: Any, format: str = "json"):
        """
        Save an artifact to the artifacts directory.

        Args:
            filename: Name of file to save
            content: Content to save
            format: "json" or "text"
        """
        path = os.path.join(self.artifacts_dir, filename)

        if format == "json":
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

    def invalidate_cache(self, cache_name: Optional[str] = None):
        """
        Invalidate cached data.

        Args:
            cache_name: Specific cache to invalidate, or None for all
        """
        if cache_name is None or cache_name == "file_notes":
            self._file_notes_cache = None
            print("[PipelineContext] Invalidated file_notes cache")

        if cache_name is None or cache_name == "corpus_index":
            self._corpus_index_cache = None
            print("[PipelineContext] Invalidated corpus_index cache")

        if cache_name is None or cache_name == "chapter_plan":
            self._chapter_plan_cache = None
            print("[PipelineContext] Invalidated chapter_plan cache")

        if cache_name is None or cache_name == "chapter_briefs":
            self._chapter_briefs_cache.clear()
            print("[PipelineContext] Invalidated chapter_briefs cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about cached data.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "file_notes_cached": self._file_notes_cache is not None,
            "file_notes_count": len(self._file_notes_cache) if self._file_notes_cache else 0,
            "corpus_index_cached": self._corpus_index_cache is not None,
            "chapter_plan_cached": self._chapter_plan_cache is not None,
            "chapter_plan_count": len(self._chapter_plan_cache) if self._chapter_plan_cache else 0,
            "chapter_briefs_count": len(self._chapter_briefs_cache),
            "compiled_patterns_count": len(self._compiled_patterns_cache)
        }

    def __repr__(self):
        """String representation."""
        stats = self.get_cache_stats()
        return (
            f"PipelineContext(\n"
            f"  ops_dir='{self.ops_dir}',\n"
            f"  file_notes: {stats['file_notes_count']} loaded,\n"
            f"  chapter_plan: {stats['chapter_plan_count']} chapters,\n"
            f"  briefs: {stats['chapter_briefs_count']} cached,\n"
            f"  patterns: {stats['compiled_patterns_count']} compiled\n"
            f")"
        )


# Global context singleton (optional convenience)
_global_context: Optional[PipelineContext] = None


def get_global_context(ops_dir: Optional[str] = None) -> PipelineContext:
    """
    Get or create the global pipeline context singleton.

    Args:
        ops_dir: Operations directory path (required on first call)

    Returns:
        Global PipelineContext instance
    """
    global _global_context

    if _global_context is None:
        if ops_dir is None:
            raise ValueError("ops_dir required for first call to get_global_context()")
        _global_context = PipelineContext(ops_dir=ops_dir)

    return _global_context


def reset_global_context():
    """Reset the global context singleton."""
    global _global_context
    _global_context = None
