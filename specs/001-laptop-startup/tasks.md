# Implementation Tasks: Laptop Startup

## US1: Auto-Start on Login

- [ ] **Verify Install Script**
  - Run `scripts/install_service.ps1` (dry-run or check logic).
  - Ensure it points to the correct `python.exe` in `.venv`.
  - Ensure it points to the correct `src/service_manager.py`.
- [ ] **Manual Test**: Run `install_service.ps1` and verify Task Scheduler entry created.

## US2: Automatic Restart on Crash

- [ ] **Integration Test**: Create `tests/test_service_recovery.py`.
  - Start `service_manager.py` in a separate thread/process.
  - Wait for services to start.
  - Kill one service (e.g., `watching-filesystem`) by PID.
  - Assert that `service_manager.py` logs the crash.
  - Assert that the service is restarted (new PID) within 10 seconds.
- [ ] **Refine Manager**: Ensure `service_manager.py` logic robustly handles rapid crash loops (backoff?). *Current logic: fixed sleep.*

## US3: Graceful Shutdown

- [ ] **Unit Test**: Test `stop_services` in `service_manager.py`.
  - Mock `subprocess.Popen` objects.
  - Call `stop_services()`.
  - Verify `terminate()` is called on all.
- [ ] **Manual Test**: Run manager, then `Ctrl+C`. Verify log shows `SHUTDOWN` events.

## US4: Logging & Validation

- [ ] **Log Verification**: Check `Vault/Logs/startup_log.md` format.
  - Ensure it matches the Markdown table format.
- [ ] **Pre-flight Checks**: Add check in `service_manager.py` for internet connection (optional but good).
