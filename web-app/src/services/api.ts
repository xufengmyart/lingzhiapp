import axios from 'axios'
import type { User, ApiResponse, IncomeLevel, JourneyStage, PartnerInfo } from '../types'
import { mockApi } from './mockApi'

// 生产环境使用真实API，开发环境根据需要切换
const USE_MOCK_API = false

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin

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

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
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

  getUserInfo: async () => {
    if (USE_MOCK_API) return mockApi.getUserInfo()
    const response = await api.get<ApiResponse<User>>('/api/user/info')
    return response.data
  },

  updateProfile: async (data: Partial<User>) => {
    if (USE_MOCK_API) return mockApi.updateProfile(data)
    const response = await api.put<ApiResponse<User>>('/api/user/profile', data)
    return response.data
  },
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
    userId: string
    userName: string
    phone: string
    currentLingzhi: number
    reason: string
  }) => {
    const response = await api.post<ApiResponse<any>>('/api/partner/apply', data)
    return response.data
  },

  getApplicationStatus: async (userId: string) => {
    const response = await api.get<ApiResponse<any>>(`/api/partner/status/${userId}`)
    return response.data
  },

  getPrivileges: async (level: string) => {
    if (USE_MOCK_API) return mockApi.getPrivileges(level)
    const response = await api.get<ApiResponse<any>>(`/api/partner/privileges?level=${level}`)
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
    const response = await api.get<ApiResponse<{ checkedIn: boolean; lingzhi: number }>>('/api/checkin/status')
    return response.data
  },

  getHistory: async (days: number = 7) => {
    if (USE_MOCK_API) return mockApi.getHistory(days)
    const response = await api.get<ApiResponse<any[]>>(`/api/checkin/history?days=${days}`)
    return response.data
  },
}

export default api
