import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type OfflineActionType = 'approve' | 'reject';

export interface OfflineAction {
  id: string;
  type: OfflineActionType;
  payload: {
    taskId: string;
    note?: string;
  };
  timestamp: number;
  retryCount: number;
}

interface OfflineQueueState {
  queue: OfflineAction[];
  addAction: (action: Omit<OfflineAction, 'id' | 'timestamp' | 'retryCount'>) => void;
  removeAction: (id: string) => void;
  incrementRetry: (id: string) => void;
  clearQueue: () => void;
}

export const useOfflineQueueStore = create<OfflineQueueState>()(
  persist(
    (set) => ({
      queue: [],
      addAction: (action) =>
        set((state) => ({
          queue: [
            ...state.queue,
            {
              ...action,
              id: Math.random().toString(36).substring(7),
              timestamp: Date.now(),
              retryCount: 0,
            },
          ],
        })),
      removeAction: (id) =>
        set((state) => ({
          queue: state.queue.filter((a) => a.id !== id),
        })),
      incrementRetry: (id) =>
        set((state) => ({
          queue: state.queue.map((a) =>
            a.id === id ? { ...a, retryCount: a.retryCount + 1 } : a
          ),
        })),
      clearQueue: () => set({ queue: [] }),
    }),
    {
      name: 'offline-queue-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
