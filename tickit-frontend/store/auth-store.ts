"use client"

import { create } from "zustand"
import { persist, createJSONStorage } from "zustand/middleware"
import { api } from "@/lib/api"
import type { User, AuthResponse } from "@/lib/types"

type LoginArgs = { username: string; password: string }
type AuthState = {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (args: LoginArgs) => Promise<void>
  logout: () => Promise<void>
  initialize: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: async ({ username, password }) => {
        // OAuth2PasswordRequestForm expects x-www-form-urlencoded: username, password
        const form = new URLSearchParams({ username, password })
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const res = await fetch(`${baseUrl}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: form,
        })
        const text = await res.text()
        const data = text ? JSON.parse(text) : {}
        if (!res.ok) {
          const message = data?.message || data?.detail || res.statusText
          throw new Error(message)
        }
        const token = data.access_token || data.token
        if (!token) throw new Error("No token returned")
        const user = data.user || { email: username, role: "agent" }
        set({ token, user, isAuthenticated: true })
      },
      logout: async () => {
        set({ token: null, user: null, isAuthenticated: false })
      },
      initialize: () => {
        const { token } = get()
        set({ isAuthenticated: Boolean(token) })
      },
    }),
    {
      name: "tickit-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({ token: s.token, user: s.user }),
    },
  ),
)
