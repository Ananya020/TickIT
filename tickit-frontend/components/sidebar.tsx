"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useUIStore } from "@/store/ui-store"
import { useAuthStore } from "@/store/auth-store"
import {
  LayoutDashboard,
  PlusSquare,
  Ticket,
  LogOut,
  Shield,
  Users,
  User,
} from "lucide-react"

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
      {/* === HEADER === */}
      <div className="h-16 flex items-center gap-2 px-4 border-b border-border/60">
        <div className="h-9 w-9 rounded-lg bg-primary/10 text-primary grid place-items-center font-semibold">
          T
        </div>
        {!collapsed && (
          <span className="font-semibold tracking-wide">
            Tick<span className="text-primary">IT</span>
          </span>
        )}
      </div>

      {/* === MAIN NAVIGATION === */}
      <nav className="flex-1 p-2 overflow-y-auto">
        {nav.map((item) => {
          const ActiveIcon = item.icon
          const active = pathname?.startsWith(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors",
                active && "bg-accent",
              )}
            >
              <ActiveIcon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}

        {/* === ROLE-SPECIFIC LINKS === */}
        {!collapsed && user?.role === "admin" && (
          <Link
            href="/admin"
            className={cn(
              "mt-2 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors",
              pathname?.startsWith("/admin") && "bg-accent",
            )}
          >
            <Shield className="h-4 w-4 shrink-0" />
            <span>Admin</span>
          </Link>
        )}
        {!collapsed && user?.role === "agent" && (
          <Link
            href="/agent"
            className={cn(
              "mt-2 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors",
              pathname?.startsWith("/agent") && "bg-accent",
            )}
          >
            <Users className="h-4 w-4 shrink-0" />
            <span>Agent</span>
          </Link>
        )}
        {!collapsed && user?.role === "end-user" && (
          <Link
            href="/end-user"
            className={cn(
              "mt-2 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors",
              pathname?.startsWith("/end-user") && "bg-accent",
            )}
          >
            <User className="h-4 w-4 shrink-0" />
            <span>End User</span>
          </Link>
        )}
      </nav>

      {/* === FOOTER / LOGOUT SECTION === */}
      <div className="mt-auto border-t border-border/60">
        <div className="p-3 flex flex-col gap-2">
          {!collapsed && (
            <div className="text-xs text-muted-foreground truncate">
              <div className="font-medium text-foreground">
                {user?.email || "user@tickit.io"}
              </div>
              <div className="capitalize">{user?.role || "agent"}</div>
            </div>
          )}

          <div className="flex items-center justify-between gap-2">
            {/* Sidebar Toggle Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggle}
              aria-label="Toggle sidebar"
              className="shrink-0"
            >
              {collapsed ? "»" : "«"}
            </Button>

            {/* Logout Button */}
            {collapsed ? (
              <Button
                variant="outline"
                size="icon"
                onClick={onLogout}
                aria-label="Logout"
                className="shrink-0"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                variant="outline"
                className="flex-1 bg-transparent truncate"
                onClick={onLogout}
              >
                <LogOut className="h-4 w-4 mr-2 shrink-0" /> Logout
              </Button>
            )}
          </div>
        </div>
      </div>
    </aside>
  )
}

