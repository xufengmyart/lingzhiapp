import React from 'react'
import { Inbox, AlertCircle, FileText, Search } from 'lucide-react'

export interface EmptyProps {
  type?: 'default' | 'error' | 'no-data' | 'no-result'
  title?: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export const Empty: React.FC<EmptyProps> = ({
  type = 'default',
  title,
  description,
  action,
  className = '',
}) => {
  const icons = {
    default: Inbox,
    error: AlertCircle,
    'no-data': FileText,
    'no-result': Search,
  }

  const Icon = icons[type]

  const defaultTexts = {
    default: { title: '暂无数据', description: '当前没有任何内容' },
    error: { title: '出错了', description: '加载失败，请稍后重试' },
    'no-data': { title: '无数据', description: '没有找到相关记录' },
    'no-result': { title: '未找到结果', description: '请尝试其他搜索关键词' },
  }

  const text = title ? { title, description } : defaultTexts[type]

  const iconColors = {
    default: 'text-gray-400',
    error: 'text-red-400',
    'no-data': 'text-gray-400',
    'no-result': 'text-blue-400',
  }

  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      <Icon className={`w-16 h-16 mb-4 ${iconColors[type]}`} />
      <h3 className="text-lg font-medium text-gray-900 mb-2">{text.title}</h3>
      <p className="text-gray-500 text-center mb-6 max-w-md">{text.description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
