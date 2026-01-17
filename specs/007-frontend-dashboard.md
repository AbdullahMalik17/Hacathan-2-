# Feature Specification: Frontend Dashboard

**Feature Branch**: `007-frontend-dashboard`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Make Frontend for this project... It will show all the details of complete tasks and pending tasks... It will show all the skills of Agent... Make a way to directly interact with agent... Use your skills project design for design... Make Proper specs by following the specifyplus structure"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Dashboard (Priority: P1)

As a user, I want to see a dashboard of all my pending and completed tasks so that I can track the agent's progress.

**Why this priority**: Core requirement to visualize the "Ralph Wiggum Loop" status.

**Independent Test**:
1. Place a file in `Vault/Needs_Action`.
2. Place a file in `Vault/Done`.
3. Open the dashboard.
4. Verify both files are visible in their respective columns.

**Acceptance Scenarios**:

1. **Given** a file `task1.md` exists in `Vault/Needs_Action`, **When** I load the dashboard, **Then** I see "task1" in the "Pending Tasks" list.
2. **Given** a file `task2.md` exists in `Vault/Done`, **When** I load the dashboard, **Then** I see "task2" in the "Completed Tasks" list.
3. **Given** a task is moved from Pending to Done by the orchestrator, **When** the dashboard refreshes, **Then** the task moves to the Completed list.

---

### User Story 2 - Interact with Agent (Priority: P1)

As a user, I want to send a message to the agent directly from the UI so that I can assign new tasks without manually creating files.

**Why this priority**: Enables the "interact with agent" requirement.

**Independent Test**:
1. Type "Hello Agent" in the chat input.
2. Click Send.
3. Verify a new file is created in `Vault/Needs_Action` containing the message.

**Acceptance Scenarios**:

1. **Given** I am on the Chat page, **When** I type "Research Kubernetes" and hit Enter, **Then** a new file (e.g., `Task_Research_Kubernetes_[TIMESTAMP].md`) is created in `Vault/Needs_Action`.
2. **Given** I sent a message, **When** I look at the task list, **Then** the new task appears immediately (optimistic UI) or after refresh.

---

### User Story 3 - View Agent Skills (Priority: P2)

As a user, I want to see a list of all available agent skills so that I know what capabilities "Abdullah Junior" possesses.

**Why this priority**: Helps the user understand what the agent can do.

**Independent Test**:
1. Open the Skills page.
2. Verify it lists skills from `SKILLS-INDEX.md` (e.g., "browsing-with-playwright").

**Acceptance Scenarios**:

1. **Given** `SKILLS-INDEX.md` contains "building-nextjs-apps", **When** I visit the Skills page, **Then** I see "building-nextjs-apps" and its description in the list.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST be built using Next.js 14+ (App Router).
- **FR-002**: System MUST use Shadcn UI for component styling.
- **FR-003**: System MUST provide a server-side mechanism (Server Actions/API Routes) to read files from `Vault/Needs_Action` and `Vault/Done`.
- **FR-004**: System MUST provide a server-side mechanism to write new Markdown files to `Vault/Needs_Action` based on user input.
- **FR-005**: System MUST parse `.claude/skills/SKILLS-INDEX.md` or `.gemini/skills/SKILLS-INDEX.md` to display available skills.
- **FR-006**: System MUST poll or revalidate data to show updates from the Orchestrator.

### Key Entities

- **Task**: Represents a file in the Vault. Attributes: filename, status (Pending/Done), content, timestamp.
- **Skill**: Represents an entry in `SKILLS-INDEX.md`. Attributes: name, description, category.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the current state of the Vault (Pending/Done) with < 1s latency on local load.
- **SC-002**: Submitting a new task via the UI results in a file creation in `Vault/Needs_Action` within 500ms.
- **SC-003**: The UI accurately reflects 100% of the skills listed in the index file.
