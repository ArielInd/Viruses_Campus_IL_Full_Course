# Implementation Plan: Downloader Core

## Phase 1: Environment and Project Structure [checkpoint: 2093313]
- [x] Task: Set up Python project structure and install dependencies (Playwright, python-dotenv). <!-- id: 0 --> <!-- bae449d -->
- [x] Task: Configure environment variables for Campus IL credentials. <!-- id: 1 --> <!-- 986acba -->
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment and Project Structure' (Protocol in workflow.md) <!-- id: 2 --> <!-- 2093313 -->

## Phase 2: Authentication and Basic Navigation [checkpoint: 7810e0e]
- [x] Task: Implement Playwright-based login flow for Campus IL. <!-- id: 3 --> <!-- bccdeed -->
- [x] Task: Verify successful login and navigation to the course homepage. <!-- id: 4 --> <!-- 544fdfb -->
- [x] Task: Conductor - User Manual Verification 'Phase 2: Authentication and Basic Navigation' (Protocol in workflow.md) <!-- id: 5 --> <!-- 7810e0e -->

## Phase 3: Course Structure Traversal [checkpoint: b3efdab]
- [x] Task: Implement logic to extract the course hierarchy (modules, sections, lectures). <!-- id: 6 --> <!-- 8dd0c61 -->
- [x] Task: Create corresponding local directory structure. <!-- id: 7 --> <!-- d1a3d1a -->
- [x] Task: Conductor - User Manual Verification 'Phase 3: Course Structure Traversal' (Protocol in workflow.md) <!-- id: 8 --> <!-- b3efdab -->

## Phase 4: Transcript Extraction and Saving [checkpoint: 9c61136]
- [x] Task: Implement logic to identify and download transcripts for each lecture. <!-- id: 9 --> <!-- 20ad050 -->
- [x] Task: Apply standardized naming convention to saved `.txt` files. <!-- id: 10 --> <!-- ab6f6d6 -->
- [x] Task: Implement "skip if exists" check. <!-- id: 11 --> <!-- ab6f6d6 -->
- [x] Task: Conductor - User Manual Verification 'Phase 4: Transcript Extraction and Saving' (Protocol in workflow.md) <!-- id: 12 --> <!-- 9c61136 -->

## Phase 5: Logging and Summary Reporting
- [x] Task: Implement functional console logging for progress tracking. <!-- id: 13 --> <!-- d44ffbc -->
- [x] Task: Implement generation of the `summary.txt` report. <!-- id: 14 --> <!-- 597ec25 -->
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Logging and Summary Reporting' (Protocol in workflow.md)
