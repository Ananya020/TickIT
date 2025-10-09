"use client"

import useSWR from "swr"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/components/ui/use-toast"
import { api } from "@/lib/api"
import { useState } from "react"
import { Brain, Sparkles } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

type Ticket = { id: string; description: string; category?: string }
type Recommendation = { text: string; score: number }

export function TicketAITools({ id }: { id: string }) {
  const { data: ticket, error, isLoading, mutate } = useSWR<Ticket>(`/tickets/${id}`)
  const { toast } = useToast()
  const [classifying, setClassifying] = useState(false)

  const {
    data: recs,
    error: recError,
    isLoading: recLoading,
    mutate: refetchRecs,
  } = useSWR<Recommendation[]>(
    ticket?.description ? ["/recommend/resolution", ticket.description] : null,
    async ([endpoint, description]) => {
      const res = await api.post(endpoint as string, { description })
      return res?.recommendations || res?.data || []
    },
  )

  const classify = async () => {
    if (!ticket?.description) return
    setClassifying(true)
    try {
      const res = await api.post("/classify/ticket", { description: ticket.description })
      const newCategory = res?.category || res?.data?.category
      if (newCategory) {
        await api.put(`/tickets/update/${id}`, { category: newCategory })
      }
      toast({ title: "Classification complete", description: newCategory ? `Category: ${newCategory}` : "Updated" })
      mutate()
    } catch (e: any) {
      toast({ title: "Classification failed", description: e?.message || "Try again later.", variant: "destructive" })
    } finally {
      setClassifying(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card className="rounded-2xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" /> AI Classification
          </CardTitle>
          <Button onClick={classify} disabled={classifying || isLoading}>
            {classifying ? "Classifying..." : "Auto-Classify"}
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-24 rounded-xl" />
          ) : error ? (
            <Alert variant="destructive">
              <AlertTitle>Ticket data unavailable</AlertTitle>
              <AlertDescription>Unable to classify without description.</AlertDescription>
            </Alert>
          ) : (
            <div className="text-sm text-muted-foreground">
              Use AI to auto-detect the best category based on the ticket description.
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-2xl">
        <CardHeader className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" /> Recommended Resolutions
          </CardTitle>
          <Button variant="secondary" onClick={() => refetchRecs()}>
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {recLoading ? (
            <Skeleton className="h-32 rounded-xl" />
          ) : recError ? (
            <Alert variant="destructive">
              <AlertTitle>Failed to load recommendations</AlertTitle>
              <AlertDescription>Please try again later.</AlertDescription>
            </Alert>
          ) : recs && recs.length > 0 ? (
            <ul className="space-y-3">
              {recs.slice(0, 3).map((r, i) => (
                <li key={i} className="p-3 rounded-xl border border-border/60">
                  <div className="text-sm leading-relaxed">{r.text}</div>
                  <div className="text-xs text-muted-foreground mt-1">Similarity: {(r.score * 100).toFixed(1)}%</div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-muted-foreground">No recommendations yet.</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
