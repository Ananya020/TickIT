"use client"

import useSWR from "swr"
import { Alert, AlertDescription } from "@/components/ui/alert"

export function HealthBanner() {
  const { data, error } = useSWR<{ status: "ok" | "down" }>("/health", { refreshInterval: 30000 })

  if (error || (data && data.status === "down")) {
    return (
      <Alert variant="destructive" className="rounded-none">
        <AlertDescription>The backend appears to be unavailable. Some actions may fail. Retrying...</AlertDescription>
      </Alert>
    )
  }
  return null
}
