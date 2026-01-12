# Track Specification: Downloader Core Implementation

## Overview
This track implements the foundational functionality for the Course Transcript Downloader. It enables a student to authenticate with Campus IL and bulk download all lecture transcripts for a specific course, organizing them into a clear folder structure with a summary report.

## Functional Requirements
- **Campus IL Authentication:** Log in using username and password provided via environment variables.
- **Course Traversal:** Navigate the course structure to find all lecture units containing video transcripts.
- **Transcript Extraction:** Download transcripts in plain text (.txt) format.
- **Standardized Naming:** Name files using the `[Index]_[Title].txt` convention.
- **Hierarchical Organization:** Save transcripts in nested folders mirroring the course's module/section structure.
- **Intelligent Skipping:** Detect and skip already downloaded files to avoid redundant work.
- **Summary Report:** Generate a `summary.txt` file listing all downloaded, skipped, and failed transcripts with relevant metadata.

## Non-Functional Requirements
- **Robustness:** Handle network issues and potential changes in website structure gracefully.
- **Progress Tracking:** Provide clear, functional console logs during execution.
- **Maintainability:** Use clean, modular Python code with Playwright for web interaction.

## Acceptance Criteria
- [ ] User can successfully authenticate with Campus IL.
- [ ] Tool correctly identifies and traverses all modules/lectures in the course.
- [ ] All available transcripts are downloaded as `.txt` files in the correct hierarchical directories.
- [ ] Filenames follow the `[Index]_[Title].txt` format.
- [ ] Re-running the tool correctly skips existing files.
- [ ] A `summary.txt` is generated with accurate details of the download session.
