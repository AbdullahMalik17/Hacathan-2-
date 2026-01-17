import { fetchSkills } from '@/app/actions'
import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

export const dynamic = 'force-dynamic'

export default async function SkillsPage() {
  const skills = await fetchSkills()
  
  // Group skills by category
  const categories: Record<string, typeof skills> = {}
  skills.forEach(skill => {
    if (!categories[skill.category]) {
        categories[skill.category] = []
    }
    categories[skill.category].push(skill)
  })

  return (
    <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex justify-between items-center border-b pb-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Agent Skills</h1>
                <p className="text-muted-foreground mt-2">
                    {skills.length} capabilities available to Abdullah Junior
                </p>
            </div>
            <Button variant="outline" asChild>
                <Link href="/">&larr; Back to Dashboard</Link>
            </Button>
        </div>

        <div className="grid gap-8">
            {Object.keys(categories).map(category => (
                <div key={category} className="space-y-4">
                    <h2 className="text-2xl font-semibold tracking-tight">{category}</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {categories[category].map((skill, idx) => (
                            <Card key={idx} className="hover:shadow-lg transition-all duration-200">
                                <CardHeader className="space-y-1">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="font-mono text-sm font-medium text-primary">
                                            {skill.name}
                                        </CardTitle>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        {skill.description}
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            ))}

            {skills.length === 0 && (
                <Card className="border-dashed">
                    <CardContent className="py-12 text-center text-muted-foreground">
                        No skills found. Check the SKILLS-INDEX.md file location.
                    </CardContent>
                </Card>
            )}
        </div>
    </div>
  )
}