# Tasks: Abdullah Junior Mobile Companion App

## Overview

Actionable, dependency-ordered tasks for implementing the mobile companion app.

**Total Estimated Time:** 15-20 days
**Priority Levels:** P0 (Critical), P1 (Important), P2 (Nice-to-have)

---

## Phase 1: Foundation (3-4 days)

### TASK-001: Initialize Expo Project
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** None

**Acceptance Criteria:**
- [ ] Create new Expo project with TypeScript template
- [ ] Configure app.json with correct bundle ID and app name
- [ ] Verify project builds and runs on simulator/device
- [ ] Add to git with proper .gitignore

**Commands:**
```bash
npx create-expo-app@latest mobile --template expo-template-blank-typescript
cd mobile
npx expo start
```

---

### TASK-002: Configure NativeWind
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** TASK-001

**Acceptance Criteria:**
- [ ] Install nativewind and tailwindcss
- [ ] Configure babel.config.js for NativeWind
- [ ] Configure metro.config.js with NativeWind transformer
- [ ] Create tailwind.config.js matching web frontend colors
- [ ] Create global.css with Tailwind directives
- [ ] Verify utility classes work in a test component

**Files to Create/Modify:**
- `mobile/tailwind.config.js`
- `mobile/global.css`
- `mobile/babel.config.js`
- `mobile/metro.config.js`

---

### TASK-003: Set Up Expo Router Navigation
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** TASK-001, TASK-002

**Acceptance Criteria:**
- [ ] Install expo-router and dependencies
- [ ] Create app directory structure with tabs layout
- [ ] Implement root _layout.tsx with providers
- [ ] Implement (tabs)/_layout.tsx with 4 tabs
- [ ] Create placeholder screens for each tab
- [ ] Verify tab navigation works

**Directory Structure:**
```
mobile/app/
├── _layout.tsx
├── (tabs)/
│   ├── _layout.tsx
│   ├── index.tsx
│   ├── approvals.tsx
│   ├── chat.tsx
│   └── settings.tsx
```

---

### TASK-004: Create Base UI Components
**Priority:** P0
**Estimate:** 4 hours
**Dependencies:** TASK-002

**Acceptance Criteria:**
- [ ] Create Button component with variants (primary, secondary, ghost)
- [ ] Create Card component with dark styling
- [ ] Create Badge component for priority/status
- [ ] Create Input component for text entry
- [ ] Create LoadingSkeleton component
- [ ] Document components with examples

**Files to Create:**
- `mobile/components/ui/Button.tsx`
- `mobile/components/ui/Card.tsx`
- `mobile/components/ui/Badge.tsx`
- `mobile/components/ui/Input.tsx`
- `mobile/components/ui/LoadingSkeleton.tsx`

---

### TASK-005: Implement Design System Constants
**Priority:** P0
**Estimate:** 1 hour
**Dependencies:** TASK-002

**Acceptance Criteria:**
- [ ] Create colors.ts with full color palette matching web
- [ ] Create typography.ts with font sizes and weights
- [ ] Create spacing.ts with consistent spacing values
- [ ] Export all constants from index file

**Files to Create:**
- `mobile/constants/colors.ts`
- `mobile/constants/typography.ts`
- `mobile/constants/index.ts`

---

### TASK-006: Create API Service
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** TASK-001

**Acceptance Criteria:**
- [ ] Install axios
- [ ] Create api.ts with base configuration
- [ ] Implement dynamic base URL from AsyncStorage
- [ ] Add all API methods matching backend endpoints
- [ ] Create TypeScript types for API responses
- [ ] Add health check endpoint call

**Files to Create:**
- `mobile/services/api.ts`
- `mobile/types/api.ts`
- `mobile/types/task.ts`

---

### TASK-007: Set Up TanStack Query
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** TASK-001, TASK-006

**Acceptance Criteria:**
- [ ] Install @tanstack/react-query
- [ ] Create QueryClient with default options
- [ ] Add QueryClientProvider to root layout
- [ ] Create useApprovals hook
- [ ] Create useDashboard hook
- [ ] Verify data fetching works

**Files to Create:**
- `mobile/hooks/useApprovals.ts`
- `mobile/hooks/useDashboard.ts`

---

## Phase 2: Core Features (4-5 days)

