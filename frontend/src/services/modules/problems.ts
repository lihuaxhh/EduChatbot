import { api } from '../apiClient'

export interface Question {
  id: number
  question: string
  normalized_question: string
  answer: string
  difficulty_tag: string
  knowledge_tag: string
  created_at: string
}

export interface QuestionListResult {
    total: number
    items: Question[]
}

export async function listQuestions(skip = 0, limit = 20, difficulty?: string, knowledge?: string) {
  const r = await api.get('/api/problems/', { params: { skip, limit, difficulty, knowledge } })
  return r.data as QuestionListResult
}

export async function uploadQuestions(file: File) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/api/problems/upload', form)
}
