import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Task } from '../types/task';
import { useToast } from '../context/ToastContext';
import { triggerHaptic } from '../utils/haptics';
import { useNetworkStatus } from './useNetworkStatus';
import { useOfflineQueueStore } from '../stores/offlineQueueStore';

export function useApprovals() {
  return useQuery({
    queryKey: ['approvals'],
    queryFn: async () => {
      const response = await apiService.getTasks('Pending_Approval');
      return response.data.tasks as Task[];
    },
    refetchInterval: 30000,
  });
}

export function useApproveTask() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const isOnline = useNetworkStatus();
  const { addAction } = useOfflineQueueStore();

  return useMutation({
    mutationFn: async ({ taskId, note }: { taskId: string; note?: string }) => {
      if (!isOnline) {
        addAction({ type: 'approve', payload: { taskId, note } });
        // Return a dummy promise to simulate success for the optimistic update
        return { success: true, offline: true };
      }
      return apiService.approveTask(taskId, note);
    },
    onMutate: async ({ taskId }) => {
      triggerHaptic.light();
      await queryClient.cancelQueries({ queryKey: ['approvals'] });
      const previousTasks = queryClient.getQueryData<Task[]>(['approvals']);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          ['approvals'],
          previousTasks.filter((t) => t.id !== taskId)
        );
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      triggerHaptic.error();
      if (context?.previousTasks) {
        queryClient.setQueryData(['approvals'], context.previousTasks);
      }
      showToast('Failed to approve task. Please try again.', 'error');
    },
    onSuccess: (data) => {
      if ((data as any).offline) {
        showToast('Action queued (Offline)', 'info');
      } else {
        triggerHaptic.success();
        showToast('Task approved successfully', 'success');
      }
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    },
  });
}

export function useRejectTask() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const isOnline = useNetworkStatus();
  const { addAction } = useOfflineQueueStore();

  return useMutation({
    mutationFn: async ({ taskId, note }: { taskId: string; note?: string }) => {
      if (!isOnline) {
        addAction({ type: 'reject', payload: { taskId, note } });
        return { success: true, offline: true };
      }
      return apiService.rejectTask(taskId, note);
    },
    onMutate: async ({ taskId }) => {
      triggerHaptic.light();
      await queryClient.cancelQueries({ queryKey: ['approvals'] });
      const previousTasks = queryClient.getQueryData<Task[]>(['approvals']);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          ['approvals'],
          previousTasks.filter((t) => t.id !== taskId)
        );
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      triggerHaptic.error();
      if (context?.previousTasks) {
        queryClient.setQueryData(['approvals'], context.previousTasks);
      }
      showToast('Failed to reject task. Please try again.', 'error');
    },
    onSuccess: (data) => {
       if ((data as any).offline) {
        showToast('Action queued (Offline)', 'info');
      } else {
        triggerHaptic.success();
        showToast('Task rejected', 'info');
      }
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    },
  });
}