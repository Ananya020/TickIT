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
        const res = (await api.post("/auth/login", { username, password })) as AuthResponse
        const token = res.access_token || res.token
        if (!token) throw new Error("No token returned")
        const user = res.user || { email: username, role: "agent" }
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
