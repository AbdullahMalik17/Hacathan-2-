import { fetchSkills } from '@/app/actions'
import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Terminal, Cpu, Database, Share2, Shield, Wrench } from "lucide-react"

export const dynamic = 'force-dynamic'

const CATEGORY_ICONS: Record<string, any> = {
    'builtin': Cpu,
    'custom': Wrench,
    'MCP': Database,
    'Integration': Share2,
    'Security': Shield
}

export default async function SkillsPage() {
  const skills = await fetchSkills()
  
  // Group skills by category
  const categories: Record<string, typeof skills> = {}
  skills.forEach(skill => {
    // Normalize category
    let cat = skill.category || 'Other';
    if (cat.toLowerCase().includes('mcp')) cat = 'MCP';
    if (cat.toLowerCase().includes('integration')) cat = 'Integration';
    
    if (!categories[cat]) {
        categories[cat] = []
    }
    categories[cat].push(skill)
  })

  return (
    <div className="min-h-screen bg-black text-zinc-300 p-6">
        <div className="max-w-[1600px] mx-auto space-y-8">
            
            {/* Header */}
            <header className="flex justify-between items-end border-b border-zinc-800 pb-6">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-1">
                        NEURAL <span className="text-blue-500">CAPABILITIES</span>
                    </h1>
                    <p className="text-sm font-mono text-zinc-500">
                        ACTIVE SKILL MATRIX • {skills.length} MODULES LOADED
                    </p>
                </div>
                <Button variant="outline" className="border-zinc-700 bg-zinc-900/50 hover:bg-zinc-800 hover:text-white" asChild>
                    <Link href="/">
                        <Terminal className="mr-2 h-4 w-4" /> 
                        COMMAND CENTER
                    </Link>
                </Button>
            </header>

            {/* Skills Grid */}
            <div className="grid gap-8">
                {Object.keys(categories).sort().map(category => {
                    const Icon = CATEGORY_ICONS[category] || Terminal;
                    return (
                        <div key={category} className="space-y-4">
                            <div className="flex items-center gap-2">
                                <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                                    <Icon className="h-5 w-5 text-zinc-400" />
                                </div>
                                <h2 className="text-lg font-bold text-white uppercase tracking-wider">{category} MODULES</h2>
                                <Badge variant="outline" className="ml-2 bg-zinc-900 text-zinc-500 border-zinc-800">
                                    {categories[category].length}
                                </Badge>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {categories[category].map((skill, idx) => (
                                    <Card key={idx} className="bg-zinc-950/50 border-zinc-800 hover:border-blue-500/50 hover:bg-zinc-900/50 transition-all duration-300 group">
                                        <CardHeader className="space-y-1 pb-2">
                                            <div className="flex items-center justify-between">
                                                <CardTitle className="font-mono text-sm font-bold text-blue-400 group-hover:text-blue-300 truncate" title={skill.name}>
                                                    {skill.name}
                                                </CardTitle>
                                                <div className="w-2 h-2 rounded-full bg-green-500/50 group-hover:bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.2)]"></div>
                                            </div>
                                        </CardHeader>
                                        <CardContent>
                                            <p className="text-xs text-zinc-500 leading-relaxed line-clamp-3 group-hover:text-zinc-400">
                                                {skill.description}
                                            </p>
                                        </CardContent>
                                        <CardFooter className="pt-0 text-[10px] font-mono text-zinc-700 justify-between">
                                            <span>v1.0.0</span>
                                            <span className="text-zinc-600">ACTIVE</span>
                                        </CardFooter>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    );
                })}

                {skills.length === 0 && (
                    <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-zinc-800 rounded-xl bg-zinc-900/20">
                        <Terminal className="h-12 w-12 text-zinc-700 mb-4" />
                        <h3 className="text-xl font-bold text-zinc-500">NO SKILLS DETECTED</h3>
                        <p className="text-zinc-600 mt-2">System is running in minimal mode.</p>
                        <p className="text-zinc-700 text-sm mt-1">Check SKILLS-INDEX.md to register new capabilities.</p>
                    </div>
                )}
            </div>
        </div>
    </div>
  )
}