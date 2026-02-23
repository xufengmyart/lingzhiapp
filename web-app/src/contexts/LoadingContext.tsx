import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { Loader2 } from 'lucide-react'

interface LoadingContextType {
  loading: boolean
  loadingText: string
  showLoading: (text?: string) => void
  hideLoading: () => void
  withLoading: <T>(promise: Promise<T>, text?: string) => Promise<T>
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined)

export const LoadingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('加载中...')

  const showLoading = useCallback((text = '加载中...') => {
    setLoadingText(text)
    setLoading(true)
  }, [])

  const hideLoading = useCallback(() => {
    setLoading(false)
  }, [])

  const withLoading = useCallback(
    async <T,>(promise: Promise<T>, text?: string): Promise<T> => {
      if (text) {
        setLoadingText(text)
      }
      setLoading(true)

      try {
        return await promise
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return (
    <LoadingContext.Provider value={{ loading, loadingText, showLoading, hideLoading, withLoading }}>
      {children}
      {loading && <LoadingOverlay />}
    </LoadingContext.Provider>
  )
}

const LoadingOverlay: React.FC = () => {
  const { loadingText } = useLoading()
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[9999]">
      <div className="bg-white rounded-lg p-6 flex items-center shadow-xl">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 mr-3" />
        <span className="text-gray-700 font-medium">{loadingText}</span>
      </div>
    </div>
  )
}

export const useLoading = () => {
  const context = useContext(LoadingContext)
  if (!context) {
    throw new Error('useLoading must be used within LoadingProvider')
  }
  return context
}
