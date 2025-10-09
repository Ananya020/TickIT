"use client"

import { useState } from "react"
import useSWR from "swr"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { TicketsTable } from "@/components/tickets/table"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { useDebouncedValue } from "@/hooks/use-debounced"
import { PlusCircle, Search } from "lucide-react"
import Link from "next/link"

type Ticket = {
  id: string
  title: string
  category: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: "Open" | "In Progress" | "Resolved" | "Closed"
  createdAt: string
}

type TicketsResponse = {
  items: Ticket[]
  page: number
  pageSize: number
  total: number
}

export default function TicketsPage() {
  const [query, setQuery] = useState("")
  const [status, setStatus] = useState<string | undefined>("All")
  const [priority, setPriority] = useState<string | undefined>("All")
  const [page, setPage] = useState(1)
  const debouncedQuery = useDebouncedValue(query, 350)

  const qs = new URLSearchParams({
    query: debouncedQuery || "",
    status: status || "",
    priority: priority || "",
    page: String(page),
  }).toString()

  const { data, error, isLoading, mutate } = useSWR<TicketsResponse>(`/tickets/all?${qs}`)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-8 w-64"
            placeholder="Search tickets..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <Select onValueChange={(v) => setStatus(v || "All")} value={status}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="Open">Open</SelectItem>
            <SelectItem value="In Progress">In Progress</SelectItem>
            <SelectItem value="Resolved">Resolved</SelectItem>
            <SelectItem value="Closed">Closed</SelectItem>
          </SelectContent>
        </Select>
        <Select onValueChange={(v) => setPriority(v || "All")} value={priority}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="Low">Low</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="High">High</SelectItem>
            <SelectItem value="Critical">Critical</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="secondary" onClick={() => mutate()}>
          Refresh
        </Button>
        <div className="ml-auto">
          <Button asChild>
            <Link href="/tickets/new">
              <PlusCircle className="mr-2 h-4 w-4" /> New Ticket
            </Link>
          </Button>
        </div>
      </div>

      {isLoading ? (
        <Skeleton className="h-64 rounded-xl" />
      ) : error ? (
        <Alert variant="destructive">
          <AlertTitle>Failed to load tickets</AlertTitle>
          <AlertDescription>Try adjusting filters or refreshing.</AlertDescription>
        </Alert>
      ) : data ? (
        <TicketsTable
          items={data.items}
          page={data.page}
          pageSize={data.pageSize}
          total={data.total}
          onPageChange={setPage}
        />
      ) : null}
    </div>
  )
}
