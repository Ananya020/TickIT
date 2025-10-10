"use client"

import type React from "react"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Loader2 } from "lucide-react"
import { mutate as mutateSWR } from "swr"

export function CreateTicketForm() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [category, setCategory] = useState("")
  const [priority, setPriority] = useState<"Low" | "Medium" | "High" | "Critical" | "">("")
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const { toast } = useToast()
  const router = useRouter()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      let payload: any
      if (file) {
        const fd = new FormData()
        fd.append("title", title)
        fd.append("description", description)
        if (category) fd.append("category", category)
        if (priority) fd.append("priority", priority)
        fd.append("image", file)
        payload = fd
      } else {
        payload = { title, description, category, priority }
      }

      const res = await api.post("/tickets/create", payload)

      // Extract ticket ID from backend response
      const id = res?.ticket_id || res?.id || res?.data?.ticket_id || res?.data?.id

      toast({ title: "Ticket created", description: "We will look into this shortly." })

      // Refresh all tickets lists (any key starting with /tickets/all)
      await mutateSWR(
        (key: any) => typeof key === "string" && key.startsWith("/tickets/all"),
        undefined,
        { revalidate: true }
      )

      // Navigate to the new ticket detail page
      if (id) router.push(`/tickets/${id}`)
      else router.push("/tickets")
    } catch (err: any) {
      toast({
        title: "Failed to create ticket",
        description: err?.message || "Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="space-y-2">
        <Label>Title</Label>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Briefly describe the issue"
          required
        />
      </div>

      <div className="space-y-2">
        <Label>Description</Label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Provide relevant details and steps to reproduce"
          rows={6}
          required
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label>Category</Label>
          <Input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., Network, Hardware, Software"
          />
        </div>
        <div className="space-y-2">
          <Label>Priority</Label>
          <Select value={priority} onValueChange={(v: any) => setPriority(v)}>
            <SelectTrigger>
              <SelectValue placeholder="Select priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Low">Low</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Critical">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Attach image</Label>
        <Input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <p className="text-xs text-muted-foreground">Optional. PNG, JPG up to ~5MB.</p>
      </div>

      <Button type="submit" disabled={loading}>
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit Ticket"}
      </Button>
    </form>
  )
}
