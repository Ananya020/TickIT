"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"

export default function HomeRedirect() {
  const router = useRouter()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  useEffect(() => {
    router.replace(isAuthenticated ? "/dashboard" : "/login")
  }, [isAuthenticated, router])
  return null
}
