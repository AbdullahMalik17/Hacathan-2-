# Abdullah Junior Mobile Companion App

A React Native (Expo) application for the Digital FTE system.

## Features

- **Push Notifications**: Receive instant alerts for approvals via Firebase Cloud Messaging (FCM).
- **Approvals Dashboard**: Swipe right to approve, left to reject.
- **Agent Chat**: Converse with Abdullah Junior in real-time.
- **Offline Mode**: Queue actions when offline and sync when connection restores.
- **Insights**: View daily stats and agent activity.

## Setup

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Configure Environment**:
    - The app connects to the backend at `http://10.0.2.2:8000` (Android Emulator) or `http://localhost:8000` (iOS Simulator) by default.
    - You can change this in the **Settings** tab.

3.  **Firebase Setup (Required for Notifications)**:
    - Place `google-services.json` in the `mobile/` root.
    - Place `GoogleService-Info.plist` in the `mobile/` root.
    - These files should be downloaded from your Firebase Console.

4.  **Run the App**:
    ```bash
    npx expo start
    ```
    - Press `a` for Android Emulator.
    - Press `i` for iOS Simulator.
    - Scan QR code with Expo Go app on physical device.

## Architecture

- **Framework**: Expo SDK 54 (React Native)
- **Styling**: NativeWind (Tailwind CSS)
- **State Management**: Zustand (Client) + TanStack Query (Server)
- **Navigation**: Expo Router (File-based)
- **Notifications**: Expo Notifications + Firebase Cloud Messaging

## Troubleshooting

- **"Network Error"**: Ensure the backend server is running and accessible. If running on a physical device, update the Backend URL in Settings to your computer's local IP address (e.g., `http://192.168.1.x:8000`).
- **Notifications not receiving**: Check if `google-services.json` is valid and the package name `com.abdullahjunior.mobile` matches your Firebase console.

## Build

To build for production (APK/IPA):

```bash
npm install -g eas-cli
eas login
eas build --profile preview --platform android
```
