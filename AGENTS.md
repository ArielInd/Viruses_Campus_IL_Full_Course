# Repository Guidelines

## Project Structure & Module Organization

- `src/`: core Python package (downloader, config, manifest generation, transcript scanning).
- `agents/`: **Quality-First multi-agent pipeline** for ebook generation (10 specialized agents).
  - `agent_*.py`: Individual agent implementations (A through J).
  - `pipeline_context.py`: Shared context manager with caching.
  - `pipeline_orchestrator.py`: Concurrent execution manager.
  - `llm_client.py`: Unified LLM interface (Gemini + OpenRouter).
  - `version_manager.py`: Git-like version control for chapters.
  - `schemas.py`: Shared data structures and utilities.
  
  **Quality-First Upgrades:**
  - All critical agents use `gemini-3-pro` for deep reasoning
  - Agent D uses 3-wave iterative writing (Outline → Sections → Synthesis)
  - Agent J (NEW) provides adversarial critique before editing
  - Agent H uses LLM-powered linguistic proofreading
  - Agent E performs active rewriting of transitions
  
- `tests/`: pytest suite (`tests/test_*.py`).
- `course_transcripts/`: downloaded transcript text files (course output).
- `book/`: compiled book assets, `book/chapters/`, and `book/manifest.json`.
- `chapters/`: source chapter drafts.
- `conductor/`: project plans, workflow, and code style references.
- `docs/`: architecture documentation and improvement guides.
- `SCRIPTS_OVERVIEW.md`: Comprehensive documentation of all scripts and their relationships.
- Root scripts: `main.py`, `generate_manifest.py`, `run_production.py` (Quality-First), `verify_*.py`.

## Build, Test, and Development Commands

### Setup & Dependencies

- `pip install -r requirements.txt`: install Python dependencies (includes httpx, aiofiles for async support).
- `python -m playwright install`: install Playwright browser binaries.

### Pipeline Execution

- `python run_optimized_pipeline.py`: **NEW** - Run optimized multi-agent pipeline with parallelization.
- `python main.py`: download transcripts into `course_transcripts/`.
- `python generate_manifest.py`: regenerate `book/manifest.json`.

### Testing

- `pytest`: run the full test suite.
- `pytest tests/test_version_manager.py`: run version manager tests.
- `pytest tests/test_agent_a_corpus_librarian.py`: run Agent A tests.
- `pytest tests/test_schemas.py`: run schema tests.
- `pytest --cov=agents`: run tests with coverage for agents module.
- `pytest -v`: run tests with verbose output.
- `pytest -k "test_version"`: run tests matching pattern.

### Code Quality

- `ruff check src tests agents`: lint Python code.

## Coding Style & Naming Conventions

- Follow Google Python style: 4-space indentation, 80-char lines, docstrings for public APIs.
- Naming: `snake_case` for functions/modules, `PascalCase` for classes, `ALL_CAPS` for constants.
- Prefer type annotations on public interfaces; avoid mutable default args.

## Testing Guidelines

- Framework: pytest with `pytest.ini` configured for `tests/`.
- Naming: add tests to `tests/test_<module>.py`.
- Coverage: target >80% for new or changed code.

## Commit & Pull Request Guidelines

- Commit messages follow a conventional pattern: `type(scope): summary`.
  - Examples: `feat(book): Draft Chapter 7`, `conductor(plan): Mark task ...`.
- PRs should include: a short summary, test commands run (with results), and any updated assets
  such as `book/` or `course_transcripts/`.

## Security & Configuration Tips

- Store credentials in `.env` with `CAMPUS_IL_USERNAME`, `CAMPUS_IL_PASSWORD`, and `COURSE_URL`.
- Never commit secrets or local output artifacts unless explicitly requested.
