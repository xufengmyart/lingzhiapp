import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { User, ApiResponse, IncomeLevel, JourneyStage, PartnerInfo, ChatResponse } from '../types'
import { mockApi } from './mockApi'
import { requestCache, generateCacheKey, clearAuthCache } from './cache'

// 生产环境使用真实API，开发环境根据需要切换
const USE_MOCK_API = false

// API地址配置：优先使用环境变量，否则使用相对路径（配合Nginx反向代理）
// Nginx会将 /api/ 请求转发到 http://127.0.0.1:8080/api/
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 重试配置
const MAX_RETRY = 2
const RETRY_DELAY = 2000

// 睡眠函数
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 增加超时时间到60秒
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
    // 记录请求日志
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      data: config.data,
      params: config.params
    })
    return config
  },
  (error) => {
    console.error('[API] 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 全局标志：是否正在进行静默验证
let isSilentVerification = false

// 设置静默验证标志（供AuthContext使用）
export const setSilentVerification = (value: boolean) => {
  isSilentVerification = value
}

// 响应拦截器 - 增强认证错误处理
api.interceptors.response.use(
  (response) => {
    console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - 成功`, {
      status: response.status,
      data: response.data
    })
    return response
  },
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { __retryCount?: number; __isRetry?: boolean }

    // 401认证错误处理 - 智能处理策略
    if (error.response?.status === 401) {
      console.warn(`[API] 401认证错误: ${config.url}`)

      // 只在登录请求失败时清除认证信息
      const isLoginRequest = config.url?.includes('/auth/login') || config.url?.includes('/register')

      if (isLoginRequest) {
        // 登录请求失败，不需要清除认证信息（本身就没有）
        return Promise.reject(error)
      }

      // 如果正在静默验证，不触发登出
      if (isSilentVerification) {
        console.log('[API] 静默验证遇到401错误，不触发登出')
        return Promise.reject(error)
      }

      // 其他请求401，可能是token过期
      // 只在非登录页面时清除并跳转
      const currentPath = window.location.pathname
      const isLoginPage = currentPath === '/' || currentPath === '/login-full' || currentPath.includes('/register')

      if (!isLoginPage) {
        console.log('[API] 认证失败，清除认证信息')
        clearAuthCache()
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('tokenCacheTime')
        // 延迟跳转，避免过于频繁的跳转
        setTimeout(() => {
          if (window.location.pathname !== '/') {
            console.log('[API] 跳转到登录页面')
            window.location.href = '/'
          }
        }, 100)
      }

      return Promise.reject(error)
    }

    // 其他错误处理
    if (!config || !error.response) {
      console.error('网络错误:', error.message)
      return Promise.reject(error)
    }

    if (error.response.status === 404) return Promise.reject(error)

    // 403禁止访问错误
    if (error.response.status === 403) {
      console.error('无权限访问，请联系管理员')
      return Promise.reject(error)
    }

    // 500服务器错误
    if (error.response.status === 500) {
      console.error('服务器错误:', error.message)
      return Promise.reject(error)
    }

    // 只对GET请求进行重试（避免重复提交POST/PUT/DELETE）
    if (config.method !== 'get') return Promise.reject(error)

    config.__retryCount = (config.__retryCount || 0) + 1

    if (config.__retryCount >= MAX_RETRY) {
      console.error('请求失败，已达到最大重试次数')
      return Promise.reject(error)
    }

    console.log('请求失败，正在重试...', config.__retryCount)
    // 指数退避
    await sleep(RETRY_DELAY * Math.pow(2, config.__retryCount - 1))

    return api.request(config)
  }
)

// 用户相关API
export const userApi = {
  login: async (username: string, password: string) => {
    if (USE_MOCK_API) return mockApi.login(username, password)

    // 登录前清除旧的认证信息和缓存
    clearAuthCache()
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/auth/login', {
      username,
      password,
    })
    return response.data
  },

  register: async (
    username: string,
    email: string,
    password: string,
    referral_code?: string,
    id_card?: string,
    bank_account?: string,
    bank_name?: string,
    phone?: string
  ) => {
    if (USE_MOCK_API) return mockApi.register({ username, email, phone: (phone || '').trim(), password, referrer: referral_code })

    // 去除所有字符串参数的首尾空格
    const cleanUsername = username?.trim() || ''
    const cleanEmail = email?.trim() || ''
    const cleanPhone = phone?.trim() || ''
    const cleanReferralCode = referral_code?.trim() || ''
    const cleanIdCard = id_card?.trim() || ''
    const cleanBankAccount = bank_account?.trim() || ''
    const cleanBankName = bank_name?.trim() || ''

    const response = await api.post<ApiResponse<{ token: string; user: User }>>('/register', {
      username: cleanUsername,
      email: cleanEmail,
      phone: cleanPhone,
      password,
      referral_code: cleanReferralCode,
      id_card: cleanIdCard,
      bank_account: cleanBankAccount,
      bank_name: cleanBankName
    })
    return response.data
  },

  getUserInfo: async (useCache: boolean = true) => {
    if (USE_MOCK_API) return mockApi.getUserInfo()

    const cacheKey = generateCacheKey('GET', '/user/info')

    // 尝试从缓存获取
    if (useCache) {
      const cached = requestCache.get(cacheKey)
      if (cached) return cached
    }

    const response = await api.get<ApiResponse<{ user: User } | User>>('/user/info')

    // 处理不同的响应格式
    let userData: User
    if ('user' in response.data.data) {
      // 后端返回格式: { success: true, data: { user: {...} } }
      userData = response.data.data.user
    } else {
      // 后端返回格式: { success: true, data: {...} }
      userData = response.data.data as User
    }

    // 缓存结果（统一格式）
    const normalizedResponse: ApiResponse<User> = {
      success: response.data.success,
      data: userData
    }
    requestCache.set(cacheKey, normalizedResponse)

    return normalizedResponse
  },

  updateProfile: async (data: Partial<User>) => {
    if (USE_MOCK_API) return mockApi.updateProfile(data)
    const response = await api.put<ApiResponse<User>>('/user/profile', data)

    // 打印响应数据
    console.log('[updateProfile] 响应:', response.data)

    // 清除用户信息缓存
    requestCache.delete(generateCacheKey('GET', '/user/info'))

    // 后端返回格式: { success: true, message: "...", user: {...} }
    // 转换为前端期望格式: { success: true, data: {...} }
    if (response.data.success && response.data.user) {
      return {
        success: true,
        data: response.data.user
      }
    } else if (response.data.success && response.data.data) {
      // 兼容其他格式
      return response.data
    } else {
      return response.data
    }
  },

  changePassword: async (data: { oldPassword: string; newPassword: string }) => {
    const response = await api.post<ApiResponse>('/user/change-password', data)
    return response.data
  },

  getReferralQrcode: async (download = false) => {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录')
    }
    
    if (download) {
      // 下载模式，直接返回文件
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/qrcode?download=true`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) {
        throw new Error('生成二维码失败')
      }
      const blob = await response.blob()
      return { blob }
    } else {
      // 显示模式，返回base64
      const response = await api.get<ApiResponse<{ qrcode: string; referral_code: string; referral_url: string }>>('/qrcode')
      return response.data
    }
  },

  getReferrer: async () => {
    const response = await api.get<ApiResponse<{ referrer: { id: number; username: string; realName: string } | null; message?: string }>>('/auth/referrer')
    return response.data
  },

  validateReferralCode: async (code: string) => {
    const response = await api.get<ApiResponse<{ referrer_id: number; referrer_username: string; referrer_avatar: string }>>(`/referral/validate?code=${code}`)
    return response.data
  },

  applyReferralCode: async (data: { user_id: number; referral_code: string }) => {
    const response = await api.post<ApiResponse<{ reward_lingzhi: number }>>('/user/referral/apply', data)
    return response.data
  }
}

