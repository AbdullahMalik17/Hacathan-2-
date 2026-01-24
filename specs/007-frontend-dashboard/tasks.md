# Frontend Dashboard - Tasks

**Feature Branch:** `007-frontend-dashboard`
**Created:** 2026-01-17
**Status:** Ready to Start
**Related Plan:** [plan.md](./plan.md)
**Related Spec:** [spec.md](../007-frontend-dashboard.md)

---

## Task List

### Phase 1: Foundation 🆕 READY

#### Task 1: Initialize Next.js Project ⏳
**Status:** TODO
**Priority:** P0 (Critical Path)
**Estimated Effort:** 30 mins

**Description:**
Initialize Next.js 14 project with App Router and TypeScript in `frontend/` directory.

**Acceptance Criteria:**
- [ ] Next.js 14+ project created with `create-next-app`
- [ ] App Router enabled (not Pages Router)
- [ ] TypeScript configured
- [ ] ESLint and Prettier configured
- [ ] Dev server runs on `http://localhost:3000`

**Test:**
```bash
cd frontend
npm run dev
# Browser opens to http://localhost:3000
```

**Commands:**
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npm run dev
```

---

#### Task 2: Install and Configure Shadcn UI ⏳
**Status:** TODO
**Priority:** P0
**Estimated Effort:** 30 mins

**Description:**
Set up Shadcn UI component library with Tailwind CSS.

**Acceptance Criteria:**
- [ ] Shadcn UI initialized with `npx shadcn-ui@latest init`
- [ ] Tailwind config updated with Shadcn theme
- [ ] Base components installed: Button, Card, Input, Badge
- [ ] `components/ui/` directory created
- [ ] Example component renders correctly

**Test:**
```tsx
// Test by adding a Button to app/page.tsx
import { Button } from "@/components/ui/button"
<Button>Test Button</Button>
```

**Commands:**
```bash
cd frontend
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input badge
```

---

#### Task 3: Create Basic Layout ⏳
**Status:** TODO
**Priority:** P0
**Estimated Effort:** 1 hour

**Description:**
Create root layout with header, sidebar navigation, and main content area.

**Acceptance Criteria:**
- [ ] `app/layout.tsx` has header, sidebar, and main content slots
- [ ] Header shows "Digital FTE Dashboard" title
- [ ] Sidebar has navigation links:
  - Dashboard (/)
  - Tasks (/tasks)
  - Chat (/chat)
  - Skills (/skills)
- [ ] Active route is highlighted in sidebar
- [ ] Responsive design (mobile: hamburger menu)

**Test:**
```bash
npm run dev
# Navigate to each route, verify sidebar updates
```

**Files to Create:**
- `app/layout.tsx`
- `components/Header.tsx`
- `components/Sidebar.tsx`

---

#### Task 4: Implement Server Actions for Vault Access ⏳
**Status:** TODO
**Priority:** P0
**Estimated Effort:** 1 hour

**Description:**
Create Server Actions to read from Vault filesystem.

**Acceptance Criteria:**
- [ ] `lib/actions.ts` created with Server Actions
- [ ] `getTasks(status)` reads from Vault/Needs_Action or Vault/Done
- [ ] `createTask(content, title)` writes to Vault/Needs_Action
- [ ] `getSkills()` parses .claude/skills/SKILLS-INDEX.md
- [ ] Error handling for missing files
- [ ] TypeScript types defined in `types/index.ts`

**Test:**
```typescript
// Test in a Server Component
const tasks = await getTasks('pending')
console.log(tasks) // Should show task objects
```

**Files to Create:**
- `lib/actions.ts`
- `lib/vault.ts`
- `types/index.ts`

**Types:**
```typescript
export interface Task {
  filename: string
  status: 'pending' | 'done'
  content: string
  timestamp: Date
  priority?: 'urgent' | 'high' | 'medium' | 'low'
  source?: string
}

