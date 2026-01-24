import React, { useRef } from 'react';
import { Animated, View, Text } from 'react-native';
import { RectButton, Swipeable } from 'react-native-gesture-handler';
import { Check, X } from 'lucide-react-native';
import { triggerHaptic } from '../../utils/haptics';

interface SwipeableRowProps {
  children: React.ReactNode;
  onApprove: () => void;
  onReject: () => void;
}

export function SwipeableRow({ children, onApprove, onReject }: SwipeableRowProps) {
  const swipeableRef = useRef<Swipeable>(null);

  const renderLeftActions = (
    progress: Animated.AnimatedInterpolation<number>,
    dragX: Animated.AnimatedInterpolation<number>
  ) => {
    const scale = dragX.interpolate({
      inputRange: [0, 80],
      outputRange: [0, 1],
      extrapolate: 'clamp',
    });

    return (
      <RectButton
        style={{
          backgroundColor: '#10B981',
          justifyContent: 'center',
          alignItems: 'center',
          width: 80,
          marginBottom: 16,
          borderRadius: 8,
          marginRight: 8,
        }}
        onPress={() => {
          swipeableRef.current?.close();
          onApprove();
        }}
      >
        <Animated.View style={{ transform: [{ scale }] }}>
          <Check color="white" size={24} />
          <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 12 }}>Approve</Text>
        </Animated.View>
      </RectButton>
    );
  };

  const renderRightActions = (
    progress: Animated.AnimatedInterpolation<number>,
    dragX: Animated.AnimatedInterpolation<number>
  ) => {
    const scale = dragX.interpolate({
      inputRange: [-80, 0],
      outputRange: [1, 0],
      extrapolate: 'clamp',
    });

    return (
      <RectButton
        style={{
          backgroundColor: '#EF4444',
          justifyContent: 'center',
          alignItems: 'center',
          width: 80,
          marginBottom: 16,
          borderRadius: 8,
          marginLeft: 8,
        }}
        onPress={() => {
          swipeableRef.current?.close();
          onReject();
        }}
      >
        <Animated.View style={{ transform: [{ scale }] }}>
          <X color="white" size={24} />
          <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 12 }}>Reject</Text>
        </Animated.View>
      </RectButton>
    );
  };

  return (
    <Swipeable
      ref={swipeableRef}
      friction={2}
      leftThreshold={40}
      rightThreshold={40}
      renderLeftActions={renderLeftActions}
      renderRightActions={renderRightActions}
      onSwipeableOpen={(direction) => {
        if (direction === 'left') {
          triggerHaptic.selection();
        } else {
          triggerHaptic.selection();
        }
      }}
    >
      {children}
    </Swipeable>
  );
}
