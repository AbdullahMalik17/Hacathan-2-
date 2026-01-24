# Frontend Dashboard - Architectural Plan

**Status:** Ready for Approval
**Branch:** `007-frontend-dashboard` (to create)
**Date:** 2026-01-17
**Related Spec:** [spec.md](../007-frontend-dashboard.md)

---

## 1. Scope and Dependencies

### In Scope
- Next.js 14+ dashboard for Digital FTE system
- Task visualization (Pending/Done)
- Agent skills catalog
- Direct agent interaction (chat interface)
- Real-time updates from Vault
- Shadcn UI component library

### Out of Scope
- Authentication (local-first application)
- Mobile app (web only)
- Real-time websockets (polling sufficient)
- Task editing (read-only, create-only)
- Historical analytics

### External Dependencies
| Dependency | Ownership | Risk |
|------------|-----------|------|
| Vault filesystem | Orchestrator | Low - already stable |
| SKILLS-INDEX.md | Agent Skills | Low - already exists |
| Shadcn UI | External | Low - well documented |
| Next.js 14 | External | Low - stable release |

---

## 2. Key Decisions and Rationale

### Decision 1: Next.js App Router vs Pages Router
**Options Considered:**
- App Router (Next.js 14+) ✅ CHOSEN
- Pages Router (Next.js 12)

**Trade-offs:**
| Aspect | App Router | Pages Router |
|--------|-----------|--------------|
| Server Actions | Native support | Requires API routes |
| File I/O | Direct in Server Components | Need API layer |
| Performance | RSC optimization | Client-heavy |
| Future-proof | Yes | Legacy path |

**Rationale:**
App Router with Server Actions allows direct filesystem access without API routes, perfect for local-first vault integration.

**Principles:**
- Simplest viable architecture
- Leverage platform features (RSC, Server Actions)
- Local-first design

### Decision 2: Polling vs WebSockets for Updates
**Options Considered:**
- Polling with revalidation ✅ CHOSEN
- WebSockets
- Server-Sent Events (SSE)

**Rationale:**
Polling is sufficient for this use case (updates every 3-5 seconds is acceptable). Simpler implementation, no connection management overhead.

**Implementation:**
- Client-side polling with `setInterval`
- Server-side ISR with `revalidatePath`
- Manual refresh button for immediate updates

### Decision 3: Markdown Rendering
**Options Considered:**
- react-markdown ✅ CHOSEN
- MDX
- Raw HTML

**Rationale:**
`react-markdown` is lightweight, secure (XSS protection), and sufficient for displaying task content without executable code.

---

## 3. Interfaces and API Contracts

### Server Actions (Next.js)

#### `getTasks(status: 'pending' | 'done'): Promise<Task[]>`
**Input:**
```typescript
type Status = 'pending' | 'done'
```

**Output:**
```typescript
interface Task {
  filename: string
  status: 'pending' | 'done'
  content: string
  timestamp: Date
  priority?: 'urgent' | 'high' | 'medium' | 'low'
  source?: 'gmail' | 'whatsapp' | 'filesystem' | 'webui'
}
```

**Errors:**
- `FileSystemError`: Cannot read Vault directory
- `ParseError`: Invalid markdown frontmatter

---

#### `createTask(content: string, title: string): Promise<Task>`
**Input:**
```typescript
interface CreateTaskInput {
  content: string
  title: string
  priority?: 'medium' | 'high' | 'urgent'
}
```

**Output:**
```typescript
interface Task {
  filename: string
  status: 'pending'
  content: string
  timestamp: Date
}
```

**Errors:**
- `ValidationError`: Empty content or title
- `FileSystemError`: Cannot write to Vault

**Idempotency:**
- Each task has unique timestamp-based filename
- Safe to retry on failure

---

#### `getSkills(): Promise<Skill[]>`
**Input:** None

**Output:**
```typescript
interface Skill {
  name: string
  description: string
  category?: string
  status?: 'available' | 'custom'
}
```

