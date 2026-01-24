# Data Model: Laptop Startup

## Entities

### ServiceManager
*Runtime state in `src/service_manager.py`*

| Field | Type | Description |
|-------|------|-------------|
| `processes` | `Dict[str, Popen]` | Map of service name to process handle |
| `SERVICES` | `Dict` | Configuration of services (command, cwd, restart_delay) |
| `running` | `bool` | Control flag for the monitor loop |

### StartupLog
*File: `Vault/Logs/startup_log.md`*

| Field | Format | Description |
|-------|--------|-------------|
| `Timestamp` | `YYYY-MM-DD HH:MM:SS` | When the event occurred |
| `Event` | `Enum` | `STARTUP`, `SHUTDOWN`, `CRASH`, `SYSTEM` |
| `Service` | `String` | Name of the service (e.g., `watching-gmail`) |
| `Status` | `String` | `SUCCESS`, `FAILED`, `EXITED` |
| `Details` | `String` | Error message, PID, or exit code |

### TaskSchedulerEntry
*Windows Task Scheduler Object*

| Property | Value |
|----------|-------|
| `TaskName` | `DigitalFTE_ServiceManager` |
| `Trigger` | `AtLogon` |
| `Action` | `python.exe src/service_manager.py` |
| `Settings` | `AllowStartIfOnBatteries`, `DontStopIfGoingOnBatteries` |
