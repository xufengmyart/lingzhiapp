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
        // 从URL中获取code和state
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')

        if (!code) {
          setStatus('error')
          setMessage('微信授权失败，未获取到授权码')
          return
        }

        // 调用后端接口处理微信登录
        const response = await fetch(`http://localhost:8001/api/wechat/callback?code=${code}&state=${state}`)
        const data = await response.json()

        if (data.success) {
          // 保存token
          localStorage.setItem('token', data.data.token)
          
          // 检查是否需要完善信息
          if (data.data.need_complete_info) {
            setStatus('success')
            setMessage('微信登录成功！正在跳转到信息完善页面...')
            setTimeout(() => {
              navigate('/complete-profile')
            }, 1500)
          } else {
            setStatus('success')
            setMessage('微信登录成功！正在跳转...')
            setTimeout(() => {
              navigate('/')
            }, 1500)
          }
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
