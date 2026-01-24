import { Text, TouchableOpacity, View } from 'react-native';
import { cn } from '../../utils/cn';

interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
  labelClassName?: string;
  children?: React.ReactNode;
  onPress?: () => void;
  disabled?: boolean;
}

export function Button({
  variant = 'default',
  size = 'default',
  className,
  labelClassName,
  children,
  onPress,
  disabled,
}: ButtonProps) {
  const baseStyles = 'flex-row items-center justify-center rounded-md';
  
  const variants = {
    default: 'bg-primary',
    destructive: 'bg-destructive',
    outline: 'border border-input bg-background',
    secondary: 'bg-secondary',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  };

  const sizes = {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 rounded-md px-3',
    lg: 'h-11 rounded-md px-8',
    icon: 'h-10 w-10',
  };

  const textBaseStyles = 'text-sm font-medium';
  const textVariants = {
    default: 'text-primary-foreground',
    destructive: 'text-destructive-foreground',
    outline: 'text-foreground',
    secondary: 'text-secondary-foreground',
    ghost: 'text-foreground',
    link: 'text-primary',
  };

  return (
    <TouchableOpacity
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        disabled && 'opacity-50',
        className
      )}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      {typeof children === 'string' ? (
        <Text
          className={cn(
            textBaseStyles,
            textVariants[variant],
            labelClassName
          )}
        >
          {children}
        </Text>
      ) : (
        children
      )}
    </TouchableOpacity>
  );
}
