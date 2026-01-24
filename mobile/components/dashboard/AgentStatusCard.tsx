import { View, Text } from 'react-native';
import { Card, CardContent } from '../ui/Card';
import { Activity } from 'lucide-react-native';
import { cn } from '../../utils/cn';

interface AgentStatusCardProps {
  status: 'online' | 'offline' | 'busy';
  lastActive?: string;
}

export function AgentStatusCard({ status, lastActive }: AgentStatusCardProps) {
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-muted-foreground',
    busy: 'bg-yellow-500',
  };

  const statusText = {
    online: 'Agent is Online',
    offline: 'Agent is Offline',
    busy: 'Agent is Busy',
  };

  return (
    <Card className="mb-4">
      <CardContent className="p-4 flex-row items-center justify-between">
        <View className="flex-row items-center space-x-3 gap-3">
          <View className="relative">
            <View className={cn('h-3 w-3 rounded-full', statusColors[status])} />
            {status === 'online' && (
              <View className="absolute -inset-1 rounded-full border border-green-500 opacity-30 animate-ping" />
            )}
          </View>
          <View>
            <Text className="font-semibold text-foreground">{statusText[status]}</Text>
            <Text className="text-xs text-muted-foreground">
              {lastActive ? `Last active: ${lastActive}` : 'System ready'}
            </Text>
          </View>
        </View>
        <Activity size={20} color="#64748B" />
      </CardContent>
    </Card>
  );
}
