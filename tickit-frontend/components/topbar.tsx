"use client"

import { ThemeToggle } from "@/components/theme-toggle"
import { useUIStore } from "@/store/ui-store"
import { Button } from "@/components/ui/button"
import { MessageCircle } from "lucide-react"

export function Topbar({ title }: { title: string }) {
  const openChat = useUIStore((s) => s.openChatbot)

  return (
    <header className="h-16 border-b border-border/60 bg-card/70 supports-[backdrop-filter]:backdrop-blur flex items-center px-4 md:px-6">
      <h1 className="text-lg font-semibold text-balance">{title}</h1>
      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        <Button variant="secondary" onClick={openChat} aria-label="Open assistant">
          <MessageCircle className="h-4 w-4 mr-2" /> Ask AI
        </Button>
      </div>
    </header>
  )
}
