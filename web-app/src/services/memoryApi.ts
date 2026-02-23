import api from './api'

export interface Memory {
  id: number
  user_id: number
  conversation_id: number | null
  type: string
  content: string
  embedding: string | null
  importance: number
  created_at: string
  accessed_at: string
  access_count: number
}

export interface Conversation {
  id: number
  user_id: number
  agent_id: number
  title: string
  created_at: string
  updated_at: string
  message_count: number
  first_message?: string
  messages?: Message[]
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: string
  created_at: string
}

export interface ConversationContext {
  recentConversations: Conversation[]
  importantMemories: Memory[]
}

/**
 * 记忆服务 API
 */
export const memoryApi = {
  /**
   * 获取用户的对话列表
   */
  getConversations: async (userId: number, page: number = 1, limit: number = 20) => {
    const response = await api.get(`/memory/conversations?user_id=${userId}&page=${page}&limit=${limit}`)
    return response.data
  },

  /**
   * 获取对话详情
   */
  getConversation: async (conversationId: number) => {
    const response = await api.get(`/memory/conversations/${conversationId}`)
    return response.data
  },

  /**
   * 创建新对话
   */
  createConversation: async (userId: number, agentId: number = 1, title?: string) => {
    const response = await api.post('/memory/conversations', {
      user_id: userId,
      'agent_id': agentId,
      title: title || '新对话'
    })
    return response.data
  },

  /**
   * 更新对话标题
   */
  updateConversation: async (conversationId: number, title: string) => {
    const response = await api.put(`/memory/conversations/${conversationId}`, { title })
    return response.data
  },

  /**
   * 删除对话
   */
  deleteConversation: async (conversationId: number) => {
    const response = await api.delete(`/memory/conversations/${conversationId}`)
    return response.data
  },

  /**
   * 添加消息到对话
   */
  addMessage: async (conversationId: number, role: string, content: string, metadata?: any) => {
    const response = await api.post(`/memory/conversations/${conversationId}/messages`, {
      role,
      content,
      metadata
    })
    return response.data
  },

  /**
   * 获取用户记忆
   */
  getMemories: async (userId: number, type?: string, limit: number = 50) => {
    const url = `/memory/memories?user_id=${userId}&limit=${limit}`
    const fullUrl = type ? `${url}&type=${type}` : url
    const response = await api.get(fullUrl)
    return response.data
  },

  /**
   * 创建记忆
   */
  createMemory: async (userId: number, content: string, type: string = 'general', importance: number = 1, conversationId?: number) => {
    const response = await api.post('/memory/memories', {
      user_id: userId,
      conversation_id: conversationId,
      type,
      content,
      importance
    })
    return response.data
  },

  /**
   * 删除记忆
   */
  deleteMemory: async (memoryId: number) => {
    const response = await api.delete(`/memory/memories/${memoryId}`)
    return response.data
  },

  /**
   * 搜索记忆
   */
  searchMemories: async (userId: number, query: string, limit: number = 10) => {
    const response = await api.post('/memory/memories/search', {
      user_id: userId,
      query,
      limit
    })
    return response.data
  },

  /**
   * 获取用户对话上下文摘要
   */
  getContext: async (userId: number) => {
    const response = await api.get(`/memory/context/${userId}`)
    return response.data
  },

  /**
   * 获取消息列表（独立端点，支持灵活查询）
   */
  getMessages: async (params: { conversation_id?: number; user_id?: number; limit?: number; offset?: number; role?: string }) => {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value))
      }
    })
    const response = await api.get(`/memory/messages?${queryParams.toString()}`)
    return response.data
  },

  /**
   * 添加消息（独立端点）
   */
  addMessageStandalone: async (conversationId: number, role: string, content: string, metadata?: any) => {
    const response = await api.post('/memory/messages', {
      conversation_id: conversationId,
      role,
      content,
      metadata
    })
    return response.data
  },

  /**
   * 获取记忆摘要
   */
  getSummary: async (params: { user_id?: number; conversation_id?: number }) => {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value))
      }
    })
    const response = await api.get(`/memory/summary?${queryParams.toString()}`)
    return response.data
  },

  /**
   * 获取用户记忆（简化版本）
   */
  getUserMemories: async (userId: number, limit: number = 20) => {
    const response = await api.get(`/memory/user-memories?user_id=${userId}&limit=${limit}`)
    return response.data
  },

  /**
   * 获取记忆启用状态
   */
  getEnableStatus: async (userId: number) => {
    const response = await api.get(`/memory/enable-status?user_id=${userId}`)
    return response.data
  },

  /**
   * 更新记忆启用状态
   */
  updateEnableStatus: async (userId: number, enabled: boolean) => {
    const response = await api.put('/memory/enable-status', {
      user_id: userId,
      enabled
    })
    return response.data
  }
}
