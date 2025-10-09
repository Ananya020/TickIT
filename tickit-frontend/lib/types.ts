export type User = {
  email: string
  role: "agent" | "admin" | "user" | string
}

export type AuthResponse = {
  access_token: string
  token?: string
  user?: User
}
