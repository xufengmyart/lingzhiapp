export interface User {
  id: string
  username: string
  email: string
  phone: string
  totalLingzhi: number
  currentStage: string
  participationLevel: string
  createdAt: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
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
