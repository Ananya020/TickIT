"use client"

import { useAuthStore } from "@/store/auth-store"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function request(path: string, options: RequestInit = {}) {
  const token = useAuthStore.getState().token
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers }).catch((e) => {
    console.error("API network error:", e)
    throw new Error("Network error. Is the backend running?")
  })
  if (res.status === 401) {
    // Clear auth on unauthorized
    useAuthStore.getState().logout()
    if (typeof window !== "undefined") window.location.replace("/login")
    throw new Error("Unauthorized")
  }
  let data: any = null
  const text = await res.text()
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }
  if (!res.ok) {
    const message = data?.message || data?.detail || res.statusText
    console.error("API error:", { path, status: res.status, message, data })
    throw new Error(message)
  }
  return data
}

export const api = {
  fetcher: (path: string) => request(path, { method: "GET" }),
  get: (path: string) => request(path, { method: "GET" }),
  post: (path: string, body?: any) => request(path, { method: "POST", body: JSON.stringify(body ?? {}) }),
  put: (path: string, body?: any) => request(path, { method: "PUT", body: JSON.stringify(body ?? {}) }),
  delete: (path: string) => request(path, { method: "DELETE" }),
}
