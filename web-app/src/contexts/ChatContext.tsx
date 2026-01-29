import React, { createContext, useContext, useState, ReactNode } from 'react'
import type { Message } from '../types'
import { agentApi } from '../services/api'

interface ChatContextType {
  messages: Message[]
  loading: boolean
  conversationId: string | null
  sendMessage: (content: string) => Promise<void>
  clearChat: () => void
  setConversationId: (id: string) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)

  const sendMessage = async (content: string) => {
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
      const res = await agentApi.sendMessage(content, conversationId || undefined)

      // 设置会话ID
      if (!conversationId) {
        setConversationId(res.data.conversationId)
      }

      // 添加助手消息
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.data.reply,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('发送消息失败:', error)

      // 根据错误类型提供不同的反馈
      let errorContent = '抱歉，我遇到了一些问题，请稍后再试。'

      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorContent = '连接超时，请检查网络连接后重试。'
      } else if (error.response?.status === 401) {
        errorContent = '请先登录后再使用对话功能。'
      } else if (error.response?.status === 429) {
        errorContent = '请求过于频繁，请稍后再试。'
      } else if (error.message) {
        errorContent = `发生错误: ${error.message}`
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorContent,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setConversationId(null)
  }

  return (
    <ChatContext.Provider
      value={{ messages, loading, conversationId, sendMessage, clearChat, setConversationId }}
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
