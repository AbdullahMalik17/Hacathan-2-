import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { useApproveTask, useRejectTask } from '../../hooks/useApprovals';
import { Button } from '../../components/ui/Button';
import { PriorityBadge } from '../../components/approvals/PriorityBadge';
import { Card } from '../../components/ui/Card';
import { Clock, FileText, AlertTriangle, ArrowLeft, Check, X } from 'lucide-react-native';
import { Task } from '../../types/task';

export default function ApprovalDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  
  const { data, isLoading } = useQuery({
    queryKey: ['task', id],
    queryFn: async () => {
      const res = await apiService.getTask(id);
      return res.data as Task;
    },
    enabled: !!id,
  });

  const approveMutation = useApproveTask();
  const rejectMutation = useRejectTask();

  const handleApprove = async () => {
    if (!id) return;
    approveMutation.mutate({ taskId: id }, {
      onSuccess: () => {
        router.back();
      }
    });
  };

  const handleReject = async () => {
    if (!id) return;
    rejectMutation.mutate({ taskId: id }, {
      onSuccess: () => {
        router.back();
      }
    });
  };

  if (isLoading || !data) {
    return (
      <SafeAreaView className="flex-1 bg-background items-center justify-center">
        <ActivityIndicator size="large" color="#2563eb" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <View className="flex-row items-center p-4 border-b border-border">
        <TouchableOpacity onPress={() => router.back()} className="mr-4">
          <ArrowLeft size={24} color="#F8FAFC" />
        </TouchableOpacity>
        <Text className="text-lg font-semibold text-foreground flex-1" numberOfLines={1}>
          Approval Details
        </Text>
      </View>

      <ScrollView className="flex-1 p-4">
        <View className="flex-row justify-between items-start mb-4">
          <PriorityBadge priority={data.priority} />
          <View className="flex-row items-center space-x-1">
            <Clock size={14} color="#94A3B8" />
            <Text className="text-sm text-muted-foreground">
              {new Date(data.created_at).toLocaleString()}
            </Text>
          </View>
        </View>

        <Text className="text-2xl font-bold text-foreground mb-4">
          {data.title}
        </Text>

        <Card className="p-4 mb-6 bg-card/50">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center space-x-2">
              <FileText size={16} color="#3B82F6" />
              <Text className="text-sm font-medium text-foreground capitalize">
                Source: {data.source.replace('_', ' ')}
              </Text>
            </View>
            {data.risk_score !== undefined && (
              <View className="flex-row items-center space-x-2">
                <AlertTriangle size={16} color={data.risk_score > 0.7 ? '#EF4444' : '#F59E0B'} />
                <Text className="text-sm font-medium text-muted-foreground">
                  Risk Score: {(data.risk_score * 100).toFixed(0)}%
                </Text>
              </View>
            )}
          </View>
        </Card>

        <Text className="text-lg font-semibold text-foreground mb-2">Description</Text>
        <Text className="text-base text-muted-foreground leading-6 mb-8">
          {data.description}
        </Text>

        {/* Action Buttons */}
        <View className="space-y-4 mb-8">
          <Button 
            onPress={handleApprove} 
            className="w-full bg-green-600 active:bg-green-700"
            size="lg"
            disabled={approveMutation.isPending || rejectMutation.isPending}
          >
            {approveMutation.isPending ? (
              <ActivityIndicator color="white" />
            ) : (
              <View className="flex-row items-center space-x-2">
                <Check size={20} color="white" />
                <Text className="text-white font-semibold ml-2">Approve Task</Text>
              </View>
            )}
          </Button>

          <Button 
            onPress={handleReject} 
            variant="destructive"
            className="w-full"
            size="lg"
            disabled={approveMutation.isPending || rejectMutation.isPending}
          >
            {rejectMutation.isPending ? (
              <ActivityIndicator color="white" />
            ) : (
              <View className="flex-row items-center space-x-2">
                <X size={20} color="white" />
                <Text className="text-white font-semibold ml-2">Reject Task</Text>
              </View>
            )}
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
