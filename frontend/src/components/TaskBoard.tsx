'use client'

import { useState } from 'react'
import type { Task } from '@/types'
import { cn } from "@/lib/utils"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"

export default function TaskBoard({ 
    initialPending, 
    initialCompleted 
}: { 
    initialPending: Task[], 
    initialCompleted: Task[] 
}) {
    const [searchTerm, setSearchTerm] = useState("")

    const filterTask = (task: Task) => {
        const matchesSearch = task.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             task.filename.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    }

    const filteredPending = initialPending.filter(filterTask)
    const filteredCompleted = initialCompleted.filter(filterTask)

    return (
        <div className="space-y-6">
            {/* Filter Bar */}
            <div className="flex items-center gap-4 bg-zinc-900/50 p-3 rounded-lg border border-zinc-800">
                <div className="relative flex-1">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-zinc-500" />
                    <Input 
                        placeholder="Filter operations..." 
                        className="pl-8 bg-black/50 border-zinc-700 text-zinc-300 placeholder:text-zinc-600 focus-visible:ring-blue-500" 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="text-xs text-zinc-500 font-mono">
                    {filteredPending.length + filteredCompleted.length} OPS
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Pending Tasks Column */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                        <h3 className="text-sm font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                           <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                           Pending Action
                        </h3>
                        <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">{filteredPending.length}</Badge>
                    </div>
                    
                    {filteredPending.length === 0 ? (
                        <div className="h-32 flex items-center justify-center border border-dashed border-zinc-800 rounded-lg text-zinc-600 text-sm">
                            {searchTerm ? "No matching operations." : "No active operations."}
                        </div>
                    ) : (
                        filteredPending.map(task => (
                            <Card key={task.id} className={cn(
                                "bg-zinc-900/50 border-zinc-800 transition-all hover:bg-zinc-900 hover:border-zinc-700 group",
                                task.importance === 'high' ? "border-l-2 border-l-red-500" : "border-l-2 border-l-yellow-500"
                            )}>
                                <CardHeader className="pb-2 pt-4 px-4">
                                    <div className="flex justify-between items-start gap-4">
                                        <CardTitle className="text-sm font-mono text-zinc-300 truncate" title={task.filename}>
                                            {task.filename}
                                        </CardTitle>
                                        {task.importance === 'high' && (
                                            <span className="text-[10px] font-bold text-red-500 animate-pulse">CRITICAL</span>
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent className="px-4 pb-4">
                                    <div className="text-xs text-zinc-500 line-clamp-3 font-mono">
                                        {task.content.substring(0, 200)}...
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>

                {/* Completed Tasks Column */}
                <div className="space-y-4">
                     <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                        <h3 className="text-sm font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                           <span className="w-2 h-2 rounded-full bg-green-500"></span>
                           Completed
                        </h3>
                        <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">{filteredCompleted.length}</Badge>
                    </div>

                    {filteredCompleted.length === 0 ? (
                         <div className="h-32 flex items-center justify-center border border-dashed border-zinc-800 rounded-lg text-zinc-600 text-sm">
                            {searchTerm ? "No matching records." : "No operations log."}
                        </div>
                    ) : (
                        filteredCompleted.map(task => (
                            <Card key={task.id} className="bg-zinc-950/50 border-zinc-900 hover:border-zinc-800 transition-colors opacity-75 hover:opacity-100">
                                <CardHeader className="pb-2 pt-4 px-4">
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-sm font-mono text-zinc-500 truncate decoration-zinc-700" title={task.filename}>
                                            {task.filename}
                                        </CardTitle>
                                        <span className="text-[10px] text-green-700 font-mono">DONE</span>
                                    </div>
                                </CardHeader>
                                <CardFooter className="pt-0 px-4 pb-2 justify-end">
                                    <span className="text-[10px] text-zinc-700 font-mono">
                                        {new Date(task.timestamp).toLocaleString()}
                                    </span>
                                </CardFooter>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
