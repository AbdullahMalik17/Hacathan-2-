# Mobile App Build Guide - Abdullah Junior

Build and distribute the Abdullah Junior mobile app using Expo EAS.

## Prerequisites

1. Node.js 18+ installed
2. Expo CLI: `npm install -g expo-cli`
3. EAS CLI: `npm install -g eas-cli`
4. Expo account: https://expo.dev/signup

## Quick Start

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Login to Expo
eas login

# Build preview APK (for testing)
eas build --platform android --profile preview
```

---

## Build Types

### 1. Preview APK (Recommended for Testing)

Direct-install APK for Android devices:

```bash
eas build --platform android --profile preview
```

After build completes:
1. Download APK from the provided URL
2. Transfer to device (ADB, email, cloud storage)
3. Install on device (enable "Install unknown apps" in settings)

### 2. Development Build

For development with hot reload:

```bash
eas build --platform android --profile development
```

### 3. Production Build

For store submission:

```bash
# Android App Bundle (for Play Store)
eas build --platform android --profile production

# iOS (requires Apple Developer account)
eas build --platform ios --profile production
```

---

## Local Development

Run on connected device/emulator:

```bash
# Start development server
npx expo start

# Android
npx expo start --android

# iOS (Mac only)
npx expo start --ios
```

### Connect to Local Backend

1. Find your computer's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Open the app's Settings screen
3. Enter: `http://192.168.x.x:8000` (your local IP)

---

## Firebase Configuration

### Android

1. Download `google-services.json` from Firebase Console
2. Place in `mobile/` directory (same level as app.json)
3. Rebuild the app

### iOS

1. Download `GoogleService-Info.plist` from Firebase Console
2. Place in `mobile/` directory
3. Rebuild the app

---

## Distribution Options

### Option A: Direct APK (Simplest)

1. Build preview APK
2. Share via email, Google Drive, or direct download link
3. Recipients install manually

### Option B: Internal Testing (Recommended)

Using EAS Update for instant updates:

```bash
# First build (creates native code)
eas build --platform android --profile preview

# Subsequent updates (instant, no rebuild)
eas update --branch preview --message "Bug fixes"
```

### Option C: Google Play Store

1. Create Google Play Developer account ($25 one-time)
2. Build production AAB: `eas build --platform android --profile production`
3. Submit: `eas submit --platform android --profile production`

### Option D: Apple App Store

1. Apple Developer account ($99/year)
2. Build: `eas build --platform ios --profile production`
3. Submit: `eas submit --platform ios --profile production`

---

## Troubleshooting

### "Build failed" errors

```bash
# Clear cache and rebuild
npx expo start --clear
eas build --platform android --profile preview --clear-cache
```

### Push notifications not working

1. Verify `google-services.json` is present
2. Check Firebase project settings
3. Ensure FCM is enabled in Firebase Console

### "App not installed" on Android

1. Enable "Install unknown apps" for your file manager
2. Check device storage space
3. Uninstall previous version if installed

### Network errors

1. Ensure device and backend are on same network
2. Check backend is running: `curl http://localhost:8000/api/health`
3. Verify firewall allows port 8000

---

## Build Commands Reference

```bash
# List all builds
eas build:list

# View build details
eas build:view <build-id>

# Cancel running build
eas build:cancel

# Local build (requires Android SDK)
eas build --platform android --local
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/mobile-build.yml
name: Mobile Build
on:
  push:
    branches: [main]
    paths: ['mobile/**']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install -g eas-cli
      - run: cd mobile && npm install
      - run: cd mobile && eas build --platform android --profile preview --non-interactive
        env:
          EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
```

---

## Version Management

Update version in `app.json`:

```json
{
  "expo": {
    "version": "1.0.1",
    "android": {
      "versionCode": 2
    },
    "ios": {
      "buildNumber": "2"
    }
  }
}
```

Or use auto-increment:

```bash
eas build --platform android --auto-increment
```
