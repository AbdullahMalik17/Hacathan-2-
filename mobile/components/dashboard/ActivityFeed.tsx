import { View, Text } from 'react-native';
import { Card, CardContent } from '../ui/Card';
import { ActivityItem } from '../../types/api';
import { Check, Edit, FileText, MessageSquare, Upload } from 'lucide-react-native';
import { cn } from '../../utils/cn';

interface ActivityFeedProps {
  activities?: ActivityItem[];
}

function getActivityIcon(action: string) {
  if (action.includes('approve')) return <Check size={16} color="#10B981" />;
  if (action.includes('reject')) return <Check size={16} color="#EF4444" />;
  if (action.includes('create')) return <FileText size={16} color="#3B82F6" />;
  if (action.includes('update')) return <Edit size={16} color="#F59E0B" />;
  if (action.includes('upload')) return <Upload size={16} color="#8B5CF6" />;
  return <MessageSquare size={16} color="#94A3B8" />;
}

function formatTime(timestamp: string) {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = (now.getTime() - date.getTime()) / 1000;

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
  } catch (e) {
    return timestamp;
  }
}

export function ActivityFeed({ activities = [] }: ActivityFeedProps) {
  if (!activities.length) {
    return (
      <View className="bg-card rounded-lg border border-border p-8 items-center justify-center">
        <Text className="text-muted-foreground">No recent activity</Text>
      </View>
    );
  }

  return (
    <Card className="border-0 bg-transparent shadow-none">
      <CardContent className="p-0 space-y-4">
        {activities.map((item, index) => (
          <View key={item.id || index} className="flex-row gap-4">
            <View className="items-center">
              <View className="bg-secondary p-2 rounded-full">
                {getActivityIcon(item.action.toLowerCase())}
              </View>
              {index !== activities.length - 1 && (
                <View className="w-[2px] flex-1 bg-border my-2" />
              )}
            </View>
            <View className="flex-1 pb-4">
              <View className="flex-row justify-between items-start">
                <Text className="text-foreground font-medium text-base">
                  {item.action}
                </Text>
                <Text className="text-xs text-muted-foreground">
                  {formatTime(item.timestamp)}
                </Text>
              </View>
              <Text className="text-sm text-muted-foreground mt-1">
                {item.details || `Performed by ${item.actor}`}
              </Text>
            </View>
          </View>
        ))}
      </CardContent>
    </Card>
  );
}