### TASK-008: Build Dashboard Screen
**Priority:** P0
**Estimate:** 4 hours
**Dependencies:** TASK-003, TASK-004, TASK-007

**Acceptance Criteria:**
- [ ] Create StatsCard component for metrics
- [ ] Display pending approvals count
- [ ] Display completed today count
- [ ] Display urgent items with badge
- [ ] Show agent status indicator (mock for now)
- [ ] Implement pull-to-refresh
- [ ] Add loading skeletons

**Files to Create:**
- `mobile/components/dashboard/StatsCard.tsx`
- `mobile/components/dashboard/AgentStatusCard.tsx`
- Modify `mobile/app/(tabs)/index.tsx`

---

### TASK-009: Build Activity Feed Component
**Priority:** P1
**Estimate:** 3 hours
**Dependencies:** TASK-008

**Acceptance Criteria:**
- [ ] Create ActivityFeed component
- [ ] Fetch recent activity from API (or logs)
- [ ] Display activity items with timestamps
- [ ] Show actor, action, and result
- [ ] Auto-scroll to latest
- [ ] Style with monospace font

**Files to Create:**
- `mobile/components/dashboard/ActivityFeed.tsx`

---

### TASK-010: Build Approvals List Screen
**Priority:** P0
**Estimate:** 4 hours
**Dependencies:** TASK-003, TASK-004, TASK-007

**Acceptance Criteria:**
- [ ] Create ApprovalCard component
- [ ] Display list of pending approvals
- [ ] Show title, source, priority, description preview
- [ ] Show risk and complexity scores
- [ ] Implement pull-to-refresh
- [ ] Add empty state when no approvals
- [ ] Add loading state with skeletons

**Files to Create:**
- `mobile/components/approvals/ApprovalCard.tsx`
- `mobile/components/approvals/PriorityBadge.tsx`
- Modify `mobile/app/(tabs)/approvals.tsx`

---

### TASK-011: Implement Approve/Reject API Calls
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** TASK-010

**Acceptance Criteria:**
- [ ] Create useApproveTask mutation hook
- [ ] Create useRejectTask mutation hook
- [ ] Implement optimistic UI updates
- [ ] Handle rollback on error
- [ ] Show success/error toast
- [ ] Invalidate queries after mutation

**Files to Modify:**
- `mobile/hooks/useApprovals.ts`

---

### TASK-012: Create Approval Detail Screen
**Priority:** P1
**Estimate:** 3 hours
**Dependencies:** TASK-010, TASK-011

**Acceptance Criteria:**
- [ ] Create approval/[id].tsx dynamic route
- [ ] Fetch full task details
- [ ] Display complete description
- [ ] Show all metadata (source, created, priority, risk)
- [ ] Add Approve and Reject buttons
- [ ] Navigate back after action

**Files to Create:**
- `mobile/app/approval/[id].tsx`

---

### TASK-013: Add Haptic Feedback
**Priority:** P1
**Estimate:** 1 hour
**Dependencies:** TASK-011

**Acceptance Criteria:**
- [ ] Install expo-haptics
- [ ] Add light haptic on button press
- [ ] Add medium haptic on approve/reject
- [ ] Add success haptic on confirmation
- [ ] Make haptics configurable in settings

**Files to Create:**
- `mobile/utils/haptics.ts`

---

## Phase 3: Push Notifications (3-4 days)

### TASK-014: Set Up Firebase Project
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** None

**Acceptance Criteria:**
- [ ] Create Firebase project in console
- [ ] Add Android app with package name
- [ ] Add iOS app with bundle ID
- [ ] Download google-services.json
- [ ] Download GoogleService-Info.plist
- [ ] Generate service account key for backend
- [ ] Enable Cloud Messaging API

**Deliverables:**
- `mobile/google-services.json`
- `mobile/GoogleService-Info.plist`
- `config/firebase-service-account.json`

---

### TASK-015: Configure Expo for FCM
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** TASK-014

**Acceptance Criteria:**
- [ ] Install expo-notifications and expo-device
- [ ] Add notification plugin to app.json
- [ ] Configure Android googleServicesFile
- [ ] Configure iOS googleServicesFile
- [ ] Add iOS background modes for notifications
- [ ] Create EAS build configuration

