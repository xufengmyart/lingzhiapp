import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { UserType } from '../types/userPersona'
import OnboardingFlow from './OnboardingFlow'
import './Onboarding.css'

const OnboardingGuard = () => {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 检查用户是否完成了引导
    const onboardingCompleted = localStorage.getItem('onboardingCompleted')

    if (!onboardingCompleted) {
      // 没有完成引导，显示引导流程
      setShowOnboarding(true)
    }

    setIsLoading(false)
  }, [])

  const handleOnboardingComplete = (userType: UserType) => {
    // 保存用户类型
    localStorage.setItem('userPersona', userType)
    localStorage.setItem('onboardingCompleted', 'true')
    setShowOnboarding(false)
    // 引导完成后，Outlet 会自动渲染子路由
  }

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#0A0D18'
      }}>
        <div style={{
          color: '#00C3FF',
          fontSize: '1.2rem'
        }}>
          加载中...
        </div>
      </div>
    )
  }

  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />
  }

  return <Outlet />
}

export default OnboardingGuard
