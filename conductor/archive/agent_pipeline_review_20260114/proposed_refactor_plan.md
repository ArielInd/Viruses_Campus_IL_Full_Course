# Proposed Refactor Plan: Agent Pipeline Optimization

## Overview
This plan addresses the architectural and code quality issues identified during the Agent Pipeline Review (2026-01-14). The goal is to improve robustness, scalability, and maintainability.

## Phase 1: Cleanup and Standardization
- [ ] Task: Remove duplicate legacy agent files (`agent_e_developmental_editor.py`, `agent_f_assessment_designer.py`, etc.).
- [ ] Task: Fix all linting errors identified by Ruff (160+ issues, mostly unused imports).
- [ ] Task: Standardize file headers and docstrings across all agents.

## Phase 2: Infrastructure Hardening
- [ ] Task: Upgrade `src/config.py` to use `pydantic-settings` for validation.
- [ ] Task: Refactor `LLMClient` to be an asynchronous context manager (`__aenter__`/`__aexit__`) for safe resource cleanup.
- [ ] Task: Centralize file path generation logic (move from agents to `PipelineContext` or `schemas.py`).

## Phase 3: Architectural Refactoring (Granularity)
- [ ] Task: Refactor `BriefBuilder` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Refactor `DraftWriter` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Refactor `DevelopmentalEditor` to accept `chapter_id` argument and process a single chapter.
- [ ] Task: Update `pipeline_orchestrator.py` to:
    -   Dynamically generate task lists based on the `chapter_plan.json`.
    -   Implement a Semaphore to limit concurrency (respecting `max_workers`).
    -   Support retrying individual failed chapter tasks without restarting the whole pipeline.

## Phase 4: Logic Improvements
- [ ] Task: Externalize `EXISTING_CHAPTERS` mapping in `DevelopmentalEditor` to a config file.
- [ ] Task: Improve validation logic in `DevelopmentalEditor` (replace fragile string matching with structured parsing or fuzzy matching).