**Files to Modify:**
- `mobile/app.json`
- Create `mobile/eas.json`

---

### TASK-016: Implement FCM Token Retrieval
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** TASK-015

**Acceptance Criteria:**
- [ ] Create useNotifications hook
- [ ] Request notification permissions
- [ ] Get native FCM token (not Expo token)
- [ ] Create Android notification channels
- [ ] Handle token refresh
- [ ] Store token locally for debugging

**Files to Create:**
- `mobile/hooks/useNotifications.ts`
- `mobile/services/notifications.ts`

---

### TASK-017: Register FCM Token with Backend
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** TASK-016, TASK-006

**Acceptance Criteria:**
- [ ] Create usePushSubscription hook
- [ ] Send FCM token to /api/notifications/subscribe
- [ ] Include device name in registration
- [ ] Handle registration errors
- [ ] Re-register on token refresh

**Files to Create:**
- `mobile/hooks/usePushSubscription.ts`

---

### TASK-018: Add FCM Support to Backend
**Priority:** P0
**Estimate:** 4 hours
**Dependencies:** TASK-014

**Acceptance Criteria:**
- [ ] Install firebase-admin package
- [ ] Create firebase_config.py with initialization
- [ ] Add send_fcm_notification method to push_service.py
- [ ] Extend SubscriptionRequest model for FCM tokens
- [ ] Detect token type (Web Push vs FCM)
- [ ] Route to appropriate send method
- [ ] Test FCM delivery

**Files to Create:**
- `src/notifications/firebase_config.py`

**Files to Modify:**
- `src/notifications/push_service.py`
- `src/notifications/api.py`
- `requirements.txt` (add firebase-admin)

---

### TASK-019: Implement Notification Tap Handling
**Priority:** P0
**Estimate:** 2 hours
**Dependencies:** TASK-016, TASK-012

**Acceptance Criteria:**
- [ ] Set up notification response listener
- [ ] Extract task ID from notification data
- [ ] Navigate to /approval/[id] on tap
- [ ] Handle notification when app is killed
- [ ] Handle notification when app is background
- [ ] Handle notification when app is foreground

**Files to Modify:**
- `mobile/services/notifications.ts`
- `mobile/app/_layout.tsx`

---

### TASK-020: Create Notification Channels (Android)
**Priority:** P1
**Estimate:** 1 hour
**Dependencies:** TASK-016

**Acceptance Criteria:**
- [ ] Create "Approvals" channel (high importance)
- [ ] Create "Suggestions" channel (default importance)
- [ ] Create "Digest" channel (low importance)
- [ ] Set custom sound for approvals
- [ ] Set vibration pattern

**Files to Modify:**
- `mobile/services/notifications.ts`

---

## Phase 4: Enhanced UX (3-4 days)

### TASK-021: Implement Swipe Gestures
**Priority:** P0
**Estimate:** 4 hours
**Dependencies:** TASK-010, TASK-011

**Acceptance Criteria:**
- [ ] Install react-native-gesture-handler
- [ ] Install react-native-reanimated
- [ ] Create SwipeableRow wrapper component
- [ ] Swipe right reveals green "Approve" background
- [ ] Swipe left reveals red "Reject" background
- [ ] Trigger action when swipe passes threshold
- [ ] Animate card off-screen on action
- [ ] Trigger haptic at threshold

**Files to Create:**
- `mobile/components/approvals/SwipeableRow.tsx`

**Files to Modify:**
- `mobile/app/(tabs)/approvals.tsx`

---

### TASK-022: Create Agent Avatar Component
**Priority:** P1
**Estimate:** 2 hours
**Dependencies:** TASK-004

**Acceptance Criteria:**
- [ ] Create AgentAvatar with pulse animation
- [ ] Show glow effect when active
- [ ] Show status indicator dot (green/red)
- [ ] Animate scale on pulse
- [ ] Make animation configurable

**Files to Create:**
- `mobile/components/agent/AgentAvatar.tsx`

---

### TASK-023: Create Typing Indicator
**Priority:** P1
**Estimate:** 1 hour
**Dependencies:** TASK-004

**Acceptance Criteria:**
- [ ] Create AgentTypingIndicator component
- [ ] Three dots with staggered bounce animation
- [ ] Match design system colors
- [ ] Smooth enter/exit animation

