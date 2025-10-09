"use client"

import { SWRConfig } from "swr"
import { api } from "@/lib/api"
import { type ReactNode, useEffect } from "react"
import { useUIStore } from "@/store/ui-store"

export function Providers({ children }: { children: ReactNode }) {
  const theme = useUIStore((s) => s.theme)
  useEffect(() => {
    const root = document.documentElement
    if (theme === "dark") root.classList.add("dark")
    else root.classList.remove("dark")
  }, [theme])

  return (
    <SWRConfig value={{ fetcher: api.fetcher, shouldRetryOnError: false, revalidateOnFocus: false }}>
      {children}
    </SWRConfig>
  )
}
