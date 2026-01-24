# Feature Specification: Abdullah Junior Mobile Companion App

## Overview

**Feature Name:** Abdullah Junior Mobile Companion App
**Version:** 1.0.0
**Status:** Approved
**Created:** 2026-01-24
**Author:** Claude (AI Architect)

---

## Executive Summary

Build a beautiful, agentic React Native mobile application that serves as a companion to the Digital FTE (Full-Time Equivalent) Personal AI Employee system. The app enables users to receive push notifications for approval requests, review and approve/reject tasks on-the-go, monitor agent status, and interact with the AI assistant through a conversational interface.

---

## Problem Statement

### Current Pain Points

1. **Approval Friction**: Users must be at their computer to approve pending tasks in the Obsidian vault
2. **Delayed Response**: Critical approvals (payments, emails, social posts) wait until laptop access
3. **No Mobile Visibility**: Cannot monitor agent status or activity from mobile devices
4. **Notification Gap**: Existing Web Push notifications don't work reliably on mobile browsers

### Business Impact

- Approval delays reduce the "always-on" value proposition of the Digital FTE
- Users miss time-sensitive opportunities (client emails, social engagement windows)
- System appears less autonomous when approvals pile up

---

## Solution

A native mobile app with:

1. **Push Notifications** via Firebase Cloud Messaging (FCM) for reliable, instant alerts
2. **Quick Approval Workflow** with swipe gestures for approve/reject
3. **Real-time Dashboard** showing agent status and activity
4. **Conversational Interface** to command the agent
5. **Telegram Bot Fallback** for when the app isn't installed

---

## User Stories

### Primary User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|--------------|------------|----------|
| US-001 | User | Receive push notifications for pending approvals | I can respond quickly from anywhere | P0 |
| US-002 | User | Approve or reject tasks with a swipe | I can process approvals in seconds | P0 |
| US-003 | User | See how many approvals are pending | I know if I need to take action | P0 |
| US-004 | User | View agent activity in real-time | I know what the system is doing | P1 |
| US-005 | User | Configure which notifications I receive | I'm not overwhelmed with alerts | P1 |
| US-006 | User | Command the agent via chat | I can delegate tasks from my phone | P2 |
| US-007 | User | Use the app offline and sync later | I can approve even without signal | P2 |

### Edge Cases

| ID | Scenario | Expected Behavior |
|----|----------|-------------------|
| EC-001 | App in background/killed | FCM delivers notification; tap opens relevant screen |
| EC-002 | No network connectivity | Queue actions locally; sync when online |
| EC-003 | Backend unreachable | Show cached data; indicate offline status |
| EC-004 | Approval already processed | Show error toast; refresh list |
| EC-005 | Multiple devices registered | All devices receive notifications |

---

## Functional Requirements

### FR-001: Push Notifications

| Requirement | Description |
|-------------|-------------|
| FR-001.1 | Register device with Firebase Cloud Messaging on app launch |
| FR-001.2 | Send FCM token to backend for storage |
| FR-001.3 | Receive notifications when app is foreground, background, or terminated |
| FR-001.4 | Display notification with task title, priority badge, and description preview |
| FR-001.5 | Navigate to approval detail screen when notification is tapped |
| FR-001.6 | Create Android notification channels (Approvals, Suggestions, Digest) |
| FR-001.7 | Support iOS notification permissions and badges |

### FR-002: Approval Workflow

| Requirement | Description |
|-------------|-------------|
| FR-002.1 | Display list of pending approval tasks from `/api/tasks?folder=Pending_Approval` |
| FR-002.2 | Show task title, source, priority, risk score, and description preview |
| FR-002.3 | Swipe right to approve with green background reveal |
| FR-002.4 | Swipe left to reject with red background reveal |
| FR-002.5 | Trigger haptic feedback when swipe passes approval threshold |
| FR-002.6 | Call `POST /api/tasks/{id}/approve` on approval action |
| FR-002.7 | Optimistically update UI before server response |
| FR-002.8 | Rollback on server error with error toast |
| FR-002.9 | Support pull-to-refresh for manual refresh |

### FR-003: Dashboard

