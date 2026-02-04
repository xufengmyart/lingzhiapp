import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

interface Notification {
  id: string
  type: NotificationType
  message: string
  duration?: number
}

interface NotificationContextType {
  notifications: Notification[]
  showNotification: (type: NotificationType, message: string, duration?: number) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const showNotification = useCallback(
    (type: NotificationType, message: string, duration = 3000) => {
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
      setNotifications((prev) => [...prev, { id, type, message, duration }])

      if (duration > 0) {
        setTimeout(() => {
          removeNotification(id)
        }, duration)
      }
    },
    []
  )

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const clearNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  return (
    <NotificationContext.Provider
      value={{ notifications, showNotification, removeNotification, clearNotifications }}
    >
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  )
}

const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotification()

  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info,
  }

  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  }

  return (
    <div className="fixed top-4 right-4 z-[100] space-y-2 max-w-md w-full pointer-events-none">
      {notifications.map((notification) => {
        const Icon = icons[notification.type]

        return (
          <div
            key={notification.id}
            className={`${colors[notification.type]} text-white rounded-lg shadow-lg pointer-events-auto transform transition-all duration-300 ease-in-out flex items-center justify-between`}
            style={{
              animation: 'slideIn 0.3s ease-out',
            }}
          >
            <div className="flex items-center p-4 flex-1">
              <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className="text-sm font-medium">{notification.message}</span>
            </div>
            <button
              onClick={() => removeNotification(notification.id)}
              className="p-3 hover:bg-white/20 transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )
      })}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

export const useNotification = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider')
  }

  // 便捷方法
  return {
    ...context,
    success: (message: string, duration?: number) => context.showNotification('success', message, duration),
    error: (message: string, duration?: number) => context.showNotification('error', message, duration),
    warning: (message: string, duration?: number) => context.showNotification('warning', message, duration),
    info: (message: string, duration?: number) => context.showNotification('info', message, duration),
  }
}
