import type { User, Message, IncomeLevel, JourneyStage, ChatResponse } from '../types'

// 模拟用户数据
let mockUser: User = {
  id: 1,
  username: '灵值体验者',
  email: 'demo@lingzhi.com',
  phone: '13800138000',
  totalLingzhi: 2850,
  currentStage: '探索者',
  participationLevel: '积极参与者',
  createdAt: '2024-01-15T00:00:00Z',
}

// 模拟签到状态
let mockCheckInState = {
  checkedIn: false,
  lingzhi: 0,
  lastCheckInDate: null as string | null,
}

// 模拟收入层级
const mockIncomeLevels: Record<string, IncomeLevel> = {
  beginner: {
    level: '新手',
    dailyContribution: 10,
    dailyIncome: 1,
    monthlyIncome: 30,
    yearlyIncome: 365,
  },
  active: {
    level: '积极参与者',
    dailyContribution: 50,
    dailyIncome: 5,
    monthlyIncome: 150,
    yearlyIncome: 1825,
  },
  expert: {
    level: '专家',
    dailyContribution: 200,
    dailyIncome: 20,
    monthlyIncome: 600,
    yearlyIncome: 7300,
  },
  master: {
    level: '大师',
    dailyContribution: 500,
    dailyIncome: 50,
    monthlyIncome: 1500,
    yearlyIncome: 18250,
  },
}

// 模拟用户旅程阶段
const mockJourneyStages: JourneyStage[] = [
  {
    stage: '注册与认知',
    stageCode: 'STAGE_1',
    description: '完成注册，了解灵值生态园的基本概念和规则',
    nextActions: ['完成用户注册', '阅读用户指南', '完成首次签到'],
    expectedLingzhi: 10,
  },
  {
    stage: '初步参与',
    stageCode: 'STAGE_2',
    description: '开始参与社区活动，贡献价值，积累灵值',
    nextActions: ['参与智能对话', '完成每日任务', '贡献有价值的内容'],
    expectedLingzhi: 100,
  },
  {
    stage: '积极参与',
    stageCode: 'STAGE_3',
    description: '持续参与，建立影响力，成为社区活跃分子',
    nextActions: ['建立个人品牌', '参与社区治理', '邀请新用户'],
    expectedLingzhi: 500,
  },
  {
    stage: '价值创造',
    stageCode: 'STAGE_4',
    description: '创造独特价值，获得社区认可，解锁更多权益',
    nextActions: ['创造独特内容', '建立专业领域影响力', '参与价值验证'],
    expectedLingzhi: 1000,
  },
  {
    stage: '影响力扩展',
    stageCode: 'STAGE_5',
    description: '扩大影响力，引领社区方向，成为意见领袖',
    nextActions: ['引领话题讨论', '组织社区活动', '培养新领袖'],
    expectedLingzhi: 5000,
  },
  {
    stage: '生态共建',
    stageCode: 'STAGE_6',
    description: '参与生态建设，共创价值，获得高级权益',
    nextActions: ['参与生态治理', '提出生态改进建议', '共建生态基础设施'],
    expectedLingzhi: 10000,
  },
  {
    stage: '合伙人',
    stageCode: 'STAGE_7',
    description: '成为生态合伙人，共享生态收益，参与战略决策',
    nextActions: ['申请成为合伙人', '参与生态分红', '参与战略决策'],
    expectedLingzhi: 10000,
  },
]

// 模拟对话消息
const mockMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: '您好！欢迎来到灵值生态园。我是您的智能助手，可以帮助您了解灵值生态、经济模型、用户旅程等内容。请问有什么我可以帮您的吗？',
    timestamp: new Date(),
  },
]

