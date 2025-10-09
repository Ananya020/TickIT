"use client"

import { useParams } from "next/navigation"
import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TicketDetailInfo } from "@/components/tickets/detail-info"
import { TicketAITools } from "@/components/tickets/ai-tools"
import { motion } from "framer-motion"

export default function TicketDetailPage() {
  const params = useParams()
  const id = useMemo(() => String(params?.id || ""), [params])

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 rounded-2xl">
          <CardHeader>
            <CardTitle>Ticket #{id}</CardTitle>
          </CardHeader>
          <CardContent>
            <TicketDetailInfo id={id} />
          </CardContent>
        </Card>
        <div className="space-y-6">
          <TicketAITools id={id} />
        </div>
      </div>
    </motion.div>
  )
}
