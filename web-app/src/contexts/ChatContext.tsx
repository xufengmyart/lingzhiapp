import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { Message } from '../types'
import { agentApi } from '../services/api'
import { memoryApi, Conversation } from '../services/memoryApi'

interface ChatContextType {
  messages: Message[]
  loading: boolean
  conversationId: string | null
  currentConversation: Conversation | null
  sendMessage: (content: string, agentId?: number, enableThinking?: boolean) => Promise<void>
  clearChat: () => void
  setConversationId: (id: string | null) => void
  loadConversationHistory: (conversationId: number) => Promise<void>
  saveConversation: () => Promise<void>
  enableMemory: boolean
  setEnableMemory: (enable: boolean) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const ChatProvider: React.FC<{ children: ReactNode; userId?: number }> = ({ children, userId = 1 }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [enableMemory, setEnableMemory] = useState(false)

  // 加载对话历史
  const loadConversationHistory = async (convId: number) => {
    try {
      setLoading(true)
      const response = await memoryApi.getConversation(convId)
      if (response.success && response.data.messages) {
        const loadedMessages: Message[] = response.data.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at)
        }))
        setMessages(loadedMessages)
        setConversationId(convId.toString())
        setCurrentConversation(response.data)
      }
    } catch (error: any) {
      console.error('加载对话历史失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 保存对话
  const saveConversation = async () => {
    if (!userId || messages.length === 0) return

    try {
      let convId: number

      // 如果没有对话ID，创建新对话
      if (!currentConversation) {
        const response = await memoryApi.createConversation(userId, 1, messages[0].content.substring(0, 50))
        if (response.success) {
          convId = response.data.conversationId
          setConversationId(convId.toString())
        } else {
          return
        }
      } else {
        convId = currentConversation.id
      }

      // 保存所有消息
      for (const msg of messages) {
        await memoryApi.addMessage(convId, msg.role, msg.content, {
          timestamp: msg.timestamp?.toISOString()
        })
      }

      console.log('对话已保存')
    } catch (error) {
      console.error('保存对话失败:', error)
    }
  }

  const sendMessage = async (content: string, agentId: number = 2, enableThinking: boolean = false) => {
    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      console.log('[ChatContext] 发送消息:', { content, conversationId, agentId, enableMemory, enableThinking })

      // 如果启用了记忆系统，传递上下文
      let context = null
      if (enableMemory && userId) {
        try {
          const contextResponse = await memoryApi.getContext(userId)
          if (contextResponse.success) {
            context = contextResponse.data
          }
        } catch (error) {
          console.error('获取上下文失败:', error)
        }
      }

      const res = await agentApi.sendMessage(
        content,
        conversationId || undefined,
        agentId,
        enableThinking
      )
      console.log('[ChatContext] 收到响应:', res)

      // 设置会话ID
      if (!conversationId && res.data?.conversationId) {
        setConversationId(res.data.conversationId)
      }

      // 添加助手消息
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.data?.response || res.data?.reply || '抱歉，未收到回复',
        timestamp: new Date(),
        thinking: (res.data as any)?.thinking  // 深度思考过程（类型断言）
      }
      setMessages((prev) => [...prev, assistantMessage])

      // 如果启用了记忆系统，自动保存对话
      if (enableMemory) {
        await saveConversation()
      }

    } catch (error: any) {
      console.error('[ChatContext] 发送消息失败:', error)

      // 根据错误类型提供不同的反馈
      let errorContent = '抱歉，我遇到了一些问题，请稍后再试。'

      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorContent = '⏱️ 连接超时，请检查网络连接后重试。'
      } else if (error.code === 'ERR_NETWORK' || !error.response) {
        errorContent = '🌐 网络连接失败，无法连接到服务器。\n\n可能原因：\n• 网络断开\n• 服务器维护中\n• 防火墙阻止\n\n请检查网络或稍后再试。'
      } else if (error.response?.status === 401) {
        errorContent = '🔐 请先登录后再使用对话功能。\n\n请刷新页面重新登录。'
      } else if (error.response?.status === 403) {
        errorContent = '🚫 无权限访问此功能。\n\n请联系管理员获取权限。'
      } else if (error.response?.status === 404) {
        errorContent = '🔍 接口不存在，请联系管理员。'
      } else if (error.response?.status === 429) {
        errorContent = '⚡ 请求过于频繁，请稍后再试（建议等待30秒）。'
      } else if (error.response?.status === 500) {
        const errorMsg = error.response?.data?.error || error.response?.data?.message || '服务器内部错误'
        errorContent = `🔧 服务器内部错误：${errorMsg}\n\n我们正在努力修复，请稍后再试。`
      } else if (error.response?.status === 502) {
        errorContent = '🚫 网关错误（502），服务器可能正在重启。\n\n请稍后再试（约30秒）。'
      } else if (error.response?.status === 503) {
        errorContent = '🚫 服务暂时不可用（503），服务器可能正在维护中。\n\n请稍后再试，或联系管理员了解详情。'
      } else if (error.response?.status === 504) {
        errorContent = '⏳ 服务器响应超时（504），请稍后再试。'
      } else if (error.message) {
        errorContent = `发生错误: ${error.message}`
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorContent,
        timestamp: new Date(),
        isError: true,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setConversationId(null)
    setCurrentConversation(null)
  }

  return (
    <ChatContext.Provider
      value={{
        messages,
        loading,
        conversationId,
        currentConversation,
        sendMessage,
        clearChat,
        setConversationId,
        loadConversationHistory,
        saveConversation,
        enableMemory,
        setEnableMemory
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export const useChat = () => {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}
