"""
Version Manager: Track and manage versions of chapter drafts and edits.
Provides git-like versioning with diffs and rollback capabilities.
"""

import os
import json
import hashlib
import difflib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class VersionMetadata:
    """Metadata for a single version."""
    version_id: str
    chapter_id: str
    timestamp: str
    agent: str
    message: str
    content_hash: str
    parent_version: Optional[str] = None
    word_count: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class VersionManager:
    """
    Manages versions of chapter content with history tracking.

    Structure:
    /ops/versions/
        ├── metadata.jsonl          # Version history log
        ├── chapters/
        │   ├── chapter_01/
        │   │   ├── v001_draft.md
        │   │   ├── v002_dev_edit.md
        │   │   └── v003_copyedit.md
        │   └── chapter_02/
        └── diffs/
            ├── chapter_01_v001_v002.diff
            └── chapter_01_v002_v003.diff
    """

    def __init__(self, ops_dir: str):
        self.ops_dir = ops_dir
        self.versions_dir = os.path.join(ops_dir, "versions")
        self.chapters_dir = os.path.join(self.versions_dir, "chapters")
        self.diffs_dir = os.path.join(self.versions_dir, "diffs")
        self.metadata_path = os.path.join(self.versions_dir, "metadata.jsonl")

        # Create directories
        os.makedirs(self.chapters_dir, exist_ok=True)
        os.makedirs(self.diffs_dir, exist_ok=True)

    def save_version(self, chapter_id: str, content: str, agent: str,
                     message: str, tags: List[str] = None) -> str:
        """
        Save a new version of a chapter.

        Args:
            chapter_id: Chapter identifier (e.g., "01", "02")
            content: The chapter content (markdown)
            agent: Name of agent creating this version
            message: Commit-style message describing changes
            tags: Optional tags (e.g., ["draft", "reviewed"])

        Returns:
            version_id: Unique identifier for this version
        """
        # Get chapter version history
        versions = self.get_chapter_versions(chapter_id)
        version_num = len(versions) + 1
        version_id = f"v{version_num:03d}"

        # Calculate content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

        # Get parent version
        parent_version = versions[-1].version_id if versions else None

        # Create metadata
        metadata = VersionMetadata(
            version_id=version_id,
            chapter_id=chapter_id,
            timestamp=datetime.now().isoformat(),
            agent=agent,
            message=message,
            content_hash=content_hash,
            parent_version=parent_version,
            word_count=len(content.split()),
            tags=tags or []
        )

        # Save content
        chapter_dir = os.path.join(self.chapters_dir, f"chapter_{chapter_id}")
        os.makedirs(chapter_dir, exist_ok=True)

        # Sanitize agent name for filename
        agent_slug = agent.lower().replace(" ", "_")[:20]
        content_path = os.path.join(chapter_dir, f"{version_id}_{agent_slug}.md")

        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Generate diff if there's a parent version
        if parent_version:
            self._generate_diff(chapter_id, parent_version, version_id)

        # Save metadata
        self._append_metadata(metadata)

        print(f"[VersionManager] Saved {chapter_id} {version_id} by {agent}")

        return version_id

    def get_version(self, chapter_id: str, version_id: str) -> Optional[str]:
        """Retrieve content of a specific version."""
        chapter_dir = os.path.join(self.chapters_dir, f"chapter_{chapter_id}")

        if not os.path.exists(chapter_dir):
            return None

        # Find file matching version_id
        for filename in os.listdir(chapter_dir):
            if filename.startswith(version_id):
                with open(os.path.join(chapter_dir, filename), 'r', encoding='utf-8') as f:
                    return f.read()

        return None

    def get_latest_version(self, chapter_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the latest version of a chapter.

        Returns:
            (version_id, content) or (None, None)
        """
        versions = self.get_chapter_versions(chapter_id)
        if not versions:
            return None, None

        latest = versions[-1]
        content = self.get_version(chapter_id, latest.version_id)
        return latest.version_id, content

    def get_chapter_versions(self, chapter_id: str) -> List[VersionMetadata]:
        """Get all versions for a specific chapter, ordered chronologically."""
        if not os.path.exists(self.metadata_path):
            return []

        versions = []
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if data['chapter_id'] == chapter_id:
                    versions.append(VersionMetadata(**data))

        return sorted(versions, key=lambda v: v.timestamp)

    def get_all_versions(self) -> List[VersionMetadata]:
        """Get all versions across all chapters."""
        if not os.path.exists(self.metadata_path):
            return []

        versions = []
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                versions.append(VersionMetadata(**json.loads(line)))

        return sorted(versions, key=lambda v: v.timestamp)

    def get_diff(self, chapter_id: str, from_version: str, to_version: str) -> Optional[str]:
        """Get diff between two versions."""
        diff_filename = f"chapter_{chapter_id}_{from_version}_{to_version}.diff"
        diff_path = os.path.join(self.diffs_dir, diff_filename)

        if os.path.exists(diff_path):
            with open(diff_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Generate on-the-fly if not cached
        from_content = self.get_version(chapter_id, from_version)
        to_content = self.get_version(chapter_id, to_version)

        if not from_content or not to_content:
            return None

        diff = self._compute_diff(from_content, to_content, from_version, to_version)

        # Cache it
        with open(diff_path, 'w', encoding='utf-8') as f:
            f.write(diff)

        return diff

    def tag_version(self, chapter_id: str, version_id: str, tag: str):
        """Add a tag to a version (e.g., 'approved', 'published')."""
        # Read all metadata
        if not os.path.exists(self.metadata_path):
            return

        updated_lines = []
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if data['chapter_id'] == chapter_id and data['version_id'] == version_id:
                    if tag not in data.get('tags', []):
                        data.setdefault('tags', []).append(tag)
                updated_lines.append(json.dumps(data, ensure_ascii=False) + '\n')

        # Write back
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

    def generate_history_report(self, chapter_id: str) -> str:
        """Generate a human-readable history report for a chapter."""
        versions = self.get_chapter_versions(chapter_id)

        if not versions:
            return f"No versions found for chapter {chapter_id}"

        report = f"# Version History: Chapter {chapter_id}\n\n"
        report += f"Total versions: {len(versions)}\n\n"

        for v in versions:
            report += f"## {v.version_id} - {v.agent}\n"
            report += f"- **Timestamp:** {v.timestamp}\n"
            report += f"- **Message:** {v.message}\n"
            report += f"- **Word count:** {v.word_count}\n"
            if v.tags:
                report += f"- **Tags:** {', '.join(v.tags)}\n"
            report += f"- **Hash:** {v.content_hash}\n"
            report += "\n"

        return report

    def _generate_diff(self, chapter_id: str, from_version: str, to_version: str):
        """Generate and save diff between two versions."""
        from_content = self.get_version(chapter_id, from_version)
        to_content = self.get_version(chapter_id, to_version)

        if not from_content or not to_content:
            return

        diff = self._compute_diff(from_content, to_content, from_version, to_version)

        diff_filename = f"chapter_{chapter_id}_{from_version}_{to_version}.diff"
        diff_path = os.path.join(self.diffs_dir, diff_filename)

        with open(diff_path, 'w', encoding='utf-8') as f:
            f.write(diff)

    def _compute_diff(self, from_content: str, to_content: str,
                      from_label: str, to_label: str) -> str:
        """Compute unified diff between two content strings."""
        from_lines = from_content.splitlines(keepends=True)
        to_lines = to_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=from_label,
            tofile=to_label,
            lineterm=''
        )

        return ''.join(diff)

    def _append_metadata(self, metadata: VersionMetadata):
        """Append metadata to JSONL log."""
        with open(self.metadata_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(metadata), ensure_ascii=False) + '\n')
