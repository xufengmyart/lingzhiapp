import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { User } from '../types'
import { userApi } from '../services/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  loginWithToken: (token: string, userData: any) => void
  logout: () => void
  updateUser: (user: User) => void
  checkRequireComplete: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser))
      // 验证token是否有效
      userApi.getUserInfo()
        .then((res) => {
          setUser(res.data)
          localStorage.setItem('user', JSON.stringify(res.data))
        })
        .catch(() => {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setUser(null)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const res = await userApi.login(username, password)
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    setUser(res.data.user)
  }

  const loginWithToken = (token: string, userData: any) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const updateUser = (user: User) => {
    setUser(user)
    localStorage.setItem('user', JSON.stringify(user))
  }

  const checkRequireComplete = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return false

      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
      const response = await fetch(`${apiBase}/api/user/require-complete`, {
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
    <AuthContext.Provider value={{ user, loading, login, loginWithToken, logout, updateUser, checkRequireComplete }}>
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
