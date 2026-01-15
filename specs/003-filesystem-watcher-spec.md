# Feature Specification: Filesystem Watcher

**Feature Branch**: `003-filesystem-watcher`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User selection from Digital FTE roadmap - Monitor local file changes

## User Scenarios & Testing

### User Story 1 - Detect New Files (Priority: P1)

When new files appear in watched directories, system creates markdown task files in Vault/Needs_Action for processing.

**Why this priority**: Core functionality - enables file automation workflows.

**Independent Test**: Create a file in watched directory and verify task appears in Needs_Action within 10 seconds.

**Acceptance Scenarios**:

1. **Given** filesystem watcher is running and watching ~/Downloads, **When** PDF file created there, **Then** task created in Needs_Action
2. **Given** task is created, **When** task file is examined, **Then** it contains file path, size, type, and suggested action
3. **Given** multiple files created rapidly, **When** debounce window closes, **Then** only one task per file (no duplicates)

---

### User Story 2 - Categorize and Suggest Actions (Priority: P1)

Watcher analyzes file type and location, suggests appropriate action (archive, process, review, delete).

**Why this priority**: High - enables intelligent automation without manual categorization.

**Independent Test**: Create files of different types (PDF, image, code) and verify suggested actions are appropriate.

**Acceptance Scenarios**:

1. **Given** PDF file created in ~/Documents/Invoices, **When** task is created, **Then** suggested action is "process_invoice"
2. **Given** old file (>30 days) in ~/Downloads, **When** task created, **Then** suggested action is "archive_old"
3. **Given** code file in ~/Projects, **When** task created, **Then** suggested action is "review_code_changes"

---

### User Story 3 - Rate Limiting and Debouncing (Priority: P1)

System debounces rapid file events and limits task creation rate to prevent overwhelming orchestrator.

**Why this priority**: Critical for stability - prevents cascading failures from excessive events.

**Independent Test**: Bulk copy many files and verify max 1 task per second, max 50 tasks per hour.

**Acceptance Scenarios**:

1. **Given** 100 files copied to watched directory simultaneously, **When** copy completes, **Then** <50 tasks created (rate limited)
2. **Given** file modified 10 times in 1 second, **When** debounce window closes, **Then** only 1 task created
3. **Given** rate limit of 50 tasks/hour reached, **When** more files appear, **Then** tasks queued for next hour

---

### User Story 4 - Safety: Never Auto-Delete (Priority: P1)

Filesystem watcher never deletes or modifies files. All destructive actions require explicit human approval.

**Why this priority**: Critical safety - prevents accidental data loss.

**Independent Test**: Create task requesting file deletion, verify it lands in Pending_Approval, never auto-executes.

**Acceptance Scenarios**:

1. **Given** temporary file detected, **When** task created to delete it, **Then** task goes to Pending_Approval
2. **Given** task in Pending_Approval, **When** user approves it, **Then** only then does deletion happen
3. **Given** no approval received, **When** time passes, **Then** file is never deleted

---

### Edge Cases

- What happens with symlinks or hard links?
- How to handle permission errors when reading file?
- What if file is still being written when event fires?
- How to detect and handle duplicate files?
- What happens with very large files (>1GB)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST monitor specified directories for file creation, modification, deletion
- **FR-002**: System MUST create markdown task in Needs_Action with file metadata (path, size, type, age)
- **FR-003**: System MUST suggest appropriate action based on file type and location
- **FR-004**: System MUST debounce rapid file events (5 second window)
- **FR-005**: System MUST rate-limit task creation (max 50/hour)
- **FR-006**: System MUST NEVER auto-delete files (always require approval)
- **FR-007**: System MUST ignore hidden files and cache directories
- **FR-008**: System MUST log all file events for audit trail

### Key Entities

- **FileEvent**: Represents detected file change
  - path, event_type (create/modify/delete), size, mime_type, timestamp
  
- **FileTask**: Markdown task for file processing
  - file_path, event_type, size, type, age_days, suggested_action, status

- **FileWatcherConfig**: Configuration for monitored directories
  - directory_path, patterns (include/exclude), debounce_ms, rate_limit

## Success Criteria

### Measurable Outcomes

- **SC-001**: <10 second latency - task created within 10 seconds of file event
- **SC-002**: 100% deduplication - no duplicate tasks for same file
- **SC-003**: Correct categorization - 95%+ accuracy on suggested actions
- **SC-004**: Zero unintended deletions - 0 files ever auto-deleted without approval
- **SC-005**: No false positives - system only triggers on watched directories
