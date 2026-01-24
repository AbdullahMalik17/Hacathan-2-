# Research: Abdullah Junior Mobile Companion App

## Overview

This document captures research findings, technology evaluations, and reference implementations for the mobile companion app.

---

## 1. Push Notification Technologies

### 1.1 Firebase Cloud Messaging (FCM)

**Official Documentation:** https://firebase.google.com/docs/cloud-messaging

**Key Findings:**

1. **Delivery Reliability**: FCM has >99% delivery rate with proper implementation
2. **Token Refresh**: Tokens can change; must handle `onTokenRefresh` callback
3. **Payload Limits**: Notification payload max 4KB; data payload max 4KB
4. **Background Handling**: Android requires notification channel; iOS requires background modes
5. **iOS Specifics**: FCM routes through APNs; requires APNs certificate in Firebase console

**Expo Integration:**
```typescript
// expo-notifications can get native FCM token
import * as Notifications from 'expo-notifications';

// This returns the native FCM/APNs token, NOT Expo push token
const token = await Notifications.getDevicePushTokenAsync();
// token.data = "fcm_token_string_here"
```

**Backend Integration (Python):**
```python
# firebase-admin package
pip install firebase-admin

# Initialize with service account
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("path/to/serviceAccount.json")
firebase_admin.initialize_app(cred)

# Send message
message = messaging.Message(
    notification=messaging.Notification(title="Title", body="Body"),
    token="device_fcm_token"
)
response = messaging.send(message)
```

### 1.2 Alternative: Expo Push Notifications

**Documentation:** https://docs.expo.dev/push-notifications/overview/

**Pros:**
- Simpler setup (no Firebase project needed)
- Handles both iOS and Android uniformly
- Free for reasonable usage

**Cons:**
- Goes through Expo's servers (privacy concern)
- Less control over notification customization
- Dependency on Expo infrastructure

**Decision:** Use FCM directly for production reliability and privacy.

### 1.3 Alternative: OneSignal

**Documentation:** https://documentation.onesignal.com/docs

**Pros:**
- Feature-rich dashboard
- A/B testing, segmentation
- React Native SDK available

**Cons:**
- Additional service dependency
- Free tier has limitations
- Overkill for single-user app

**Decision:** Not needed; FCM is sufficient for our use case.

---

## 2. React Native Framework Options

### 2.1 Expo (Recommended)

**Version:** SDK 54 (Latest stable)

**Documentation:** https://docs.expo.dev/

**Pros:**
- Faster development cycle (no native compilation for most changes)
- EAS Build for cloud-based iOS/Android builds
- Rich ecosystem of pre-built modules
- expo-notifications supports native FCM tokens
- TypeScript first-class support

**Cons:**
- Slightly larger app bundle (~5-10MB overhead)
- Some native modules require development builds
- Ejecting can be complex if needed

**Configuration for FCM:**
```json
// app.json
{
  "expo": {
    "plugins": [
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#2563eb"
        }
      ]
    ],
    "android": {
      "googleServicesFile": "./google-services.json"
    },
    "ios": {
      "googleServicesFile": "./GoogleService-Info.plist"
    }
  }
}
```

### 2.2 Bare React Native

**Pros:**
- Full native control
- Smaller bundle size
- Direct native module access

**Cons:**
- Requires Xcode + Android Studio
- Slower iteration (native rebuild for changes)
- More complex CI/CD setup

**Decision:** Use Expo for faster development; can eject later if needed.

### 2.3 React Native with Ignite Boilerplate

**Documentation:** https://github.com/infinitered/ignite

**Pros:**
- Production-ready project structure
- Built-in state management, navigation
- Generator CLI for components

**Cons:**
- Opinionated structure
- Learning curve for generators
- May conflict with our design system

**Decision:** Not using; we have specific requirements that don't align.

---

## 3. UI Styling Approaches

### 3.1 NativeWind (Recommended)

**Version:** v4.x

**Documentation:** https://www.nativewind.dev/

**Pros:**
- Direct Tailwind CSS syntax in React Native
- Compiles to native StyleSheet (performant)
- Dark mode via `dark:` prefix
- Matches our web frontend exactly

**Cons:**
- Requires Babel + Metro configuration
- Some Tailwind utilities not supported
- Must use `className` prop (different from web `class`)

**Setup:**
```javascript
// babel.config.js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }]],
    plugins: ['nativewind/babel'],
  };
};

// metro.config.js
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');
const config = getDefaultConfig(__dirname);
module.exports = withNativeWind(config, { input: './global.css' });
```

### 3.2 Alternative: Tamagui

**Documentation:** https://tamagui.dev/

**Pros:**
- Cross-platform (web + native)
- Optimizing compiler
- Built-in components

**Cons:**
- Different syntax from Tailwind
- Would require relearning
- Doesn't match existing design system

