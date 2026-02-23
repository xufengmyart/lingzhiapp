import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { User } from '../types'
import { userApi, setSilentVerification } from '../services/api'

// Token 缓存配置
const TOKEN_CACHE_DURATION = 24 * 60 * 60 * 1000 // 24小时（大幅延长缓存时间，避免刷新退出）
const MAX_RETRY_ATTEMPTS = 3 // 最大重试次数

interface AuthContextType {
  user: User | null
  loading: boolean
  authError: string | null
  login: (username: string, password: string) => Promise<boolean>
  register: (username: string, email: string, password: string, referrer?: string, phone?: string) => Promise<boolean>
  loginWithToken: (token: string, userData: any) => void
  logout: () => void
  updateUser: (user: User) => void
  checkRequireComplete: () => Promise<boolean>
  retryAuth: () => Promise<boolean>
  isRetrying: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [authError, setAuthError] = useState<string | null>(null)
  const [isRetrying, setIsRetrying] = useState(false)
  const [tokenCacheTime, setTokenCacheTime] = useState<number | null>(null)

  // 跳转到登录页的函数
  const redirectToLogin = () => {
    console.log('[AuthContext] 跳转到登录页')
    window.location.href = '/'
  }

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    const savedCacheTime = localStorage.getItem('tokenCacheTime')

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
        if (savedCacheTime) {
          setTokenCacheTime(parseInt(savedCacheTime))
        }
        setLoading(false)

        // 修复：完全禁用页面刷新时的自动token验证
        // 只在以下情况下才验证token：
        // 1. token缓存时间超过24小时（一天）
        // 2. 用户主动调用retryAuth()
        // 这样可以避免页面刷新时因网络问题或后端问题导致的自动登出
        const cacheTime = savedCacheTime ? parseInt(savedCacheTime) : 0
        const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000

        if (Date.now() - cacheTime > oneDayAgo) {
          console.log('[AuthContext] Token缓存超过24小时，静默验证token')
          verifyTokenWithRetry(token, 0)
        } else {
          console.log('[AuthContext] Token缓存有效，跳过验证')
        }
      } catch (e) {
        console.error('解析用户数据失败:', e)
        localStorage.removeItem('user')
        localStorage.removeItem('tokenCacheTime')
        localStorage.removeItem('token')
        setUser(null)
        setLoading(false)
        redirectToLogin()
      }
    } else {
      setLoading(false)
    }
  }, [])

  const verifyTokenWithRetry = async (token: string, retryCount: number) => {
    try {
      // 设置静默验证标志，避免API拦截器触发登出
      setSilentVerification(true)
      const res = await userApi.getUserInfo()
      setUser(res.data)
      localStorage.setItem('user', JSON.stringify(res.data))
      localStorage.setItem('tokenCacheTime', Date.now().toString())
      setTokenCacheTime(Date.now())
      setAuthError(null)
      console.log('[AuthContext] Token 验证成功')
    } catch (err: any) {
      console.error(`[AuthContext] Token 验证失败 (尝试 ${retryCount + 1}/${MAX_RETRY_ATTEMPTS}):`, err)

      // 修复：只有在明确的 401 错误时才清除数据并跳转
      // 网络错误、500错误等情况都保留用户数据，避免因网络波动导致的自动登出
      if (err.response?.status === 401) {
        console.error('[AuthContext] Token 无效或过期，清除认证信息')
        setAuthError('登录已过期，请重新登录')
        // 清除过期的认证信息
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('tokenCacheTime')
        setUser(null)
        setTokenCacheTime(null)
        // 跳转到登录页
        redirectToLogin()
      } else if (retryCount < MAX_RETRY_ATTEMPTS - 1) {
        // 其他错误（网络错误、服务器错误），重试但不清除数据
        console.log('[AuthContext] 网络或服务器错误，准备重试...')
        setIsRetrying(true)
        await new Promise(resolve => setTimeout(resolve, 2000 * (retryCount + 1))) // 指数退避
        setIsRetrying(false)
        await verifyTokenWithRetry(token, retryCount + 1)
      } else {
        // 达到最大重试次数，保持用户数据（不强制登出）
        console.warn('[AuthContext] 达到最大重试次数，保留用户数据')
        setAuthError('网络连接不稳定，部分功能可能受限')
        // 不清除用户数据，让用户可以继续使用
      }
    } finally {
      // 重置静默验证标志
      setSilentVerification(false)
    }
  }

  const retryAuth = async () => {
    const token = localStorage.getItem('token')
    if (!token) return false

    setLoading(true)
    setIsRetrying(true)
    setAuthError(null)

    try {
      // 设置静默验证标志，避免API拦截器触发登出
      setSilentVerification(true)
      const res = await userApi.getUserInfo()
      setUser(res.data)
      localStorage.setItem('user', JSON.stringify(res.data))
      localStorage.setItem('tokenCacheTime', Date.now().toString())
      setTokenCacheTime(Date.now())
      setAuthError(null)
      return true
    } catch (err: any) {
      console.error('重新验证失败:', err)
      // 只有在明确的 401 错误时才清除数据并跳转
      if (err.response?.status === 401) {
        console.error('[AuthContext] Token 无效或过期，清除认证信息')
        setAuthError('登录已过期，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('tokenCacheTime')
        setUser(null)
        setTokenCacheTime(null)
        // 跳转到登录页
        redirectToLogin()
      } else {
        // 网络错误或其他错误，保留数据
        console.warn('[AuthContext] 验证失败但保留用户数据')
        setAuthError('网络连接失败，请稍后重试')
      }
      return false
    } finally {
      setLoading(false)
      setIsRetrying(false)
      // 重置静默验证标志
      setSilentVerification(false)
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const res = await userApi.login(username, password)
      // 登录成功后存储新的token和用户数据
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('tokenCacheTime', Date.now().toString())
      setTokenCacheTime(Date.now())
      setUser(res.data.user)
      setAuthError(null)
      
      // 显示新用户灵值奖励提醒
      if (res.data.is_new_user && res.data.bonus_message) {
        setTimeout(() => {
          alert(res.data.bonus_message)
        }, 500)
      }
      
      return true
    } catch (err: any) {
      console.error('登录失败:', err)
      setAuthError(err.response?.data?.message || '登录失败')
      return false
    }
  }

  const register = async (username: string, email: string, password: string, referrer?: string, phone?: string): Promise<boolean> => {
    const res = await userApi.register(username, email, password, referrer, phone)
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    localStorage.setItem('tokenCacheTime', Date.now().toString())
    setTokenCacheTime(Date.now())
    setUser(res.data.user)
    return true
  }

  const loginWithToken = (token: string, userData: any) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('tokenCacheTime', Date.now().toString())
    setTokenCacheTime(Date.now())
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('tokenCacheTime')
    setUser(null)
    setTokenCacheTime(null)
    setAuthError(null)
  }

  const updateUser = (user: User) => {
    setUser(user)
    localStorage.setItem('user', JSON.stringify(user))
  }

  const checkRequireComplete = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return false

      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/user/require-complete`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      return data.data?.need_complete || false
    } catch (error) {
      return false
    }
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      authError, 
      login, 
      register, 
      loginWithToken, 
      logout, 
      updateUser, 
      checkRequireComplete, 
      retryAuth,
      isRetrying
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
