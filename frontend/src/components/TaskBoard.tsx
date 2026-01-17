'use client'

import { useState } from 'react'
import { submitTask } from '@/app/actions'
import type { Task } from '@/types'
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { Search } from "lucide-react"

export default function TaskBoard({ 
    initialPending, 
    initialCompleted 
}: { 
    initialPending: Task[], 
    initialCompleted: Task[] 
}) {
    const [searchTerm, setSearchTerm] = useState("")
    const [showImportantOnly, setShowImportantOnly] = useState(false)

    const filterTask = (task: Task) => {
        const matchesSearch = task.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             task.filename.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesImportance = !showImportantOnly || task.importance === 'high';
        return matchesSearch && matchesImportance;
    }

    const filteredPending = initialPending.filter(filterTask)
    const filteredCompleted = initialCompleted.filter(filterTask)

    return (
        <div className="space-y-8">
            <div className="flex gap-4 items-start">
                <Card className="flex-grow border-2 border-primary/10 shadow-lg">
                    <CardHeader>
                        <CardTitle>New Task</CardTitle>
                        <CardDescription>Assign a new mission to Abdullah Junior.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form action={async (formData) => {
                            const promise = submitTask(formData);
                            toast.promise(promise, {
                                loading: 'Assigning task...',
                                success: 'Task assigned successfully!',
                                error: 'Failed to assign task',
                            });
                            await promise;
                        }} className="flex flex-col gap-4">
                            <div className="space-y-2">
                                <label htmlFor="title" className="text-sm font-medium">
                                    Task Title
                                </label>
                                <Input
                                    id="title"
                                    name="title"
                                    placeholder="Brief task summary..."
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="content" className="text-sm font-medium">
                                    Task Details
                                </label>
                                <Textarea
                                    id="content"
                                    name="content"
                                    placeholder="Describe the task in detail (Markdown supported)..."
                                    minRows={3}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="priority" className="text-sm font-medium">
                                    Priority
                                </label>
                                <select
                                    id="priority"
                                    name="priority"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                >
                                    <option value="low">Low</option>
                                    <option value="medium" selected>Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                            <div className="flex justify-end">
                                <Button type="submit">
                                    Send Task
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
                
                <Card className="w-1/3 hidden lg:block">
                     <CardHeader>
                        <CardTitle>Quick Filters</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input 
                                placeholder="Search tasks..." 
                                className="pl-8" 
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <input 
                                type="checkbox" 
                                id="important" 
                                checked={showImportantOnly}
                                onChange={(e) => setShowImportantOnly(e.target.checked)}
                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <label htmlFor="important" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Show High Importance Only
                            </label>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Mobile Search/Filter */}
            <div className="lg:hidden space-y-4">
                <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                        placeholder="Search tasks..." 
                        className="pl-8" 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="flex items-center space-x-2">
                    <input 
                        type="checkbox" 
                        id="important-mobile" 
                        checked={showImportantOnly}
                        onChange={(e) => setShowImportantOnly(e.target.checked)}
                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <label htmlFor="important-mobile" className="text-sm font-medium">High Importance Only</label>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                {/* Pending Tasks Column */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold flex items-center gap-2">
                           <Badge variant="warning" className="h-6 w-6 rounded-full p-0 flex items-center justify-center">{filteredPending.length}</Badge>
                           Pending Action
                        </h3>
                    </div>
                    
                    {filteredPending.length === 0 ? (
                        <Card className="bg-muted/50 border-dashed">
                            <CardContent className="py-8 text-center text-muted-foreground">
                                {searchTerm || showImportantOnly ? "No matching pending tasks." : "No pending tasks. Agent is idle."}
                            </CardContent>
                        </Card>
                    ) : (
                        filteredPending.map(task => (
                            <Card key={task.id} className={cn(
                                "hover:shadow-md transition-shadow border-l-4",
                                task.importance === 'high' ? "border-l-red-500 ring-1 ring-red-100" : "border-l-yellow-400"
                            )}>
                                <CardHeader className="pb-2">
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-base font-mono text-muted-foreground truncate w-2/3" title={task.filename}>
                                            {task.filename}
                                        </CardTitle>
                                        <div className="flex items-center gap-2">
                                            {task.importance === 'high' && (
                                                <Badge variant="destructive" className="text-[10px] px-1 py-0 animate-pulse">IMPORTANT</Badge>
                                            )}
                                            <Badge variant="outline" className="text-xs">
                                                {new Date(task.timestamp).toLocaleDateString()}
                                            </Badge>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="prose prose-sm dark:prose-invert max-w-none line-clamp-3 whitespace-pre-wrap">
                                        {task.content}
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>

                {/* Completed Tasks Column */}
                <div className="space-y-4">
                     <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold flex items-center gap-2">
                           <Badge variant="success" className="h-6 w-6 rounded-full p-0 flex items-center justify-center">{filteredCompleted.length}</Badge>
                           Completed
                        </h3>
                    </div>

                    {filteredCompleted.length === 0 ? (
                         <Card className="bg-muted/50 border-dashed">
                            <CardContent className="py-8 text-center text-muted-foreground">
                                {searchTerm || showImportantOnly ? "No matching completed tasks." : "No completed tasks yet."}
                            </CardContent>
                        </Card>
                    ) : (
                        filteredCompleted.map(task => (
                            <Card key={task.id} className={cn(
                                "opacity-80 hover:opacity-100 transition-opacity border-l-4",
                                task.importance === 'high' ? "border-l-red-800" : "border-l-green-500"
                            )}>
                                <CardHeader className="pb-2">
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-base font-mono text-muted-foreground truncate w-2/3" title={task.filename}>
                                            {task.filename}
                                        </CardTitle>
                                        <div className="flex items-center gap-2">
                                             {task.importance === 'high' && (
                                                <Badge className="bg-red-900/20 text-red-900 border-red-900/20 text-[10px] px-1 py-0">IMPORTANT</Badge>
                                            )}
                                            <Badge variant="secondary" className="text-xs">
                                                Done
                                            </Badge>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="prose prose-sm dark:prose-invert max-w-none line-clamp-3 text-muted-foreground whitespace-pre-wrap">
                                        {task.content}
                                    </div>
                                </CardContent>
                                <CardFooter className="pt-0 text-xs text-muted-foreground justify-end">
                                    {new Date(task.timestamp).toLocaleString()}
                                </CardFooter>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
