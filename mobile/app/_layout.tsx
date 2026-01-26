import '../global.css';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '../context/ToastContext';
import { useNotifications } from '../hooks/useNotifications';
import { useOfflineQueue } from '../hooks/useOfflineQueue';
import { OfflineBanner } from '../components/shared/OfflineBanner';
import { ErrorBoundary } from '../components/ErrorBoundary';

const queryClient = new QueryClient();

function AppContent() {
  // Initialize notifications
  useNotifications();
  // Initialize offline queue processing
  useOfflineQueue();

  return (
    <View className="flex-1 bg-background">
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      </Stack>
      <OfflineBanner />
      <StatusBar style="light" />
    </View>
  );
}

export default function RootLayout() {
  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <AppContent />
          </ToastProvider>
        </QueryClientProvider>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
