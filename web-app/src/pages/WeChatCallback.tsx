import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const WeChatCallback = () => {
  const navigate = useNavigate()
  const { loginWithToken } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('正在处理微信登录...')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search)
        
        // 模拟模式：直接从 URL 获取 token 和 user 数据
        const token = urlParams.get('token')
        const userParam = urlParams.get('user')
        const simulate = urlParams.get('simulate')
        
        // 处理模拟模式
        if (simulate === 'true' && token && userParam) {
          try {
            const userData = JSON.parse(decodeURIComponent(userParam))
            
            // 保存微信信息到localStorage（使用统一的键名和格式）
            localStorage.setItem('wechat_info', JSON.stringify({
              wechat_openid: `mock_${token}`,
              wechat_unionid: '',
              wechat_nickname: userData.username,
              wechat_avatar: userData.avatar_url,
              is_new_user: true
            }))
            
            setStatus('success')
            setMessage('微信登录成功！正在跳转到注册页面...')
            
            setTimeout(() => {
              // 获取推荐人ID（从sessionStorage获取）
              const referrerId = sessionStorage.getItem('referrer_id')
              const queryParams = referrerId ? `?referrer_id=${referrerId}&simulate=true` : '?simulate=true'
              navigate(`/wechat-register${queryParams}`)
            }, 1500)
            return
          } catch (e) {
            console.error('解析用户数据失败:', e)
            setStatus('error')
            setMessage('登录数据解析失败')
            setTimeout(() => {
              navigate('/login')
            }, 3000)
            return
          }
        }

        // 处理真实微信登录回调
        const code = urlParams.get('code')
        const state = urlParams.get('state')

        if (!code) {
          setStatus('error')
          setMessage('微信授权失败，未获取到授权码')
          return
        }

        const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
        const response = await fetch(`${apiBase}/wechat/callback?code=${code}&state=${state}`)
        const data = await response.json()

        if (data.success) {
          // 保存微信信息到localStorage
          localStorage.setItem('wechat_info', JSON.stringify({
            wechat_openid: data.data.wechat_openid,
            wechat_unionid: data.data.wechat_unionid,
            wechat_nickname: data.data.wechat_nickname,
            wechat_avatar: data.data.wechat_avatar,
            is_new_user: data.data.is_new_user
          }))
          
          // 获取推荐人ID（从sessionStorage获取）
          const referrerId = sessionStorage.getItem('referrer_id')
          const queryParams = referrerId ? `?referrer_id=${referrerId}` : ''
          
          setStatus('success')
          setMessage('微信登录成功！正在跳转到注册页面...')
          setTimeout(() => {
            navigate(`/wechat-register${queryParams}`)
          }, 1500)
        } else {
          setStatus('error')
          setMessage(data.message || '微信登录失败')
          setTimeout(() => {
            navigate('/login')
          }, 3000)
        }
      } catch (error) {
        setStatus('error')
        setMessage('微信登录失败，请重试')
        console.error('微信登录错误:', error)
        setTimeout(() => {
          navigate('/login')
        }, 3000)
      }
    }

    handleCallback()
  }, [navigate, loginWithToken])

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          {/* 状态图标 */}
          <div className="mb-6">
            {status === 'loading' && (
              <div className="w-20 h-20 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
                <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
            {status === 'success' && (
              <div className="w-20 h-20 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
            {status === 'error' && (
              <div className="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            )}
          </div>

          {/* 状态文本 */}
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {status === 'loading' && '处理中...'}
            {status === 'success' && '登录成功'}
            {status === 'error' && '登录失败'}
          </h2>

          <p className="text-gray-600 mb-8">{message}</p>

          {/* 进度条（仅加载状态显示） */}
          {status === 'loading' && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WeChatCallback
