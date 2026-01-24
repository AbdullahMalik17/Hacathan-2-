import { fetchTasks, fetchFinancials } from '@/app/actions'
import TaskBoard from '@/components/TaskBoard'
import AgentTerminal from '@/components/AgentTerminal'
import AgentChat from '@/components/AgentChat'
import FinancialWidget from '@/components/widgets/FinancialWidget'
import SocialWidget from '@/components/widgets/SocialWidget'

export const dynamic = 'force-dynamic'

export default async function Home() {
  const { pending, completed } = await fetchTasks()
  const financials = await fetchFinancials()

  return (
    <div className="min-h-screen bg-black text-zinc-300 p-6">
        <div className="max-w-[1600px] mx-auto space-y-6">
            {/* Header */}
            <header className="flex justify-between items-end border-b border-zinc-800 pb-6">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-1">
                        ABDULLAH <span className="text-blue-500">JUNIOR</span>
                    </h1>
                    <p className="text-sm font-mono text-zinc-500">
                        DIGITAL FTE • PLATINUM TIER • CLOUD/LOCAL HYBRID
                    </p>
                </div>
                <div className="flex gap-4 text-xs font-mono">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>SYSTEM ONLINE</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>SYNC ACTIVE</span>
                    </div>
                </div>
            </header>

            {/* Main Command Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                
                {/* Left Column: Input & Status */}
                <div className="space-y-6 lg:col-span-1">
                    <AgentChat />
                    <FinancialWidget data={financials} />
                    <SocialWidget />
                </div>

                {/* Middle/Right Column: Terminal (Wide) */}
                <div className="lg:col-span-3 space-y-6">
                    <AgentTerminal />
                    
                    {/* Task Board embedded here for better width */}
                    <div className="pt-4">
                        <div className="flex items-center gap-2 mb-4">
                            <h2 className="text-xl font-bold text-white">Active Operations</h2>
                            <span className="px-2 py-0.5 rounded text-xs bg-zinc-800 text-zinc-400">
                                {pending.length} PENDING
                            </span>
                        </div>
                        <TaskBoard initialPending={pending} initialCompleted={completed} />
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}