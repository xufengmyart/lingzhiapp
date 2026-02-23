import { useState, useEffect } from 'react'
import { Sparkles, Gift, Trophy, Star, Calendar, CheckCircle, Zap, Heart } from 'lucide-react'

interface CheckInRitualProps {
  onCheckIn: () => Promise<void>
  currentStreak: number
  todayReward: number
  totalLingzhi: number
}

const CheckInRitual = ({ onCheckIn, currentStreak, todayReward, totalLingzhi }: CheckInRitualProps) => {
  const [isAnimating, setIsAnimating] = useState(false)
  const [showRitual, setShowRitual] = useState(false)
  const [ritualStep, setRitualStep] = useState(0)
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([])
  const [confettiActive, setConfettiActive] = useState(false)

  const ritualSteps = [
    { icon: <Sparkles className="w-16 h-16" />, text: "开启今日能量", color: "from-blue-500 to-cyan-500" },
    { icon: <Zap className="w-16 h-16" />, text: "积累灵值", color: "from-yellow-500 to-orange-500" },
    { icon: <Star className="w-16 h-16" />, text: "点亮成就", color: "from-purple-500 to-pink-500" },
    { icon: <Gift className="w-16 h-16" />, text: "领取奖励", color: "from-green-500 to-emerald-500" },
  ]

  useEffect(() => {
    if (confettiActive) {
      // 生成五彩纸屑
      const newParticles = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        delay: Math.random() * 1000
      }))
      setParticles(newParticles)
    }
  }, [confettiActive])

  const handleCheckIn = async () => {
    setIsAnimating(true)
    setShowRitual(true)
    setRitualStep(0)

    // 播放仪式动画
    for (let i = 0; i < ritualSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800))
      setRitualStep(i + 1)
    }

    // 触发五彩纸屑
    setConfettiActive(true)

    // 执行签到
    await onCheckIn()

    // 延迟关闭仪式
    setTimeout(() => {
      setConfettiActive(false)
      setShowRitual(false)
      setIsAnimating(false)
      setRitualStep(0)
    }, 2000)
  }

  if (showRitual) {
    return (
      <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-[999999]">
        {/* 五彩纸屑效果 */}
        {confettiActive && (
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {particles.map(p => (
              <div
                key={p.id}
                className="absolute w-2 h-2 rounded-full"
                style={{
                  left: `${p.x}%`,
                  top: `${p.y}%`,
                  backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][Math.floor(Math.random() * 5)],
                  animation: `fall 2s ease-out ${p.delay}ms forwards`,
                  transform: `rotate(${Math.random() * 360}deg)`
                }}
              />
            ))}
          </div>
        )}

        {/* 仪式进度 */}
        <div className="relative max-w-md w-full mx-4">
          {/* 进度条 */}
          <div className="mb-8">
            <div className="h-1 bg-[#121A2F] rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#00C3FF] to-[#0080FF] transition-all duration-500"
                style={{ width: `${((ritualStep + 1) / ritualSteps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* 仪式步骤 */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            {ritualSteps.map((step, index) => (
              <div
                key={index}
                className={`p-6 rounded-2xl transition-all duration-500 ${
                  index <= ritualStep
                    ? 'bg-gradient-to-br from-[#00C3FF]/20 to-[#0080FF]/20 border border-[#00C3FF]/30'
                    : 'bg-[#121A2F]/50 border border-[#00C3FF]/10 opacity-50'
                }`}
              >
                <div className={`w-16 h-16 mx-auto mb-3 rounded-2xl flex items-center justify-center bg-gradient-to-r ${step.color} text-white ${
                  index <= ritualStep ? 'scale-110' : 'scale-100'
                } transition-transform duration-300`}>
                  {step.icon}
                </div>
                <div className="text-center text-white text-sm font-medium">{step.text}</div>
              </div>
            ))}
          </div>

          {/* 当前步骤文字 */}
          {ritualStep < ritualSteps.length && (
            <div className="text-center">
              <div className={`text-2xl font-bold text-white mb-2 ${isAnimating ? 'animate-pulse' : ''}`}>
                {ritualSteps[ritualStep].text}
              </div>
              <div className="text-[#B4C7E7]">
                {ritualStep + 1} / {ritualSteps.length}
              </div>
            </div>
          )}

          {/* 成功提示 */}
          {ritualStep >= ritualSteps.length && confettiActive && (
            <div className="text-center animate-bounce">
              <Trophy className="w-20 h-20 mx-auto mb-4 text-[#FFD700]" />
              <div className="text-3xl font-bold text-white mb-2">签到成功!</div>
              <div className="text-[#00C3FF] text-xl">
                +{todayReward} 灵值
              </div>
              <div className="text-[#B4C7E7] mt-2">
                连续签到 {currentStreak} 天
              </div>
            </div>
          )}
        </div>

        <style>{`
          @keyframes fall {
            0% { opacity: 1; transform: translateY(0) rotate(0deg); }
            100% { opacity: 0; transform: translateY(100vh) rotate(720deg); }
          }
        `}</style>
      </div>
    )
  }

  return (
    <button
      onClick={handleCheckIn}
      disabled={isAnimating}
      className="w-full relative overflow-hidden bg-gradient-to-r from-[#00C3FF] to-[#0080FF] text-white font-bold py-4 px-8 rounded-xl hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <div className="flex items-center justify-center gap-3 relative z-10">
        <Sparkles className={`w-6 h-6 ${isAnimating ? 'animate-spin' : ''}`} />
        <span className="text-lg">{isAnimating ? '签到中...' : '立即签到'}</span>
      </div>

      {/* 光效 */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

      {/* 粒子效果 */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
              animationDuration: `${1 + Math.random()}s`
            }}
          />
        ))}
      </div>
    </button>
  )
}

export default CheckInRitual
