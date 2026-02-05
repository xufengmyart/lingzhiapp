import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, User, Sparkles, Heart, Star, Moon, Sun, RefreshCw, MessageCircle } from 'lucide-react'

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

// 梦幻式设计风格配置
const dreamStyles = {
  // 风格1: 晨曦之梦（粉色+橙色渐变）
  dawn: {
    bg: 'bg-gradient-to-br from-pink-100 via-purple-50 to-orange-50',
    cardBg: 'bg-white/80 backdrop-blur-lg',
    buttonBg: 'from-pink-500 to-orange-400',
    buttonHover: 'from-pink-600 to-orange-500',
    accent: 'text-pink-600',
    decorColors: ['bg-pink-300', 'bg-purple-300', 'bg-orange-300'],
  },
  // 风格2: 星空梦境（深蓝+紫色）
  galaxy: {
    bg: 'bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900',
    cardBg: 'bg-white/90 backdrop-blur-lg',
    buttonBg: 'from-indigo-500 to-purple-500',
    buttonHover: 'from-indigo-600 to-purple-600',
    accent: 'text-indigo-600',
    decorColors: ['bg-indigo-400', 'bg-purple-400', 'bg-blue-400'],
  },
  // 风格3: 森林之梦（绿色+青色）
  forest: {
    bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-emerald-500 to-teal-500',
    buttonHover: 'from-emerald-600 to-teal-600',
    accent: 'text-emerald-600',
    decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-cyan-300'],
  },
  // 风格4: 极光之梦（彩虹渐变）
  aurora: {
    bg: 'bg-gradient-to-br from-rose-100 via-purple-100 to-blue-100',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-rose-500 to-purple-500',
    buttonHover: 'from-rose-600 to-purple-600',
    accent: 'text-rose-600',
    decorColors: ['bg-rose-300', 'bg-purple-300', 'bg-blue-300'],
  },
}

