import { TextInput, View, Text } from 'react-native';
import { cn } from '../../utils/cn';

interface InputProps extends React.ComponentProps<typeof TextInput> {
  label?: string;
  error?: string;
  containerClassName?: string;
}

export function Input({
  className,
  containerClassName,
  label,
  error,
  ...props
}: InputProps) {
  return (
    <View className={cn('space-y-2', containerClassName)}>
      {label && (
        <Text className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-foreground">
          {label}
        </Text>
      )}
      <TextInput
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-destructive',
          className
        )}
        placeholderTextColor="#94A3B8" // muted-foreground
        {...props}
      />
      {error && (
        <Text className="text-sm font-medium text-destructive">{error}</Text>
      )}
    </View>
  );
}
