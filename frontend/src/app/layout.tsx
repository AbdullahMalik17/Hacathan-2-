import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"
import { Toaster } from "sonner"

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Abdullah Junior | Digital FTE',
  description: 'Agent Task Orchestrator Interface',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn(inter.className, "min-h-screen bg-background font-sans antialiased")}>
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
            <div className="relative flex min-h-screen flex-col">
                <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                    <div className="container flex h-14 items-center">
                        <div className="mr-4 hidden md:flex">
                            <Link href="/" className="mr-6 flex items-center space-x-2">
                                <span className="hidden font-bold sm:inline-block">Abdullah Junior</span>
                            </Link>
                            <nav className="flex items-center space-x-6 text-sm font-medium">
                                <Link href="/" className="transition-colors hover:text-foreground/80 text-foreground/60 hover:underline underline-offset-4">
                                    Dashboard
                                </Link>
                                <Link href="/skills" className="transition-colors hover:text-foreground/80 text-foreground/60 hover:underline underline-offset-4">
                                    Skills
                                </Link>
                            </nav>
                        </div>
                        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                            <div className="w-full flex-1 md:w-auto md:flex-none">
                                <span className="text-xs text-muted-foreground bg-secondary px-2 py-1 rounded-full">
                                    System Status: Online
                                </span>
                            </div>
                            <ModeToggle />
                        </div>
                    </div>
                </header>
                <main className="flex-1 container py-6">
                    {children}
                </main>
                <footer className="py-6 md:px-8 md:py-0">
                    <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                        <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
                            Built for the <strong>Hacathan_2</strong> Project.
                        </p>
                    </div>
                </footer>
            </div>
            <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