// 智能体相关API
export const agentApi = {
  sendMessage: async (message: string, conversationId?: string, agentId?: number, enableThinking?: boolean) => {
    if (USE_MOCK_API) return mockApi.sendMessage(message, conversationId)
    const response = await api.post<ApiResponse<ChatResponse>>(
      '/chat',
      { message, conversationId, agentId: agentId || 1, enableThinking: enableThinking || false }
    )
    return response.data
  },

  getConversationHistory: async (conversationId: string) => {
    if (USE_MOCK_API) return mockApi.getConversationHistory(conversationId)
    const response = await api.get<ApiResponse<{ messages: any[] }>>(
      `/agent/conversations/${conversationId}`
    )
    return response.data
  },

  getAgents: async () => {
    const response = await api.get<ApiResponse<any[]>>('/admin/agents')
    return response.data
  },
}

// 经济模型API
export const economyApi = {
  getIncomeProjection: async (level: string) => {
    if (USE_MOCK_API) return mockApi.getIncomeProjection(level)
    const response = await api.get<ApiResponse<IncomeLevel>>(
      `/economy/income-projection?level=${level}`
    )
    return response.data
  },

  calculateLingzhiValue: async (contribution: number, lockPeriod?: string) => {
    if (USE_MOCK_API) return mockApi.calculateLingzhiValue(contribution, lockPeriod)
    const params = new URLSearchParams({ contribution: contribution.toString() })
    if (lockPeriod) {
      params.append('lockPeriod', lockPeriod)
    }
    const response = await api.get<ApiResponse<any>>(`/economy/value?${params}`)
    return response.data
  },

  getExchangeInfo: async () => {
    if (USE_MOCK_API) return mockApi.getExchangeInfo()
    const response = await api.get<ApiResponse<any>>('/economy/exchange-info')
    return response.data
  },
}