export interface Skill {
  name: string
  description: string
  category?: string
}
```

---

### Phase 2: Task Dashboard 🔄 BLOCKED BY PHASE 1

#### Task 5: Build Pending Tasks View ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 1 hour
**Blocked By:** Task 4

**Description:**
Create dashboard page to display pending tasks from Vault/Needs_Action.

**Acceptance Criteria:**
- [ ] `app/tasks/page.tsx` created
- [ ] Fetches tasks using `getTasks('pending')`
- [ ] Displays tasks in grid layout with TaskCard components
- [ ] Shows task filename, timestamp, priority badge
- [ ] Truncates long content with "Read more" link
- [ ] Empty state: "No pending tasks" message

**Test:**
1. Create test file: `Vault/Needs_Action/test_task.md`
2. Visit `/tasks`
3. Verify task appears in grid

**Files to Create:**
- `app/tasks/page.tsx`
- `components/TaskCard.tsx`
- `components/TaskList.tsx`

---

#### Task 6: Build Completed Tasks View ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 30 mins
**Blocked By:** Task 5

**Description:**
Add tab or section for completed tasks from Vault/Done.

**Acceptance Criteria:**
- [ ] Tabs component: "Pending" and "Completed"
- [ ] Completed tab shows tasks from `getTasks('done')`
- [ ] Same TaskCard component reused
- [ ] Different visual styling (muted colors for done)
- [ ] Empty state: "No completed tasks"

**Test:**
1. Move test file to `Vault/Done/test_task.md`
2. Switch to "Completed" tab
3. Verify task appears

**Files to Modify:**
- `app/tasks/page.tsx`

**Components Needed:**
```bash
npx shadcn-ui@latest add tabs
```

---

#### Task 7: Implement Auto-Refresh Polling ⏳
**Status:** BLOCKED
**Priority:** P2
**Estimated Effort:** 30 mins
**Blocked By:** Task 6

**Description:**
Add client-side polling to refresh task list every 5 seconds.

**Acceptance Criteria:**
- [ ] Client component wraps task list
- [ ] `useEffect` hook polls every 5 seconds
- [ ] Uses `router.refresh()` to revalidate Server Component
- [ ] Manual refresh button also available
- [ ] Polling stops when user navigates away

**Test:**
1. Visit `/tasks`
2. Add new file to `Vault/Needs_Action` manually
3. Verify task appears within 5 seconds (no manual refresh)

**Files to Create:**
- `components/TaskListClient.tsx`

**Code Pattern:**
```typescript
'use client'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function TaskListClient({ children }) {
  const router = useRouter()

  useEffect(() => {
    const interval = setInterval(() => {
      router.refresh()
    }, 5000)
    return () => clearInterval(interval)
  }, [router])

  return <>{children}</>
}
```

---

### Phase 3: Agent Interaction 🔄 BLOCKED BY PHASE 2

#### Task 8: Build Chat Interface for Task Creation ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 1 hour
**Blocked By:** Task 7

**Description:**
Create chat page with input for sending messages to agent (creating tasks).

**Acceptance Criteria:**
- [ ] `app/chat/page.tsx` created
- [ ] Text input at bottom of page
- [ ] Send button (Enter key also works)
- [ ] Message history display (simple list)
- [ ] Visual distinction: user messages vs system responses

**Test:**
1. Visit `/chat`
2. Type "Test task" and hit Enter
3. Verify input clears and message appears in history

**Files to Create:**
- `app/chat/page.tsx`
- `components/ChatInput.tsx`
- `components/MessageList.tsx`

**Components Needed:**
```bash
npx shadcn-ui@latest add textarea
```

---

#### Task 9: Implement Task Creation Server Action ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 45 mins
**Blocked By:** Task 8

**Description:**
Connect chat input to `createTask` Server Action.

**Acceptance Criteria:**
- [ ] Form submission calls `createTask(content, title)`
- [ ] Creates markdown file in `Vault/Needs_Action/`
- [ ] Filename format: `Task_WebUI_YYYY-MM-DDTHH-mm-ss-SSSZ.md`
- [ ] Frontmatter includes: source=webui, created timestamp
- [ ] Returns success/error message
- [ ] Error handling displays to user

**Test:**
1. Submit message in chat: "Research Next.js performance"
2. Check `Vault/Needs_Action/` for new file
3. Verify file contains correct content and frontmatter

**Example File Created:**
```markdown
---
source: webui
priority: medium
created: 2026-01-17T10:30:00Z
status: pending
---

