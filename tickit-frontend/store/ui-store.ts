"use client"

import { create } from "zustand"
import { persist, createJSONStorage } from "zustand/middleware"

type ChatMessage = { role: "user" | "assistant"; content: string }

type UIState = {
  sidebarCollapsed: boolean
  toggleSidebar: () => void

  theme: "dark" | "light"
  setTheme: (t: "dark" | "light") => void

  chatbotOpen: boolean
  openChatbot: () => void
  closeChatbot: () => void
  chatHistory: ChatMessage[]
  addMessage: (m: ChatMessage) => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

      theme: "dark",
      setTheme: (t) => set({ theme: t }),

      chatbotOpen: false,
      openChatbot: () => set({ chatbotOpen: true }),
      closeChatbot: () => set({ chatbotOpen: false }),
      chatHistory: [],
      addMessage: (m) => set((s) => ({ chatHistory: [...s.chatHistory, m] })),
    }),
    {
      name: "tickit-ui",
      storage: createJSONStorage(() => localStorage),
    },
  ),
)