// 用户旅程API
export const journeyApi = {
  getJourneyStage: async (userId: string) => {
    if (USE_MOCK_API) return mockApi.getJourneyStage(userId)
    const response = await api.get<ApiResponse<JourneyStage>>(`/journey/stage/${userId}`)
    return response.data
  },

  updateProgress: async (userId: string, data: any) => {
    if (USE_MOCK_API) return mockApi.updateProgress(userId, data)
    const response = await api.put<ApiResponse<any>>(`/journey/progress/${userId}`, data)
    return response.data
  },

  getMilestones: async (userId: string) => {
    if (USE_MOCK_API) return mockApi.getMilestones(userId)
    const response = await api.get<ApiResponse<any>>(`/journey/milestones/${userId}`)
    return response.data
  },
}

// 合伙人API
export const partnerApi = {
  checkQualification: async (userId: string, currentLingzhi: number) => {
    const response = await api.post<ApiResponse<PartnerInfo>>('/partner/check-qualification', {
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
    const response = await api.post<ApiResponse<any>>('/partner/apply', data)
    return response.data
  },

  getApplicationStatus: async (userId: number | string) => {
    const response = await api.get<ApiResponse<any>>(`/partner/status/${userId}`)
    return response.data
  },

  getPrivileges: async (level: string) => {
    if (USE_MOCK_API) return mockApi.getPrivileges(level)
    const response = await api.get<ApiResponse<any>>(`/partner/privileges?level=${level}`)
    return response.data
  },
}

// 中视频项目API
export const videoApi = {
  getProjects: async () => {
    const response = await api.get<ApiResponse<any[]>>('/video/projects')
    return response.data
  },

  createProject: async (data: {
    title: string
    description?: string
    video_url?: string
    cover_image?: string
    lingzhi_cost?: number
  }) => {
    const response = await api.post<ApiResponse<{ id: number }>>('/video/projects', data)
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
    const response = await api.get<ApiResponse<any[]>>('/aesthetic/projects')
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
    const response = await api.post<ApiResponse<{ id: number }>>('/aesthetic/projects', data)
    return response.data
  },
}

// 合伙人项目API
export const partnerProjectApi = {
  getProjects: async () => {
    const response = await api.get<ApiResponse<any[]>>('/partner/projects')
    return response.data
  },

  createProject: async (data: {
    project_name: string
    project_type: string
    investment_amount?: number
    expected_return?: number
    description?: string
  }) => {
    const response = await api.post<ApiResponse<{ id: number }>>('/partner/projects', data)
    return response.data
  },

  getEarnings: async () => {
    const response = await api.get<ApiResponse<any[]>>('/partner/earnings')
    return response.data
  },
}

// 灵值修复API
export const lingzhiFixApi = {
  checkUserLingzhi: async (userId: number) => {
    const response = await api.get<ApiResponse<any>>(`/lingzhi/check/${userId}`)
    return response.data
  },

  fixUserLingzhi: async (userId: number) => {
    const response = await api.post<ApiResponse<any>>(`/lingzhi/fix/user/${userId}`)
    return response.data
  },

  fixAllUsers: async () => {
    const response = await api.post<ApiResponse<any>>('/lingzhi/fix/all')
    return response.data
  },
}

// 签到API
export const checkInApi = {
  checkIn: async () => {
    if (USE_MOCK_API) return mockApi.checkIn()
    const response = await api.post<ApiResponse<{
      rewards: number
      total_lingzhi: number
      todayLingzhi: number
      streak: number
      message: string
    }>>('/checkin')
    return response.data
  },

  getTodayStatus: async (useCache: boolean = true) => {
    if (USE_MOCK_API) return mockApi.getTodayStatus()
    
    const cacheKey = generateCacheKey('GET', '/checkin/status')
    
    // 尝试从缓存获取
    if (useCache) {
      const cached = requestCache.get(cacheKey)
      if (cached) return cached
    }
    
    const response = await api.get<ApiResponse<{
      checkedIn: boolean
      today: boolean
      lingzhi: number
      todayLingzhi: number
      streak: number
      canCheckIn: boolean
      rewards: number[]
    }>>('/checkin/status')
    
    // 缓存结果（1分钟）
    requestCache.set(cacheKey, response.data, 60 * 1000)
    
    return response.data
  },

  getHistory: async (days: number = 7) => {
    if (USE_MOCK_API) return mockApi.getHistory(days)
    const response = await api.get<ApiResponse<any[]>>(`/checkin/history?days=${days}`)
    return response.data
  },
}

// 推荐API
export const referralApi = {
  getReferralStats: async () => {
    if (USE_MOCK_API) {
      return {
        success: true,
        data: {
          totalReferrals: 5,
          activeReferrals: 3,
          totalRewards: 100,
        }
      }
    }
    const response = await api.get<ApiResponse<{
      totalReferrals: number
      activeReferrals: number
      totalRewards: number
    }>>('/user/referral-stats')
    return response.data
  },

  getReferralList: async () => {
    if (USE_MOCK_API) {
      return {
        success: true,
        data: [
          { id: 1, username: '用户A', createdAt: '2024-01-01', status: 'active' },
          { id: 2, username: '用户B', createdAt: '2024-01-02', status: 'inactive' },
        ]
      }
    }
    const response = await api.get<ApiResponse<any[]>>('/user/referrals')
    return response.data
  },

  validateReferralCode: async (code: string) => {
    if (USE_MOCK_API) {
      return {
        success: true,
        data: {
          valid: true,
          referrerId: 1,
          referrerUsername: '推荐人',
        }
      }
    }
    const response = await api.post<ApiResponse<{
      valid: boolean
      referrerId?: number
      referrerUsername?: string
    }>>('/user/referral/validate', { code })
    return response.data
  },

  applyReferralCode: async (code: string) => {
    if (USE_MOCK_API) {
      return {
        success: true,
        data: {
          applied: true,
          reward: 10,
        }
      }
    }
    const response = await api.post<ApiResponse<{
      applied: boolean
      reward?: number
      message?: string
    }>>('/user/referral/apply', { code })
    return response.data
  },
}

export default api
