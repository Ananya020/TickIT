"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

type Ticket = {
  id: string
  title: string
  category: string
  priority: "Low" | "Medium" | "High" | "Critical"
  status: "Open" | "In Progress" | "Resolved" | "Closed"
  createdAt: string
}
export function TicketsTable({
  items,
  page,
  pageSize,
  total,
  onPageChange,
}: {
  items: Ticket[]
  page: number
  pageSize: number
  total: number
  onPageChange: (p: number) => void
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-border/60 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items?.map((t) => (
              <TableRow key={t.id}>
                <TableCell className="font-mono text-xs">{t.id}</TableCell>
                <TableCell>{t.title}</TableCell>
                <TableCell>{t.category}</TableCell>
                <TableCell>
                  <Badge variant="outline">{t.priority}</Badge>
                </TableCell>
                <TableCell>{t.status}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(t.createdAt).toLocaleString()}
                </TableCell>
                <TableCell className="text-right">
                  <Button asChild size="sm" variant="secondary">
                    <Link href={`/tickets/${t.id}`}>View</Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious onClick={() => onPageChange(Math.max(1, page - 1))} />
          </PaginationItem>
          <div className="px-3 text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </div>
          <PaginationItem>
            <PaginationNext onClick={() => onPageChange(Math.min(totalPages, page + 1))} />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  )
}
