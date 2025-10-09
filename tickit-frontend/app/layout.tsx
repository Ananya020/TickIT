import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/toaster"
import { Suspense } from "react"

export const metadata: Metadata = {
  title: "TickIT | AI Service Desk",
  description: "AI-powered IT help desk dashboard for intelligent incident management.",
  generator: "v0.app",
  applicationName: "TickIT",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`font-sans ${GeistSans.variable} ${GeistMono.variable} antialiased bg-background text-foreground`}
      >
        <Providers>
          <Suspense fallback={<div>Loading...</div>}>
            {children}
            <Toaster />
          </Suspense>
        </Providers>
        <Analytics />
      </body>
    </html>
  )
}