**Decision:** NativeWind aligns better with existing Tailwind setup.

### 3.3 Alternative: React Native Paper

**Documentation:** https://callstack.github.io/react-native-paper/

**Pros:**
- Material Design components
- Accessibility built-in
- Theming support

**Cons:**
- Material Design aesthetic
- Doesn't match our dark theme
- Additional dependency

**Decision:** Building custom components with NativeWind for exact design match.

---

## 4. State Management

### 4.1 Zustand (Recommended for Client State)

**Version:** v5.x

**Documentation:** https://github.com/pmndrs/zustand

**Pros:**
- Tiny (1.2KB)
- Simple hook-based API
- Persist middleware for AsyncStorage
- No boilerplate (unlike Redux)

**Cons:**
- Less structured than Redux
- No built-in devtools (available as middleware)

**Persist Configuration:**
```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

const useStore = create(
  persist(
    (set) => ({
      offlineQueue: [],
      addToQueue: (action) => set((s) => ({
        offlineQueue: [...s.offlineQueue, action]
      })),
    }),
    {
      name: 'offline-queue',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

### 4.2 TanStack Query (Recommended for Server State)

**Version:** v5.x

**Documentation:** https://tanstack.com/query/latest

**Pros:**
- Automatic caching and background refetch
- Optimistic updates built-in
- Devtools available
- Query invalidation for related data

**Cons:**
- Learning curve for cache management
- Can be complex for simple cases

**Optimistic Update Pattern:**
```typescript
const mutation = useMutation({
  mutationFn: approveTask,
  onMutate: async (taskId) => {
    await queryClient.cancelQueries(['approvals']);
    const previous = queryClient.getQueryData(['approvals']);
    queryClient.setQueryData(['approvals'], (old) =>
      old.filter(t => t.id !== taskId)
    );
    return { previous };
  },
  onError: (_, __, context) => {
    queryClient.setQueryData(['approvals'], context.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries(['approvals']);
  },
});
```

### 4.3 Alternative: Redux Toolkit

**Pros:**
- Well-established patterns
- Excellent devtools
- RTK Query for server state

**Cons:**
- More boilerplate
- Larger bundle size (~12KB)
- Overkill for our needs

**Decision:** Zustand + TanStack Query provides better DX with smaller footprint.

---

## 5. Navigation

### 5.1 Expo Router (Recommended)

**Version:** v4.x

**Documentation:** https://docs.expo.dev/router/introduction/

**Pros:**
- File-based routing (like Next.js)
- Type-safe navigation
- Deep linking out of the box
- Tab and stack navigation built-in

**Cons:**
- Newer than React Navigation
- Some advanced patterns require workarounds

**Structure:**
```
app/
├── _layout.tsx       # Root layout
├── (tabs)/
│   ├── _layout.tsx   # Tab bar
│   ├── index.tsx     # Dashboard tab
│   └── approvals.tsx # Approvals tab
└── approval/[id].tsx # Dynamic route
```

### 5.2 Alternative: React Navigation

**Documentation:** https://reactnavigation.org/

**Pros:**
- Mature and battle-tested
- Extensive documentation
- More flexibility

**Cons:**
- More verbose configuration
- No file-based routing

**Decision:** Expo Router for modern DX and deep linking support.

---

## 6. Animations

### 6.1 React Native Reanimated (Recommended)

**Version:** v3.x

**Documentation:** https://docs.swmansion.com/react-native-reanimated/

**Pros:**
- 60 FPS animations on UI thread
- Gesture handler integration
- Layout animations
- Worklet-based (runs outside JS thread)

**Cons:**
- Learning curve for worklets
- Requires understanding of shared values

**Swipe Animation Example:**
```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

function SwipeableCard() {
  const translateX = useSharedValue(0);

  const gesture = Gesture.Pan()
    .onUpdate((e) => {
      translateX.value = e.translationX;
    })
    .onEnd(() => {
      if (translateX.value > 100) {
        // Approve
      } else {
        translateX.value = withSpring(0);
      }
    });

  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={style}>
        {/* Card content */}
      </Animated.View>
    </GestureDetector>
  );
}
```

### 6.2 Lottie for Success/Error Animations

**Documentation:** https://airbnb.io/lottie/

**Pros:**
- Complex animations from After Effects
- Small file size (JSON-based)
- Cross-platform

**Usage:**
```typescript
import LottieView from 'lottie-react-native';

<LottieView
  source={require('./success.json')}
  autoPlay
  loop={false}
  style={{ width: 100, height: 100 }}
