const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export interface User {
  id: string
  nickname: string
}

export async function register(nickname: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nickname, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "회원가입 실패")
  return data
}

export async function login(nickname: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nickname, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "로그인 실패")
  return data
}

export async function refreshAccessToken(): Promise<string> {
  const refresh = localStorage.getItem("naion_refresh_token")
  if (!refresh) throw new Error("No refresh token")
  const res = await fetch(`${API_BASE}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error("Refresh failed")
  localStorage.setItem("naion_access_token", data.access_token)
  return data.access_token
}

export function storeAuth(data: { access_token: string; refresh_token: string; user: User }) {
  localStorage.setItem("naion_access_token", data.access_token)
  localStorage.setItem("naion_refresh_token", data.refresh_token)
  localStorage.setItem("naion_user", JSON.stringify(data.user))
}

export function getStoredUser(): User | null {
  const u = localStorage.getItem("naion_user")
  return u ? JSON.parse(u) : null
}

export function clearAuth() {
  localStorage.removeItem("naion_access_token")
  localStorage.removeItem("naion_refresh_token")
  localStorage.removeItem("naion_user")
}

export function getAccessToken(): string | null {
  return localStorage.getItem("naion_access_token")
}
