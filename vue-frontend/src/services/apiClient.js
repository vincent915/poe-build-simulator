import axios from 'axios'

// FastAPI 基礎 URL
const FASTAPI_BASE_URL = import.meta.env.VITE_FASTAPI_URL || 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: FASTAPI_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API 請求:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ 請求錯誤:', error)
    return Promise.reject(error)
  }
)

// 回應攔截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API 回應:', response.config.url)
    return response.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message
    console.error('❌ 回應錯誤:', message)
    return Promise.reject(error)
  }
)

export default apiClient