/>
```

---

## 7. Offline Support Patterns

### 7.1 Offline Queue Pattern

**Reference:** https://tanstack.com/query/latest/docs/react/guides/offline-mode

**Implementation:**
1. Detect network status with `@react-native-community/netinfo`
2. If offline, queue action in Zustand (persisted to AsyncStorage)
3. Show "pending sync" indicator
4. When online, process queue sequentially
5. Handle conflicts (task already processed)

### 7.2 Optimistic UI Updates

**Pattern:**
1. Update UI immediately on action
2. Send request to server
3. On success: confirm (already reflected)
4. On error: rollback to previous state + show error

**Benefits:**
- Instant feedback to user
- Works naturally with offline queue

---

## 8. Telegram Bot Implementation

### 8.1 python-telegram-bot Library

**Version:** v20.x

**Documentation:** https://docs.python-telegram-bot.org/

**Pros:**
- Async-first (asyncio)
- Type hints
- Well-maintained

**Setup:**
```python
from telegram.ext import Application, CommandHandler

app = Application.builder().token("BOT_TOKEN").build()

async def status(update, context):
    await update.message.reply_text("System online!")

app.add_handler(CommandHandler("status", status))
app.run_polling()
```

### 8.2 Inline Keyboard Buttons

**Pattern for Approve/Reject:**
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{task_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{task_id}")
    ]
])

await bot.send_message(chat_id, text, reply_markup=keyboard)

# Handle callback
async def button_callback(update, context):
    query = update.callback_query
    await query.answer()

    action, task_id = query.data.split("_", 1)
    if action == "approve":
        # Call approval API
        pass
```

---

## 9. GCP Free Tier Analysis

### 9.1 Always Free Resources

| Resource | Free Limit | Our Usage |
|----------|------------|-----------|
| e2-micro VM | 1 instance (us regions) | Backend |
| Cloud Storage | 5GB | Backups |
| Cloud Functions | 2M invocations/month | Optional |
| Firebase FCM | Unlimited | Notifications |
| Firebase Auth | 10K users/month | Not needed |

### 9.2 Estimated Costs

**Within Free Tier:**
- e2-micro: $0 (1 instance in us-central1)
- FCM: $0 (unlimited)
- Egress: $0 (up to 1GB/month)

**Potential Costs:**
- Static IP: $3.65/month (if needed)
- Domain: ~$12/year

### 9.3 Comparison with Alternatives

| Provider | Compute | Monthly Cost |
|----------|---------|--------------|
| GCP (e2-micro) | 1 vCPU, 1GB | $0 (free tier) |
| Hetzner (CX22) | 2 vCPU, 4GB | €4.51 |
| DigitalOcean | 1 vCPU, 1GB | $6 |
| Fly.io | 3 shared VMs | $0 (free tier) |

**Decision:** GCP selected for native Firebase integration and adequate free tier.

---

## 10. Security Considerations

### 10.1 FCM Token Security

- Tokens are device-specific, not user secrets
- Store in backend, not in notification payload
- Rotate handling: update backend on token refresh

### 10.2 API Security

- All communication over HTTPS
- Consider API key or token auth for mobile app
- Rate limiting already implemented in backend

### 10.3 Notification Content

- Don't include sensitive data in notification body
- Use data payload for task IDs, fetch details in-app
- Implement certificate pinning (optional, Phase 2)

---

## 11. Reference Implementations

### 11.1 Expo Notifications Example

**Repository:** https://github.com/expo/examples/tree/master/with-push-notifications

### 11.2 Swipeable List Example

**Repository:** https://github.com/software-mansion/react-native-gesture-handler/tree/main/example

### 11.3 Zustand Persist Example

**Repository:** https://github.com/pmndrs/zustand/tree/main/examples

---

## 12. Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Expo vs bare RN? | Expo - faster development, FCM support |
| FCM vs Expo Push? | FCM - production reliability, privacy |
| Redux vs Zustand? | Zustand - simpler, smaller, sufficient |
| NativeWind vs Tamagui? | NativeWind - matches existing Tailwind |
| Expo Router vs React Navigation? | Expo Router - file-based, modern DX |
| GCP vs Hetzner? | GCP - Firebase integration, user preference |
| Telegram fallback? | Yes - user requested for reliability |

---

## 13. Resources

### Official Documentation
- Expo: https://docs.expo.dev/
- Firebase FCM: https://firebase.google.com/docs/cloud-messaging
- NativeWind: https://www.nativewind.dev/
- TanStack Query: https://tanstack.com/query/latest
- Zustand: https://github.com/pmndrs/zustand
- Reanimated: https://docs.swmansion.com/react-native-reanimated/

### Tutorials
- Expo Push Notifications: https://docs.expo.dev/push-notifications/overview/
- React Native Gestures: https://docs.swmansion.com/react-native-gesture-handler/
- Firebase Admin Python: https://firebase.google.com/docs/admin/setup

### Community
- Expo Discord: https://chat.expo.dev/
- React Native Community: https://reactnative.dev/community/overview
