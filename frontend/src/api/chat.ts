const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export async function* streamChat(
  message: string,
  sessionId: string,
  userId: string,
  onReasonCount: (count: number) => void,
  context?: string
) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, user_id: userId, context }),
  })

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split("\n").filter(l => l.startsWith("data: "))

    for (const line of lines) {
      const data = JSON.parse(line.slice(6))
      if (data.type === "text") yield data.content
      if (data.type === "done") onReasonCount(data.reason_count)
    }
  }
}

export async function seedTestSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/dev/seed/${sessionId}`, { method: "POST" })
  return res.json()
}

export async function* streamSummary(sessionId: string, userId: string) {
  const response = await fetch(`${API_BASE}/api/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, user_id: userId }),
  })

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split("\n").filter(l => l.startsWith("data: "))

    for (const line of lines) {
      const data = JSON.parse(line.slice(6))
      if (data.type === "text") yield data.content
    }
  }
}
