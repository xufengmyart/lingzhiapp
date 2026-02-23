import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, ArrowRight, User, Eye, EyeOff, RefreshCw, AlertCircle, Smartphone, Mail } from 'lucide-react'

// 科幻太空风格配置
const vrStyle = {
  bg: 'bg-gradient-to-br from-[#2a4559] via-[#3e8bb6]/40 to-[#2a4559]',
  cardBg: 'bg-[#2a4559]/60 backdrop-blur-xl',
  buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
  buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
  accent: 'text-[#3e8bb6]',
  glow: 'shadow-[0_0_30px_rgba(62,139,182,0.3)]',
}

/**
 * 改进的登录页面
 * 解决以下问题：
 * 1. 微信登录后的手机号登录问题
 * 2. 页面变黑问题（通过防止错误传播）
 * 3. 友好的错误提示
 * 4. 支持用户名、手机号、邮箱登录
 */
const LoginFixed = () => {
  const navigate = useNavigate()
  const { login, user } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [errorType, setErrorType] = useState<'error' | 'warning' | 'info'>('error')
  const [showPassword, setShowPassword] = useState(false)

  // 如果用户已登录，跳转到dashboard
  useEffect(() => {
    const currentPath = window.location.pathname
    const isLoginPage = currentPath === '/' || currentPath === '/login-fixed'

    // 检查并保存推荐人ID
    const urlParams = new URLSearchParams(window.location.search)
    const referrerId = urlParams.get('referrer_id')
    if (referrerId) {
      sessionStorage.setItem('referrer_id', referrerId)
    }

    if (user && !isLoginPage) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  // 清除错误提示
  const clearError = () => {
    setError('')
    setErrorType('error')
  }

  // 显示错误提示
  const showError = (message: string, type: 'error' | 'warning' | 'info' = 'error') => {
    setError(message)
    setErrorType(type)

    // 5秒后自动清除
    setTimeout(() => {
      clearError()
    }, 5000)
  }

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setLoading(true)

    try {
      // 验证输入
      if (!username.trim()) {
        showError('请输入用户名、手机号或邮箱', 'warning')
        setLoading(false)
        return
      }

      if (!password.trim()) {
        showError('请输入密码', 'warning')
        setLoading(false)
        return
      }

      // 调用登录API
      const success = await login(username, password)

      if (success) {
        // 登录成功，跳转到dashboard
        navigate('/dashboard')
      } else {
        // 登录失败，显示错误
        showError('登录失败，请检查用户名和密码', 'error')
        setLoading(false)
      }
    } catch (err: any) {
      console.error('登录错误:', err)

      // 防止错误传播导致页面变黑
      setLoading(false)

      // 根据错误类型显示不同的提示
      if (err.response?.data?.error_code) {
        const errorCode = err.response.data.error_code
        const message = err.response.data.message || '登录失败'

        switch (errorCode) {
          case 'MISSING_USERNAME':
            showError('请输入用户名、手机号或邮箱', 'warning')
            break
          case 'MISSING_PASSWORD':
            showError('请输入密码', 'warning')
            break
          case 'USER_NOT_FOUND':
            showError('用户不存在，请先注册', 'error')
            break
          case 'WRONG_PASSWORD':
            showError('密码错误，请重试', 'error')
            break
          case 'ACCOUNT_DISABLED':
            showError('账号已被禁用，请联系管理员', 'error')
            break
          case 'TOO_MANY_ATTEMPTS':
            showError('登录过于频繁，请稍后再试', 'warning')
            break
          default:
            showError(message, 'error')
        }
      } else if (err.response?.status === 401) {
        showError('用户名或密码错误，请重试', 'error')
      } else if (err.response?.status === 403) {
        showError('账号已被禁用，请联系管理员', 'error')
      } else if (err.response?.status === 429) {
        showError('登录过于频繁，请稍后再试', 'warning')
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        showError('网络连接失败，请检查网络后重试', 'warning')
      } else if (err.response?.data?.message) {
        showError(err.response.data.message, 'error')
      } else {
        showError('登录失败，请稍后重试', 'error')
      }
    }
  }

  // 微信登录（暂时禁用，显示友好提示）
  const handleWechatLogin = () => {
    showError('微信登录功能正在开发中，请使用手机号登录', 'info')
  }

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center px-4 py-6 relative overflow-hidden ${vrStyle.bg}`}>
      {/* 科幻主题光晕装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#3e8bb6]/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#b5cbdb]/20 rounded-full blur-[128px]"></div>
      </div>

      {/* 登录卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white whitespace-nowrap drop-shadow-lg">
            欢迎登录灵值生态园
          </h1>
          <p className="text-sm text-[#b5cbdb] mt-2 drop-shadow-md">
            请使用用户名、手机号或邮箱登录
          </p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div
            className={`mb-4 rounded-lg px-4 py-3 text-sm backdrop-blur-sm ${
              errorType === 'error'
                ? 'bg-red-500/20 border border-red-500/50 text-red-300'
                : errorType === 'warning'
                ? 'bg-yellow-500/20 border border-yellow-500/50 text-yellow-300'
                : 'bg-blue-500/20 border border-blue-500/50 text-blue-300'
            }`}
          >
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p>{error}</p>
              </div>
              <button
                onClick={clearError}
                className="text-white/50 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* 登录表单 */}
        <div className={`${vrStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/20 backdrop-blur-xl ${vrStyle.glow}`}>
          <form onSubmit={handleLoginSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">
                用户名 / 手机号 / 邮箱
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => {
                    setUsername(e.target.value)
                    clearError()
                  }}
                  className="block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入用户名、手机号或邮箱"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">密码</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    clearError()
                  }}
                  className="block w-full pl-10 pr-10 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入密码"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#b5cbdb] hover:text-[#3e8bb6] transition-colors"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* 登录按钮组 */}
            <div className="space-y-3 pt-2">
              {/* 账号密码登录 */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full relative py-3 px-4 bg-gradient-to-r ${vrStyle.buttonBg} text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 overflow-hidden group ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                {loading ? (
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto" />
                ) : (
                  <span className="flex items-center justify-center">
                    <Lock className="w-5 h-5 mr-2" />
                    登录
                  </span>
                )}
              </button>

              {/* 微信登录（暂时禁用） */}
              <button
                type="button"
                onClick={handleWechatLogin}
                disabled={loading}
                className="w-full relative py-3 px-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white font-semibold rounded-xl shadow-lg transition-all overflow-hidden opacity-60 cursor-not-allowed"
              >
                <div className="flex items-center justify-center">
                  <span className="text-sm">微信登录（开发中）</span>
                </div>
              </button>
            </div>
          </form>

          {/* 其他选项 */}
          <div className="mt-6 pt-4 border-t border-white/10">
            <div className="flex justify-center space-x-6 text-sm">
              <button
                onClick={() => navigate('/register-full')}
                className="text-[#b5cbdb] hover:text-[#3e8bb6] font-medium transition-colors"
                disabled={loading}
              >
                注册账号
              </button>
              <span className="text-white/30">|</span>
              <button
                onClick={() => navigate('/forgot-password')}
                className="text-gray-400 hover:text-gray-300 transition-colors"
                disabled={loading}
              >
                忘记密码？
              </button>
            </div>
          </div>
        </div>

        {/* 提示信息 */}
        <div className="mt-6 text-center text-sm text-[#b5cbdb]">
          <p>默认密码：123</p>
          <p className="mt-1 text-xs opacity-70">如有问题请联系管理员</p>
        </div>
      </div>
    </div>
  )
}

export default LoginFixed
