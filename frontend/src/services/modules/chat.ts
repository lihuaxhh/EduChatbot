import { api } from '../apiClient'

export async function listSessions(userId: number) {
  const r = await api.get(`/api/sessions`, { params: { user_id: userId } })
  return r.data as Array<{ session_id: string; title: string; is_pinned: boolean; created_at: string; updated_at: string }>
}

export async function streamChat(payload: { message: string; session_id?: string; user_id?: number }, onChunk: (t: string) => void) {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  const reader = resp.body!.getReader()
  const decoder = new TextDecoder('utf-8')
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    onChunk(decoder.decode(value, { stream: true }))
  }
}

export async function getHistory(sessionId: string) {
  const r = await api.get(`/api/sessions/${sessionId}/history`)
  return r.data as Array<{ role: 'user'|'assistant'; content: string }>
}

export async function createSession(userId: number) {
  const r = await api.post(`/api/sessions`, null, { params: { user_id: userId } })
  return r.data as { session_id: string }
}
