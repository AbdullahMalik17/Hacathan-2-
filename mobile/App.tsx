import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import { SplashScreen, Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { useColorScheme } from 'react-native';
import { Colors } from './constants/colors';
import Config from './config/AppConfig';

// Initialize the app with configuration
SplashScreen.preventAutoHideAsync();

export default function App() {
  const [appReady, setAppReady] = useState(false);
  const colorScheme = useColorScheme();

  useEffect(() => {
    // Initialize app configuration
    initializeApp().then(() => {
      setAppReady(true);
      SplashScreen.hideAsync();
    });
  }, []);

  const initializeApp = async (): Promise<void> => {
    // Set up any initial configuration
    console.log('App initialized with config:', Config);

    // You can perform additional initialization here
    // such as setting up API base URL, checking for updates, etc.
  };

  if (!appReady) {
    return null; // Render nothing while loading
  }

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme ?? 'light'].background }]}>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="+not-found" />
      </Stack>
      <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
