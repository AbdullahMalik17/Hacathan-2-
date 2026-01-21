# Implementation Tasks: Sprint 2

## Filesystem Watcher (003)

- [ ] **Rate Limiting**:
  - Add `self.task_history: List[float]` to `FileHandler`.
  - In `on_created`, filter history for `t > current_time - 3600`.
  - If `len(history) >= 50`, reject event.
- [ ] **Multi-Path Support**:
  - Update `main` to accept `--paths` argument.
  - Loop `observer.schedule` for each path.
- [ ] **Validation**: Create `tests/test_fs_watcher.py` to verify rate limits.

## CEO Briefing (004)

- [ ] **ROI Logic**:
  - Implement value mapping for common actions.
  - Sum values in `analyze_actions`.
- [ ] **Claude Narrative**:
  - Implement `get_ai_summary(report_text)` in `ceo_briefing.py`.
  - Call an available CLI agent with the prompt.
- [ ] **Email Distribution**:
  - Add logic to call `src/mcp_servers/email_sender.py` (or use it as a tool if possible).
- [ ] **Validation**: Run manual generation and verify AI summary appears.
