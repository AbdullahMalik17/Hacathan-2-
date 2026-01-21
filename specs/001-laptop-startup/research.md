# Research Findings: Laptop Startup

## 1. Existing Implementation Analysis

### Service Manager (`src/service_manager.py`)
- **Status**: Implemented.
- **Capabilities**:
  - Starts services defined in `SERVICES` dict.
  - Monitors PIDs.
  - Restarts on exit (Watchdog pattern).
  - Handles SIGINT/SIGTERM for graceful shutdown.
  - Logs to `Vault/Logs/startup_log.md`.
- **Services Managed**:
  - `watching-gmail`
  - `watching-filesystem`
  - `watching-whatsapp`
  - `digital-fte-orchestrator`

### Installation Script (`scripts/install_service.ps1`)
- **Status**: Implemented.
- **Mechanism**: Windows Task Scheduler (`New-ScheduledTaskAction`, `Register-ScheduledTask`).
- **Trigger**: `-AtLogon`.
- **Target**: `python.exe` running `src/service_manager.py`.

### Architecture Alignment
- The `service_manager.py` points to `.claude/skills/*/scripts/run.py`.
- These scripts wrap `src/watchers/*.py`.
- **Conclusion**: The architecture is consistent with the "Skills" migration mentioned in status docs.

## 2. Technical Decisions

### Auto-Start Mechanism
- **Choice**: Windows Task Scheduler.
- **Rationale**: Robust, supports "AtLogon", handles battery states, runs with user privileges (needed for some UI interactions like Playwright).
- **Alternative**: Registry `Run` key (less control), Service (harder to interact with GUI/Browser).

### Process Supervision
- **Choice**: Python-based `ServiceManager`.
- **Rationale**: Cross-platform (can run on Linux/Mac with minor tweaks), simple, easy to customize logging/logic.
- **Alternative**: `pm2` (Node dependency), `supervisord` (Unix only).

## 3. Gaps & Requirements

- **Verification**: Need to verify `install_service.ps1` actually works on the target environment (paths are correct).
- **Logging**: `service_manager.py` logs to `startup_log.md`. Spec requires specific fields. Current implementation looks adequate but should be verified against `FR-003`.
- **Environment Validation**: `FR-004` requires validating environment. `service_manager.py` has `verify_skill` function. This seems covered.
