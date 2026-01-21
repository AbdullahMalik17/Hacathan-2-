# Implementation Plan: Sprint 2

## 1. Filesystem Watcher Enhancements

- **Rate Limiting**: Add a sliding window counter to `FileHandler` to track tasks per hour. If > 50, log and skip (or queue).
- **Multi-Folder**: Update `main()` and `argparse` to allow a list of directories.
- **Improved Categorization**: Use `python-magic` or similar if available, otherwise expand the extension mapping.

## 2. CEO Briefing Enhancements

- **Metric Engine**: Implement `compute_roi(entries)` in `ceo_briefing.py`.
- **LLM Integration**: Add `generate_narrative_summary(metrics)` using available AI agents (Gemini/Claude).
- **Email Integration**: Add `--email` flag to `ceo_briefing.py`. If set, use `EmailSenderMCP` to distribute the report.

## 3. Integration

- Ensure `service_manager.py` starts the updated FS Watcher with correct arguments.
- Schedule `ceo_briefing.py` via `scripts/install_service.ps1` as a separate recurring task.
