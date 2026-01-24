# Firebase Setup for Abdullah Junior Mobile App

This guide walks you through setting up Firebase Cloud Messaging (FCM) for push notifications.

## Quick Start (5 minutes)

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"** (or select existing)
3. Name it `abdullah-junior` (or any name)
4. Disable Google Analytics (optional, simplifies setup)
5. Click **Create Project**

### Step 2: Add Android App

1. In Firebase Console, click **"Add app"** → **Android**
2. Enter package name: `com.abdullahjunior.mobile`
3. Enter nickname: `Abdullah Junior`
4. Click **Register app**
5. Download `google-services.json`
6. Place it in `mobile/` directory

### Step 3: Generate Service Account (for Backend)

1. Go to **Project Settings** → **Service accounts**
2. Click **"Generate new private key"**
3. Download the JSON file
4. Rename it to `firebase-service-account.json`
5. Place it in `config/` directory

### Step 4: Configure Mobile App

The app is already configured. Just ensure `google-services.json` is in place.

---

## Detailed Configuration

### Backend (Local Development)

Place the service account file:

```bash
# File location
config/firebase-service-account.json
```

### Backend (Fly.io Deployment)

Set the service account as a secret:

```bash
# Read the file and set as secret
fly secrets set FIREBASE_SERVICE_ACCOUNT="$(cat config/firebase-service-account.json)"
```

### Mobile App Configuration

1. **Android** (`mobile/android/app/`):
   - Place `google-services.json` in `mobile/android/app/`
   - The file contains your Firebase config

2. **iOS** (`mobile/ios/`):
   - Download `GoogleService-Info.plist` from Firebase Console
   - Add to Xcode project

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREBASE_SERVICE_ACCOUNT` | JSON string of service account | Cloud only |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Path to service account file | Optional |

---

## Testing Push Notifications

### 1. Get FCM Token from Mobile App

When the app starts, it registers for push notifications and sends the FCM token to the backend. Check the Settings screen to see registration status.

### 2. Send Test Notification

Using the API:

```bash
# Send test notification
curl -X POST http://localhost:8000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Hello from Abdullah Junior!"}'
```

### 3. Verify in Firebase Console

1. Go to **Cloud Messaging** → **Compose notification**
2. Send a test message to your app

---

## Notification Channels (Android)

The app creates these notification channels:

| Channel ID | Name | Description |
|------------|------|-------------|
| `approvals` | Approvals | High priority - approval requests |
| `tasks` | Tasks | Task updates and completions |
| `default` | General | Other notifications |

---

## Troubleshooting

### "Firebase credentials not found"

1. Check file exists: `ls config/firebase-service-account.json`
2. Verify JSON is valid: `python -c "import json; json.load(open('config/firebase-service-account.json'))"`

### "FCM token not received"

1. Ensure Google Play Services is available (Android)
2. Check internet connection
3. Verify `google-services.json` is in correct location

### Notifications not appearing

1. Check notification permissions in device settings
2. Verify app is not in "force stopped" state
3. Check battery optimization settings

---

## Security Notes

- **NEVER** commit `firebase-service-account.json` to git
- **NEVER** commit `google-services.json` to git (contains API keys)
- Both files are in `.gitignore`

---

## Firebase Console Links

- [Firebase Console](https://console.firebase.google.com/)
- [Cloud Messaging](https://console.firebase.google.com/project/_/messaging)
- [Project Settings](https://console.firebase.google.com/project/_/settings/general)
