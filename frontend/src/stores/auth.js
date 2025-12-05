import { defineStore } from 'pinia'
import * as authApi from '@/api/auth'
import { uploadFile } from '@/api/common'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    refreshTokenStr: localStorage.getItem('refreshToken') || null,
    loading: false,
    error: null,
    showLoginModal: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    openLoginModal() {
      this.showLoginModal = true
    },
    closeLoginModal() {
      this.showLoginModal = false
    },
    // 错误处理辅助函数
    handleActionError(error) {
      // 记录错误用于调试
      console.error('Auth Action Error:', error)
      
      // 如果已经是标准化错误，直接返回
      if (error instanceof Error && !error.isAxiosError) {
        return error
      }

      // 如果是 request.js 抛出的业务错误对象 (Plain Object)
      if (error && error.code && error.message && !error.response) {
          const newError = new Error(error.message)
          newError.code = error.code
          newError.isGloballyHandled = error.isGloballyHandled
          newError.body = error.body
          return newError
      }

      // 处理 Axios 错误
      if (error.response) {
        // 服务器响应错误状态
        const data = error.response.data
        const message = data?.message || data?.detail || '请求失败'
        const newError = new Error(message)
        newError.code = data?.code
        newError.original = error
        if (error.isGloballyHandled) {
            newError.isGloballyHandled = true
        }
        return newError
      } else if (error.request) {
        // 请求已发出但无响应
        const newError = new Error('网络连接失败，请检查您的网络')
        if (error.isGloballyHandled) {
            newError.isGloballyHandled = true
        }
        return newError
      }
      
      return new Error(error.message || '未知错误')
    },

    async sendCode(phone, scene) {
      try {
        const data = await authApi.sendCode({ phone, scene })
        return data
      } catch (err) {
        throw this.handleActionError(err)
      }
    },

    async loginWithCode(phone, code) {
      this.loading = true
      this.error = null
      try {
        const data = await authApi.loginWithCode({ phone, code })
        this.setAuth(data)
        return true
      } catch (err) {
        const handledError = this.handleActionError(err)
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async loginWithPassword(phone, password) {
      this.loading = true
      this.error = null
      try {
        const data = await authApi.loginWithPassword({ phone, password })
        this.setAuth(data)
        return true
      } catch (err) {
        const handledError = this.handleActionError(err)
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async register(phone, code, password) {
      this.loading = true
      this.error = null
      try {
        const data = await authApi.register({ phone, code, password })
        this.setAuth(data)
        return true
      } catch (err) {
        const handledError = this.handleActionError(err)
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async fetchProfile() {
      try {
        const user = await authApi.getProfile()
        this.user = user
        // Update local storage if needed, but usually user object in LS is static or updated on login.
        // Better to keep store user reactive.
        localStorage.setItem('user', JSON.stringify(user))
        return user
      } catch (err) {
        console.error('Failed to fetch profile', err)
      }
    },

    async updateProfile(data) {
      try {
        const resData = await authApi.updateProfile(data)
        this.user = { ...this.user, ...resData }
        localStorage.setItem('user', JSON.stringify(this.user))
        return true
      } catch (err) {
        throw this.handleActionError(err)
      }
    },

    async changePassword(data) {
       try {
         const resData = await authApi.changePassword(data)
         return resData
       } catch (err) {
         throw this.handleActionError(err)
       }
    },

    async verifyOldPhone(code) {
        try {
            const resData = await authApi.verifyOldPhone({ code })
            return resData
        } catch (err) {
            throw this.handleActionError(err)
        }
    },

    async changeNewPhone(phone, code) {
        try {
            const data = await authApi.changeNewPhone({ phone, code })
             // 使用后端返回的数据更新用户信息，包含已脱敏的手机号
             if (data && data.user) {
                this.user = data.user
             } else {
                this.user.phone = phone
             }
             localStorage.setItem('user', JSON.stringify(this.user))
             return true
        } catch (err) {
            throw this.handleActionError(err)
        }
    },

    async uploadAvatar(file) {
        try {
            const formData = new FormData()
            formData.append('file', file)
            // Use common uploadFile with type='avatar'
            const data = await uploadFile(formData, 'avatar')
            const avatarUrl = data.url
            
            // Update profile with new avatar URL
            await authApi.updateProfile({ avatar: avatarUrl })
            
             this.user.avatar = avatarUrl
             localStorage.setItem('user', JSON.stringify(this.user))
             return avatarUrl
        } catch (err) {
            throw this.handleActionError(err)
        }
    },

    setAuth(data) {
      this.token = data.token
      this.refreshTokenStr = data.refresh
      this.user = data.user
      localStorage.setItem('token', data.token)
      if (data.refresh) localStorage.setItem('refreshToken', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
    },
    
    setAuthTokens(token, refresh) {
      this.token = token
      this.refreshTokenStr = refresh
      localStorage.setItem('token', token)
      if (refresh) localStorage.setItem('refreshToken', refresh)
    },

    logout() {
      this.token = null
      this.refreshTokenStr = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    }
  }
})
