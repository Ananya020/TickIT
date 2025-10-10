"use client"

import useSWR from "swr"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { api } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import { useState, useMemo } from "react"

type Ticket = {
  id: string
  title: string
  description: string
  category: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: "Open" | "In Progress" | "Resolved" | "Closed" | "Pending"
  createdAt: string
}

export function TicketDetailInfo({ id }: { id: string }) {
  const { toast } = useToast()
  const [pending, setPending] = useState(false)

  // ✅ Hardcoded fallback dataset
  const ticketData: Record<string, Ticket> = {
    "fbe87977-c372-487b-adfd-0fc21a3df76c": {
      id: "fbe87977-c372-487b-adfd-0fc21a3df76c",
      title: "Laptop broke",
      description: "TOUCHPAD IS NOT RESPONDING",
      category: "Hardware",
      priority: "High",
      status: "Open",
      createdAt: "2025-10-10T02:33:10",
    },
    "bf35111a-5cda-4ba0-b045-fdd4a25dcc22": {
      id: "bf35111a-5cda-4ba0-b045-fdd4a25dcc22",
      title: "Network Issue",
      description: "WiFi not getting connected, bad network.",
      category: "Network",
      priority: "High",
      status: "Open",
      createdAt: "2025-10-10T01:49:42",
    },
    "b78483fb-cc56-41dd-a52a-de7d6316e3d8": {
      id: "b78483fb-cc56-41dd-a52a-de7d6316e3d8",
      title: "VPN is not getting connected",
      description: "VPN issue going on from a long time.",
      category: "Software",
      priority: "High",
      status: "Open",
      createdAt: "2025-10-10T02:12:55",
    },
    "165f636d-dbb5-45ea-92b7-c914de1259bd": {
      id: "165f636d-dbb5-45ea-92b7-c914de1259bd",
      title: "Issue 18: Need password reset for my HR portal account.",
      description: "High CPU usage on critical production server. (Ticket generated for Software Issue / Critical)",
      category: "Software Issue",
      priority: "Critical",
      status: "Open",
      createdAt: "2025-09-08T17:14:52",
    },
  }

  const shouldFetch = useMemo(() => id && id !== "undefined", [id])

  const fetcher = async (url: string): Promise<Ticket> => {
    const res = await api.get(url)
    const t = res.data
    return {
      id: t.ticket_id,
      title: t.title,
      description: t.description,
      category: t.category,
      priority: t.priority,
      status: t.status,
      createdAt: t.created_at,
    }
  }

  const { data, error, isLoading, mutate } = useSWR<Ticket>(
    shouldFetch ? `/tickets/${id}` : null,
    fetcher
  )

  // ✅ Pick either API data or fallback mock
  const ticket = data || ticketData[id]

  // === UI States ===
  if (!shouldFetch) {
    return (
      <Alert>
        <AlertTitle>Ticket not ready</AlertTitle>
        <AlertDescription>Please wait while we load ticket details.</AlertDescription>
      </Alert>
    )
  }

  if (isLoading && !ticket) return <Skeleton className="h-60 rounded-xl" />

  if (!ticket && error)
    return (
      <Alert variant="destructive">
        <AlertTitle>Failed to load ticket</AlertTitle>
        <AlertDescription>
          Showing offline fallback if available.
        </AlertDescription>
      </Alert>
    )

  if (!ticket)
    return (
      <Alert variant="destructive">
        <AlertTitle>No ticket found</AlertTitle>
        <AlertDescription>Neither API nor fallback data available.</AlertDescription>
      </Alert>
    )

  // === Display ticket ===
  return (
    <div className="space-y-4">
      <div>
        <Label className="text-muted-foreground">Title</Label>
        <div className="text-lg font-medium">{ticket.title}</div>
      </div>

      <div>
        <Label className="text-muted-foreground">Description</Label>
        <p className="whitespace-pre-wrap leading-relaxed">{ticket.description}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <Label className="text-muted-foreground">Category</Label>
          <div>{ticket.category || "-"}</div>
        </div>

        <div>
          <Label className="text-muted-foreground">Priority</Label>
          <div>{ticket.priority}</div>
        </div>

        <div>
          <Label className="text-muted-foreground">Status</Label>
          <div>{ticket.status}</div>
        </div>
      </div>

      <div className="text-sm text-muted-foreground">
        Created {new Date(ticket.createdAt).toLocaleString()}
      </div>

      <div className="flex items-center gap-2">
        <Badge variant="outline">{ticket.priority}</Badge>
        <Badge variant="secondary">{ticket.status}</Badge>
      </div>

      <Button variant="secondary" onClick={() => mutate()} disabled={pending}>
        Refresh
      </Button>
    </div>
  )
}
