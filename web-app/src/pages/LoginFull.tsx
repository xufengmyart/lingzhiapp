import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, ArrowRight, Star, Sparkles, Heart, RefreshCw, MessageCircle, CheckCircle, User } from 'lucide-react'

// 梦幻式设计风格配置
const dreamStyles = {
  ecosystem: {
    bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-amber-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-emerald-500 to-amber-500',
    buttonHover: 'from-emerald-600 to-amber-600',
    accent: 'text-emerald-600',
    decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-amber-300'],
  },
  aurora: {
    bg: 'bg-gradient-to-br from-rose-100 via-purple-100 to-blue-100',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-rose-500 to-purple-500',
    buttonHover: 'from-rose-600 to-purple-600',
    accent: 'text-rose-600',
    decorColors: ['bg-rose-300', 'bg-purple-300', 'bg-blue-300'],
  },
  sakura: {
    bg: 'bg-gradient-to-br from-pink-50 via-rose-50 to-fuchsia-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-pink-400 to-fuchsia-400',
    buttonHover: 'from-pink-500 to-fuchsia-500',
    accent: 'text-pink-500',
    decorColors: ['bg-pink-200', 'bg-rose-200', 'bg-fuchsia-200'],
  },
  ocean: {
    bg: 'bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-cyan-500 to-blue-500',
    buttonHover: 'from-cyan-600 to-blue-600',
    accent: 'text-cyan-600',
    decorColors: ['bg-cyan-300', 'bg-blue-300', 'bg-indigo-300'],
  },
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
  const [styleKey, setStyleKey] = useState<keyof typeof dreamStyles>('ecosystem')
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showStyleSwitcher, setShowStyleSwitcher] = useState(false)
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
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleWechatLogin = () => {
    window.location.href = '/api/wechat/login'
  }

  const currentStyle = dreamStyles[styleKey]
  const currentFeature = ecosystemFeatures[featureIndex]
  const FeatureIcon = currentFeature.icon

  return (
    <div className={`min-h-screen flex items-center justify-center px-4 relative overflow-hidden ${currentStyle.bg}`}>
      {/* 静态背景装饰（无动画） */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 ${currentStyle.decorColors[0]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${currentStyle.decorColors[1]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${currentStyle.decorColors[2]} rounded-full blur-3xl opacity-20`}></div>
        <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-white/30 backdrop-blur rounded-2xl rotate-12"></div>
        <div className="absolute bottom-32 right-1/4 w-20 h-20 bg-white/40 backdrop-blur rounded-3xl -rotate-6"></div>
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-12 h-24 bg-white/20 backdrop-blur rounded-full"></div>
      </div>

      {/* 风格切换按钮 */}
      <button onClick={() => setShowStyleSwitcher(!showStyleSwitcher)} className="absolute top-4 right-4 z-50 p-2 bg-white/50 backdrop-blur rounded-full hover:bg-white/70 shadow-lg" title="切换设计风格"><RefreshCw className="w-6 h-6 text-gray-700" /></button>

      {/* 风格切换器 */}
      {showStyleSwitcher && (
        <div className="absolute top-16 right-4 z-50 bg-white/90 backdrop-blur-lg rounded-2xl p-4 shadow-2xl border border-white/30">
          <div className="text-sm font-semibold text-gray-700 mb-3">选择梦幻风格</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(dreamStyles).map(([key, style]) => (
              <button key={key} onClick={() => { setStyleKey(key as keyof typeof dreamStyles); setShowStyleSwitcher(false); }} className={`p-3 rounded-xl border-2 transition-all ${styleKey === key ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300'}`}>
                <div className={`w-full h-12 rounded-lg ${style.bg} mb-2 flex items-center justify-center text-2xl`}>
                  {key === 'ecosystem' && '🌿'}
                  {key === 'aurora' && '🌈'}
                  {key === 'sakura' && '🌸'}
                  {key === 'ocean' && '🌊'}
                </div>
                <div className="text-xs font-medium text-gray-800">{key}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 登录卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 生态特点 - 光扫动画 */}
        <div className="mb-6">
          <div className={`${currentStyle.cardBg} rounded-2xl p-4 shadow-xl border border-white/50 backdrop-blur-xl overflow-hidden relative`}>
            <div className="relative z-10 flex items-center justify-between">
              {ecosystemFeatures.map((feature, idx) => (
                <div key={idx} className={`flex flex-col items-center transition-all duration-500 ${featureIndex === idx ? 'opacity-100 transform scale-110' : 'opacity-50'}`}>
                  <div className={`w-12 h-12 ${currentStyle.buttonBg} rounded-full flex items-center justify-center mb-2 shadow-lg`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className={`text-2xl font-bold ${currentStyle.accent}`}>{feature.title}</div>
                  <div className="text-xs text-gray-600">{feature.subtitle}</div>
                </div>
              ))}
            </div>
            {/* 光扫效果 */}
            <div className={`absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-transparent via-white/50 to-transparent transition-all duration-300`} style={{ left: `${featureIndex * 33.33}%` }}></div>
          </div>
        </div>

        {/* 登录表单 */}
        <div className={`${currentStyle.cardBg} rounded-2xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
          {/* 头部 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center space-x-2 mb-4">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <Heart className="w-5 h-5 text-emerald-500" />
              <Star className="w-5 h-5 text-teal-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800">欢迎回到灵值生态园</h1>
            <p className="text-sm text-gray-600 mt-2">资源匹配·价值变现·生态共生</p>
          </div>

          {/* 表单 */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><User className="w-5 h-5 text-gray-400" /></div>
                <input type="text" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors" placeholder="请输入用户名" required />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><Lock className="w-5 h-5 text-gray-400" /></div>
                <input type="password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors" placeholder="请输入密码" required />
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            {/* 忘记密码链接 */}
            <div className="text-right"><Link to="/forgot-password" className="text-sm text-emerald-600 hover:text-emerald-700">忘记密码？</Link></div>

            {/* 合一的登录按钮 */}
            <div className="space-y-3">
              <button type="submit" disabled={loading} className={`w-full py-3 px-4 bg-gradient-to-r ${currentStyle.buttonBg} text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center ${loading ? 'opacity-70' : ''}`}>
                {loading ? <RefreshCw className="w-5 h-5 animate-spin mr-2" /> : <Lock className="w-5 h-5 mr-2" />}
                {loading ? '登录中...' : '登录'}
              </button>
              <button type="button" onClick={handleWechatLogin} className="w-full py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center">
                <MessageCircle className="w-5 h-5 mr-2" />微信登录
              </button>
            </div>
          </form>

          {/* 注册链接 */}
          <div className="mt-6 text-center text-sm text-gray-600">
            还没有账户？<Link to="/register-full" className={`font-semibold ${currentStyle.accent} hover:underline`}>立即注册</Link>
          </div>
        </div>

        {/* 返回风格选择器 */}
        <div className="mt-6 text-center"><Link to="/dream-selector" className="text-sm text-gray-600 hover:text-gray-800 transition-colors">切换风格</Link></div>
      </div>
    </div>
  )
}

export default LoginFull
