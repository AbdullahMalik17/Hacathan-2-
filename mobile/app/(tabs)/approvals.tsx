import React from 'react';
import { View, Text, FlatList, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useApprovals, useApproveTask, useRejectTask } from '../../hooks/useApprovals';
import { ApprovalCard } from '../../components/approvals/ApprovalCard';
import { SwipeableRow } from '../../components/approvals/SwipeableRow';
import { Skeleton } from '../../components/ui/LoadingSkeleton';
import { CheckSquare } from 'lucide-react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function ApprovalsScreen() {
  const { data: tasks, isLoading, refetch, isRefetching } = useApprovals();
  const approveMutation = useApproveTask();
  const rejectMutation = useRejectTask();

  const onRefresh = React.useCallback(() => {
    refetch();
  }, [refetch]);

  const handleApprove = (id: string) => {
    approveMutation.mutate({ taskId: id });
  };

  const handleReject = (id: string) => {
    rejectMutation.mutate({ taskId: id });
  };

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-background p-4">
        <Text className="text-2xl font-bold text-foreground mb-4">Pending Approvals</Text>
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-48 w-full mb-4" />
        ))}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background p-4 pb-0">
      <GestureHandlerRootView className="flex-1">
        <View className="mb-4">
          <Text className="text-2xl font-bold text-foreground">Pending Approvals</Text>
          <Text className="text-muted-foreground">
            {tasks?.length || 0} tasks waiting for your review
          </Text>
        </View>

        <FlatList
          data={tasks}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <SwipeableRow
              onApprove={() => handleApprove(item.id)}
              onReject={() => handleReject(item.id)}
            >
              <ApprovalCard task={item} />
            </SwipeableRow>
          )}
          contentContainerStyle={{ paddingBottom: 20 }}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={isRefetching} onRefresh={onRefresh} tintColor="#fff" />
          }
          ListEmptyComponent={
            <View className="flex-1 items-center justify-center py-20">
              <View className="bg-secondary p-6 rounded-full mb-4">
                <CheckSquare size={48} color="#94A3B8" />
              </View>
              <Text className="text-lg font-medium text-foreground">All caught up!</Text>
              <Text className="text-muted-foreground text-center px-8 mt-2">
                You have no pending approvals at the moment. Great job!
              </Text>
            </View>
          }
        />
      </GestureHandlerRootView>
    </SafeAreaView>
  );
}