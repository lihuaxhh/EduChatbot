import { defineStore } from 'pinia'
import { listQuestions, type Question } from '../../services/modules/problems'
import { createAssignment, type AssignmentCreate } from '../../services/modules/assignments'

export const useProblemsStore = defineStore('problems', {
  state: () => ({
    questions: [] as Question[],
    total: 0,
    loading: false,
    selectedQuestions: [] as Question[]
  }),
  actions: {
    async fetchQuestions(skip = 0, limit = 20, difficulty?: string, knowledge?: string) {
      this.loading = true
      try {
        const res = await listQuestions(skip, limit, difficulty, knowledge)
        this.questions = res.items
        this.total = res.total
      } finally {
        this.loading = false
      }
    },
    async createAssignment(payload: AssignmentCreate) {
      this.loading = true
      try {
        await createAssignment(payload)
        return true
      } catch (e) {
        console.error(e)
        return false
      } finally {
        this.loading = false
      }
    }
  }
})