**Files to Create:**
- `mobile/components/agent/AgentTypingIndicator.tsx`

---

### TASK-024: Build Agent Chat Screen
**Priority:** P1
**Estimate:** 4 hours
**Dependencies:** TASK-003, TASK-022, TASK-023

**Acceptance Criteria:**
- [ ] Create chat screen layout
- [ ] Display message bubbles (user right, agent left)
- [ ] Show typing indicator when waiting
- [ ] Implement message input with send button
- [ ] Store chat history locally
- [ ] Add quick action chips

**Files to Create:**
- `mobile/components/agent/AgentMessage.tsx`
- `mobile/components/agent/ChatInput.tsx`
- `mobile/components/agent/QuickActionChips.tsx`

**Files to Modify:**
- `mobile/app/(tabs)/chat.tsx`

---

### TASK-025: Implement Offline Queue
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** TASK-011

**Acceptance Criteria:**
- [ ] Install @react-native-community/netinfo
- [ ] Create offlineQueueStore with Zustand
- [ ] Persist queue to AsyncStorage
- [ ] Queue approve/reject when offline
- [ ] Show "pending sync" indicator
- [ ] Process queue when network restored
- [ ] Handle retry logic (max 3 attempts)

**Files to Create:**
- `mobile/stores/offlineQueueStore.ts`
- `mobile/hooks/useNetworkStatus.ts`
- `mobile/hooks/useOfflineQueue.ts`

---

### TASK-026: Add Offline Indicator
**Priority:** P1
**Estimate:** 1 hour
**Dependencies:** TASK-025

**Acceptance Criteria:**
- [ ] Show banner when offline
- [ ] Show queued action count
- [ ] Animate banner appearance
- [ ] Auto-hide when back online

**Files to Create:**
- `mobile/components/shared/OfflineBanner.tsx`

---

### TASK-027: Build Settings Screen
**Priority:** P1
**Estimate:** 3 hours
**Dependencies:** TASK-003, TASK-004

**Acceptance Criteria:**
- [ ] Create settings screen layout
- [ ] Add backend URL input
- [ ] Add notification toggles by category
- [ ] Add theme selector (Dark/Light/System)
- [ ] Show connection status
- [ ] Show FCM token (for debugging)
- [ ] Add version info

**Files to Create:**
- `mobile/stores/settingsStore.ts`

**Files to Modify:**
- `mobile/app/(tabs)/settings.tsx`

---

## Phase 5: Telegram Bot (2 days)

### TASK-028: Create Telegram Bot
**Priority:** P1
**Estimate:** 1 hour
**Dependencies:** None

**Acceptance Criteria:**
- [ ] Create bot via @BotFather
- [ ] Set bot name and description
- [ ] Get bot token
- [ ] Get personal chat ID
- [ ] Add to .env.example

**Deliverables:**
- Bot token
- Chat ID
- Updated .env.example

---

### TASK-029: Implement Telegram Notifier
**Priority:** P1
**Estimate:** 3 hours
**Dependencies:** TASK-028

**Acceptance Criteria:**
- [ ] Install python-telegram-bot
- [ ] Create TelegramNotifier class
- [ ] Implement send_approval_request with inline buttons
- [ ] Implement send_digest for daily summary
- [ ] Handle button callbacks (approve/reject)
- [ ] Integrate with notification service

**Files to Create:**
- `src/notifications/telegram_bot.py`

**Files to Modify:**
- `src/notifications/push_service.py`
- `requirements.txt`

---

### TASK-030: Add Telegram Commands
**Priority:** P2
**Estimate:** 2 hours
**Dependencies:** TASK-029

**Acceptance Criteria:**
- [ ] Implement /status command
- [ ] Implement /pending command
- [ ] Implement /approve {id} command
- [ ] Implement /reject {id} command
- [ ] Add help text

**Files to Modify:**
- `src/notifications/telegram_bot.py`

---

## Phase 6: Polish (2-3 days)

### TASK-031: Add Error Boundaries
**Priority:** P1
**Estimate:** 2 hours
**Dependencies:** All Phase 2

