# Product Guidelines: Course Transcript Downloader

## Communication Style
- **Tone:** Functional and direct. Logs should provide clear status updates without unnecessary prose.
- **Error Handling:** If an individual download fails, the tool should log the error and continue with the remaining items to ensure maximum overall progress.

## File Organization & Naming
- **Naming Convention:** Files should use a standardized format: `[Index]_[Title].txt` (e.g., `01_Introduction_to_Virology.txt`).
- **Output Format:** Plain text (.txt) files only.

## Security & Configuration
- **Credential Management:** Sensitive information like login credentials must be managed via environment variables (e.g., a `.env` file) and never hardcoded.

## User Experience (CLI)
- **Simplicity First:** The tool should aim for a "zero-config" experience where a single command initiates the bulk download process using sensible defaults.
