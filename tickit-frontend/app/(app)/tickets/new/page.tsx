"use client"

import { CreateTicketForm } from "@/components/forms/create-ticket-form"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"

export default function NewTicketPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <Card className="rounded-2xl">
        <CardHeader>
          <CardTitle>Create New Ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateTicketForm />
        </CardContent>
      </Card>
    </motion.div>
  )
}
