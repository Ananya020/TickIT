"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function EndUserPage() {
  const user = useAuthStore((s) => s.user)
  const router = useRouter()
  useEffect(() => {
    if (user && user.role !== "end-user") router.replace("/dashboard")
  }, [user, router])

  return (
    <div className="space-y-6">
      <Card className="rounded-2xl">
        <CardHeader>
          <CardTitle>My Support</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Create and track your support tickets easily.
        </CardContent>
      </Card>
      <div className="flex gap-3">
        <Button asChild>
          <Link href="/tickets/new">Create Ticket</Link>
        </Button>
        <Button variant="secondary" asChild>
          <Link href="/tickets">View All Tickets</Link>
        </Button>
      </div>
    </div>
  )
}
