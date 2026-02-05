import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, User, Sparkles, Heart, Star, RefreshCw, MessageCircle, CheckCircle, AlertCircle } from 'lucide-react'

// 梦幻式设计风格配置
const dreamStyles = {
  dawn: {
    bg: 'bg-gradient-to-br from-pink-100 via-purple-50 to-orange-50',
    cardBg: 'bg-white/80 backdrop-blur-lg',
    buttonBg: 'from-pink-500 to-orange-400',
    buttonHover: 'from-pink-600 to-orange-500',
    accent: 'text-pink-600',
    decorColors: ['bg-pink-300', 'bg-purple-300', 'bg-orange-300'],
  },
  galaxy: {
    bg: 'bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900',
    cardBg: 'bg-white/90 backdrop-blur-lg',
    buttonBg: 'from-indigo-500 to-purple-500',
    buttonHover: 'from-indigo-600 to-purple-600',
    accent: 'text-indigo-600',
    decorColors: ['bg-indigo-400', 'bg-purple-400', 'bg-blue-400'],
  },
  forest: {
    bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-emerald-500 to-teal-500',
    buttonHover: 'from-emerald-600 to-teal-600',
    accent: 'text-emerald-600',
    decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-cyan-300'],
  },
  aurora: {
    bg: 'bg-gradient-to-br from-rose-100 via-purple-100 to-blue-100',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-rose-500 to-purple-500',
    buttonHover: 'from-rose-600 to-purple-600',
    accent: 'text-rose-600',
    decorColors: ['bg-rose-300', 'bg-purple-300', 'bg-blue-300'],
  },
}

const RegisterFull = () => {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [styleKey, setStyleKey] = useState<keyof typeof dreamStyles>('dawn')
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showStyleSwitcher, setShowStyleSwitcher] = useState(false)

  const currentStyle = dreamStyles[styleKey]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 验证
    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      setLoading(false)
      return
    }

    if (!formData.agreeTerms) {
      setError('请阅读并同意服务条款')
      setLoading(false)
      return
    }

    try {
      await register(formData.username, formData.email, formData.password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleWechatRegister = () => {
    // 微信注册逻辑
    window.location.href = '/api/wechat/login?action=register'
  }

  return (
    <div className={`min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden ${currentStyle.bg}`}>
      
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
            className="absolute text-white/40 animate-pulse"
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
          {/* Logo */}
          <div className="relative inline-block mb-4">
            <div className={`w-20 h-20 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl flex items-center justify-center mx-auto transform rotate-3 hover:rotate-6 transition-transform duration-300 shadow-xl`}>
              <User className="w-10 h-10 text-white" />
            </div>
            {/* 光晕效果 */}
            <div className={`absolute inset-0 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl blur-xl opacity-50`}></div>
          </div>

          {/* 欢迎文案 */}
          <div className="space-y-3">
            <div className="flex items-center justify-center space-x-2">
              <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
              <Heart className="w-5 h-5 text-red-400 animate-pulse delay-300" />
              <Star className="w-5 h-5 text-purple-500 animate-pulse delay-700" />
            </div>
            <div className="text-2xl font-bold text-gray-800 leading-tight">
              创建你的账户
            </div>
            <div className={`text-sm ${currentStyle.accent} font-medium`}>
              加入灵值生态园，开启智慧之旅
            </div>
          </div>
        </div>

        {/* 注册表单 */}
        <div className={`${currentStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                用户名
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all hover:border-gray-300 bg-white/50 backdrop-blur"
                  placeholder="设置用户名"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                邮箱地址
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all hover:border-gray-300 bg-white/50 backdrop-blur"
                  placeholder="输入邮箱地址"
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
                  placeholder="设置密码"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                确认密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all hover:border-gray-300 bg-white/50 backdrop-blur"
                  placeholder="再次输入密码"
                  required
                />
              </div>
            </div>

            {/* 服务条款 */}
            <div className="flex items-start space-x-2">
              <input
                type="checkbox"
                id="agreeTerms"
                checked={formData.agreeTerms}
                onChange={(e) => setFormData({ ...formData, agreeTerms: e.target.checked })}
                className="mt-1 w-4 h-4 text-pink-500 rounded border-gray-300 focus:ring-pink-500"
                required
              />
              <label htmlFor="agreeTerms" className="text-sm text-gray-600">
                我已阅读并同意{' '}
                <Link to="/terms" className={`font-semibold ${currentStyle.accent} hover:underline`}>
                  服务条款
                </Link>
                {' '}和{' '}
                <Link to="/privacy" className={`font-semibold ${currentStyle.accent} hover:underline`}>
                  隐私政策
                </Link>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full bg-gradient-to-r ${currentStyle.buttonBg} text-white py-3 rounded-xl font-semibold hover:${currentStyle.buttonHover} transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg transform hover:scale-[1.02]`}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>注册中...</span>
                </>
              ) : (
                <>
                  <span>创建账户</span>
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

          {/* 微信注册 */}
          <button
            onClick={handleWechatRegister}
            className="w-full bg-[#07c160] text-white py-3 rounded-xl font-semibold hover:bg-[#06ad56] transition-all flex items-center justify-center space-x-2 shadow-lg transform hover:scale-[1.02]"
          >
            <MessageCircle className="w-5 h-5" />
            <span>微信注册</span>
          </button>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              已有账户？{' '}
              <Link to="/login" className={`font-semibold ${currentStyle.accent} hover:underline`}>
                立即登录
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RegisterFull
