// 修复User类型
export interface User {
  id: number
  username: string
  email?: string
  phone?: string
  balance?: number
  total_lingzhi?: number
  totalLingzhi?: number  // 兼容驼峰式命名（后端返回）
  contribution_value?: number
  avatar?: string | null
  avatar_url?: string | null  // 兼容后端返回
  realName?: string | null  // 兼容后端返回
  real_name?: string | null  // 兼容后端返回
  status: string
  created_at: string
  updated_at?: string
  is_verified?: boolean
  login_type?: string
  title?: string
  position?: string
  gender?: number
  bio?: string
  location?: string
  website?: string
  referral_code?: string
  referee_id?: number
  referee_username?: string
  participationLevel?: number
  currentStage?: any
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}
