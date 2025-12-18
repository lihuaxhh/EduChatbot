import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/apiClient'
import router from '../app/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!token.value)
  const role = computed(() => {
      if (token.value && token.value.includes('.')) {
          try {
            const parts = token.value.split('.')
            if (parts.length > 1) {
                const base64Url = parts[1]
                if (!base64Url) return null
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
                const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
                }).join(''))
                return JSON.parse(jsonPayload).role
            }
          } catch(e) { return null }
      }
      return null
  })

  async function login(payload: any) {
    const params = new URLSearchParams()
    params.append('username', payload.username)
    params.append('password', payload.password)
    
    const r = await api.post('/api/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    token.value = r.data.access_token
    localStorage.setItem('token', token.value)
    await fetchMe()
  }

  async function register(payload: any) {
    const r = await api.post('/api/auth/register', payload)
    return r.data
  }

  async function updateProfile(payload: any) {
    const r = await api.put('/api/auth/profile', payload)
    user.value = r.data
    return r.data
  }

  async function fetchMe() {
    if (!token.value) return
    try {
        const r = await api.get('/api/auth/me')
        user.value = r.data
    } catch (e) {
        logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, user, isAuthenticated, role, login, register, fetchMe, logout, updateProfile }
})
