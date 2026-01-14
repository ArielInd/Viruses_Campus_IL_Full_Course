# Specification: Agent Pipeline Optimization

## Overview
This track implements the refactoring plan developed during the Agent Pipeline Review. The goal is to address architectural inconsistencies, code quality issues, and granularity mismatches to create a more robust and scalable pipeline.

## Scope
### In-Scope
*   **Cleanup:** Removing legacy/duplicate files and fixing linting errors.
*   **Infrastructure:** Hardening configuration and LLM client resource management.
*   **Architecture:** Refactoring key agents (`BriefBuilder`, `DraftWriter`, `DevelopmentalEditor`) to operate at the single-chapter level.
*   **Orchestration:** Updating `pipeline_orchestrator.py` to manage fine-grained tasks and enforce concurrency limits.
*   **Logic:** Improving validation and configuration management in `DevelopmentalEditor`.

### Out-of-Scope
*   Changing the underlying prompts or LLM logic (unless necessary for the refactor).
*   Adding new agents or pipeline stages.

## Deliverables
*   Cleaned up `agents/` directory (no legacy files).
*   Lint-free codebase (passing `ruff check`).
*   Refactored agents accepting `chapter_id`.
*   Updated `pipeline_orchestrator.py` with dynamic task generation and semaphore-based concurrency.
*   Updated tests reflecting the architectural changes.

## Acceptance Criteria
*   All existing tests pass.
*   The pipeline runs successfully from end-to-end.
*   Concurrency limits are respected (verified by logs or observation).
*   No "legacy" files remain in the codebase.
