import { useState, useRef, useCallback } from 'react'
import api from '../services/api'

interface BillingInfo {
  startTime: number | null
  duration: number // 秒
  consumedLingzhi: number // 消耗的灵值
  earnedLingzhi: number // 获得的灵值（通过反馈）
  hasSubmittedFeedback: boolean
}

const LINGZHI_PER_5_MINUTES = 1 // 每5分钟消耗1灵值
const FIVE_MINUTES_IN_SECONDS = 5 * 60

/**
 * 计算消耗的灵值
 * 规则：5分钟消耗1灵值，不足5分钟按5分钟计算
 */
export const calculateConsumedLingzhi = (durationSeconds: number): number => {
  if (durationSeconds <= 0) return 0
  return Math.ceil(durationSeconds / FIVE_MINUTES_IN_SECONDS)
}

export const useChatBilling = () => {
  const [billingInfo, setBillingInfo] = useState<BillingInfo>({
    startTime: null,
    duration: 0,
    consumedLingzhi: 0,
    earnedLingzhi: 0,
    hasSubmittedFeedback: false
  })
  const intervalRef = useRef<number | null>(null)

  // 开始对话计费
  const startBilling = useCallback(() => {
    const now = Date.now()
    setBillingInfo({
      startTime: now,
      duration: 0,
      consumedLingzhi: 0,
      earnedLingzhi: 0,
      hasSubmittedFeedback: false
    })

    // 每秒更新计费信息
    intervalRef.current = window.setInterval(() => {
      setBillingInfo(prev => {
        if (!prev.startTime) return prev
        const now = Date.now()
        const duration = Math.floor((now - prev.startTime) / 1000)
        return {
          ...prev,
          duration,
          consumedLingzhi: calculateConsumedLingzhi(duration)
        }
      })
    }, 1000)

    console.log('[计费] 开始计费，时间:', new Date(now).toLocaleString())
  }, [])

  // 停止对话计费
  const stopBilling = useCallback((): BillingInfo => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    const finalBillingInfo = {
      ...billingInfo,
      startTime: billingInfo.startTime ? Date.now() : null
    }

    console.log('[计费] 停止计费，最终信息:', finalBillingInfo)
    return finalBillingInfo
  }, [billingInfo])

  // 重置计费信息
  const resetBilling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setBillingInfo({
      startTime: null,
      duration: 0,
      consumedLingzhi: 0,
      earnedLingzhi: 0,
      hasSubmittedFeedback: false
    })
    console.log('[计费] 重置计费信息')
  }, [])

  // 添加反馈奖励
  const addFeedbackReward = useCallback((reward: number) => {
    setBillingInfo(prev => ({
      ...prev,
      earnedLingzhi: prev.earnedLingzhi + reward,
      hasSubmittedFeedback: true
    }))
    console.log('[计费] 添加反馈奖励:', reward)
  }, [])

  // 格式化时长显示
  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    if (minutes > 0) {
      return `${minutes}分${remainingSeconds}秒`
    }
    return `${remainingSeconds}秒`
  }

  return {
    billingInfo,
    startBilling,
    stopBilling,
    resetBilling,
    addFeedbackReward,
    formatDuration,
    isBilling: billingInfo.startTime !== null
  }
}