**Errors:**
- `FileNotFoundError`: SKILLS-INDEX.md missing
- `ParseError`: Invalid skill file format

---

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| Page load (local) | < 1s | Lighthouse |
| Task list render | < 500ms | React DevTools |
| Task creation | < 500ms | Network tab |
| Polling interval | 5s | Configurable |

### Reliability
- **SLO**: 99.9% uptime (local development)
- **Error Budget**: 0.1% (4.3 minutes/month downtime acceptable)
- **Degradation Strategy**: Show cached data if Vault unreachable

### Security
- **No AuthN/AuthZ**: Localhost-only application
- **XSS Protection**: react-markdown sanitizes output
- **Path Traversal**: Validate file paths against Vault base directory
- **Secrets**: No secrets in frontend code

### Cost
- Zero runtime cost (local development)
- Build time: < 30s for production build

---

## 5. Data Management and Migration

### Source of Truth
- **Vault filesystem** is the source of truth
- Frontend is read-only with create-only operations
- No database, no caching layer

### Schema Evolution
- Task markdown files have YAML frontmatter
- Backward compatible: missing fields get defaults
- Forward compatible: ignore unknown frontmatter keys

### Data Retention
- Vault manages retention (Archive/ folder after 30 days)
- Frontend does not enforce retention

### No Migration Needed
- Filesystem-based, no schema migrations
- Graceful degradation for missing/malformed files

---

## 6. Operational Readiness

### Observability
- **Logs**: Console logs for errors (development)
- **Metrics**: None (local app)
- **Traces**: React DevTools profiling

### Alerting
- Not applicable (local development)

### Deployment
- **Development**: `npm run dev` (localhost:3000)
- **Production Build**: `npm run build && npm run start`
- **Static Export**: Not needed (dynamic data)

### Rollback
- Git revert to previous commit
- No data loss (Vault is independent)

---

## 7. Risk Analysis and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Vault path changes | High | Low | Use environment variable for VAULT_PATH |
| Large task lists (>1000 files) | Medium | Medium | Implement pagination, limit to 100 most recent |
| Malformed markdown breaks UI | Low | Medium | Error boundaries, try-catch in rendering |
| Concurrent writes to Vault | Medium | Low | Use atomic file writes, timestamp-based naming |

**Kill Switches:**
- Emergency: Stop Next.js dev server
- Rollback: `git checkout main && npm run dev`

---

## 8. Evaluation and Validation

### Definition of Done
- [ ] All user stories from spec have passing tests
- [ ] Lighthouse score > 90 (Performance, Accessibility)
- [ ] No console errors in browser
- [ ] Works on Chrome, Firefox, Safari
- [ ] README updated with frontend setup instructions

### Testing Strategy
| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Unit | Server Actions | Jest |
| Integration | Full page flow | Playwright |
| Visual | Component library | Storybook (optional) |
| E2E | User scenarios | Manual testing |

---

## 9. Implementation Phases

### Phase 1: Foundation (Tasks 1-4)
1. Initialize Next.js 14 project with App Router
2. Install and configure Shadcn UI
3. Create basic layout (header, sidebar, main area)
4. Implement Server Actions for Vault access

### Phase 2: Task Dashboard (Tasks 5-7)
5. Build Pending Tasks view with card layout
6. Build Completed Tasks view
7. Implement auto-refresh polling

### Phase 3: Agent Interaction (Tasks 8-10)
8. Build chat interface for task creation
9. Implement task creation Server Action
10. Add optimistic UI updates

### Phase 4: Skills Catalog (Tasks 11-12)
11. Parse SKILLS-INDEX.md
12. Display skills in grid/list view

### Phase 5: Polish & Testing (Tasks 13-15)
13. Add loading states and error boundaries
14. End-to-end testing
15. Documentation and README

---

## 10. Technology Stack

### Frontend Framework
- **Next.js 14.2+** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety

### UI Components
- **Shadcn UI** - Component library (Radix UI + Tailwind CSS)
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Icon library

