import React, { useEffect } from 'react';
import { View } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat, 
  withTiming, 
  withSequence,
  withDelay
} from 'react-native-reanimated';

export function AgentTypingIndicator() {
  const dot1 = useSharedValue(0);
  const dot2 = useSharedValue(0);
  const dot3 = useSharedValue(0);

  useEffect(() => {
    const duration = 600;
    
    dot1.value = withRepeat(
      withSequence(
        withTiming(-4, { duration: duration / 2 }),
        withTiming(0, { duration: duration / 2 })
      ),
      -1,
      true
    );

    dot2.value = withDelay(
      duration / 3,
      withRepeat(
        withSequence(
          withTiming(-4, { duration: duration / 2 }),
          withTiming(0, { duration: duration / 2 })
        ),
        -1,
        true
      )
    );

    dot3.value = withDelay(
      (duration * 2) / 3,
      withRepeat(
        withSequence(
          withTiming(-4, { duration: duration / 2 }),
          withTiming(0, { duration: duration / 2 })
        ),
        -1,
        true
      )
    );
  }, []);

  const style1 = useAnimatedStyle(() => ({ transform: [{ translateY: dot1.value }] }));
  const style2 = useAnimatedStyle(() => ({ transform: [{ translateY: dot2.value }] }));
  const style3 = useAnimatedStyle(() => ({ transform: [{ translateY: dot3.value }] }));

  return (
    <View className="flex-row items-center space-x-1 h-6 px-2 bg-secondary/50 rounded-full self-start">
      <Animated.View className="h-1.5 w-1.5 rounded-full bg-muted-foreground" style={style1} />
      <Animated.View className="h-1.5 w-1.5 rounded-full bg-muted-foreground" style={style2} />
      <Animated.View className="h-1.5 w-1.5 rounded-full bg-muted-foreground" style={style3} />
    </View>
  );
}
