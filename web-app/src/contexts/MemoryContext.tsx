import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { memoryApi, Memory, Conversation, Message, ConversationContext } from '../services/memoryApi'

interface MemoryContextType {
  conversations: Conversation[]
  currentConversation: Conversation | null
  memories: Memory[]
  context: ConversationContext | null
  loading: boolean
  error: string | null

  // 对话操作
  loadConversations: (userId: number) => Promise<void>
  loadConversation: (conversationId: number) => Promise<void>
  createConversation: (userId: number, agentId?: number, title?: string) => Promise<Conversation>
  updateConversation: (conversationId: number, title: string) => Promise<void>
  deleteConversation: (conversationId: number) => Promise<void>
  addMessage: (conversationId: number, role: string, content: string, metadata?: any) => Promise<void>
  setCurrentConversation: (conversation: Conversation | null) => void

  // 记忆操作
  loadMemories: (userId: number, type?: string) => Promise<void>
  createMemory: (userId: number, content: string, type?: string, importance?: number, conversationId?: number) => Promise<void>
  deleteMemory: (memoryId: number) => Promise<void>
  searchMemories: (userId: number, query: string) => Promise<Memory[]>

  // 上下文操作
  loadContext: (userId: number) => Promise<void>
  clearContext: () => void
}

const MemoryContext = createContext<MemoryContextType | undefined>(undefined)

export const MemoryProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [memories, setMemories] = useState<Memory[]>([])
  const [context, setContext] = useState<ConversationContext | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 加载对话列表
  const loadConversations = async (userId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.getConversations(userId)
      if (response.success) {
        setConversations(response.data.conversations)
      }
    } catch (err: any) {
      setError(err.message || '加载对话列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载单个对话
  const loadConversation = async (conversationId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.getConversation(conversationId)
      if (response.success) {
        setCurrentConversation(response.data)
      }
    } catch (err: any) {
      setError(err.message || '加载对话失败')
    } finally {
      setLoading(false)
    }
  }

  // 创建新对话
  const createConversation = async (userId: number, agentId: number = 1, title?: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.createConversation(userId, agentId, title)
      if (response.success) {
        const newConversation: Conversation = {
          id: response.data.conversationId,
          user_id: userId,
          agent_id: agentId,
          title: response.data.title || '新对话',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          message_count: 0
        }
        setConversations(prev => [newConversation, ...prev])
        return newConversation
      }
      throw new Error('创建对话失败')
    } catch (err: any) {
      setError(err.message || '创建对话失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 更新对话
  const updateConversation = async (conversationId: number, title: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.updateConversation(conversationId, title)
      if (response.success) {
        setConversations(prev =>
          prev.map(conv =>
            conv.id === conversationId ? { ...conv, title } : conv
          )
        )
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(prev => prev ? { ...prev, title } : null)
        }
      }
    } catch (err: any) {
      setError(err.message || '更新对话失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除对话
  const deleteConversation = async (conversationId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.deleteConversation(conversationId)
      if (response.success) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId))
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null)
        }
      }
    } catch (err: any) {
      setError(err.message || '删除对话失败')
    } finally {
      setLoading(false)
    }
  }

  // 添加消息
  const addMessage = async (conversationId: number, role: string, content: string, metadata?: any) => {
    try {
      const response = await memoryApi.addMessage(conversationId, role, content, metadata)
      if (response.success) {
        // 更新当前对话
        if (currentConversation?.id === conversationId) {
          const newMessage: Message = {
            id: response.data.messageId,
            conversation_id: conversationId,
            role: role as any,
            content,
            metadata: metadata ? JSON.stringify(metadata) : undefined,
            created_at: new Date().toISOString()
          }
          setCurrentConversation(prev => {
            if (!prev) return prev
            return {
              ...prev,
              message_count: prev.message_count + 1,
              messages: [...(prev.messages || []), newMessage],
              updated_at: new Date().toISOString()
            }
          })
        }
      }
    } catch (err: any) {
      console.error('添加消息失败:', err)
    }
  }

  // 加载记忆
  const loadMemories = async (userId: number, type?: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.getMemories(userId, type)
      if (response.success) {
        setMemories(response.data.memories)
      }
    } catch (err: any) {
      setError(err.message || '加载记忆失败')
    } finally {
      setLoading(false)
    }
  }

  // 创建记忆
  const createMemory = async (userId: number, content: string, type: string = 'general', importance: number = 1, conversationId?: number) => {
    try {
      const response = await memoryApi.createMemory(userId, content, type, importance, conversationId)
      if (response.success) {
        const newMemory: Memory = {
          id: response.data.memoryId,
          user_id: userId,
          conversation_id: conversationId || null,
          type,
          content,
          embedding: null,
          importance,
          created_at: new Date().toISOString(),
          accessed_at: new Date().toISOString(),
          access_count: 0
        }
        setMemories(prev => [newMemory, ...prev])
      }
    } catch (err: any) {
      console.error('创建记忆失败:', err)
    }
  }

  // 删除记忆
  const deleteMemory = async (memoryId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.deleteMemory(memoryId)
      if (response.success) {
        setMemories(prev => prev.filter(mem => mem.id !== memoryId))
      }
    } catch (err: any) {
      setError(err.message || '删除记忆失败')
    } finally {
      setLoading(false)
    }
  }

  // 搜索记忆
  const searchMemories = async (userId: number, query: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.searchMemories(userId, query)
      if (response.success) {
        return response.data.memories
      }
      return []
    } catch (err: any) {
      setError(err.message || '搜索记忆失败')
      return []
    } finally {
      setLoading(false)
    }
  }

  // 加载上下文
  const loadContext = async (userId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await memoryApi.getContext(userId)
      if (response.success) {
        setContext(response.data)
      }
    } catch (err: any) {
      setError(err.message || '加载上下文失败')
    } finally {
      setLoading(false)
    }
  }

  // 清除上下文
  const clearContext = () => {
    setContext(null)
  }

  return (
    <MemoryContext.Provider
      value={{
        conversations,
        currentConversation,
        memories,
        context,
        loading,
        error,
        loadConversations,
        loadConversation,
        createConversation,
        updateConversation,
        deleteConversation,
        addMessage,
        setCurrentConversation,
        loadMemories,
        createMemory,
        deleteMemory,
        searchMemories,
        loadContext,
        clearContext
      }}
    >
      {children}
    </MemoryContext.Provider>
  )
}

export const useMemory = () => {
  const context = useContext(MemoryContext)
  if (context === undefined) {
    throw new Error('useMemory must be used within a MemoryProvider')
  }
  return context
}
