import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { User, ApiResponse, IncomeLevel, JourneyStage, PartnerInfo } from '../types'
import { mockApi } from './mockApi'
import { requestCache, generateCacheKey, clearAuthCache } from './cache'

// 生产环境使用真实API，开发环境根据需要切换
const USE_MOCK_API = false

// API地址配置：使用相对路径，配合Nginx反向代理
// Nginx会将 /api/ 请求转发到 http://127.0.0.1:8001/api/
const API_BASE_URL = '/api'

// 重试配置
const MAX_RETRY = 3
const RETRY_DELAY = 1000

// 睡眠函数
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 添加重试机制
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { __retryCount?: number }

    // 不重试的情况
    if (!config || !error.response) return Promise.reject(error)
    if (error.response.status === 401) {
      // 清除缓存并跳转登录
      clearAuthCache()
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(error)
    }
    if (error.response.status === 404) return Promise.reject(error)
    if (config.method !== 'get') return Promise.reject(error) // 只重试GET请求

    config.__retryCount = config.__retryCount || 0

    if (config.__retryCount >= MAX_RETRY) {
      return Promise.reject(error)
    }

    config.__retryCount += 1

    // 指数退避
    await sleep(RETRY_DELAY * Math.pow(2, config.__retryCount - 1))

    return api.request(config)
  }
)

// 用户相关API
export const userApi = {
  login: async (username: string, password: string) => {
    if (USE_MOCK_API) return mockApi.login(username, password)
    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/api/login', {
      username,
      password,
    })
    return response.data
  },

  register: async (data: { username: string; email: string; phone: string; password: string }) => {
    if (USE_MOCK_API) return mockApi.register(data)
    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/api/register', data)
    return response.data
  },

  getUserInfo: async (useCache: boolean = true) => {
    if (USE_MOCK_API) return mockApi.getUserInfo()
    
    const cacheKey = generateCacheKey('GET', '/api/user/info')
    
    // 尝试从缓存获取
    if (useCache) {
      const cached = requestCache.get(cacheKey)
      if (cached) return cached
    }
    
    const response = await api.get<ApiResponse<User>>('/api/user/info')
    
    // 缓存结果
    requestCache.set(cacheKey, response.data)
    
    return response.data
  },

  updateProfile: async (data: Partial<User>) => {
    if (USE_MOCK_API) return mockApi.updateProfile(data)
    const response = await api.put<ApiResponse<User>>('/api/user/profile', data)
    
    // 清除用户信息缓存
    requestCache.delete(generateCacheKey('GET', '/api/user/info'))
    
    return response.data
  }
}

// 智能体相关API
export const agentApi = {
  sendMessage: async (message: string, conversationId?: string, agentId?: number) => {
    if (USE_MOCK_API) return mockApi.sendMessage(message, conversationId)
    const response = await api.post<ApiResponse<{ reply: string; conversationId: string; agentId: number }>>(
      '/api/agent/chat',
      { message, conversationId, agentId: agentId || 1 }
    )
    return response.data
  },

  getConversationHistory: async (conversationId: string) => {
    if (USE_MOCK_API) return mockApi.getConversationHistory(conversationId)
    const response = await api.get<ApiResponse<{ messages: any[] }>>(
      `/api/agent/conversations/${conversationId}`
    )
    return response.data
  },

  getAgents: async () => {
    const response = await api.get<ApiResponse<any[]>>('/api/admin/agents')
    return response.data
  },
}

// 经济模型API
export const economyApi = {
  getIncomeProjection: async (level: string) => {
    if (USE_MOCK_API) return mockApi.getIncomeProjection(level)
    const response = await api.get<ApiResponse<IncomeLevel>>(
      `/api/economy/income-projection?level=${level}`
    )
    return response.data
  },

  calculateLingzhiValue: async (contribution: number, lockPeriod?: string) => {
    if (USE_MOCK_API) return mockApi.calculateLingzhiValue(contribution, lockPeriod)
    const params = new URLSearchParams({ contribution: contribution.toString() })
    if (lockPeriod) {
      params.append('lockPeriod', lockPeriod)
    }
    const response = await api.get<ApiResponse<any>>(`/api/economy/value?${params}`)
    return response.data
  },

  getExchangeInfo: async () => {
    if (USE_MOCK_API) return mockApi.getExchangeInfo()
    const response = await api.get<ApiResponse<any>>('/api/economy/exchange-info')
    return response.data
  },
}

