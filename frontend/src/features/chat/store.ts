import { defineStore } from 'pinia'
import { listSessions, streamChat, getHistory, createSession } from '../../services/modules/chat'

export const useChatStore = defineStore('chat', {
  state: () => ({
    userId: 1 as number,
    sessions: [] as Array<{ session_id: string; title: string; is_pinned: boolean; created_at: string; updated_at: string }>,
    activeSessionId: '' as string,
    messages: [] as Array<{ role: 'user' | 'assistant'; content: string }>,
    loading: false as boolean
  }),
  actions: {
    async loadSessions() {
      const data = await listSessions(this.userId)
      this.sessions = data
      if (!this.activeSessionId && this.sessions.length > 0) {
        this.activeSessionId = this.sessions[0]!.session_id
        this.messages = await getHistory(this.activeSessionId)
      } else if (this.activeSessionId) {
        this.messages = await getHistory(this.activeSessionId)
      }
    },
    async selectSession(id: string) {
      this.activeSessionId = id
      this.messages = await getHistory(id)
    },
    async newSession() {
      const r = await createSession(this.userId)
      this.activeSessionId = r.session_id
      this.messages = []
      await this.loadSessions()
    },
    async sendMessage(text: string) {
      if (this.loading) return
      this.loading = true
      const before = [...this.sessions]
      this.messages.push({ role: 'user', content: text })
      const idx = this.messages.push({ role: 'assistant', content: '' }) - 1
      await streamChat({ message: text, session_id: this.activeSessionId || undefined, user_id: this.userId }, chunk => {
        const cur = this.messages[idx]
        if (cur) cur.content = (cur.content || '') + chunk
      })
      await this.loadSessions()
      if (!this.activeSessionId && this.sessions.length > 0) {
        const created = this.sessions.find(s => !before.some(b => b.session_id === s.session_id))
        if (created) this.activeSessionId = created.session_id
      }
      this.loading = false
    }
  }
})
