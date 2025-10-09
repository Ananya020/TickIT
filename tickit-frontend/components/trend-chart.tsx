"use client"

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend, CartesianGrid } from "recharts"
import { useMemo } from "react"

type Props = { data: { date: string; open: number; resolved: number }[] }

export function TrendChart({ data }: Props) {
  const chartData = useMemo(() => data ?? [], [data])
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid stroke="hsl(var(--color-border))" strokeDasharray="3 3" />
          <XAxis dataKey="date" stroke="hsl(var(--color-muted-foreground))" />
          <YAxis stroke="hsl(var(--color-muted-foreground))" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="open" stroke="oklch(var(--chart-1))" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="resolved" stroke="oklch(var(--chart-3))" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
