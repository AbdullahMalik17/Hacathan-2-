import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { DashboardResponse } from '../types/api';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await apiService.getDashboard();
      return response.data as DashboardResponse;
    },
    refetchInterval: 15000, // Poll every 15s
  });
}
