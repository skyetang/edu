import axios from 'axios'
import { createDiscreteApi } from 'naive-ui'
import { themeOverrides } from '@/theme'

// 独立使用 message API（非组件内），并注入全局主题配置
const { message: globalMessage } = createDiscreteApi(
  ['message'],
  {
    configProviderProps: {
      themeOverrides
    }
  }
)

// 配置 axios 默认值
const service = axios.create({
  baseURL: '/api'
})

service.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 是否正在刷新 token
let isRefreshing = false
// 重试队列，每一项是一个函数
let requests = []

// 处理业务错误
function handleBusinessError(code, msg, config) {
  if (config?.silent) return false
  
  switch (code) {
    case 'SERVER_ERROR':
      globalMessage.error(msg || '服务器内部错误')
      return true
    case 'RATE_LIMITED':
      globalMessage.warning(msg || '请求太频繁，请稍后再试')
      return true
    case 'UNKNOWN_ERROR':
      globalMessage.error(msg || '发生未知错误')
      return true
    // 对于校验错误，默认不全局提示，交由组件处理。如果需要全局提示，可以在 catch 中处理
    // case 'VALIDATION_ERROR': 
    //   break
    default:
      // 可选：对于其他未定义错误，是否兜底提示？
      // globalMessage.error(msg)
      break
  }
  return false
}

// 处理 HTTP 错误
function handleHttpError(status, msg, config) {
  if (config?.silent) return false

  switch (status) {
    case 429:
      globalMessage.warning('请求过于频繁，请稍后重试')
      return true
    case 500:
    case 502:
    case 503:
    case 504:
      globalMessage.error('服务器服务异常，请稍后再试')
      return true
    case 404:
       // 接口 404 通常不提示，或者提示资源不存在
       // globalMessage.error('请求的资源不存在')
       break
    case 403:
       // 403 仅代表权限不足
       globalMessage.error(msg || '没有权限执行此操作')
       return true
    default:
      if (msg === 'Network Error') {
          globalMessage.error('网络连接异常，请检查网络')
          return true
      }
      break
  }
  return false
}

service.interceptors.response.use(
  (res) => {
    const body = res.data
    const config = res.config
    
    // 如果响应体直接是数组或对象且没有 success 字段（非标准封装），直接返回
    if (body && body.success === undefined) return body
    // 标准封装
    if (body && body.success) {
      // 如果有 meta 信息（如分页），连同 data 一起返回
      if (body.meta) {
        return {
          data: body.data,
          meta: body.meta
        }
      }
      return body.data
    }
    
    const code = body?.code || 'UNKNOWN_ERROR'
    const message = body?.message || '请求失败'
    
    const isHandled = handleBusinessError(code, message, config)
    
    return Promise.reject({ code, message, body, isGloballyHandled: isHandled })
  },
  async (error) => {
    const originalRequest = error.config || {}; // 兼容 error.config 可能为空
    const status = error.response?.status
    // 优先使用后端返回的错误消息
    const backendMessage = error.response?.data?.message
    const message = backendMessage || error.message || '网络错误'
    
    // 覆写 error.message，让组件 catch 时能直接获取到业务错误信息
    error.message = message
    // 将业务错误码挂载到 error 对象上
    if (error.response?.data?.code) {
      error.code = error.response.data.code
    }

    // 优先处理 429, 5xx 等通用错误
    const isHandled = handleHttpError(status, message, originalRequest)
    if (isHandled) {
        error.isGloballyHandled = true
    }

    // 如果是 401 错误，且未重试过，且不是刷新请求本身
    if (status === 401 && !originalRequest.url.includes('/auth/token/refresh')) {
      // 如果已经在刷新中，则将请求挂起，放入队列
      if (isRefreshing) {
        return new Promise((resolve) => {
          requests.push((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`
            resolve(service(originalRequest))
          })
        })
      }

      // 标记是否已重试，防止死循环 (虽然有 isRefreshing 保护，但为了保险保留)
      if (originalRequest._retry) {
        return Promise.reject(error)
      }
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        // 避免在 request.js 中直接导入 store，以防循环引用
        // 直接操作 localStorage 或使用 Pinia 的非组件内调用方式
        // 但这里最简单的是直接操作 localStorage 获取 refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            throw new Error("No refresh token");
        }

        // 使用干净的 axios 实例进行刷新，避免拦截器循环
        const response = await axios.post('/api/auth/token/refresh', { refresh_token: refreshToken });
        
        if (response.data.success) {
            const { token, refresh } = response.data.data;
            
            // 更新本地存储
            localStorage.setItem('token', token);
            if (refresh) localStorage.setItem('refreshToken', refresh);
            
            // 如果能获取到 store 实例更好，但为了避免循环引用，这里只更新 localStorage
            // Pinia store 会在下次初始化或刷新页面时读取新的 storage
            // 如果需要实时更新 store，可以尝试动态导入但需小心
            // 这里我们尝试动态导入 store 来更新状态，但要注意 authStore 必须在应用挂载后才能使用
             const { useAuthStore } = await import('@/stores/auth');
             // 检查 Pinia 是否已激活
             try {
                const authStore = useAuthStore();
                authStore.setAuthTokens(token, refresh);
             } catch (e) {
                console.warn('Pinia not active, only localStorage updated');
             }
            
            // 更新请求头并重试原始请求
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            
            // 执行队列中的请求
            requests.forEach(cb => cb(token))
            requests = []
            
            return service(originalRequest);
        }
      } catch (refreshError) {
        // 清除登录状态
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        
        // 刷新失败，拒绝队列中的请求
        requests = [] // 也可以遍历 reject，但页面通常会跳转
        
        window.location.href = '/'; 
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default service
