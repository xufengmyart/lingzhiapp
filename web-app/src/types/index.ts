export interface User {
  id: number
  username: string
  email: string
  phone: string
  totalLingzhi?: number  // camelCase命名规范（前端使用）
  total_lingzhi?: number  // snake_case命名规范（后端返回）
  avatarUrl?: string  // camelCase命名规范（前端使用）
  avatar_url?: string  // snake_case命名规范（后端返回）
  realName?: string  // camelCase命名规范（前端使用）
  real_name?: string  // snake_case命名规范（后端返回）
  title?: string
  position?: string
  gender?: string
  bio?: string
  location?: string
  website?: string
  referrerId?: number  // 推荐人ID（我推荐的）
  referrer_id?: number  // 推荐人ID（我推荐的）
  refereeId?: number  // 推荐人ID（推荐我的）
  referee_id?: number  // 推荐人ID（推荐我的）
  refereeUsername?: string  // 推荐人用户名
  referee_username?: string  // 推荐人用户名
  referralCode?: string  // camelCase命名规范（前端使用）
  referral_code?: string  // snake_case命名规范（后端返回）
  createdAt?: string  // camelCase命名规范（前端使用）
  created_at?: string  // snake_case命名规范（后端返回）
  updatedAt?: string  // camelCase命名规范（前端使用）
  updated_at?: string  // snake_case命名规范（后端返回）
  loginType?: string
  login_type?: string
  isVerified?: number
  is_verified?: number
  // 以下字段用于前端逻辑
  currentStage?: string
  participationLevel?: string
  isCompleted?: boolean
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isError?: boolean  // 标记是否为错误消息
  thinking?: string  // 深度思考过程
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

// 智能体相关类型
export interface Agent {
  id: number
  name: string
  description: string
  avatar?: string
  status: 'active' | 'inactive'
  model?: string
  systemPrompt?: string
  createdAt?: string
}

export interface ChatResponse {
  reply: string
  response: string
  conversationId: string
  agentId: number
  message: string
  thinking?: string | null
}

// 签到相关类型
export interface CheckinStatus {
  checkedIn: boolean
  todayLingzhi: number
  consecutiveDays: number
  totalLingzhi: number
  rewards: CheckinReward[]
  tomorrow?: {
    reward: number
    baseReward: number
    bonus: number
    consecutiveDays: number
    tip: string
    description: string
  }
  checkinTip?: string
  milestoneTip?: string
}

export interface CheckinReward {
  day: number
  lingzhi: number
}

export interface CheckinResult {
  todayLingzhi: number
  consecutiveDays: number
  totalLingzhi: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}