const LoginFull = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [styleKey, setStyleKey] = useState<keyof typeof dreamStyles>('dawn')
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [emotionalText, setEmotionalText] = useState('')
  const [showStyleSwitcher, setShowStyleSwitcher] = useState(false)

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

  const handleWechatLogin = () => {
    // 微信登录逻辑
    window.location.href = '/api/wechat/login'
  }

  const currentStyle = dreamStyles[styleKey]

  return (
    <div className={`min-h-screen flex items-center justify-center px-4 relative overflow-hidden ${currentStyle.bg}`}>
      
      {/* 装饰性背景元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* 顶部装饰 */}
        <div className={`absolute top-20 left-20 w-32 h-32 ${currentStyle.decorColors[0]} rounded-full blur-3xl opacity-30 animate-pulse`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${currentStyle.decorColors[1]} rounded-full blur-3xl opacity-30 animate-pulse delay-1000`}></div>
        
        {/* 中部装饰 */}
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${currentStyle.decorColors[2]} rounded-full blur-3xl opacity-20 animate-pulse delay-500`}></div>
        
        {/* 底部装饰 - 三个装饰块 */}
        <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-white/30 backdrop-blur rounded-2xl rotate-12 transform hover:scale-110 transition-transform duration-500"></div>
        <div className="absolute bottom-32 right-1/4 w-20 h-20 bg-white/40 backdrop-blur rounded-3xl -rotate-6 transform hover:scale-110 transition-transform duration-700"></div>
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-12 h-24 bg-white/20 backdrop-blur rounded-full transform hover:scale-110 transition-transform duration-600"></div>
        
        {/* 飘动的星星 */}
        {[...Array(6)].map((_, i) => (
          <Star
            key={i}
            className={`absolute text-white/40 animate-pulse`}
            style={{
              top: `${20 + Math.random() * 60}%`,
              left: `${10 + Math.random() * 80}%`,
              width: `${8 + Math.random() * 12}px`,
              height: `${8 + Math.random() * 12}px`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      {/* 风格切换按钮 */}
      <button
        onClick={() => setShowStyleSwitcher(!showStyleSwitcher)}
        className="absolute top-4 right-4 z-50 p-2 bg-white/50 backdrop-blur rounded-full hover:bg-white/70 transition-all shadow-lg"
        title="切换设计风格"
      >
        <RefreshCw className="w-6 h-6 text-gray-700" />
      </button>

      {/* 风格切换器 */}
      {showStyleSwitcher && (
        <div className="absolute top-16 right-4 z-50 bg-white/90 backdrop-blur-lg rounded-2xl p-4 shadow-2xl border border-white/30">
          <div className="text-sm font-semibold text-gray-700 mb-3">选择梦幻风格</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(dreamStyles).map(([key, style]) => (
              <button
                key={key}
                onClick={() => setStyleKey(key as keyof typeof dreamStyles)}
                className={`p-2 rounded-lg border-2 transition-all ${
                  styleKey === key
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-transparent hover:border-gray-300'
                }`}
              >
                <div className={`w-full h-8 rounded-md ${style.bg}`}></div>
                <div className="text-xs mt-1 text-gray-600 capitalize">{key}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="w-full max-w-md relative z-10">
        {/* 顶部区域 */}
        <div className="text-center mb-8">
          {/* Logo - 带有梦幻效果 */}
          <div className="relative inline-block mb-4">
            <div className={`w-20 h-20 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl flex items-center justify-center mx-auto transform rotate-3 hover:rotate-6 transition-transform duration-300 shadow-xl`}>
              <User className="w-10 h-10 text-white" />
            </div>
            {/* 光晕效果 */}
            <div className={`absolute inset-0 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl blur-xl opacity-50`}></div>
          </div>

          {/* 情绪价值文案 */}
          <div className="space-y-3">
            <div className="flex items-center justify-center space-x-2">
              <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
              <Heart className="w-5 h-5 text-red-400 animate-pulse delay-300" />
              <Star className="w-5 h-5 text-purple-500 animate-pulse delay-700" />
            </div>
            <div className="text-2xl font-bold text-gray-800 leading-tight">
              {emotionalText}
            </div>
            <div className={`text-sm ${currentStyle.accent} font-medium`}>
              欢迎回到灵值生态园
            </div>
          </div>
        </div>

        {/* 登录表单 */}
        <div className={`${currentStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-center space-x-2">
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
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all hover:border-gray-300 bg-white/50 backdrop-blur"
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
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all hover:border-gray-300 bg-white/50 backdrop-blur"
                  placeholder="请输入密码"
                  required
                />
              </div>
            </div>

            {/* 忘记密码 */}
            <div className="flex justify-end">
              <Link to="/forgot-password" className={`text-sm ${currentStyle.accent} hover:underline`}>
                忘记密码？
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full bg-gradient-to-r ${currentStyle.buttonBg} text-white py-3 rounded-xl font-semibold hover:${currentStyle.buttonHover} transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg transform hover:scale-[1.02]`}
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

          {/* 分隔线 */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-gray-200"></div>
            <div className="px-4 text-sm text-gray-500">或</div>
            <div className="flex-1 border-t border-gray-200"></div>
          </div>

          {/* 微信登录 */}
          <button
            onClick={handleWechatLogin}
            className="w-full bg-[#07c160] text-white py-3 rounded-xl font-semibold hover:bg-[#06ad56] transition-all flex items-center justify-center space-x-2 shadow-lg transform hover:scale-[1.02]"
          >
            <MessageCircle className="w-5 h-5" />
            <span>微信登录</span>
          </button>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              还没有账户？{' '}
              <Link to="/register" className={`font-semibold ${currentStyle.accent} hover:underline`}>
                立即创建
              </Link>
            </p>
          </div>
        </div>

        {/* 底部提示 */}
        <div className="mt-6 text-center text-xs text-gray-500">
          登录即表示您同意我们的{' '}
          <Link to="/terms" className="underline">服务条款</Link>
          {' '}和{' '}
          <Link to="/privacy" className="underline">隐私政策</Link>
        </div>
      </div>
    </div>
  )
}

export default LoginFull
