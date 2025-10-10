"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import DashboardPage from "../dashboard/page"

export default function AgentPage() {
  const user = useAuthStore((s) => s.user)
  const router = useRouter()
  useEffect(() => {
    if (user && user.role !== "agent") router.replace("/dashboard")
  }, [user, router])
  // Reuse dashboard for agents
  return <DashboardPage />
}
