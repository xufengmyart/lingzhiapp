import React from 'react'
import { ChevronRight } from 'lucide-react'

export interface CardProps {
  children: React.ReactNode
  title?: string
  subtitle?: string
  className?: string
  onClick?: () => void
  hoverable?: boolean
  footer?: React.ReactNode
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  className = '',
  onClick,
  hoverable = false,
  footer,
}) => {
  const cardClass = `
    bg-white rounded-lg shadow-md
    ${hoverable ? 'hover:shadow-lg cursor-pointer transition-shadow' : ''}
    ${onClick ? 'cursor-pointer' : ''}
    ${className}
  `

  return (
    <div className={cardClass} onClick={onClick}>
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b">
          {title && (
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              {hoverable && <ChevronRight className="w-5 h-5 text-gray-400" />}
            </div>
          )}
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className="p-6">{children}</div>
      {footer && (
        <div className="px-6 py-4 bg-gray-50 border-t rounded-b-lg">{footer}</div>
      )}
    </div>
  )
}

export const CardHeader: React.FC<{
  children: React.ReactNode
  className?: string
}> = ({ children, className = '' }) => {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>
}

export const CardTitle: React.FC<{
  children: React.ReactNode
  className?: string
}> = ({ children, className = '' }) => {
  return <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>{children}</h3>
}

export const CardDescription: React.FC<{
  children: React.ReactNode
  className?: string
}> = ({ children, className = '' }) => {
  return <p className={`text-sm text-gray-500 mt-1 ${className}`}>{children}</p>
}

export const CardContent: React.FC<{
  children: React.ReactNode
  className?: string
}> = ({ children, className = '' }) => {
  return <div className={`p-6 ${className}`}>{children}</div>
}
