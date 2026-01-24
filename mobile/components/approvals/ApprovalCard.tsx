import { View, Text, TouchableOpacity } from 'react-native';
import { Card, CardContent, CardFooter, CardHeader } from '../ui/Card';
import { PriorityBadge } from './PriorityBadge';
import { Task } from '../../types/task';
import { cn } from '../../utils/cn';
import { Clock, AlertTriangle, FileText } from 'lucide-react-native';
import { Link } from 'expo-router';

interface ApprovalCardProps {
  task: Task;
}

export function ApprovalCard({ task }: ApprovalCardProps) {
  return (
    <Link href={`/approval/${task.id}`} asChild>
      <TouchableOpacity activeOpacity={0.8}>
        <Card className="mb-4">
          <CardHeader className="pb-2">
            <View className="flex-row justify-between items-start">
              <PriorityBadge priority={task.priority} />
              <View className="flex-row items-center space-x-1">
                <Clock size={12} color="#94A3B8" />
                <Text className="text-xs text-muted-foreground">
                  {new Date(task.created_at).toLocaleDateString()}
                </Text>
              </View>
            </View>
            <Text className="text-lg font-semibold text-foreground mt-2" numberOfLines={2}>
              {task.title}
            </Text>
          </CardHeader>
          <CardContent>
            <Text className="text-muted-foreground text-sm" numberOfLines={3}>
              {task.description}
            </Text>
            
            <View className="flex-row mt-4 space-x-4">
              {task.risk_score !== undefined && (
                <View className="flex-row items-center space-x-1">
                  <AlertTriangle size={14} color={task.risk_score > 0.7 ? '#EF4444' : '#F59E0B'} />
                  <Text className="text-xs text-muted-foreground">
                    Risk: {(task.risk_score * 100).toFixed(0)}%
                  </Text>
                </View>
              )}
              <View className="flex-row items-center space-x-1">
                <FileText size={14} color="#3B82F6" />
                <Text className="text-xs text-muted-foreground capitalize">
                  {task.source.replace('_', ' ')}
                </Text>
              </View>
            </View>
          </CardContent>
        </Card>
      </TouchableOpacity>
    </Link>
  );
}
