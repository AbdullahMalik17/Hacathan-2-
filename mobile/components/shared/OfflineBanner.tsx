import React, { useEffect } from 'react';
import { View, Text } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming, 
  withDelay
} from 'react-native-reanimated';
import { WifiOff } from 'lucide-react-native';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';
import { useOfflineQueueStore } from '../../stores/offlineQueueStore';
import { SafeAreaInsetsContext } from 'react-native-safe-area-context';

export function OfflineBanner() {
  const isOnline = useNetworkStatus();
  const { queue } = useOfflineQueueStore();
  
  const height = useSharedValue(0);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (!isOnline) {
      height.value = withTiming(40);
      opacity.value = withTiming(1);
    } else {
      height.value = withDelay(2000, withTiming(0));
      opacity.value = withDelay(2000, withTiming(0));
    }
  }, [isOnline]);

  const style = useAnimatedStyle(() => ({
    height: height.value,
    opacity: opacity.value,
  }));

  if (isOnline && height.value === 0) return null;

  return (
    <Animated.View
      style={[style, { overflow: 'hidden' }]}
      className="bg-destructive items-center justify-center flex-row space-x-2 w-full absolute bottom-0 z-50"
    >
      <SafeAreaInsetsContext.Consumer>
        {(insets) => (
          <View className="flex-row items-center justify-center pb-1" style={{ marginBottom: insets?.bottom }}>
            <WifiOff size={16} color="white" />
            <Text className="text-white text-xs font-medium ml-2">
              You are offline. 
              {queue.length > 0 ? ` ${queue.length} action(s) queued.` : ' Changes will sync when online.'}
            </Text>
          </View>
        )}
      </SafeAreaInsetsContext.Consumer>
    </Animated.View>
  );
}
