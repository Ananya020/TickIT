"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useUIStore } from "@/store/ui-store"
import { useAuthStore } from "@/store/auth-store"
import { LayoutDashboard, PlusSquare, Ticket, LogOut } from "lucide-react"

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/tickets", label: "All Tickets", icon: Ticket },
  { href: "/tickets/new", label: "New Ticket", icon: PlusSquare },
]

export function SidebarNav() {
  const pathname = usePathname()
  const collapsed = useUIStore((s) => s.sidebarCollapsed)
  const toggle = useUIStore((s) => s.toggleSidebar)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const router = useRouter()

  const onLogout = async () => {
    await logout()
    router.replace("/login")
  }

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r border-border/60 bg-sidebar w-64 transition-[width] duration-200",
        collapsed && "w-20",
      )}
    >
      <div className="h-16 flex items-center gap-2 px-4 border-b border-border/60">
        <div className="h-9 w-9 rounded-lg bg-primary/10 text-primary grid place-items-center font-semibold">T</div>
        {!collapsed && <span className="font-semibold tracking-wide">TickIT</span>}
      </div>

      <nav className="flex-1 p-2">
        {nav.map((item) => {
          const ActiveIcon = item.icon
          const active = pathname?.startsWith(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn("flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent", active && "bg-accent")}
            >
              <ActiveIcon className="h-4 w-4" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="mt-auto p-3 space-y-2 border-t border-border/60">
        {!collapsed && (
          <div className="text-xs text-muted-foreground">
            <div className="font-medium text-foreground">{user?.email || "user@tickit.io"}</div>
            <div className="capitalize">{user?.role || "agent"}</div>
          </div>
        )}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle sidebar">
            {collapsed ? "»" : "«"}
          </Button>
          <Button variant="outline" className="w-full bg-transparent" onClick={onLogout}>
            <LogOut className="h-4 w-4 mr-2" /> {!collapsed && "Logout"}
          </Button>
        </div>
      </div>
    </aside>
  )
}
