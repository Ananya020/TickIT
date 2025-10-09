"use client"

import useSWR from "swr"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { api } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import { useState } from "react"

type Ticket = {
  id: string
  title: string
  description: string
  category: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: "Open" | "In Progress" | "Resolved" | "Closed"
  createdAt: string
}

export function TicketDetailInfo({ id }: { id: string }) {
  const { data, error, isLoading, mutate } = useSWR<Ticket>(`/tickets/${id}`)
  const [pending, setPending] = useState(false)
  const { toast } = useToast()

  if (isLoading) return <Skeleton className="h-60 rounded-xl" />
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Failed to load ticket</AlertTitle>
        <AlertDescription>
          <button onClick={() => mutate()} className="underline">
            Retry
          </button>
        </AlertDescription>
      </Alert>
    )
  }
  if (!data) return null

  const update = async (patch: Partial<Ticket>) => {
    setPending(true)
    try {
      await api.put(`/tickets/update/${id}`, patch)
      await mutate()
      toast({ title: "Ticket updated" })
    } catch (e: any) {
      toast({ title: "Update failed", description: e?.message || "Please try again.", variant: "destructive" })
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <Label className="text-muted-foreground">Title</Label>
        <div className="text-lg font-medium">{data.title}</div>
      </div>
      <div>
        <Label className="text-muted-foreground">Description</Label>
        <p className="whitespace-pre-wrap leading-relaxed">{data.description}</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <Label className="text-muted-foreground">Category</Label>
          <div>{data.category || "-"}</div>
        </div>
        <div className="space-y-2">
          <Label className="text-muted-foreground">Priority</Label>
          <Select value={data.priority} onValueChange={(v: any) => update({ priority: v })} disabled={pending}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Low">Low</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Critical">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label className="text-muted-foreground">Status</Label>
          <Select value={data.status} onValueChange={(v: any) => update({ status: v })} disabled={pending}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Open">Open</SelectItem>
              <SelectItem value="In Progress">In Progress</SelectItem>
              <SelectItem value="Resolved">Resolved</SelectItem>
              <SelectItem value="Closed">Closed</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="text-sm text-muted-foreground">Created {new Date(data.createdAt).toLocaleString()}</div>
      <div className="flex items-center gap-2">
        <Badge variant="outline">{data.priority}</Badge>
        <Badge variant="secondary">{data.status}</Badge>
      </div>
      <Button variant="secondary" onClick={() => mutate()} disabled={pending}>
        Refresh
      </Button>
    </div>
  )
}