# Research Next.js performance

[Message content here]
```

**Files to Modify:**
- `lib/actions.ts` (add createTask function)

---

#### Task 10: Add Optimistic UI Updates ⏳
**Status:** BLOCKED
**Priority:** P2
**Estimated Effort:** 30 mins
**Blocked By:** Task 9

**Description:**
Show task immediately in chat history before server response.

**Acceptance Criteria:**
- [ ] User message appears instantly (optimistic)
- [ ] Success confirmation appears after Server Action completes
- [ ] Error message if Server Action fails
- [ ] Failed messages show retry button

**Test:**
1. Submit task in chat
2. Verify message appears immediately (not waiting for server)
3. Verify success confirmation appears after ~500ms

**Implementation:**
```typescript
const [optimisticMessages, addOptimisticMessage] = useOptimistic(messages)

// On submit:
addOptimisticMessage(newMessage)
await createTask(content, title)
```

---

### Phase 4: Skills Catalog 🔄 BLOCKED BY PHASE 3

#### Task 11: Parse SKILLS-INDEX.md ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 45 mins
**Blocked By:** Task 10

**Description:**
Implement `getSkills()` Server Action to parse skills index file.

**Acceptance Criteria:**
- [ ] Reads `.claude/skills/SKILLS-INDEX.md`
- [ ] Parses markdown list format
- [ ] Extracts skill name and description
- [ ] Categorizes: "Custom Skills" vs "Built-in Skills"
- [ ] Returns array of Skill objects
- [ ] Handles missing file gracefully

**Test:**
```typescript
const skills = await getSkills()
console.log(skills)
// Expected: Array of {name, description, category}
```

**Files to Modify:**
- `lib/actions.ts` (add getSkills function)
- `lib/skills.ts` (parsing utilities)

**Parsing Logic:**
- Look for section headers: `## Custom Skills` vs `## Built-in Skills`
- Parse list items: `- skill-name: description`

---

#### Task 12: Display Skills in Grid View ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 45 mins
**Blocked By:** Task 11

**Description:**
Create skills page to display all agent skills.

**Acceptance Criteria:**
- [ ] `app/skills/page.tsx` created
- [ ] Fetches skills using `getSkills()`
- [ ] Displays in responsive grid (3 columns desktop, 1 mobile)
- [ ] SkillCard shows name, description, category badge
- [ ] Search/filter input (filter by name or description)
- [ ] Empty state if no skills found

**Test:**
1. Visit `/skills`
2. Verify all skills from SKILLS-INDEX.md appear
3. Test search input filters correctly

**Files to Create:**
- `app/skills/page.tsx`
- `components/SkillCard.tsx`

---

### Phase 5: Polish & Testing 🔄 BLOCKED BY PHASE 4

#### Task 13: Add Loading States and Error Boundaries ⏳
**Status:** BLOCKED
**Priority:** P2
**Estimated Effort:** 1 hour
**Blocked By:** Task 12

**Description:**
Add proper loading states and error handling to all pages.

**Acceptance Criteria:**
- [ ] `loading.tsx` files for each route show skeleton UI
- [ ] `error.tsx` files show user-friendly error messages
- [ ] Error boundaries catch and display errors gracefully
- [ ] Retry button on error pages
- [ ] Loading spinners for async operations

**Test:**
1. Throttle network to slow 3G
2. Navigate to each page
3. Verify loading state appears
4. Simulate error (rename Vault folder temporarily)
5. Verify error page appears with retry button

**Files to Create:**
- `app/loading.tsx`
- `app/error.tsx`
- `app/tasks/loading.tsx`
- `app/tasks/error.tsx`
- `app/chat/loading.tsx`
- `app/chat/error.tsx`
- `app/skills/loading.tsx`
- `app/skills/error.tsx`

**Components Needed:**
```bash
npx shadcn-ui@latest add skeleton alert
```

---

#### Task 14: End-to-End Testing ⏳
**Status:** BLOCKED
**Priority:** P1
**Estimated Effort:** 1 hour
**Blocked By:** Task 13

