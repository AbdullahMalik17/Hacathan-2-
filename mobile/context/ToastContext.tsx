import React, { createContext, useContext, useState, useCallback } from 'react';
import { View, Text, Animated } from 'react-native';
import { SafeAreaInsetsContext } from 'react-native-safe-area-context';
import { cn } from '../utils/cn';
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react-native';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toast, setToast] = useState<Toast | null>(null);
  const [fadeAnim] = useState(new Animated.Value(0));

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(7);
    setToast({ id, message, type });

    Animated.sequence([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.delay(3000),
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setToast(null);
    });
  }, [fadeAnim]);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && (
        <SafeAreaInsetsContext.Consumer>
          {(insets) => (
            <Animated.View
              style={{
                opacity: fadeAnim,
                position: 'absolute',
                top: (insets?.top || 0) + 10,
                left: 20,
                right: 20,
                transform: [
                  {
                    translateY: fadeAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-20, 0],
                    }),
                  },
                ],
              }}
              className="z-50"
            >
              <View
                className={cn(
                  'flex-row items-center p-4 rounded-lg shadow-lg border',
                  toast.type === 'success' && 'bg-background border-green-500',
                  toast.type === 'error' && 'bg-background border-red-500',
                  toast.type === 'info' && 'bg-background border-blue-500',
                )}
              >
                {toast.type === 'success' && <CheckCircle size={24} color="#10B981" />}
                {toast.type === 'error' && <XCircle size={24} color="#EF4444" />}
                {toast.type === 'info' && <AlertCircle size={24} color="#3B82F6" />}
                <Text className="ml-3 text-foreground font-medium flex-1">
                  {toast.message}
                </Text>
              </View>
            </Animated.View>
          )}
        </SafeAreaInsetsContext.Consumer>
      )}
    </ToastContext.Provider>
  );
}
