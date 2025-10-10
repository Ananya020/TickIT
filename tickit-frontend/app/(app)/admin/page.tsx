"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AdminPage() {
  const user = useAuthStore((s) => s.user)
  const router = useRouter()
  useEffect(() => {
    if (user && user.role !== "admin") router.replace("/dashboard")
  }, [user, router])
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card className="rounded-2xl">
        <CardHeader>
          <CardTitle>Admin Overview</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Manage users, roles, and system settings.</CardContent>
      </Card>
      <Card className="rounded-2xl">
        <CardHeader>
          <CardTitle>Reports</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Organization-wide ticket analytics.</CardContent>
      </Card>
    </div>
  )
}
