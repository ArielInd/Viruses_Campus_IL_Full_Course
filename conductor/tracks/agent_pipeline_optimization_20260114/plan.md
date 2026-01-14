# Plan: Agent Pipeline Optimization

This plan executes the refactoring strategy defined in the review phase.

## Phase 1: Cleanup and Standardization
- [x] Task: Remove duplicate legacy agent files (`agent_e_developmental_editor.py`, `agent_f_assessment_designer.py`, etc. ) 5619be9
- [x] Task: Fix all linting errors identified by Ruff (160+ issues, mostly unused imports). 4afc349
- [x] Task: Standardize file headers and docstrings across all agents. a606799

## Phase 2: Infrastructure Hardening
- [x] Task: Upgrade `src/config.py` to use `pydantic-settings` for validation. 88788d1
- [x] Task: Refactor `LLMClient` to be an asynchronous context manager (`__aenter__`/`__aexit__`) for safe resource cleanup. 6772c8a
- [x] Task: Centralize file path generation logic (move from agents to `PipelineContext` or `schemas.py`). 219bbb9
- [x] Task: Conductor - User Manual Verification 'Phase 2: Infrastructure Hardening' (Protocol in workflow.md)

## Phase 3: Architectural Refactoring (Granularity)
- [ ] Task: Refactor `BriefBuilder` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Refactor `DraftWriter` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Refactor `DevelopmentalEditor` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Update `pipeline_orchestrator.py` to support dynamic task generation and semaphore-based concurrency.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Architectural Refactoring (Granularity)' (Protocol in workflow.md)

## Phase 4: Logic Improvements and Final Verification
- [ ] Task: Externalize `EXISTING_CHAPTERS` mapping in `DevelopmentalEditor` to a config file.
- [ ] Task: Improve validation logic in `DevelopmentalEditor` (replace fragile string matching).
- [ ] Task: Verify end-to-end pipeline execution with the new architecture.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Logic Improvements and Final Verification' (Protocol in workflow.md)
