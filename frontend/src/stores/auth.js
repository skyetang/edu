import { defineStore } from 'pinia'
import axios from 'axios'

// Configure axios defaults
// Assuming the backend is proxy-ed via vite to /api, or we need to set base URL
// Since dev server is running on port 8000 for backend, and frontend is on 5173
// We should check vite.config.js, but for now let's assume relative path /api works if proxy is set
// or use absolute path. Let's try relative /api first.
const api = axios.create({
  baseURL: '/api'
})

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    async sendCode(phone, scene) {
      try {
        const response = await api.post('/auth/send_code', { phone, scene })
        return response.data
      } catch (err) {
        throw err.response?.data || err
      }
    },

    async loginWithCode(phone, code) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/login/code', { phone, code })
        if (response.data.success) {
          this.setAuth(response.data.data)
          return true
        } else {
          throw new Error(response.data.message)
        }
      } catch (err) {
        this.error = err.response?.data?.message || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async loginWithPassword(phone, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/login/password', { phone, password })
        if (response.data.success) {
          this.setAuth(response.data.data)
          return true
        } else {
          throw new Error(response.data.message)
        }
      } catch (err) {
        this.error = err.response?.data?.message || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async register(phone, code, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/register', { phone, code, password })
        if (response.data.success) {
          this.setAuth(response.data.data)
          return true
        } else {
          throw new Error(response.data.message)
        }
      } catch (err) {
        this.error = err.response?.data?.message || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    setAuth(data) {
      this.token = data.token
      this.user = data.user
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      // Set default header for future requests
      // api.defaults.headers.common['Authorization'] = `Bearer ${data.token}` 
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
