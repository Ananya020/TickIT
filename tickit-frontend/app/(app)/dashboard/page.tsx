"use client"

import useSWR from "swr"
import { KPICard } from "@/components/kpi-card"
import { TrendChart } from "@/components/trend-chart"
import { RecentTicketsTable } from "@/components/recent-tickets-table"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { BadgeCheck, Timer, ListChecks, Ticket } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type Metrics = {
  totalTickets: number
  openTickets: number
  resolvedToday: number
  avgResolutionTimeHours: number
}

type TrendPoint = { date: string; open: number; resolved: number }

export default function DashboardPage() {
  const {
    data: metrics,
    error: metricsError,
    isLoading: metricsLoading,
    mutate: refetchMetrics,
  } = useSWR<Metrics>("/dashboard/metrics")
  const {
    data: trends,
    error: trendError,
    isLoading: trendLoading,
    mutate: refetchTrends,
  } = useSWR<TrendPoint[]>("/dashboard/trends")

  return (
    <div className="space-y-6">
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
              <AlertDescription>
                Check your connection.{" "}
                <button onClick={() => refetchTrends()} className="underline">
                  Retry
                </button>
              </AlertDescription>
            </Alert>
          ) : trends ? (
            <TrendChart data={trends} />
          ) : null}
        </CardContent>
      </Card>

      <RecentTicketsTable />
    </div>
  )
}
