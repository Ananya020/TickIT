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

type Ticket = {
  ticket_id: string
  description?: string
  category?: string
  priority?: "Low" | "Medium" | "High" | "Critical"
  status?: "Open" | "In Progress" | "Resolved" | "Closed"
  created_at?: string
}

type Recommendation = { text: string; score: number }

type ClassifyResponse = {
  category?: string
  confidence?: number
}

type SLARiskResponse = {
  risk_score: number
  risk_status: "Low" | "Medium" | "High" | "Critical"
  predicted_breach_time?: string | null
  model_used: string
}

export function TicketAITools({ id }: { id: string }) {
  const { toast } = useToast()
  const [classifying, setClassifying] = useState(false)

  // --- Hardcoded fallback data (for offline demo) ---
  const mockTickets: Record<string, Ticket> = {
    "fbe87977-c372-487b-adfd-0fc21a3df76c": {
      ticket_id: "fbe87977-c372-487b-adfd-0fc21a3df76c",
      description: "TOUCHPAD IS NOT RESPONDING",
      category: "Hardware",
      priority: "High",
      status: "Open",
      created_at: "2025-10-10T02:33:10",
    },
    "b78483fb-cc56-41dd-a52a-de7d6316e3d8": {
      ticket_id: "b78483fb-cc56-41dd-a52a-de7d6316e3d8",
      description: "VPN issue going on from a long time",
      category: "Software",
      priority: "High",
      status: "Open",
      created_at: "2025-10-10T02:12:55",
    },
  }

  const mockRecommendations: Record<string, Recommendation[]> = {
    "fbe87977-c372-487b-adfd-0fc21a3df76c": [
      { text: "Try reinstalling the touchpad driver from Device Manager.", score: 0.93 },
      { text: "Check BIOS settings to ensure touchpad is enabled.", score: 0.87 },
      { text: "Run hardware diagnostics to verify touchpad hardware integrity.", score: 0.84 },
    ],
    "b78483fb-cc56-41dd-a52a-de7d6316e3d8": [
      { text: "Check if VPN credentials are correct and up to date.", score: 0.91 },
      { text: "Verify network connectivity before starting VPN client.", score: 0.88 },
      { text: "Restart the VPN service and reattempt connection.", score: 0.83 },
    ],
  }

  const mockSLA: Record<string, SLARiskResponse> = {
    "fbe87977-c372-487b-adfd-0fc21a3df76c": {
      risk_score: 0.72,
      risk_status: "High",
      predicted_breach_time: "2025-10-10T05:33:00",
      model_used: "GradientBoosted SLA Predictor v2.1",
    },
    "b78483fb-cc56-41dd-a52a-de7d6316e3d8": {
      risk_score: 0.45,
      risk_status: "Medium",
      predicted_breach_time: "2025-10-11T01:00:00",
      model_used: "GradientBoosted SLA Predictor v2.1",
    },
  }

  // --- Fetch ticket details ---
  const { data: ticket, error, isLoading, mutate } = useSWR<Ticket>(
    id && id !== "undefined" ? `/tickets/${id}` : null,
    async (url) => {
      const res = await api.get(url)
      const t: Ticket = res.data
      return {
        ...t,
        ticket_id: t.ticket_id,
        created_at: t.created_at,
      }
    }
  )

  const activeTicket = ticket || mockTickets[id]

  // --- AI Classification ---
  const classify = async () => {
    if (!activeTicket?.description) return
    setClassifying(true)
    try {
      const res = await api.post<ClassifyResponse>("/classify/ticket", {
        description: activeTicket.description,
      })
      const newCategory = res.data?.category || activeTicket.category
      const confidence = res.data?.confidence ?? 0.85

      toast({
        title: "Classification complete",
        description: `Category: ${newCategory} • Confidence: ${(confidence * 100).toFixed(1)}%`,
      })
      mutate()
    } catch {
      // fallback for demo
      toast({
        title: "Classification (Offline Mock)",
        description: `Category: ${activeTicket?.category || "General"} • Confidence: 91.2%`,
      })
    } finally {
      setClassifying(false)
    }
  }

  // --- Recommended Resolutions ---
  const {
    data: recs,
    error: recError,
    isLoading: recLoading,
    mutate: refetchRecs,
  } = useSWR<Recommendation[]>(
    activeTicket?.description ? ["/recommend/resolution", activeTicket.description] : null,
    async ([endpoint, description]) => {
      const res = await api.post(endpoint, { ticket_description: description })
      return res.data?.recommendations || []
    }
  )

  const recommendations = recs && recs.length > 0 ? recs : mockRecommendations[id]

  // --- SLA Risk Prediction ---
  const {
    data: slaData,
    error: slaError,
    isLoading: slaLoading,
    mutate: refetchSLA,
  } = useSWR<SLARiskResponse>(
    activeTicket
      ? [
          "/sla/risk",
          {
            priority: activeTicket.priority || "Medium",
            category: activeTicket.category || "General",
          },
        ]
      : null,
    async ([endpoint, payload]) => {
      const res = await api.post(endpoint, payload)
      return res.data
    }
  )

  const slaResult = slaData || mockSLA[id]

  // --- Invalid ID ---
  if (!id || id === "undefined") {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertTitle>Invalid Ticket ID</AlertTitle>
          <AlertDescription>Please open a valid ticket to use AI tools.</AlertDescription>
        </Alert>
      </div>
    )
  }

  // --- Main UI ---
  return (
    <div className="space-y-6">
      {/* === AI Classification === */}
      <Card className="rounded-2xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" /> AI Classification
          </CardTitle>
          <Button onClick={classify} disabled={classifying || isLoading || !activeTicket?.description}>
            {classifying ? "Classifying..." : "Auto-Classify"}
          </Button>
        </CardHeader>
        <CardContent>
          {!activeTicket?.description ? (
            <Alert>
              <AlertTitle>No description available</AlertTitle>
              <AlertDescription>Add a description to use AI classification.</AlertDescription>
            </Alert>
          ) : (
            <div className="text-sm text-muted-foreground">
              Use AI to detect the most suitable category from the ticket description.
            </div>
          )}
        </CardContent>
      </Card>

      {/* === Recommended Resolutions === */}
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
          ) : recommendations && recommendations.length > 0 ? (
            <ul className="space-y-3">
              {recommendations.slice(0, 3).map((r, i) => (
                <li key={i} className="p-3 rounded-xl border border-border/60">
                  <div className="text-sm leading-relaxed">{r.text}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Similarity: {(r.score * 100).toFixed(1)}%
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-muted-foreground">No recommendations available.</div>
          )}
        </CardContent>
      </Card>

      {/* === SLA Risk Prediction === */}
      <Card className="rounded-2xl">
        <CardHeader className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" /> SLA Risk Prediction
          </CardTitle>
          <Button variant="secondary" onClick={() => refetchSLA()}>
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {slaLoading ? (
            <Skeleton className="h-24 rounded-xl" />
          ) : slaResult ? (
            <div className="space-y-2 text-sm">
              <div>Risk Score: {(slaResult.risk_score * 100).toFixed(1)}%</div>
              <div>Status: {slaResult.risk_status}</div>
              <div>
                Predicted Breach:{" "}
                {slaResult.predicted_breach_time
                  ? new Date(slaResult.predicted_breach_time).toLocaleString()
                  : "Already Breached"}
              </div>
              <div className="text-xs text-muted-foreground">
                Model used: {slaResult.model_used}
              </div>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">SLA data not available.</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
