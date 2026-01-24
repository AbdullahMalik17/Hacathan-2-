import { View, Text } from 'react-native';
import { Card, CardContent } from '../ui/Card';
import { cn } from '../../utils/cn';
import { LucideIcon } from 'lucide-react-native';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  className?: string;
  iconColor?: string;
}

export function StatsCard({ title, value, icon: Icon, trend, className, iconColor }: StatsCardProps) {
  return (
    <Card className={cn('flex-1', className)}>
      <CardContent className="p-4">
        <View className="flex-row items-center justify-between space-y-0 pb-2">
          <Text className="text-sm font-medium text-muted-foreground">
            {title}
          </Text>
          <Icon size={16} color={iconColor || '#94A3B8'} />
        </View>
        <View>
          <Text className="text-2xl font-bold text-foreground">{value}</Text>
          {trend && (
            <Text className="text-xs text-muted-foreground mt-1">
              {trend}
            </Text>
          )}
        </View>
      </CardContent>
    </Card>
  );
}