// 模拟API响应延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Mock API服务
export const mockApi = {
  // 用户相关
  async login(_username: string, _password: string) {
    await delay(500)
    return {
      success: true,
      data: {
        token: 'mock-token-' + Date.now(),
        user: mockUser,
      },
    }
  },

  async register(data: any) {
    await delay(800)
    return {
      success: true,
      data: {
        token: 'mock-token-' + Date.now(),
        user: { ...mockUser, username: data.username },
      },
    }
  },

  async getUserInfo() {
    await delay(300)
    return {
      success: true,
      data: mockUser,
    }
  },

  async updateProfile(data: Partial<User>) {
    await delay(500)
    return {
      success: true,
      data: { ...mockUser, ...data },
    }
  },

  // 智能对话
  async sendMessage(message: string, _conversationId?: string) {
    await delay(1000)

    const responses = [
      `您说的是"${message}"，这是一个很好的问题！在灵值生态园中，我们通过贡献价值来获得灵值，灵值可以兑换为实际收益。`,
      `关于"${message}"，灵值生态园采用创新的激励机制，每个用户的贡献都会被量化为灵值。`,
      `灵值生态园的核心在于共建共享，"${message}"正是我们关注的重点。`,
      `在灵值生态园，您可以参与多种活动来获得灵值，"${message}"就是其中之一。`,
    ]

    const reply = responses[Math.floor(Math.random() * responses.length)]

    return {
      success: true,
      data: {
        reply,
        response: reply,
        conversationId: _conversationId || 'conv-' + Date.now(),
        agentId: 1,
        message: message
      } as ChatResponse,
    }
  },

  async getConversationHistory(_conversationId: string) {
    await delay(300)
    return {
      success: true,
      data: {
        messages: mockMessages,
      },
    }
  },

  // 经济模型
  async getIncomeProjection(level: string = 'active') {
    await delay(400)
    return {
      success: true,
      data: mockIncomeLevels[level] || mockIncomeLevels.active,
    }
  },

  async calculateLingzhiValue(contribution: number, lockPeriod?: string) {
    await delay(300)
    const baseValue = contribution * 0.1
    const bonus = lockPeriod ? baseValue * 0.5 : 0
    return {
      success: true,
      data: {
        baseValue,
        bonus,
        totalValue: baseValue + bonus,
        lockPeriod,
        exchangeRate: 0.1,
      },
    }
  },

  async getExchangeInfo() {
    await delay(200)
    return {
      success: true,
      data: {
        currentPrice: 0.1,
        dailyChange: 2.5,
        totalSupply: 1000000,
        marketCap: 100000,
      },
    }
  },

  // 用户旅程
  async getJourneyStage(_userId: string) {
    await delay(300)
    // 根据灵值数确定阶段
    const userLingzhi = mockUser.total_lingzhi
    let stageIndex = 0
    if (userLingzhi >= 10000) stageIndex = 6
    else if (userLingzhi >= 5000) stageIndex = 5
    else if (userLingzhi >= 1000) stageIndex = 4
    else if (userLingzhi >= 500) stageIndex = 3
    else if (userLingzhi >= 100) stageIndex = 2
    else if (userLingzhi >= 10) stageIndex = 1
    
    return {
      success: true,
      data: mockJourneyStages[stageIndex],
    }
  },

  async updateProgress(_userId: string, _data: any) {
    await delay(400)
    return {
      success: true,
      data: {
        userId: _userId,
        progress: _data?.progress || 0,
        message: '进度已更新',
      },
    }
  },

  async getMilestones(_userId: string) {
    await delay(300)
    return {
      success: true,
      data: mockJourneyStages.map((stage, index) => ({
        ...stage,
        completed: index < 2, // 假设前两个阶段已完成
      })),
    }
  },

  // 合伙人
  async checkQualification(userId: string, currentLingzhi: number) {
    await delay(400)
    const isQualified = currentLingzhi >= 10000
    return {
      success: true,
      data: {
        userId,
        currentLingzhi,
        isQualified,
        requiredLingzhi: 10000,
        partnerLevel: isQualified ? '初级合伙人' : null,
        applicationStatus: null,
      },
    }
  },

  async submitApplication(_data: any) {
    await delay(1000)
    return {
      success: true,
      data: {
        applicationId: 'app-' + Date.now(),
        status: 'pending',
        message: '申请已提交，审核中',
      },
    }
  },

  async getApplicationStatus(userId: string) {
    await delay(300)
    return {
      success: true,
      data: {
        userId,
        status: 'pending',
        submitTime: '2024-01-20T00:00:00Z',
      },
    }
  },

  async getPrivileges(level: string) {
    await delay(300)
    const privileges = {
      '初级合伙人': ['月度分红 1%', '优先参与新功能', '专属徽章'],
      '中级合伙人': ['月度分红 2%', '优先参与新功能', '专属徽章', '生态投票权'],
      '高级合伙人': ['月度分红 3%', '优先参与新功能', '专属徽章', '生态投票权', '战略咨询'],
    }
    return {
      success: true,
      data: {
        level,
        privileges: privileges[level as keyof typeof privileges] || [],
      },
    }
  },

  // 签到
  async checkIn() {
    await delay(500)

    // 获取今天的日期字符串
    const today = new Date().toISOString().split('T')[0]

    // 检查今天是否已经签到
    if (mockCheckInState.lastCheckInDate === today) {
      return {
        success: false,
        message: '今天已经签到过了',
        data: {
          lingzhi: 0,
        },
      }
    }

    // 更新签到状态
    mockCheckInState.checkedIn = true
    mockCheckInState.lingzhi = 10
    mockCheckInState.lastCheckInDate = today

    // 更新用户总灵值
    mockUser.total_lingzhi += 10

    return {
      success: true,
      data: {
        rewards: 10,  // 本次获得的灵值
        total_lingzhi: mockUser.total_lingzhi,  // 总灵值
        todayLingzhi: 10,  // 今日获得的灵值
        streak: 1,  // 连续签到天数
        message: '签到成功！获得10灵值',
      },
    }
  },

  async getTodayStatus() {
    await delay(200)

    // 获取今天的日期字符串
    const today = new Date().toISOString().split('T')[0]

    // 检查是否是今天的签到
    const isToday = mockCheckInState.lastCheckInDate === today

    return {
      success: true,
      data: {
        checkedIn: isToday,
        today: isToday,
        lingzhi: mockUser.total_lingzhi,  // 总灵值
        todayLingzhi: isToday ? mockCheckInState.lingzhi : 0,  // 今日获得的灵值
        streak: isToday ? 1 : 0,  // 连续签到天数
        canCheckIn: !isToday,
        rewards: [1, 2, 3, 5, 8, 13, 21, 34],
      },
    }
  },

  async getHistory(days: number = 7) {
    await delay(300)
    const history = Array.from({ length: days }, (_, i) => ({
      date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      lingzhi: i === 0 ? 0 : 10,
      checkedIn: i !== 0,
    }))
    return {
      success: true,
      data: history,
    }
  },
}

export default mockApi
