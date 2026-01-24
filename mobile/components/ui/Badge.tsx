import { View, Text } from 'react-native';
import { cn } from '../../utils/cn';

interface BadgeProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  className?: string;
  children: React.ReactNode;
}

export function Badge({ variant = 'default', className, children }: BadgeProps) {
  const variants = {
    default: 'border-transparent bg-primary text-primary-foreground',
    secondary: 'border-transparent bg-secondary text-secondary-foreground',
    destructive: 'border-transparent bg-destructive text-destructive-foreground',
    outline: 'text-foreground',
    success: 'border-transparent bg-green-600 text-white',
    warning: 'border-transparent bg-yellow-600 text-white',
  };

  return (
    <View
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5',
        variants[variant],
        className
      )}
    >
      <Text className={cn('text-xs font-semibold', variant === 'outline' ? 'text-foreground' : 'text-white')}>
        {children}
      </Text>
    </View>
  );
}
