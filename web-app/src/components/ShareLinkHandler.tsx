import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * 分享链接处理组件
 * 功能：
 * 1. 从URL参数中提取推荐人信息
 * 2. 如果用户已登录，直接跳转到dashboard
 * 3. 如果用户未登录，跳转到登录页面并保存推荐人信息
 */
const ShareLinkHandler = () => {
  const navigate = useNavigate()

  useEffect(() => {
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search)
    const referrerId = urlParams.get('referrer_id')
    const referrerName = urlParams.get('referrer')
    const referrerPhone = urlParams.get('referrer_phone')
    const referrerEmail = urlParams.get('referrer_email')

    // 如果有推荐人信息，保存到sessionStorage
    if (referrerId || referrerName || referrerPhone || referrerEmail) {
      const referrerInfo: any = {}

      if (referrerId) referrerInfo.id = referrerId
      if (referrerName) referrerInfo.username = referrerName
      if (referrerPhone) referrerInfo.phone = referrerPhone
      if (referrerEmail) referrerInfo.email = referrerEmail

      sessionStorage.setItem('referrer_info', JSON.stringify(referrerInfo))
      console.log('[ShareLinkHandler] 推荐人信息已保存:', referrerInfo)
    }

    // 检查用户是否已登录
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    if (token && user) {
      // 用户已登录，跳转到dashboard
      navigate('/dashboard', { replace: true })
    } else {
      // 用户未登录，跳转到登录页面
      navigate('/login', { replace: true })
    }
  }, [navigate])

  // 加载中提示
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#2a4559] to-[#3e8bb6]">
      <div className="text-white text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
        <p>正在跳转...</p>
      </div>
    </div>
  )
}

export default ShareLinkHandler
