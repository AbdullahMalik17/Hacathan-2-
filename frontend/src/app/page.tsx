import { fetchTasks } from '@/app/actions'
import TaskBoard from '@/components/TaskBoard'

export const dynamic = 'force-dynamic'

export default async function Home() {
  const { pending, completed } = await fetchTasks()

  return (
    <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col space-y-2">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">Dashboard</h1>
            <p className="text-xl text-muted-foreground">
                Monitor and orchestrate your Digital FTE, Abdullah Junior.
            </p>
        </div>
        
        <div className="border-t pt-8">
            <TaskBoard initialPending={pending} initialCompleted={completed} />
        </div>
    </div>
  )
}