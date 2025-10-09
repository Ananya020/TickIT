"use client"

import useSWR from "swr"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { useRouter } from "next/navigation"

type Ticket = {
  id: string
  title: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: string
  createdAt: string
}

export function RecentTicketsTable() {
  const { data, error, isLoading, mutate } = useSWR<Ticket[]>("/tickets/all?limit=10")
  const router = useRouter()

  if (isLoading) return <Skeleton className="h-64 rounded-xl" />
  if (error) {
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
  }

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
          {data?.map((t) => (
            <TableRow
              key={t.id}
              className="cursor-pointer hover:bg-accent"
              onClick={() => router.push(`/tickets/${t.id}`)}
            >
              <TableCell className="font-mono text-xs">{t.id}</TableCell>
              <TableCell>{t.title}</TableCell>
              <TableCell>
                <Badge variant="outline">{t.priority}</Badge>
              </TableCell>
              <TableCell>{t.status}</TableCell>
              <TableCell className="text-sm text-muted-foreground">{new Date(t.createdAt).toLocaleString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
