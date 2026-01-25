import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

// Configure notification behavior when app is foregrounded
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const NotificationService = {
  async registerForPushNotificationsAsync() {
    let token;

    if (Platform.OS === 'android') {
      try {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });

        // Create dedicated channels
        await Notifications.setNotificationChannelAsync('approvals', {
          name: 'Approvals',
          importance: Notifications.AndroidImportance.HIGH,
          sound: 'default',
          enableVibrate: true,
        });

        await Notifications.setNotificationChannelAsync('suggestions', {
          name: 'Suggestions',
          importance: Notifications.AndroidImportance.DEFAULT,
        });
      } catch (error) {
        console.error('Error setting up notification channels:', error);
      }
    }

    if (Device.isDevice) {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        alert('Failed to get push token for push notification!');
        return;
      }
      
      // Get the FCM token specifically
      try {
        // We use getDevicePushTokenAsync to get the native token (FCM for Android, APNs for iOS)
        // Note: For managed workflow, we might need projectId. But we are using direct FCM integration.
        // For standard Expo push, we would use getExpoPushTokenAsync().
        // For this architecture (FCM direct), we want the device token, BUT expo-notifications
        // usually abstracts this. The research doc said:
        // "This returns the native FCM/APNs token, NOT Expo push token: await Notifications.getDevicePushTokenAsync();"
        
        const tokenData = await Notifications.getDevicePushTokenAsync();
        token = tokenData.data;
        
        // Store for debugging
        await AsyncStorage.setItem('fcm_token', token);
        console.log('FCM Token:', token);
      } catch (e) {
        console.error('Error fetching push token', e);
      }
    } else {
      // alert('Must use physical device for Push Notifications');
      console.log('Push notifications not supported on simulator');
    }

    return token;
  },

  async getStoredToken() {
    return await AsyncStorage.getItem('fcm_token');
  },

  setupNotificationListeners() {
    // This listener is fired whenever a notification is received while the app is foregrounded
    const notificationListener = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
    });

    // This listener is fired whenever a user taps on or interacts with a notification
    // (works when app is foreground, background, or killed)
    const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      const data = response.notification.request.content.data;
      const type = data.type;
      
      if (type === 'approval_request' && data.taskId) {
        // Navigate to approval detail
        // We use a small timeout to ensure navigation is ready
        setTimeout(() => {
          router.push(`/approval/${data.taskId}`);
        }, 500);
      }
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }
};
