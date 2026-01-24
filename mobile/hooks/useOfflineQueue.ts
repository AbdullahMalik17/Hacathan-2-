import { useEffect } from 'react';
import { useNetworkStatus } from './useNetworkStatus';
import { useOfflineQueueStore } from '../stores/offlineQueueStore';
import { apiService } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useQueryClient } from '@tanstack/react-query';

export function useOfflineQueue() {
  const isOnline = useNetworkStatus();
  const { queue, removeAction, incrementRetry } = useOfflineQueueStore();
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (isOnline && queue.length > 0) {
      processQueue();
    }
  }, [isOnline, queue.length]);

  const processQueue = async () => {
    for (const action of queue) {
      try {
        if (action.type === 'approve') {
          await apiService.approveTask(action.payload.taskId, action.payload.note);
        } else if (action.type === 'reject') {
          await apiService.rejectTask(action.payload.taskId, action.payload.note);
        }
        
        removeAction(action.id);
        
        // Notify success if it was a queued action
        if (queue.length > 0) {
           queryClient.invalidateQueries({ queryKey: ['approvals'] });
           queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        }
      } catch (error) {
        console.error('Failed to process offline action:', error);
        if (action.retryCount >= 3) {
           removeAction(action.id);
           showToast(`Failed to sync action for task ${action.payload.taskId} after 3 attempts`, 'error');
        } else {
           incrementRetry(action.id);
        }
      }
    }
    
    if (queue.length > 0) {
        showToast('Offline actions synced', 'success');
    }
  };
}
