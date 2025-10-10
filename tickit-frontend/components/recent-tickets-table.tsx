"use client"

import useSWR from "swr"
import { useRouter } from "next/navigation"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { api } from "@/lib/api"

type Ticket = {
  ticket_id: string
  title: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: "Open" | "In Progress" | "Resolved" | "Closed" | "Pending"
  created_at: string
}

type TicketsResponse = {
  items: Ticket[]
  page: number
  pageSize: number
  total: number
}

function priorityClasses(priority: Ticket["priority"]) {
  switch (priority) {
    case "Low":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/20"
    case "Medium":
      return "bg-amber-500/15 text-amber-400 border-amber-500/20"
    case "High":
      return "bg-orange-500/15 text-orange-400 border-orange-500/20"
    case "Critical":
      return "bg-red-500/15 text-red-400 border-red-500/20"
    default:
      return ""
  }
}

export function RecentTicketsTable() {
  const router = useRouter()

  const { data, error, isLoading, mutate } = useSWR<TicketsResponse>(
    "/tickets/all?page=1&page_size=10",
    api.fetcher
  )

  if (isLoading) return <Skeleton className="h-64 rounded-xl" />

  if (error)
    return (
      <Alert variant="destructive">
        <AlertTitle>Failed to load recent tickets</AlertTitle>
        <AlertDescription>
          <button onClick={() => mutate()} className="underline">
            Retry
          </button>
        </AlertDescription>
      </Alert>
    )

  const tickets = data?.items || []

  if (tickets.length === 0)
    return <div className="text-sm text-muted-foreground">No recent tickets found.</div>

  return (
    <div className="rounded-2xl border border-border/60 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((t, index) => (
            <TableRow
              key={t.ticket_id ?? `ticket-${index}`}
              className="cursor-pointer hover:bg-accent"
              onClick={() => router.push(`/tickets/${t.ticket_id}`)}
            >
              <TableCell className="font-mono text-xs truncate max-w-[120px]">
                {t.ticket_id}
              </TableCell>
              <TableCell className="max-w-[300px] truncate">{t.title}</TableCell>
              <TableCell>
                <Badge variant="outline" className={priorityClasses(t.priority)}>
                  {t.priority}
                </Badge>
              </TableCell>
              <TableCell>{t.status}</TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {t.created_at ? new Date(t.created_at).toLocaleString() : "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
