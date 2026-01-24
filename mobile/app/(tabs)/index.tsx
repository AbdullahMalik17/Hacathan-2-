import React from 'react';
import { View, Text, ScrollView, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react-native';
import { useDashboard } from '../../hooks/useDashboard';
import { StatsCard } from '../../components/dashboard/StatsCard';
import { AgentStatusCard } from '../../components/dashboard/AgentStatusCard';
import { ActivityFeed } from '../../components/dashboard/ActivityFeed';
import { Skeleton } from '../../components/ui/LoadingSkeleton';

export default function DashboardScreen() {
  const { data, isLoading, refetch, isRefetching } = useDashboard();

  // Mock data for initial development/fallback
  const stats = data || {
    pending_count: 0,
    completed_today: 0,
    urgent_count: 0,
    agent_status: 'online' as const,
    recent_activity: [],
  };

  const onRefresh = React.useCallback(() => {
    refetch();
  }, [refetch]);

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-background p-4">
        <Skeleton className="h-20 w-full mb-4" />
        <View className="flex-row gap-4 mb-4">
          <Skeleton className="h-32 flex-1" />
          <Skeleton className="h-32 flex-1" />
        </View>
        <Skeleton className="h-32 w-1/2" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <ScrollView
        contentContainerStyle={{ padding: 16 }}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={onRefresh} tintColor="#fff" />
        }
      >
        <View className="mb-6">
          <Text className="text-3xl font-bold text-foreground">Good Morning,</Text>
          <Text className="text-muted-foreground text-lg">Abdullah</Text>
        </View>

        <AgentStatusCard status={stats.agent_status} />

        <View className="flex-row gap-4 mb-4">
          <StatsCard
            title="Pending"
            value={stats.pending_count}
            icon={Clock}
            iconColor="#F59E0B"
            className="bg-amber-500/10 border-amber-500/20"
          />
          <StatsCard
            title="Completed"
            value={stats.completed_today}
            icon={CheckCircle2}
            iconColor="#10B981"
            className="bg-emerald-500/10 border-emerald-500/20"
          />
        </View>

        <View className="flex-row gap-4 mb-8">
          <StatsCard
            title="Urgent"
            value={stats.urgent_count}
            icon={AlertCircle}
            iconColor="#EF4444"
            className="bg-red-500/10 border-red-500/20"
          />
        </View>

        <Text className="text-xl font-semibold text-foreground mb-4">Recent Activity</Text>
        <ActivityFeed activities={stats.recent_activity} />
      </ScrollView>
    </SafeAreaView>
  );
}