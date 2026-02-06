export interface User {
  id: number  // 修改为 number 类型，与后端一致
  username: string
  email: string
  phone: string
  totalLingzhi: number
  avatar_url?: string
  real_name?: string
  created_at?: string
  updated_at?: string
  login_type?: string
  is_verified?: number
  // 以下字段用于前端逻辑（如果后端不提供，前端可以设置默认值）
  currentStage?: string
  participationLevel?: string
  createdAt?: string  // 兼容旧代码
  is_completed?: boolean
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isError?: boolean  // 标记是否为错误消息
}

export interface IncomeLevel {
  level: string
  dailyContribution: number
  dailyIncome: number
  monthlyIncome: number
  yearlyIncome: number
}

export interface JourneyStage {
  stage: string
  stageCode: string
  description: string
  nextActions: string[]
  expectedLingzhi: number
}

export interface PartnerInfo {
  userId: string
  currentLingzhi: number
  isQualified: boolean
  requiredLingzhi: number
  partnerLevel: string | null
  applicationStatus: string | null
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}
