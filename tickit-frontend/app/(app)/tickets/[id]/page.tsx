"use client"

import { useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TicketDetailInfo } from "@/components/tickets/detail-info"
import { TicketAITools } from "@/components/tickets/ai-tools"
import { motion } from "framer-motion"

export default function TicketDetailPage() {
  const params = useParams()
  // Handle both string and array types for dynamic routes
  const id = typeof params?.id === "string" ? params.id : Array.isArray(params?.id) ? params.id[0] : undefined

  if (!id) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Invalid or missing ticket ID.
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="p-4 sm:p-6"
    >
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main ticket details card */}
        <Card className="lg:col-span-2 rounded-2xl border border-border/60 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg sm:text-xl font-semibold">
              Ticket #{id}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TicketDetailInfo id={id} />
          </CardContent>
        </Card>

        {/* Right column: AI tools and utilities */}
        <div className="space-y-6">
          <TicketAITools id={id} />
        </div>
      </div>
    </motion.div>
  )
}

