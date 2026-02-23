import { useState, useEffect } from 'react'
import { X, ChevronRight, CheckCircle, Sparkles, Gift, Users, Coins, TrendingUp } from 'lucide-react'

interface OnboardingGuideProps {
  onClose: () => void
}

interface GuideStep {
  id: number
  title: string
  description: string
  icon: React.ReactNode
  action?: string
}

const OnboardingGuide = ({ onClose }: OnboardingGuideProps) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())

  const steps: GuideStep[] = [
    {
      id: 1,
      title: '欢迎来到灵值生态园',
      description: '这是一个让您日常行为产生真实收益的数字资产系统。通过签到、对话、参与项目等方式积累灵值，兑换现金收益。',
      icon: <Sparkles className="w-12 h-12 text-[#00C3FF]" />,
      action: '开始探索'
    },
    {
      id: 2,
      title: '每日签到',
      description: '每天打开APP点击签到，即可获得灵值奖励。连续签到天数越多，奖励越丰厚！',
      icon: <CheckCircle className="w-12 h-12 text-green-400" />,
      action: '去签到'
    },
    {
      id: 3,
      title: '智能对话',
      description: '与AI智能体交流，获取系统使用指导，探索生态价值。智能体随时为您解答问题。',
      icon: <Sparkles className="w-12 h-12 text-purple-400" />,
      action: '开始对话'
    },
    {
      id: 4,
      title: '参与项目',
      description: '参与中视频项目、美学项目等，获得更多灵值奖励和实物奖品。',
      icon: <Gift className="w-12 h-12 text-pink-400" />,
      action: '浏览项目'
    },
    {
      id: 5,
      title: '推荐好友',
      description: '邀请好友加入灵值生态园，构建您的客户网络，享受推荐收益。',
      icon: <Users className="w-12 h-12 text-blue-400" />,
      action: '去邀请'
    },
    {
      id: 6,
      title: '灵值兑换',
      description: '积累的灵值可以兑换现金、参与分红池、解锁高级功能等。',
      icon: <Coins className="w-12 h-12 text-yellow-400" />,
      action: '去兑换'
    },
    {
      id: 7,
      title: '成为合伙人',
      description: '累计10,000灵值，申请成为合伙人，享受更高收益倍数和专属权益。',
      icon: <TrendingUp className="w-12 h-12 text-orange-400" />,
      action: '查看详情'
    }
  ]

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCompletedSteps(prev => new Set([...prev, steps[currentStep].id]))
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const skip = () => {
    setCompletedSteps(prev => new Set([...prev, steps[currentStep].id]))
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handleComplete = () => {
    // 保存已完成状态到localStorage
    localStorage.setItem('onboarding-completed', 'true')
    onClose()
  }

  const handleStepClick = (stepIndex: number) => {
    if (completedSteps.has(steps[stepIndex].id)) {
      setCurrentStep(stepIndex)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[999999] p-4">
      <div className="bg-gradient-to-br from-[#091422] to-[#0A1628] border border-[#00C3FF]/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl shadow-[#00C3FF]/20">
        {/* 关闭按钮 */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#B4C7E7] hover:text-white transition-colors z-10"
        >
          <X className="w-6 h-6" />
        </button>

        {/* 进度条 */}
        <div className="h-1 bg-[#121A2F] w-full">
          <div
            className="h-full bg-gradient-to-r from-[#00C3FF] to-[#0080FF] transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* 步骤指示器 */}
        <div className="flex items-center justify-center gap-2 p-6">
          {steps.map((step, index) => (
            <button
              key={step.id}
              onClick={() => handleStepClick(index)}
              className={`w-3 h-3 rounded-full transition-all ${
                currentStep === index
                  ? 'w-6 bg-[#00C3FF]'
                  : completedSteps.has(step.id)
                  ? 'bg-green-400'
                  : 'bg-[#121A2F]'
              }`}
            />
          ))}
        </div>

        {/* 当前步骤内容 */}
        <div className="px-8 pb-8">
          <div className="flex flex-col items-center text-center mb-8">
            <div className="mb-6 p-6 bg-[#121A2F]/50 rounded-3xl border border-[#00C3FF]/20">
              {steps[currentStep].icon}
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">{steps[currentStep].title}</h2>
            <p className="text-[#B4C7E7] text-lg leading-relaxed">{steps[currentStep].description}</p>
          </div>

          {/* 按钮组 */}
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={skip}
              className={`px-6 py-3 rounded-xl font-medium transition-all ${
                currentStep === steps.length - 1
                  ? 'bg-[#121A2F] text-[#B4C7E7] hover:bg-[#1A2332]'
                  : 'bg-transparent text-[#B4C7E7] hover:text-white'
              }`}
            >
              {currentStep === steps.length - 1 ? '完成' : '跳过'}
            </button>
            <button
              onClick={nextStep}
              className="px-8 py-3 bg-gradient-to-r from-[#00C3FF] to-[#0080FF] text-white font-bold rounded-xl hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center gap-2"
            >
              {currentStep === steps.length - 1 ? '开始使用' : steps[currentStep].action}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 底部提示 */}
        <div className="px-8 pb-6">
          <div className="text-center text-[#B4C7E7] text-sm">
            步骤 {currentStep + 1} / {steps.length}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OnboardingGuide