| Requirement | Description |
|-------------|-------------|
| FR-003.1 | Display pending approval count prominently |
| FR-003.2 | Show tasks completed today count |
| FR-003.3 | Display urgent items count with red badge |
| FR-003.4 | Show agent connection status (online/offline) with animated indicator |
| FR-003.5 | Display recent activity feed (last 10 actions) |
| FR-003.6 | Auto-refresh dashboard data every 30 seconds |

### FR-004: Agent Chat

| Requirement | Description |
|-------------|-------------|
| FR-004.1 | Display conversational interface with message bubbles |
| FR-004.2 | Show typing indicator when agent is processing |
| FR-004.3 | Support sending text commands to the agent |
| FR-004.4 | Display agent responses with typing animation effect |
| FR-004.5 | Show quick action chips for common commands |
| FR-004.6 | Persist chat history locally |

### FR-005: Settings

| Requirement | Description |
|-------------|-------------|
| FR-005.1 | Allow configuring backend server URL |
| FR-005.2 | Toggle notification categories (Approvals, Suggestions, Digest) |
| FR-005.3 | Configure quiet hours for notifications |
| FR-005.4 | Display connection status and last sync time |
| FR-005.5 | Show FCM token for debugging |
| FR-005.6 | Support theme selection (Dark/Light/System) |

### FR-006: Offline Support

| Requirement | Description |
|-------------|-------------|
| FR-006.1 | Queue approve/reject actions when offline |
| FR-006.2 | Display queued actions with "pending sync" indicator |
| FR-006.3 | Automatically process queue when network restored |
| FR-006.4 | Persist queue to device storage |
| FR-006.5 | Show offline indicator in header |

### FR-007: Telegram Bot Fallback

| Requirement | Description |
|-------------|-------------|
| FR-007.1 | Send approval requests to Telegram with inline buttons |
| FR-007.2 | Support /status command to show pending count |
| FR-007.3 | Support /pending command to list pending approvals |
| FR-007.4 | Process approve/reject button callbacks |
| FR-007.5 | Send daily digest message at 9 AM |

---

## Non-Functional Requirements

### NFR-001: Performance

| Requirement | Target |
|-------------|--------|
| App launch time | < 2 seconds (cold start) |
| Time to interactive | < 3 seconds |
| Approval action response | < 500ms (optimistic UI) |
| Pull-to-refresh completion | < 2 seconds |
| Animation frame rate | 60 FPS |

### NFR-002: Reliability

| Requirement | Target |
|-------------|--------|
| Push notification delivery | > 99% (FCM SLA) |
| Offline queue persistence | 100% (no data loss) |
| Crash-free sessions | > 99.5% |
| API call success rate | > 99% (with retries) |

### NFR-003: Security

| Requirement | Description |
|-------------|-------------|
| NFR-003.1 | Store FCM token securely in device keychain |
| NFR-003.2 | Use HTTPS for all API communications |
| NFR-003.3 | No sensitive data in notification payloads (title/preview only) |
| NFR-003.4 | Implement certificate pinning (optional Phase 2) |

### NFR-004: Accessibility

| Requirement | Description |
|-------------|-------------|
| NFR-004.1 | Minimum touch target size of 44x44 points |
| NFR-004.2 | Support screen reader labels on all interactive elements |
| NFR-004.3 | Sufficient color contrast (WCAG AA) |
| NFR-004.4 | Support dynamic type sizes |

### NFR-005: Compatibility

| Requirement | Target |
|-------------|--------|
| iOS version | iOS 15+ |
| Android version | Android 10+ (API 29) |
| Screen sizes | 4.7" to 6.7" phones |
| Orientation | Portrait only |

---

## Design Requirements

### Visual Identity