**Description:**
Test all user scenarios from the spec.

**Test Scenarios:**

**Scenario 1: Task Dashboard**
1. Start with empty Vault/Needs_Action
2. Add test file manually
3. Visit `/tasks`
4. Verify task appears within 5 seconds
5. Move file to Vault/Done
6. Switch to "Completed" tab
7. Verify task appears in completed list

**Scenario 2: Agent Interaction**
1. Visit `/chat`
2. Type "Test task from UI"
3. Submit
4. Verify message appears immediately
5. Check Vault/Needs_Action for new file
6. Verify file has correct frontmatter and content

**Scenario 3: Skills Catalog**
1. Visit `/skills`
2. Verify all skills from SKILLS-INDEX.md appear
3. Test search/filter functionality
4. Verify custom skills are labeled separately

**Acceptance Criteria:**
- [ ] All scenarios pass
- [ ] No console errors
- [ ] Mobile responsive (test on 375px width)
- [ ] Lighthouse score > 90

---

#### Task 15: Documentation and README ⏳
**Status:** BLOCKED
**Priority:** P2
**Estimated Effort:** 30 mins
**Blocked By:** Task 14

**Description:**
Create README for frontend and update main project README.

**Acceptance Criteria:**
- [ ] `frontend/README.md` created with:
  - Setup instructions
  - Development commands
  - Environment variables
  - Architecture overview
  - Troubleshooting section
- [ ] Main `README.md` updated with frontend section
- [ ] Screenshots added to frontend README
- [ ] Environment variables documented in `.env.example`

**Files to Create:**
- `frontend/README.md`
- `frontend/.env.example`

**Files to Modify:**
- `README.md` (add frontend section)

**Environment Variables:**
```bash
# frontend/.env.example
VAULT_PATH=../Vault
SKILLS_INDEX_PATH=../.claude/skills/SKILLS-INDEX.md
NEXT_PUBLIC_POLL_INTERVAL=5000
```

---

## Progress Summary

### Overall Status: 0% Complete (Ready to Start)

**Phase Status:**
- ⏳ Phase 1: Foundation (0/4 tasks)
- ⏳ Phase 2: Task Dashboard (0/3 tasks)
- ⏳ Phase 3: Agent Interaction (0/3 tasks)
- ⏳ Phase 4: Skills Catalog (0/2 tasks)
- ⏳ Phase 5: Polish & Testing (0/3 tasks)

**Total: 0/15 tasks complete**

---

## Critical Path

1. Task 1: Initialize Next.js → Task 2: Shadcn UI → Task 3: Layout → Task 4: Server Actions
2. Task 4 → Task 5: Pending Tasks → Task 6: Completed Tasks → Task 7: Auto-refresh
3. Task 7 → Task 8: Chat UI → Task 9: Create Task Action → Task 10: Optimistic UI
4. Task 10 → Task 11: Parse Skills → Task 12: Display Skills
5. Task 12 → Task 13: Polish → Task 14: Testing → Task 15: Docs

---

## Dependencies

```
Task 1 (Init) ─┐
Task 2 (Shadcn)├─→ Task 3 (Layout) ─→ Task 4 (Actions)
               │
               └─→ [All other tasks depend on 1-4]

Task 4 ─→ Task 5 ─→ Task 6 ─→ Task 7
Task 7 ─→ Task 8 ─→ Task 9 ─→ Task 10
Task 10 ─→ Task 11 ─→ Task 12
Task 12 ─→ Task 13 ─→ Task 14 ─→ Task 15
```

---

## Next Steps

1. **Immediate:** Start Task 1 (Initialize Next.js Project)
2. **Then:** Complete Phase 1 (Tasks 1-4) in sequence
3. **After Phase 1:** Begin Phase 2 (Task Dashboard)
4. **Timeline:** All phases estimated at 9 hours total

---

## Notes

- Frontend runs independently from orchestrator
- No breaking changes to existing Vault structure
- All file I/O uses Node.js native APIs (no external dependencies)
- TypeScript ensures type safety across client/server boundary