// 用户旅程API
export const journeyApi = {
  getJourneyStage: async (userId: string) => {
    if (USE_MOCK_API) return mockApi.getJourneyStage(userId)
    const response = await api.get<ApiResponse<JourneyStage>>(`/api/journey/stage/${userId}`)
    return response.data
  },

  updateProgress: async (userId: string, data: any) => {
    if (USE_MOCK_API) return mockApi.updateProgress(userId, data)
    const response = await api.put<ApiResponse<any>>(`/api/journey/progress/${userId}`, data)
    return response.data
  },

  getMilestones: async (userId: string) => {
    if (USE_MOCK_API) return mockApi.getMilestones(userId)
    const response = await api.get<ApiResponse<any>>(`/api/journey/milestones/${userId}`)
    return response.data
  },
}

// 合伙人API
export const partnerApi = {
  checkQualification: async (userId: string, currentLingzhi: number) => {
    const response = await api.post<ApiResponse<PartnerInfo>>('/api/partner/check-qualification', {
      userId,
      currentLingzhi,
    })
    return response.data
  },

  submitApplication: async (data: {
    userId: number | string
    userName: string
    phone: string
    currentLingzhi: number
    reason: string
  }) => {
    const response = await api.post<ApiResponse<any>>('/api/partner/apply', data)
    return response.data
  },

  getApplicationStatus: async (userId: number | string) => {
    const response = await api.get<ApiResponse<any>>(`/api/partner/status/${userId}`)
    return response.data
  },

  getPrivileges: async (level: string) => {
    if (USE_MOCK_API) return mockApi.getPrivileges(level)
    const response = await api.get<ApiResponse<any>>(`/api/partner/privileges?level=${level}`)
    return response.data
  },
}

// 中视频项目API
export const videoApi = {
  getProjects: async () => {
    const response = await api.get<ApiResponse<any[]>>('/api/video/projects')
    return response.data
  },

  createProject: async (data: {
    title: string
    description?: string
    video_url?: string
    cover_image?: string
    lingzhi_cost?: number
  }) => {
    const response = await api.post<ApiResponse<{ id: number }>>('/api/video/projects', data)
    return response.data
  },

  updateProject: async (id: number, data: {
    title?: string
    description?: string
    video_url?: string
    cover_image?: string
    lingzhi_cost?: number
    status?: string
  }) => {
    const response = await api.put<ApiResponse<any>>(`/api/video/projects/${id}`, data)
    return response.data
  },
}

// 西安美学侦探API
export const aestheticApi = {
  getProjects: async () => {
    const response = await api.get<ApiResponse<any[]>>('/api/aesthetic/projects')
    return response.data
  },

  createProject: async (data: {
    project_name: string
    location?: string
    theme?: string
    discovery_data?: string
    images?: string
    lingzhi_cost?: number
  }) => {
    const response = await api.post<ApiResponse<{ id: number }>>('/api/aesthetic/projects', data)
    return response.data
  },
}

// 合伙人项目API
export const partnerProjectApi = {
  getProjects: async () => {
    const response = await api.get<ApiResponse<any[]>>('/api/partner/projects')
    return response.data
  },

  createProject: async (data: {
    project_name: string
    project_type: string
    investment_amount?: number
    expected_return?: number
    description?: string
  }) => {
    const response = await api.post<ApiResponse<{ id: number }>>('/api/partner/projects', data)
    return response.data
  },

  getEarnings: async () => {
    const response = await api.get<ApiResponse<any[]>>('/api/partner/earnings')
    return response.data
  },
}

// 签到API
export const checkInApi = {
  checkIn: async () => {
    if (USE_MOCK_API) return mockApi.checkIn()
    const response = await api.post<ApiResponse<{ lingzhi: number }>>('/api/checkin')
    return response.data
  },

  getTodayStatus: async () => {
    if (USE_MOCK_API) return mockApi.getTodayStatus()
    
    const cacheKey = generateCacheKey('GET', '/api/checkin/status')
    
    // 尝试从缓存获取
    const cached = requestCache.get(cacheKey)
    if (cached) return cached
    
    const response = await api.get<ApiResponse<{ checkedIn: boolean; lingzhi: number }>>('/api/checkin/status')
    
    // 缓存结果（1分钟）
    requestCache.set(cacheKey, response.data, 60 * 1000)
    
    return response.data
  },

  getHistory: async (days: number = 7) => {
    if (USE_MOCK_API) return mockApi.getHistory(days)
    const response = await api.get<ApiResponse<any[]>>(`/api/checkin/history?days=${days}`)
    return response.data
  },
}

export default api
