import { useState, useEffect } from 'react';
import { NotificationService } from '../services/notifications';
import { apiService } from '../services/api';
import * as Device from 'expo-device';

export function useNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string | undefined>('');
  const [notification, setNotification] = useState<any>(false);

  useEffect(() => {
    let cleanupListeners: () => void;

    const register = async () => {
      try {
        const token = await NotificationService.registerForPushNotificationsAsync();
        setExpoPushToken(token);

        if (token) {
          // Register with backend
          try {
            // Use device name or model name
            const deviceName = Device.modelName || 'Unknown Device';
            await apiService.registerPush(token, deviceName);
            console.log('Registered with backend successfully');
          } catch (e) {
            console.error('Failed to register with backend', e);
            // Don't fail if backend registration fails
          }
        }

        cleanupListeners = NotificationService.setupNotificationListeners();
      } catch (error) {
        console.error('Error initializing notifications:', error);
        // Don't crash the app if notifications fail to initialize
      }
    };

    register();

    return () => {
      if (cleanupListeners) cleanupListeners();
    };
  }, []);

  return { expoPushToken, notification };
}
