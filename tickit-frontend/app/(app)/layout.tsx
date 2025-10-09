"use client"

import type React from "react"

import { useEffect, useMemo } from "react"
import { usePathname, useRouter } from "next/navigation"
import { SidebarNav } from "@/components/sidebar"
import { Topbar } from "@/components/topbar"
import { motion, AnimatePresence } from "framer-motion"
import { HealthBanner } from "@/components/health-banner"
import { Chatbot } from "@/components/chatbot"
import { useAuthStore } from "@/store/auth-store"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const initialize = useAuthStore((s) => s.initialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  useEffect(() => {
    if (!isAuthenticated) {
      // Avoid redirect loop if already on login
      router.replace("/login")
    }
  }, [isAuthenticated, router])

  const pageTitle = useMemo(() => {
    if (pathname?.startsWith("/dashboard")) return "Dashboard"
    if (pathname === "/tickets") return "All Tickets"
    if (pathname?.startsWith("/tickets/new")) return "Create Ticket"
    if (pathname?.startsWith("/tickets/")) return "Ticket Detail"
    return "TickIT"
  }, [pathname])

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="flex min-h-dvh">
      <SidebarNav />
      <div className="flex-1 flex flex-col">
        <HealthBanner />
        <Topbar title={pageTitle} />
        <main className="p-6 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      <Chatbot />
    </div>
  )
}
