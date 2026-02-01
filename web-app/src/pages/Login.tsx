import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, TrendingUp, Clock, Zap } from 'lucide-react'

const FeatureCard = ({ icon: Icon, title, value, subtitle, color, delay }: any) => {
  const [count, setCount] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  useEffect(() => {
    if (isVisible && typeof value === 'number') {
      let start = 0
      const end = value
      const duration = 1500
      const increment = end / (duration / 16)

      const timer = setInterval(() => {
        start += increment
        if (start >= end) {
          setCount(end)
          clearInterval(timer)
        } else {
          setCount(Math.floor(start))
        }
      }, 16)

      return () => clearInterval(timer)
    } else if (isVisible && typeof value === 'string') {
      setCount(1)
    }
  }, [isVisible, value])

  return (
    <div
      className={`bg-white rounded-xl p-4 text-center shadow-md hover:shadow-xl transform hover:-translate-y-2 transition-all duration-500 cursor-default ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
    >
      <div className={`w-12 h-12 ${color} bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3 animate-pulse`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
      <div className={`text-2xl font-bold ${color} mb-1`}>
        {typeof value === 'number' ? count : value}
      </div>
      <div className="text-xs text-gray-600">{subtitle}</div>
    </div>
  )
}

const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(formData.username, formData.password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleWeChatLogin = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8001/api/wechat/login')
      const data = await response.json()

      if (data.success && data.data.auth_url) {
        // 跳转到微信授权页面
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
        {/* Logo和标题 - 添加悬浮动画 */}
        <div className="text-center mb-8 animate-bounce">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl hover:shadow-2xl hover:scale-110 transition-all duration-300 cursor-pointer">
            <Lock className="w-10 h-10 text-white animate-pulse" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent animate-gradient-x">
            欢迎回到灵值生态园
          </h1>
          <p className="text-gray-600 mt-2">登录您的账户，开启价值创造之旅</p>
        </div>

        {/* 登录表单 */}
        <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow duration-300">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm animate-shake">
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
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300"
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
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300"
                  placeholder="请输入密码"
                  required
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Link
                to="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-700 transition-colors hover:underline"
              >
                忘记密码？
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0"
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

          {/* 微信登录 */}
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
              className="mt-4 w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-all flex items-center justify-center space-x-2 hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.5 13.5c-2.5 0-4.5-2-4.5-4.5S6 4.5 8.5 4.5s4.5 2 4.5 4.5-2 4.5-4.5 4.5zm7 0c-.3 0-.5 0-.8 0-1.5 2.2-4 3.5-6.7 3.5-4.4 0-8-3.6-8-8s3.6-8 8-8c4.4 0 8 3.6 8 8 0 1.5-.4 2.8-1.1 4-1.7.4-3 2-3 3.8v.7h.1c1.5 0 3-.6 4.1-1.5l.2.2c.8-.8 1.9-1.3 3-1.3 2.5 0 4.5 2 4.5 4.5s-2 4.5-4.5 4.5-4.5-2-4.5-4.5c0-1.2.5-2.3 1.3-3.1.6-1.8 2-3.4 3.7-4.2z"/>
              </svg>
              <span>微信登录</span>
            </button>
          </div>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              还没有账户？{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-semibold hover:underline">
                立即注册
              </Link>
            </p>
          </div>
        </div>

        {/* 功能亮点 - 动画卡片 */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <FeatureCard
            icon={TrendingUp}
            title="价值确定性"
            value={100}
            subtitle="价值确定性"
            color="text-primary-600"
            delay={0}
          />
          <FeatureCard
            icon={Clock}
            title="快速到账"
            value="T+1"
            subtitle="快速到账"
            color="text-secondary-600"
            delay={200}
          />
          <FeatureCard
            icon={Zap}
            title="零手续费"
            value="0"
            subtitle="0手续费"
            color="text-teal-600"
            delay={400}
          />
        </div>
      </div>
    </div>
  )
}

export default Login
