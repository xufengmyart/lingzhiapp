import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, ArrowRight, Sparkles, Heart, Star, RefreshCw, CheckCircle, User, MessageCircle, Eye, EyeOff } from 'lucide-react'

// 生态之梦风格（固定）
const ecosystemStyle = {
  bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-amber-50',
  cardBg: 'bg-white/85 backdrop-blur-lg',
  buttonBg: 'from-emerald-500 to-amber-500',
  buttonHover: 'from-emerald-600 to-amber-600',
  accent: 'text-emerald-600',
  decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-amber-300'],
}

// 生态特点配置（底部）
const ecosystemFeatures = [
  { title: '100', subtitle: '价值确定性', icon: CheckCircle },
  { title: 'T+1', subtitle: '快速到账', icon: ArrowRight },
  { title: '0', subtitle: '0手续费', icon: Sparkles },
]

const LoginFull = () => {
  const navigate = useNavigate()
  const { login, user } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // 如果用户已登录，直接跳转到dashboard
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  // 光扫动画轮播
  const [featureIndex, setFeatureIndex] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => {
      setFeatureIndex((prev) => (prev + 1) % ecosystemFeatures.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleWechatLogin = () => {
    window.location.href = '/api/wechat/login'
  }

  const currentFeature = ecosystemFeatures[featureIndex]
  const FeatureIcon = currentFeature.icon

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center px-4 py-6 relative overflow-hidden ${ecosystemStyle.bg}`}>
      {/* 静态背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 ${ecosystemStyle.decorColors[0]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${ecosystemStyle.decorColors[1]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${ecosystemStyle.decorColors[2]} rounded-full blur-3xl opacity-20`}></div>
      </div>

      {/* 登录卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center space-x-2 mb-3">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <Heart className="w-5 h-5 text-emerald-500" />
            <Star className="w-5 h-5 text-teal-500" />
          </div>
          <h1 className="text-xl font-bold text-gray-800 whitespace-nowrap">欢迎回到灵值生态园</h1>
          <p className="text-xs text-gray-600 mt-1">资源匹配·价值变现·生态共生</p>
        </div>

        {/* 登录表单 */}
        <div className={`${ecosystemStyle.cardBg} rounded-2xl shadow-2xl p-6 border border-white/50 backdrop-blur-xl`}>
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors text-sm"
                  placeholder="请输入用户名"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-9 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors text-sm"
                  placeholder="请输入密码"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            {/* 登录按钮组 */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                type="submit"
                disabled={loading}
                className={`py-2.5 px-4 bg-gradient-to-r ${ecosystemStyle.buttonBg} text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center ${loading ? 'opacity-70' : ''}`}
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                <span className="ml-2 text-sm">登录</span>
              </button>
              <button
                type="button"
                onClick={handleWechatLogin}
                className="py-2.5 px-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center"
              >
                <MessageCircle className="w-4 h-4" />
                <span className="ml-2 text-sm">微信</span>
              </button>
            </div>
          </form>

          {/* 其他选项 */}
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex justify-center space-x-4 text-sm">
              <button
                onClick={() => navigate('/register-full')}
                className="text-emerald-600 hover:text-emerald-700 font-medium"
              >
                注册账号
              </button>
              <span className="text-gray-300">|</span>
              <button
                onClick={() => navigate('/forgot-password')}
                className="text-gray-600 hover:text-gray-700"
              >
                忘记密码？
              </button>
            </div>
          </div>
        </div>

        {/* 生态特点 - 底部 */}
        <div className="mt-4">
          <div className={`${ecosystemStyle.cardBg} rounded-xl p-3 shadow-lg border border-white/50 backdrop-blur-xl overflow-hidden relative`}>
            <div className="relative z-10 flex items-center justify-around">
              {ecosystemFeatures.map((feature, idx) => (
                <div key={idx} className={`flex flex-col items-center transition-all duration-500 ${featureIndex === idx ? 'opacity-100 transform scale-110' : 'opacity-50'}`}>
                  <div className={`w-10 h-10 ${ecosystemStyle.buttonBg} rounded-full flex items-center justify-center mb-1 shadow-md`}>
                    <feature.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className={`text-xl font-bold ${ecosystemStyle.accent}`}>{feature.title}</div>
                  <div className="text-xs text-gray-600">{feature.subtitle}</div>
                </div>
              ))}
            </div>
            {/* 光扫效果 */}
            <div className={`absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-transparent via-white/50 to-transparent transition-all duration-300`} style={{ left: `${featureIndex * 33.33}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginFull
