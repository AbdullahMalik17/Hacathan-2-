import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface SettingsState {
  theme: 'dark' | 'light' | 'system';
  apiBaseUrl: string;
  notifications: {
    approvals: boolean;
    suggestions: boolean;
    digest: boolean;
  };
  setTheme: (theme: 'dark' | 'light' | 'system') => void;
  setApiBaseUrl: (url: string) => void;
  toggleNotification: (key: 'approvals' | 'suggestions' | 'digest') => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'dark',
      apiBaseUrl: 'http://10.0.2.2:8000',
      notifications: {
        approvals: true,
        suggestions: true,
        digest: true,
      },
      setTheme: (theme) => set({ theme }),
      setApiBaseUrl: (url) => set({ apiBaseUrl: url }),
      toggleNotification: (key) =>
        set((state) => ({
          notifications: {
            ...state.notifications,
            [key]: !state.notifications[key],
          },
        })),
    }),
    {
      name: 'settings-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
