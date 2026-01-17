'use server'

import { getPendingTasks, getCompletedTasks, createTask, getSkills } from '@/lib/vault';
import type { Task, Skill } from '@/types';
import { revalidatePath } from 'next/cache';

export async function fetchTasks(): Promise<{ pending: Task[], completed: Task[] }> {
  const [pending, completed] = await Promise.all([
    getPendingTasks(),
    getCompletedTasks()
  ]);
  return { pending, completed };
}

export async function submitTask(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;
  const priority = (formData.get('priority') as string) || 'medium';

  if (!title || !content) return;

  await createTask(title, content, priority);
  revalidatePath('/');
}

export async function fetchSkills(): Promise<Skill[]> {
  return await getSkills();
}
