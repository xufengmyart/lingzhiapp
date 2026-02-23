import { useState, useEffect, useRef } from 'react'
import api from '../services/api'

interface ConversationBilling {
  conversationId: string | null
  startTime: number | null
  duration: number  // 对话时长（秒）
  cost: number  // 消耗灵值
  isActive: boolean
}

interface ConversationBillingReturn {
  conversationBilling: ConversationBilling
  startConversation: (conversationId: string) => void
  endConversation: (feedbackScore?: number) => Promise<{
    success: boolean
    duration: number
    durationMinutes: number
    cost: number
    feedbackLingzhiReward: number
    totalLingzhiChange: number
    currentBalance: number
    message: string
  } | null>
  getBillingInfo: (conversationId: string) => Promise<any>
  isEnding: boolean
}

export const useConversationBilling = (): ConversationBillingReturn => {
  const [conversationBilling, setConversationBilling] = useState<ConversationBilling>({
    conversationId: null,
    startTime: null,
    duration: 0,
    cost: 0,
    isActive: false
  })
  const [isEnding, setIsEnding] = useState(false)
  const timerRef = useRef<number | null>(null)
  const unblockRef = useRef<(() => void) | null>(null)

  // 更新对话时长
  useEffect(() => {
    if (conversationBilling.isActive && conversationBilling.startTime) {
      timerRef.current = window.setInterval(() => {
        const now = Date.now()
        const elapsed = Math.floor((now - conversationBilling.startTime!) / 1000)
        setConversationBilling(prev => ({
          ...prev,
          duration: elapsed,
          cost: calculateCost(elapsed)
        }))
      }, 1000)
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [conversationBilling.isActive, conversationBilling.startTime])

  // 计算消耗（5分钟/灵值，不足5分钟按5分钟计算）
  const calculateCost = (seconds: number): number => {
    const minutes = seconds / 60
    const costUnits = Math.max(1, Math.ceil(minutes / 5))
    return costUnits
  }

  // 开始对话
  const startConversation = (conversationId: string) => {
    setConversationBilling({
      conversationId,
      startTime: Date.now(),
      duration: 0,
      cost: 1,  // 至少消耗1灵值
      isActive: true
    })

    // 阻止页面直接关闭
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = '您正在进行对话，确定要离开吗？对话将自动结束并计算消耗。'
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    unblockRef.current = () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }

  // 结束对话
  const endConversation = async (feedbackScore?: number) => {
    if (!conversationBilling.conversationId || !conversationBilling.isActive || isEnding) {
      return null
    }

    setIsEnding(true)

    try {
      // 调用后端API
      const response = await api.post(`/api/conversation/${conversationBilling.conversationId}/end`, {
        duration: conversationBilling.duration,
        feedback_score: feedbackScore
      })

      if (response.data.success) {
        // 清理计时器
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }

        // 清理事件监听器
        if (unblockRef.current) {
          unblockRef.current()
          unblockRef.current = null
        }

        // 重置状态
        setConversationBilling({
          conversationId: null,
          startTime: null,
          duration: 0,
          cost: 0,
          isActive: false
        })

        return response.data
      }
    } catch (error) {
      console.error('结束对话失败:', error)
    } finally {
      setIsEnding(false)
    }

    return null
  }

  // 获取计费信息
  const getBillingInfo = async (conversationId: string) => {
    try {
      const response = await api.get(`/api/conversation/${conversationId}/billing-info`)
      return response.data
    } catch (error) {
      console.error('获取计费信息失败:', error)
      return null
    }
  }

  return {
    conversationBilling,
    startConversation,
    endConversation,
    getBillingInfo,
    isEnding
  }
}

// 对话结束提示组件
interface ConversationEndDialogProps {
  isOpen: boolean
  onClose: () => void
  duration: number
  cost: number
  onConfirm: (feedbackScore?: number) => void
  onSkip: () => void
}

export const ConversationEndDialog: React.FC<ConversationEndDialogProps> = ({
  isOpen,
  onClose,
  duration,
  cost,
  onConfirm,
  onSkip
}) => {
  const [selectedScore, setSelectedScore] = useState<number | null>(null)

  if (!isOpen) return null

  const durationMinutes = (duration / 60).toFixed(1)

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-white/20 rounded-2xl shadow-2xl max-w-md w-full p-6">
        {/* 标题 */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">对话结束</h3>
          <p className="text-gray-400 text-sm">感谢您的使用，本次对话信息如下</p>
        </div>

        {/* 消耗信息 */}
        <div className="bg-white/5 rounded-xl p-4 mb-6 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">对话时长</span>
            <span className="text-white font-semibold">{durationMinutes} 分钟</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400">消耗灵值</span>
            <span className="text-cyan-400 font-bold text-lg">{cost} 灵值</span>
          </div>
          <div className="text-xs text-gray-500 text-center mt-2">
            计费规则：5分钟/灵值，不足5分钟按5分钟计算
          </div>
        </div>

        {/* 反馈评分 */}
        <div className="mb-6">
          <p className="text-gray-400 text-sm mb-3 text-center">
            请为本次对话评分（可获得灵值奖励）
          </p>
          <div className="flex justify-center space-x-2">
            {[1, 2, 3, 4, 5].map((score) => (
              <button
                key={score}
                onClick={() => setSelectedScore(score)}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                  selectedScore === score
                    ? 'bg-gradient-to-br from-yellow-400 to-orange-500 scale-110'
                    : 'bg-white/10 hover:bg-white/20'
                }`}
              >
                <span className={`text-xl font-bold ${selectedScore === score ? 'text-white' : 'text-gray-400'}`}>
                  {score}
                </span>
              </button>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2 px-4">
            <span>不满意</span>
            <span>非常满意</span>
          </div>
        </div>

        {/* 按钮 */}
        <div className="flex space-x-3">
          <button
            onClick={onSkip}
            className="flex-1 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all font-medium"
          >
            跳过反馈
          </button>
          <button
            onClick={() => onConfirm(selectedScore || undefined)}
            className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white rounded-xl transition-all font-medium"
          >
            提交反馈
          </button>
        </div>

        {/* 提示 */}
        <div className="mt-4 text-center text-xs text-gray-500">
          满意及以上可获得 2 灵值奖励，一般可获得 1 灵值奖励
        </div>
      </div>
    </div>
  )
}

import { Sparkles } from 'lucide-react'
