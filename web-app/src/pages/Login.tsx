import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, Smartphone, RefreshCw } from 'lucide-react'

const Login = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    phoneCode: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [needPhoneCode, setNeedPhoneCode] = useState(false)
  const [sendingCode, setSendingCode] = useState(false)
  const [countdown, setCountdown] = useState(0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (data.success) {
        localStorage.setItem('token', data.data.token)
        localStorage.setItem('user', JSON.stringify(data.data.user))
        navigate('/')
      } else if (data.need_phone_code) {
        setNeedPhoneCode(true)
        setError(data.message)
      } else {
        setError(data.message || '登录失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleSendCode = async () => {
    if (countdown > 0) return

    setSendingCode(true)
    setError('')

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
        }),
      })

      const data = await response.json()

      if (data.success && data.data.user?.phone) {
        const codeResponse = await fetch(`${apiBase}/api/send-code`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            phone: data.data.user.phone,
          }),
        })

        const codeData = await codeResponse.json()

        if (codeData.success) {
          setCountdown(60)
          const timer = setInterval(() => {
            setCountdown((prev) => {
              if (prev <= 1) {
                clearInterval(timer)
                return 0
              }
              return prev - 1
            })
          }, 1000)

          alert(`验证码已发送（测试环境：${codeData.data.code}）`)
        } else {
          setError(codeData.message || '发送验证码失败')
        }
      } else {
        setError(data.message || '获取手机号失败')
      }
    } catch (err) {
      setError('发送验证码失败，请重试')
    } finally {
      setSendingCode(false)
    }
  }

  const handleWeChatLogin = async () => {
    try {
      setLoading(true)
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
      const response = await fetch(`${apiBase}/api/wechat/login`)
      const data = await response.json()

      if (data.success && data.data.auth_url) {
        window.location.href = data.data.auth_url
      } else {
        setError(data.message || '微信登录配置错误')
      }
    } catch (err) {
      setError('微信登录失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl">
            <Lock className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            欢迎回到灵值生态园
          </h1>
          <p className="text-gray-600 mt-2">登录您的账户，开启价值创造之旅</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请输入用户名"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">密码</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请输入密码"
                  required
                />
              </div>
            </div>

            {needPhoneCode && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">手机验证码</label>
                <div className="flex space-x-2">
                  <div className="relative flex-1">
                    <Smartphone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={formData.phoneCode}
                      onChange={(e) => setFormData({ ...formData, phoneCode: e.target.value })}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="请输入验证码"
                      required
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleSendCode}
                    disabled={sendingCode || countdown > 0}
                    className="px-4 py-3 bg-primary-500 text-white rounded-lg font-semibold hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 whitespace-nowrap"
                  >
                    {sendingCode ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : countdown > 0 ? (
                      <span>{countdown}秒后重试</span>
                    ) : (
                      <span>发送验证码</span>
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">为保护账户安全，登录需要手机验证码验证</p>
              </div>
            )}

            <div className="flex items-center justify-between">
              <Link
                to="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-700 transition-colors"
              >
                忘记密码？
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>登录中...</span>
                </>
              ) : (
                <>
                  <span>登录</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">或使用以下方式登录</span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => handleWeChatLogin()}
              className="mt-4 w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-all flex items-center justify-center space-x-2"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.5 13.5c-2.5 0-4.5-2-4.5-4.5S6 4.5 8.5 4.5s4.5 2 4.5 4.5-2 4.5-4.5 4.5zm7 0c-.3 0-.5 0-.8 0-1.5 2.2-4 3.5-6.7 3.5-4.4 0-8-3.6-8-8s3.6-8 8-8c4.4 0 8 3.6 8 8 0 1.5-.4 2.8-1.1 4-1.7.4-3 2-3 3.8v.7h.1c1.5 0 3-.6 4.1-1.5l.2.2c.8-.8 1.9-1.3 3-1.3 2.5 0 4.5 2 4.5 4.5s-2 4.5-4.5 4.5-4.5-2-4.5-4.5c0-1.2.5-2.3 1.3-3.1.6-1.8 2-3.4 3.7-4.2z"/>
              </svg>
              <span>微信登录</span>
            </button>
          </div>

          <div className="mt-6 text-center text-sm text-gray-600">
            还没有账号？{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-semibold">
              立即注册
            </Link>
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-gray-500">
          登录即表示您同意我们的{' '}
          <Link to="/terms" className="text-primary-600 hover:underline">
            服务条款
          </Link>{' '}
          和{' '}
          <Link to="/privacy" className="text-primary-600 hover:underline">
            隐私政策
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Login
