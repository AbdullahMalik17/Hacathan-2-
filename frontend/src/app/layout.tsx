import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"
import { Toaster } from "sonner"
import PWAProvider from '@/components/pwa/PWAProvider'
import MobileNav from '@/components/MobileNav'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Abdullah Junior | Digital FTE',
  description: 'Your AI-powered Digital Full-Time Employee - Control your agent from anywhere',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Abdullah Junior',
  },
  icons: {
    icon: '/icons/icon.svg',
    apple: '/icons/icon.svg',
  },
}

export const viewport: Viewport = {
  themeColor: '#000000',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="application-name" content="Abdullah Junior" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body className={cn(inter.className, "min-h-screen bg-background font-sans antialiased")}>
        <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
        >
            <div className="relative flex min-h-screen flex-col">
                {/* Header */}
                <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                    <div className="container flex h-14 items-center px-4">
                        <div className="mr-4 flex">
                            <Link href="/" className="mr-6 flex items-center space-x-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                                    <span className="text-white font-bold text-sm">AJ</span>
                                </div>
                                <span className="font-bold hidden sm:inline-block">Abdullah Junior</span>
                            </Link>
                            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
                                <Link href="/" className="transition-colors hover:text-foreground/80 text-foreground/60">
                                    Dashboard
                                </Link>
                                <Link href="/skills" className="transition-colors hover:text-foreground/80 text-foreground/60">
                                    Skills
                                </Link>
                            </nav>
                        </div>
                        <div className="flex flex-1 items-center justify-end space-x-2">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-xs text-muted-foreground hidden sm:inline">Online</span>
                            </div>
                            <ModeToggle />
                        </div>
                    </div>
                </header>

                {/* Main content */}
                <main className="flex-1 container py-4 md:py-6 px-4 pb-20 md:pb-6">
                    {children}
                </main>

                {/* Mobile navigation */}
                <MobileNav />

                {/* Desktop footer */}
                <footer className="hidden md:block py-6 border-t">
                    <div className="container text-center text-sm text-muted-foreground">
                        Digital FTE - Platinum Tier
                    </div>
                </footer>
            </div>

            {/* PWA Components */}
            <PWAProvider />
            <Toaster position="top-center" />
        </ThemeProvider>
      </body>
    </html>
  )
}
