import { View } from 'react-native';
import { cn } from '../../utils/cn';

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <View
      className={cn(
        'rounded-lg border border-border bg-card text-card-foreground shadow-sm',
        className
      )}
    >
      {children}
    </View>
  );
}

export function CardHeader({ className, children }: CardProps) {
  return (
    <View className={cn('flex-col space-y-1.5 p-6', className)}>
      {children}
    </View>
  );
}

export function CardTitle({ className, children }: CardProps) {
  return (
    <View className={cn('text-2xl font-semibold leading-none tracking-tight', className)}>
      {children}
    </View>
  );
}

export function CardContent({ className, children }: CardProps) {
  return (
    <View className={cn('p-6 pt-0', className)}>
      {children}
    </View>
  );
}

export function CardFooter({ className, children }: CardProps) {
  return (
    <View className={cn('flex-row items-center p-6 pt-0', className)}>
      {children}
    </View>
  );
}
