// Type definitions for Digital FTE Dashboard

export interface Task {
  id: string
  filename: string
  content: string
  status: 'pending' | 'done'
  timestamp: number
  importance: 'high' | 'medium' | 'low'
  priority?: 'urgent' | 'high' | 'medium' | 'low'
  source?: string
  title?: string
}

export interface Skill {
  name: string
  description: string
  category: string
  status?: 'available'
}

export interface CreateTaskInput {
  content: string
  title: string
  priority?: 'medium' | 'high' | 'urgent'
}
