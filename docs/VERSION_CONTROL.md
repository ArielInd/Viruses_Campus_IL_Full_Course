# Version Control System

The ebook pipeline includes a built-in version control system for tracking changes to chapter content across the editing pipeline.

## Overview

The `VersionManager` provides git-like versioning capabilities:
- **Version history** - All chapter revisions are saved and tracked
- **Diffs** - Changes between versions are computed and cached
- **Metadata** - Each version includes agent, timestamp, message, tags
- **Rollback** - Previous versions can be retrieved at any time

## Directory Structure

```
/ops/versions/
├── metadata.jsonl          # Version history log (append-only)
├── chapters/
│   ├── chapter_01/
│   │   ├── v001_draftwriter.md
│   │   ├── v002_dev_editor.md
│   │   └── v003_copyeditor.md
│   └── chapter_02/
│       └── v001_draftwriter.md
└── diffs/
    ├── chapter_01_v001_v002.diff
    └── chapter_01_v002_v003.diff
```

## Usage

### In Agent Code

```python
from agents.version_manager import VersionManager

# Initialize
version_mgr = VersionManager(ops_dir="/path/to/ops")

# Save a new version
version_id = version_mgr.save_version(
    chapter_id="01",
    content=chapter_markdown,
    agent="DraftWriter",
    message="Initial draft from transcripts",
    tags=["draft"]
)
# Returns: "v001"

# Get latest version
version_id, content = version_mgr.get_latest_version("01")

# Get specific version
content = version_mgr.get_version("01", "v002")

# Get version history
versions = version_mgr.get_chapter_versions("01")
for v in versions:
    print(f"{v.version_id}: {v.message} by {v.agent}")

# Get diff between versions
diff = version_mgr.get_diff("01", "v001", "v002")
print(diff)

# Tag a version (e.g., as approved)
version_mgr.tag_version("01", "v003", "approved")

# Generate history report
report = version_mgr.generate_history_report("01")
```

### Command Line Usage

```bash
# View version history for a chapter
python -c "
from agents.version_manager import VersionManager
vm = VersionManager('ops')
print(vm.generate_history_report('01'))
"

# View diff between versions
python -c "
from agents.version_manager import VersionManager
vm = VersionManager('ops')
print(vm.get_diff('01', 'v001', 'v002'))
"

# Get all versions across all chapters
python -c "
from agents.version_manager import VersionManager
vm = VersionManager('ops')
versions = vm.get_all_versions()
for v in versions:
    print(f'{v.chapter_id} {v.version_id}: {v.message}')
"
```

## Version Metadata

Each version includes:
- `version_id` - Sequential identifier (v001, v002, ...)
- `chapter_id` - Chapter number ("01", "02", ...)
- `timestamp` - ISO 8601 timestamp
- `agent` - Name of agent that created this version
- `message` - Commit-style message describing changes
- `content_hash` - SHA256 hash (first 16 chars) for integrity
- `parent_version` - Previous version ID (for history chain)
- `word_count` - Total words in this version
- `tags` - List of tags (e.g., ["draft", "reviewed", "approved"])

## Integration with Agents

### Agent D (DraftWriter)
```python
# Save initial draft
version_id = self.version_manager.save_version(
    chapter_id=chapter_id,
    content=draft_content,
    agent=AGENT_NAME,
    message=f"Initial draft for {chapter_title}",
    tags=["draft"]
)
```

### Agent E (DevelopmentalEditor)
```python
# Get latest version
_, content = self.version_manager.get_latest_version(chapter_id)

# Make edits...
edited_content = self.edit_chapter(content)

# Save edited version
version_id = self.version_manager.save_version(
    chapter_id=chapter_id,
    content=edited_content,
    agent=AGENT_NAME,
    message="Improved structure and flow",
    tags=["dev_edited"]
)
```

### Agent H (Copyeditor)
```python
# Save final version
version_id = self.version_manager.save_version(
    chapter_id=chapter_id,
    content=final_content,
    agent=AGENT_NAME,
    message="Final copyedit - fixed typos and grammar",
    tags=["copyedited", "ready_for_review"]
)

# Tag as approved after review
self.version_manager.tag_version(chapter_id, version_id, "approved")
```

## Diff Format

Diffs use unified diff format (like `git diff`):

```diff
--- v001
+++ v002
@@ -10,7 +10,7 @@
 ## מהם החיים?

-החיים הם תכונה מורכבת שקשה להגדיר.
+החיים הם תכונה מורכבת הכוללת מטרה, מבנה ותפקוד.

 בפרק זה נלמד על:
```

## Benefits

1. **Audit Trail** - Complete history of all changes
2. **Rollback** - Can revert to any previous version
3. **Comparison** - See exactly what changed between versions
4. **Blame/Attribution** - Know which agent made each change
5. **Quality Control** - Tag versions as reviewed/approved
6. **Reproducibility** - Recreate any state of the book

## Best Practices

1. **Meaningful messages** - Write clear commit-style messages
2. **Atomic versions** - One logical change per version
3. **Use tags** - Mark milestones (draft, reviewed, approved, published)
4. **Regular saves** - Save after each significant editing pass
5. **Review diffs** - Check diffs before finalizing major edits

## Notes

- Versions are **append-only** (no deletion for integrity)
- Each agent should save at least one version per chapter
- Version IDs are sequential per chapter (independent counters)
- Diffs are cached for performance
- Content hashes ensure integrity
