import { Task } from './task';

export interface DashboardResponse {
  pending_count: number;
  completed_today: number;
  urgent_count: number;
  agent_status: 'online' | 'offline' | 'busy';
  recent_activity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  action: string;
  actor: string;
  timestamp: string;
  details?: string;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PushSubscriptionRequest {
  fcm_token: string;
  device_name: string;
  platform: 'ios' | 'android';
}