- **Theme**: Dark-first design matching existing web dashboard
- **Primary Color**: Blue-600 (#2563eb)
- **Background**: Zinc-950 (#09090b)
- **Card Background**: Zinc-900 (#18181b)
- **Typography**: Inter (UI), JetBrains Mono (code/logs)

### Navigation

- Bottom tab bar with 4 tabs: Dashboard, Approvals, Chat, Settings
- Floating action button for quick command input
- Gesture-based navigation (swipe to approve/reject)

### Animations

- Agent avatar pulse animation (breathing effect)
- Swipe reveal with spring physics
- Typing indicator (bouncing dots)
- Card enter/exit with fade and slide
- Success/error feedback animations

---

## API Dependencies

### Existing Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List tasks by folder |
| `/api/tasks/{id}` | GET | Get task details |
| `/api/tasks/{id}/approve` | POST | Approve or reject task |
| `/api/dashboard` | GET | Get dashboard summary |
| `/api/health` | GET | Health check |
| `/api/notifications/subscribe` | POST | Register push subscription |
| `/api/notifications/vapid-public-key` | GET | Get VAPID key |

### New Endpoints Required

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message to agent |
| `/api/chat/history` | GET | Get chat history |

### Backend Modifications

1. Add Firebase Admin SDK for FCM
2. Extend subscription model for FCM tokens
3. Add Telegram bot integration

---

## Dependencies

### External Services

| Service | Purpose | Credentials Required |
|---------|---------|---------------------|
| Firebase Cloud Messaging | Push notifications | Service account JSON |
| Google Cloud Platform | Hosting (optional) | GCP project |
| Telegram Bot API | Fallback notifications | Bot token |

### Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| expo | ~54.0.0 | Framework |
| expo-notifications | ~0.30.0 | Push notifications |
| expo-router | ~4.0.0 | Navigation |
| nativewind | ^4.1.0 | Tailwind styling |
| @tanstack/react-query | ^5.0.0 | Data fetching |
| zustand | ^5.0.0 | State management |
| react-native-reanimated | ~3.17.0 | Animations |
| react-native-gesture-handler | ~2.21.0 | Gestures |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Approval response time | < 5 minutes (P90) | Time from notification to action |
| Daily active users | 100% of registered users | Analytics |
| Notification tap rate | > 60% | FCM analytics |
| Offline queue success | 100% sync rate | Error logging |
| App Store rating | > 4.5 stars | Store metrics |

---

## Out of Scope

1. **Voice commands** - Planned for Phase 2
2. **iPad/Tablet support** - Portrait phone only
3. **Multi-user accounts** - Single user per device
4. **End-to-end encryption** - Not required for MVP
5. **Biometric authentication** - Optional Phase 2
6. **Widgets (iOS/Android)** - Planned for Phase 2

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FCM delivery delays | Low | Medium | Telegram fallback channel |
| iOS App Store rejection | Medium | High | Follow HIG guidelines; no hidden features |
| Backend API changes | Low | Medium | Version API endpoints |
| Firebase quota limits | Low | Low | Monitor usage; upgrade if needed |
| Expo SDK issues | Low | Medium | Pin to stable version; test thoroughly |

---

## Acceptance Criteria

### MVP (Phase 1)

- [ ] User can install app from APK/TestFlight
- [ ] User receives push notification for pending approval
- [ ] User can approve/reject with swipe gesture
- [ ] User sees dashboard with pending count
- [ ] App works offline and syncs when online
- [ ] Telegram bot sends approval requests

### Full Release

- [ ] All functional requirements implemented
- [ ] Performance targets met
- [ ] Accessibility requirements met
- [ ] Both iOS and Android builds pass store review
- [ ] Documentation complete

---

## Appendix

### Wireframes

See `/specs/009-mobile-companion-app/wireframes/` for screen mockups.

### API Response Examples

```json
// GET /api/tasks?folder=Pending_Approval
{
  "tasks": [
    {
      "id": "LinkedIn_2026-01-23_20-55_weekly_update",
      "title": "LinkedIn Post: Weekly Update",
      "description": "Prepared a LinkedIn post about...",
      "priority": "medium",
      "source": "ceo_briefing",
      "risk_score": 0.3,
      "complexity_score": 0.2,
      "created_at": "2026-01-23T20:55:20Z"
    }
  ],
  "count": 1
}
```

### Notification Payload

```json
{
  "notification": {
    "title": "Approval Required",
    "body": "LinkedIn Post: Weekly Update"
  },
  "data": {
    "type": "approval_request",
    "taskId": "LinkedIn_2026-01-23_20-55_weekly_update",
    "priority": "medium"
  }
}
```
