import React, { useEffect } from 'react';
import { View } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat, 
  withTiming, 
  withSequence,
  Easing
} from 'react-native-reanimated';
import { Bot } from 'lucide-react-native';
import { cn } from '../../utils/cn';

interface AgentAvatarProps {
  status?: 'online' | 'offline' | 'busy' | 'typing';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AgentAvatar({ status = 'online', size = 'md', className }: AgentAvatarProps) {
  const pulseScale = useSharedValue(1);
  const pulseOpacity = useSharedValue(0.5);

  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  const iconSizes = {
    sm: 16,
    md: 24,
    lg: 32,
  };

  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-muted-foreground',
    busy: 'bg-yellow-500',
    typing: 'bg-blue-500',
  };

  useEffect(() => {
    if (status === 'online' || status === 'typing') {
      pulseScale.value = withRepeat(
        withSequence(
          withTiming(1.2, { duration: 1500, easing: Easing.inOut(Easing.ease) }),
          withTiming(1, { duration: 1500, easing: Easing.inOut(Easing.ease) })
        ),
        -1,
        false
      );
      pulseOpacity.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 1500 }),
          withTiming(0.5, { duration: 1500 })
        ),
        -1,
        false
      );
    } else {
      pulseScale.value = 1;
      pulseOpacity.value = 0;
    }
  }, [status]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }],
    opacity: pulseOpacity.value,
  }));

  return (
    <View className={cn('relative items-center justify-center', className)}>
      <Animated.View
        className={cn('absolute rounded-full bg-primary/30', sizeClasses[size])}
        style={animatedStyle}
      />
      <View
        className={cn(
          'items-center justify-center rounded-full bg-primary border-2 border-background z-10',
          sizeClasses[size]
        )}
      >
        <Bot size={iconSizes[size]} color="white" />
      </View>
      <View
        className={cn(
          'absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-background z-20',
          statusColors[status]
        )}
      />
    </View>
  );
}
