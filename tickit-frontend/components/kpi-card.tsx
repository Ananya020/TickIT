"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { LucideIcon } from "lucide-react"

export function KPICard({ label, value, icon: Icon }: { label: string; value: number | string; icon: LucideIcon }) {
  return (
    <Card className="rounded-2xl hover:shadow transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
        <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary grid place-items-center">
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
      </CardContent>
    </Card>
  )
}
