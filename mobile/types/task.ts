export interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  source: string;
  created_at: string;
  folder?: string;
  risk_score?: number;
  complexity_score?: number;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}