### Markdown Rendering
- **react-markdown** - Safe markdown rendering
- **remark-gfm** - GitHub Flavored Markdown support

### File Operations
- **Node.js fs/promises** - Native filesystem access (server-side)
- **gray-matter** - YAML frontmatter parsing

### Development
- **ESLint** - Linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking

---

## 11. File Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Dashboard home (task overview)
│   ├── tasks/
│   │   ├── page.tsx            # Task list view
│   │   └── [id]/page.tsx       # Task detail view
│   ├── chat/
│   │   └── page.tsx            # Chat interface for agent
│   ├── skills/
│   │   └── page.tsx            # Skills catalog
│   └── api/
│       └── tasks/
│           └── route.ts        # API route (if needed for polling)
├── components/
│   ├── ui/                     # Shadcn UI components
│   ├── TaskCard.tsx            # Task display card
│   ├── TaskList.tsx            # Task list container
│   ├── ChatInput.tsx           # Chat input component
│   ├── SkillCard.tsx           # Skill display card
│   └── Header.tsx              # App header
├── lib/
│   ├── actions.ts              # Server Actions
│   ├── vault.ts                # Vault filesystem utilities
│   ├── skills.ts               # Skills parsing utilities
│   └── utils.ts                # General utilities
├── types/
│   └── index.ts                # TypeScript type definitions
├── public/
│   └── icons/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

---

## 12. Architectural Decision Records (ADRs)

### ADR-001: Use Next.js App Router for Filesystem Integration
**Context:** Need to access Vault filesystem without creating API layer.

**Decision:** Use Next.js 14 App Router with Server Components and Server Actions.

**Consequences:**
- ✅ Simpler architecture (no API routes needed)
- ✅ Direct fs access in Server Components
- ✅ Type-safe data flow (TypeScript end-to-end)
- ⚠️ Learning curve for App Router patterns

### ADR-002: Local-First, No Authentication
**Context:** Digital FTE runs locally on user's machine.

**Decision:** No authentication layer, assume localhost-only access.

**Consequences:**
- ✅ Simpler implementation
- ✅ Faster development
- ⚠️ Cannot expose to network without adding auth layer later

### ADR-003: Polling Instead of WebSockets
**Context:** Need to show real-time updates from Vault.

**Decision:** Use client-side polling (5s interval) instead of WebSockets.

**Consequences:**
- ✅ Simpler implementation
- ✅ No connection management overhead
- ⚠️ Slight delay (5s) in showing updates
- ✅ Sufficient for use case (not mission-critical real-time)

---

## 13. Acceptance Criteria

### Functional
- [ ] User can view pending tasks from Vault/Needs_Action
- [ ] User can view completed tasks from Vault/Done
- [ ] User can create new tasks via chat interface
- [ ] New tasks appear in pending list immediately (optimistic UI)
- [ ] User can view all agent skills with descriptions
- [ ] Task list auto-refreshes every 5 seconds
- [ ] Markdown content renders correctly

### Non-Functional
- [ ] Page load < 1s on localhost
- [ ] No console errors
- [ ] Mobile responsive (min 375px width)
- [ ] Lighthouse score > 90
- [ ] All links and navigation work
- [ ] Error states display user-friendly messages

### Operational
- [ ] README has setup instructions
- [ ] Environment variables documented
- [ ] Dev server starts with `npm run dev`
- [ ] Production build succeeds

---

## 14. Estimated Effort

- **Phase 1 (Foundation):** 4 tasks - 2-3 hours
- **Phase 2 (Task Dashboard):** 3 tasks - 2 hours
- **Phase 3 (Agent Interaction):** 3 tasks - 2 hours
- **Phase 4 (Skills Catalog):** 2 tasks - 1 hour
- **Phase 5 (Polish & Testing):** 3 tasks - 2 hours

**Total:** 15 tasks

---

**Next Steps:**
1. Create `specs/007-frontend-dashboard/tasks.md`
2. Create branch `007-frontend-dashboard`
3. Initialize Next.js project in `frontend/` directory
4. Implement Phase 1 (Foundation)