**Acceptance Criteria:**
- [ ] Create ErrorBoundary component
- [ ] Wrap screens with error boundary
- [ ] Show friendly error message
- [ ] Add "Try Again" button
- [ ] Log errors for debugging

**Files to Create:**
- `mobile/components/shared/ErrorBoundary.tsx`

---

### TASK-032: Create Empty States
**Priority:** P1
**Estimate:** 2 hours
**Dependencies:** TASK-010, TASK-008

**Acceptance Criteria:**
- [ ] Create EmptyState component
- [ ] Add illustration/icon
- [ ] Show message and optional action
- [ ] Use for: no approvals, no activity, no chat history

**Files to Create:**
- `mobile/components/shared/EmptyState.tsx`

---

### TASK-033: Accessibility Improvements
**Priority:** P1
**Estimate:** 3 hours
**Dependencies:** All Phase 4

**Acceptance Criteria:**
- [ ] Add accessibilityLabel to all interactive elements
- [ ] Add accessibilityHint where helpful
- [ ] Ensure 44x44 touch targets
- [ ] Test with screen reader
- [ ] Verify color contrast

---

### TASK-034: Performance Optimization
**Priority:** P2
**Estimate:** 2 hours
**Dependencies:** All Phase 4

**Acceptance Criteria:**
- [ ] Memoize expensive components
- [ ] Optimize FlatList with keyExtractor
- [ ] Add lazy loading for chat history
- [ ] Profile and fix any jank

---

### TASK-035: Write Documentation
**Priority:** P1
**Estimate:** 2 hours
**Dependencies:** All previous tasks

**Acceptance Criteria:**
- [ ] Create mobile/README.md
- [ ] Document setup instructions
- [ ] Document Firebase configuration
- [ ] Document environment variables
- [ ] Add screenshots

**Files to Create:**
- `mobile/README.md`

---

### TASK-036: Create Build and Deploy
**Priority:** P0
**Estimate:** 3 hours
**Dependencies:** All previous tasks

**Acceptance Criteria:**
- [ ] Configure EAS Build
- [ ] Create development build for testing
- [ ] Create preview build for stakeholders
- [ ] Create production build
- [ ] Document build process

**Files to Create/Modify:**
- `mobile/eas.json`
- `mobile/README.md`

---

## Task Dependencies Graph

```
TASK-001 (Init)
    │
    ├── TASK-002 (NativeWind)
    │       │
    │       ├── TASK-003 (Router)
    │       │       │
    │       │       ├── TASK-008 (Dashboard)
    │       │       │       └── TASK-009 (Activity)
    │       │       │
    │       │       ├── TASK-010 (Approvals List)
    │       │       │       └── TASK-011 (API Calls)
    │       │       │               └── TASK-012 (Detail)
    │       │       │               └── TASK-021 (Swipe)
    │       │       │               └── TASK-025 (Offline)
    │       │       │
    │       │       ├── TASK-024 (Chat)
    │       │       │
    │       │       └── TASK-027 (Settings)
    │       │
    │       ├── TASK-004 (UI Components)
    │       │       ├── TASK-022 (Avatar)
    │       │       └── TASK-023 (Typing)
    │       │
    │       └── TASK-005 (Constants)
    │
    ├── TASK-006 (API Service)
    │       └── TASK-007 (TanStack Query)
    │
    └── TASK-014 (Firebase Project)
            ├── TASK-015 (Expo FCM Config)
            │       └── TASK-016 (Token Retrieval)
            │               ├── TASK-017 (Register Backend)
            │               ├── TASK-019 (Tap Handling)
            │               └── TASK-020 (Channels)
            │
            └── TASK-018 (Backend FCM)

TASK-028 (Create Telegram Bot)
    └── TASK-029 (Telegram Notifier)
            └── TASK-030 (Commands)
```

---

## Summary

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| Foundation | TASK-001 to TASK-007 | 3-4 days |
| Core Features | TASK-008 to TASK-013 | 4-5 days |
| Push Notifications | TASK-014 to TASK-020 | 3-4 days |
| Enhanced UX | TASK-021 to TASK-027 | 3-4 days |
| Telegram Bot | TASK-028 to TASK-030 | 2 days |
| Polish | TASK-031 to TASK-036 | 2-3 days |
| **Total** | **36 tasks** | **15-20 days** |
