import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, User, Heart, Sparkles } from 'lucide-react'

// 情绪价值文案配置
const emotionalTexts = {
  morning: [
    '早安！每一天都是新的开始',
    '清晨的阳光为你而来',
    '今天也要元气满满哦',
  ],
  afternoon: [
    '下午好，保持好心情',
    '忙碌之中别忘了休息',
    '你的努力值得被看见',
  ],
  evening: [
    '晚上好，辛苦了',
    '放松一下，明天会更好',
    '每一个夜晚都是成长的见证',
  ],
  welcome: [
    '好久不见，甚是想念',
    '期待再次与你相遇',
    '欢迎回家，我的朋友',
  ],
}

// 获取时间段
const getTimePeriod = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return 'morning'
  if (hour >= 12 && hour < 18) return 'afternoon'
  return 'evening'
}

// 获取情绪价值文案
const getEmotionalText = (period?: string) => {
  const timePeriod = period || getTimePeriod()
  const texts = emotionalTexts[timePeriod as keyof typeof emotionalTexts]
  return texts[Math.floor(Math.random() * texts.length)]
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
  const [emotionalText, setEmotionalText] = useState('')
  const [timePeriod, setTimePeriod] = useState('')

  // 获取个性化欢迎词
  const fetchPersonalizedWelcome = async (username: string) => {
    try {
      const response = await fetch(`/api/user/welcome?username=${username}`)
      if (response.ok) {
        const data = await response.json()
        return data.welcome_text
      }
    } catch (err) {
      console.error('获取个性化欢迎词失败:', err)
    }
    return null
  }

  // 初始化情绪文案
  useEffect(() => {
    const period = getTimePeriod()
    setTimePeriod(period)
    setEmotionalText(getEmotionalText(period))
  }, [])

  // 监听用户名输入，获取个性化欢迎词
  useEffect(() => {
    if (formData.username.length >= 3) {
      fetchPersonalizedWelcome(formData.username).then((welcomeText) => {
        if (welcomeText) {
          setEmotionalText(welcomeText)
        }
      })
    }
  }, [formData.username])

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

  // 智能排版：根据内容长度调整样式
  const getHeadlineSize = () => {
    return emotionalText.length > 10 ? 'text-2xl' : 'text-3xl'
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="w-full max-w-md">
        {/* 顶部区域 - 简洁设计，无动画 */}
        <div className="text-center mb-6">
          {/* 简洁Logo - 无渐变，无动画 */}
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-3">
            <User className="w-8 h-8 text-white" />
          </div>

          {/* 智能排版：情绪价值文案 */}
          <div className="space-y-2">
            <div className={`font-bold ${getHeadlineSize()} text-gray-800 leading-tight`}>
              {emotionalText}
            </div>
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <Sparkles className="w-4 h-4" />
              <span>登录你的账户</span>
            </div>
          </div>
        </div>

        {/* 登录表单 - 优化布局 */}
        <div className="bg-white rounded-2xl shadow-sm p-8 border border-gray-100">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-center space-x-2">
              <span className="text-red-500">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                用户名 / 邮箱
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-gray-300"
                  placeholder="请输入用户名或邮箱"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-gray-300"
                  placeholder="请输入密码"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-sm"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>登录中...</span>
                </>
              ) : (
                <>
                  <span>继续</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              还没有账户？{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium transition-colors">
                立即创建
              </Link>
            </p>
          </div>
        </div>

        {/* 情绪价值提示 - 底部 */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-pink-50 to-purple-50 rounded-full border border-pink-100">
            <Heart className="w-4 h-4 text-pink-500" />
            <span className="text-sm text-gray-600">
              我们懂你的每一个情绪
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
