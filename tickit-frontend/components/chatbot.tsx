"use client"

import { useEffect, useState, useRef } from "react"
import type React from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useUIStore } from "@/store/ui-store"
import { api } from "@/lib/api"
import { MessageCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import { motion } from "framer-motion"

export function Chatbot() {
  const open = useUIStore((s) => s.chatbotOpen)
  const close = useUIStore((s) => s.closeChatbot)
  const history = useUIStore((s) => s.chatHistory)
  const addMessage = useUIStore((s) => s.addMessage)
  const [text, setText] = useState("")
  const [sending, setSending] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [history, sending, open])

  const send = async () => {
    if (!text.trim()) return
    const content = text.trim()
    setText("")
    addMessage({ role: "user", content })
    setSending(true)
    try {
      const res = await api.post("/api/chat", { query: content })
      const reply = (res && (res.response || res.answer)) || JSON.stringify(res)
      addMessage({ role: "assistant", content: reply })
    } catch (e: any) {
      console.error("Chatbot error:", e)
      addMessage({ role: "assistant", content: "Sorry, I could not process that. Please try again." })
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <>
      <button
        className="fixed bottom-6 right-6 h-12 w-12 rounded-full bg-primary text-primary-foreground shadow-lg grid place-items-center hover:opacity-90"
        onClick={() => useUIStore.getState().openChatbot()}
        aria-label="Open AI Assistant"
      >
        <MessageCircle className="h-5 w-5" />
      </button>

      <Dialog open={open} onOpenChange={(o) => (o ? useUIStore.getState().openChatbot() : close())}>
        <DialogContent className="sm:max-w-lg max-h-[85vh]">
          <DialogHeader>
            <DialogTitle>AI Assistant</DialogTitle>
          </DialogHeader>

          <div className="flex flex-col h-[60vh]">
            <ScrollArea className="flex-1 pr-2 overflow-hidden">
              <div className="space-y-3 pb-2 w-full">
                {history.map((m, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.15 }}
                    className={cn(
                      "p-3 rounded-xl max-w-[85%] w-fit overflow-hidden text-sm leading-relaxed break-words whitespace-pre-wrap",
                      m.role === "user" ? "ml-auto bg-primary/10 text-foreground" : "mr-auto bg-accent text-foreground"
                    )}
                    style={{
                      wordBreak: "break-word",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {m.content}
                  </motion.div>
                ))}

                {sending && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mr-auto text-sm text-muted-foreground flex items-center gap-1"
                  >
                    <div className="flex gap-1">
                      <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                      <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                      <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                    </div>
                    Assistant is typing...
                  </motion.div>
                )}

                <div ref={endRef} />
              </div>
            </ScrollArea>

            <div className="mt-3 flex gap-2">
              <Input
                ref={inputRef}
                placeholder="Type your question and hit Enter"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={onKeyDown}
              />
              <Button onClick={send} disabled={sending}>
                Send
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
