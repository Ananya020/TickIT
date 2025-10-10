"use client"

import useSWR from "swr"
import { KPICard } from "@/components/kpi-card"
import { TrendChart } from "@/components/trend-chart"
import { RecentTicketsTable } from "@/components/recent-tickets-table"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { BadgeCheck, Timer, ListChecks, Ticket, AlertTriangle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"

type Metrics = {
  totalTickets: number
  openTickets: number
  resolvedToday: number
  avgResolutionTimeHours: number
}

type TrendPoint = { date: string; open: number; resolved: number }

type Anomaly = {
  date: string
  volume: number
  category_hint: string
  reason: string
}

type HeatmapPoint = {
  lat: number
  lon: number
  value: number
  city: string
}

export default function DashboardPage() {
  // ✅ Metrics
  const { data: metrics, error: metricsError, isLoading: metricsLoading, mutate: refetchMetrics } =
    useSWR<Metrics>("/dashboard/metrics")

  // ✅ Trends
  const { data: trends, error: trendError, isLoading: trendLoading, mutate: refetchTrends } =
    useSWR<TrendPoint[]>("/dashboard/trends")

  // ✅ Anomalies
  const { data: anomalies, error: anomalyError, isLoading: anomalyLoading } =
    useSWR<{ anomalies: Anomaly[] }>("/anomaly/detect_anomalies")

  const hasAnomalies = (anomalies?.anomalies?.length ?? 0) > 0

  // ✅ Heatmap
  const { data: heatmapResponse, error: heatmapError, isLoading: heatmapLoading } =
    useSWR<{ type: string; data: HeatmapPoint[] }>("/dashboard/heatmap")
  const heatmap = heatmapResponse?.data || []

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metricsLoading ? (
          <>
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
          </>
        ) : metricsError ? (
          <Alert variant="destructive" className="sm:col-span-2 lg:col-span-4">
            <AlertTitle>Failed to load metrics</AlertTitle>
            <AlertDescription>
              Please try again.{" "}
              <button onClick={() => refetchMetrics()} className="underline">
                Retry
              </button>
            </AlertDescription>
          </Alert>
        ) : metrics ? (
          <>
            <KPICard icon={Ticket} label="Total Tickets" value={metrics.totalTickets} />
            <KPICard icon={ListChecks} label="Open Tickets" value={metrics.openTickets} />
            <KPICard icon={BadgeCheck} label="Resolved Today" value={metrics.resolvedToday} />
            <KPICard icon={Timer} label="Avg. Resolution (h)" value={metrics.avgResolutionTimeHours} />
          </>
        ) : null}
      </div>

      {/* AI Anomalies */}
      {hasAnomalies && (
        <Alert className="border-l-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-950/40">
          <AlertTriangle className="h-5 w-5 text-yellow-600" />
          <AlertTitle className="font-semibold text-yellow-800 dark:text-yellow-200">
            ⚠️ AI Insights: Potential Anomalies Detected
          </AlertTitle>
          <AlertDescription className="text-sm text-yellow-700 dark:text-yellow-300">
            The anomaly detection model identified {anomalies!.anomalies.length} unusual spikes in ticket activity — typically
            linked to {anomalies!.anomalies[0]?.category_hint}.
          </AlertDescription>
        </Alert>
      )}

      {/* Ticket Trends */}
      <Card className="rounded-2xl">
        <CardHeader>
          <CardTitle>Ticket Trends</CardTitle>
        </CardHeader>
        <CardContent>
          {trendLoading ? (
            <Skeleton className="h-64 rounded-xl" />
          ) : trendError ? (
            <Alert variant="destructive">
              <AlertTitle>Failed to load trends</AlertTitle>
            </Alert>
          ) : trends ? (
            <TrendChart data={trends} anomalies={anomalies?.anomalies} />
          ) : null}
        </CardContent>
      </Card>

      

      {/* Recent Tickets Table */}
      <RecentTicketsTable />
    </div>
  )
}
