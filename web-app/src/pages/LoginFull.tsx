import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, ArrowRight, Sparkles, Heart, Star, RefreshCw, CheckCircle, User, MessageCircle } from 'lucide-react'

// 生态之梦风格（固定）
const ecosystemStyle = {
  bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-amber-50',
  cardBg: 'bg-white/85 backdrop-blur-lg',
  buttonBg: 'from-emerald-500 to-amber-500',
  buttonHover: 'from-emerald-600 to-amber-600',
  accent: 'text-emerald-600',
  decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-amber-300'],
}

// 生态特点配置
const ecosystemFeatures = [
  { title: '100', subtitle: '价值确定性', icon: CheckCircle },
  { title: 'T+1', subtitle: '快速到账', icon: ArrowRight },
  { title: '0', subtitle: '0手续费', icon: Sparkles },
]

const LoginFull = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [featureIndex, setFeatureIndex] = useState(0)

  // 光扫动画轮播
  useEffect(() => {
    const interval = setInterval(() => {
      setFeatureIndex((prev) => (prev + 1) % ecosystemFeatures.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(formData.username, formData.password)
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
    <div className={`min-h-screen flex items-center justify-center px-4 relative overflow-hidden ${ecosystemStyle.bg}`}>
      {/* 静态背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 ${ecosystemStyle.decorColors[0]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${ecosystemStyle.decorColors[1]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${ecosystemStyle.decorColors[2]} rounded-full blur-3xl opacity-20`}></div>
        <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-white/30 backdrop-blur rounded-2xl rotate-12"></div>
        <div className="absolute bottom-32 right-1/4 w-20 h-20 bg-white/40 backdrop-blur rounded-3xl -rotate-6"></div>
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-12 h-24 bg-white/20 backdrop-blur rounded-full"></div>
      </div>

      {/* 登录卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 生态特点 - 光扫动画 */}
        <div className="mb-6">
          <div className={`${ecosystemStyle.cardBg} rounded-2xl p-4 shadow-xl border border-white/50 backdrop-blur-xl overflow-hidden relative`}>
            <div className="relative z-10 flex items-center justify-between">
              {ecosystemFeatures.map((feature, idx) => (
                <div key={idx} className={`flex flex-col items-center transition-all duration-500 ${featureIndex === idx ? 'opacity-100 transform scale-110' : 'opacity-50'}`}>
                  <div className={`w-12 h-12 ${ecosystemStyle.buttonBg} rounded-full flex items-center justify-center mb-2 shadow-lg`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className={`text-2xl font-bold ${ecosystemStyle.accent}`}>{feature.title}</div>
                  <div className="text-xs text-gray-600">{feature.subtitle}</div>
                </div>
              ))}
            </div>
            {/* 光扫效果 */}
            <div className={`absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-transparent via-white/50 to-transparent transition-all duration-300`} style={{ left: `${featureIndex * 33.33}%` }}></div>
          </div>
        </div>

        {/* 登录表单 */}
        <div className={`${ecosystemStyle.cardBg} rounded-2xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
          {/* 头部 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center space-x-2 mb-4">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <Heart className="w-5 h-5 text-emerald-500" />
              <Star className="w-5 h-5 text-teal-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 whitespace-nowrap">欢迎回到灵值生态园</h1>
            <p className="text-sm text-gray-600 mt-2 whitespace-nowrap">资源匹配·价值变现·生态共生</p>
          </div>

          {/* 表单 */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 whitespace-nowrap">用户名</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><User className="w-5 h-5 text-gray-400" /></div>
                <input type="text" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors" placeholder="请输入用户名" required />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 whitespace-nowrap">密码</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><Lock className="w-5 h-5 text-gray-400" /></div>
                <input type="password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors" placeholder="请输入密码" required />
              </div>
            </div>

            {error && <div className="text-red-500 text-sm whitespace-nowrap">{error}</div>}

            {/* 忘记密码链接 */}
            <div className="text-right"><Link to="/forgot-password" className="text-sm text-emerald-600 hover:text-emerald-700 whitespace-nowrap">忘记密码？</Link></div>

            {/* 登录按钮组 */}
            <div className="grid grid-cols-2 gap-3">
              <button type="submit" disabled={loading} className={`py-3 px-4 bg-gradient-to-r ${ecosystemStyle.buttonBg} text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center ${loading ? 'opacity-70' : ''}`}>
                {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Lock className="w-5 h-5" />}
              </button>
              <button type="button" onClick={handleWechatLogin} className="py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center">
                <MessageCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3 text-center text-sm font-medium text-gray-700">
              <span>密码登录</span>
              <span>微信登录</span>
            </div>
          </form>

          {/* 注册链接 */}
          <div className="mt-6 text-center text-sm text-gray-600 whitespace-nowrap">
            还没有账户？<Link to="/register-full" className={`font-semibold ${ecosystemStyle.accent} hover:underline`}>立即注册</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginFull
