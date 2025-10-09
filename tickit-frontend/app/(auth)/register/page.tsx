"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { motion } from "framer-motion"
import { useToast } from "@/components/ui/use-toast"
import { ShieldCheck, Loader2 } from "lucide-react"
import { api } from "@/lib/api"

export default function RegisterPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post("/auth/register", { email, password })
      toast({ title: "Account created", description: "You can now sign in." })
      router.replace("/login")
    } catch (err: any) {
      toast({
        title: "Registration failed",
        description: err?.message || "Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-dvh flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-md"
      >
        <Card className="backdrop-blur supports-[backdrop-filter]:bg-card/90 border-border/40 shadow-xl rounded-2xl">
          <CardHeader className="space-y-2 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <CardTitle className="text-2xl">Create your account</CardTitle>
            <CardDescription className="text-sm text-muted-foreground">Join TickIT — AI-Powered IT Help Desk</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create account"}
              </Button>
              <Button type="button" variant="ghost" className="w-full" onClick={() => router.push("/login")}>
                Already have an account? Sign in
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}


