"use client"

import { useMemo } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Scatter
} from "recharts"

type Props = {
  data: { date: string; open: number; resolved: number }[]
  anomalies?: { date: string; volume: number; category_hint: string; reason: string }[]
}

export function TrendChart({ data, anomalies = [] }: Props) {
  // Merge anomalies with main chart data for tooltip lookup
  const chartData = useMemo(() => data ?? [], [data])

  // Map anomalies to plot points
  const anomalyPoints = useMemo(() => {
    if (!anomalies?.length) return []
    return anomalies.map(a => ({
      date: a.date,
      volume: a.volume,
      category_hint: a.category_hint,
      reason: a.reason
    }))
  }, [anomalies])

  if (!chartData.length) {
    return <div className="h-72 flex items-center justify-center text-muted-foreground">No data available</div>
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <defs>
            <linearGradient id="colorOpen" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="oklch(var(--chart-1))" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="oklch(var(--chart-1))" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="oklch(var(--chart-3))" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="oklch(var(--chart-3))" stopOpacity={0}/>
            </linearGradient>
          </defs>

          <CartesianGrid stroke="hsl(var(--color-border))" strokeDasharray="3 3" />
          <XAxis dataKey="date" stroke="hsl(var(--color-muted-foreground))" />
          <YAxis stroke="hsl(var(--color-muted-foreground))" />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--background))",
              border: "1px solid hsl(var(--color-border))",
            }}
            labelStyle={{ color: "hsl(var(--color-muted-foreground))" }}
            formatter={(value, name) =>
              [value, name === "open" ? "Open Tickets" : name === "resolved" ? "Resolved Tickets" : "Anomaly Volume"]
            }
          />
          <Legend formatter={(value) =>
            value === "open" ? "Open Tickets"
              : value === "resolved" ? "Resolved Tickets"
              : "Detected Anomalies"
          } />

          {/* Lines */}
          <Line
            type="monotone"
            dataKey="open"
            stroke="oklch(var(--chart-1))"
            strokeWidth={2}
            dot={false}
            fillOpacity={1}
            fill="url(#colorOpen)"
          />
          <Line
            type="monotone"
            dataKey="resolved"
            stroke="oklch(var(--chart-3))"
            strokeWidth={2}
            dot={false}
            fillOpacity={1}
            fill="url(#colorResolved)"
          />

          {/* Scatter points for anomalies */}
          {anomalyPoints.length > 0 && (
            <Scatter
              name="Anomalies"
              data={anomalyPoints}
              fill="hsl(var(--destructive))"
              shape="circle"
              legendType="circle"
              tooltipType="none"
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      {/* Optional hint below chart */}
      {anomalyPoints.length > 0 && (
        <div className="mt-2 text-xs text-muted-foreground text-center">
          ⚠️ {anomalyPoints.length} anomalies detected — hover over red dots to inspect unusual ticket spikes.
        </div>
      )}
    </div>
  )
}
