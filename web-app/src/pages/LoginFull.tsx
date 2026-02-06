import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, ArrowRight, Sparkles, Heart, Star, RefreshCw, CheckCircle, User, MessageCircle, Eye, EyeOff, Globe, Zap, Shield } from 'lucide-react'

// VR情景式风格配置
const vrStyle = {
  bg: 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900',
  cardBg: 'bg-white/10 backdrop-blur-xl',
  buttonBg: 'from-cyan-500 via-purple-500 to-pink-500',
  buttonHover: 'from-cyan-400 via-purple-400 to-pink-400',
  accent: 'text-cyan-400',
  glow: 'shadow-[0_0_30px_rgba(168,85,247,0.3)]',
}

// VR特点配置（底部）
const vrFeatures = [
  { title: '沉浸', subtitle: '全息交互', icon: Globe },
  { title: '即时', subtitle: '秒级响应', icon: Zap },
  { title: '安全', subtitle: '量子加密', icon: Shield },
]

// 粒子系统
const ParticleSystem = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Array<{ x: number; y: number; vx: number; vy: number; size: number; alpha: number }>>([])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // 初始化粒子
    const particleCount = 150
    for (let i = 0; i < particleCount; i++) {
      particlesRef.current.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 0.5,
        alpha: Math.random() * 0.5 + 0.2,
      })
    }

    // 动画循环
    let animationId: number
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particlesRef.current.forEach((particle) => {
        // 更新位置
        particle.x += particle.vx
        particle.y += particle.vy

        // 边界检查
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1

        // 绘制粒子
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(168, 85, 247, ${particle.alpha})`
        ctx.fill()
      })

      // 绘制连接线
      particlesRef.current.forEach((p1, i) => {
        particlesRef.current.slice(i + 1).forEach((p2) => {
          const dx = p1.x - p2.x
          const dy = p1.y - p2.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 100) {
            ctx.beginPath()
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = `rgba(168, 85, 247, ${0.1 * (1 - distance / 100)})`
            ctx.stroke()
          }
        })
      })

      animationId = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none" />
}

// 星星组件
const Stars = () => {
  const starsRef = useRef<Array<{ id: number; top: string; left: string; size: number; duration: number; delay: number }>>([])

  useEffect(() => {
    starsRef.current = Array.from({ length: 100 }, (_, i) => ({
      id: i,
      top: `${Math.random() * 100}%`,
      left: `${Math.random() * 100}%`,
      size: Math.random() * 3 + 1,
      duration: Math.random() * 2 + 1,
      delay: Math.random() * 2,
    }))
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {starsRef.current.map((star) => (
        <div
          key={star.id}
          className="absolute bg-white rounded-full"
          style={{
            top: star.top,
            left: star.left,
            width: `${star.size}px`,
            height: `${star.size}px`,
            opacity: 0,
            animation: `twinkle ${star.duration}s ease-in-out infinite ${star.delay}s`,
          }}
        />
      ))}
    </div>
  )
}

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
      setFeatureIndex((prev) => (prev + 1) % vrFeatures.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // 验证输入
    if (!username.trim() || !password.trim()) {
      setError('请输入用户名和密码')
      setLoading(false)
      return
    }

    try {
      const success = await login(username, password)
      if (success) {
        navigate('/dashboard')
      } else {
        setError('登录失败，请检查用户名和密码')
        setLoading(false)
      }
    } catch (err: any) {
      console.error('登录错误:', err)
      
      // 根据错误类型显示不同的提示
      if (err.response?.status === 401) {
        setError('用户名或密码错误，请重试')
      } else if (err.response?.status === 403) {
        setError('账号已被禁用，请联系管理员')
      } else if (err.response?.status === 429) {
        setError('登录过于频繁，请稍后再试')
      } else if (err.response?.status === 500) {
        setError('服务器错误，请稍后重试或联系客服')
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        setError('网络连接失败，请检查网络后重试')
      } else if (err.response?.data?.message) {
        setError(err.response.data.message)
      } else {
        setError('登录失败，请稍后重试')
      }
      setLoading(false)
    }
  }

  const handleWechatLogin = () => {
    window.location.href = '/api/wechat/login'
  }

  const currentFeature = vrFeatures[featureIndex]
  const FeatureIcon = currentFeature.icon

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center px-4 py-6 relative overflow-hidden ${vrStyle.bg}`}>
      {/* VR背景效果 */}
      <ParticleSystem />
      <Stars />

      {/* VR光晕装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/10 rounded-full blur-[200px]"></div>
      </div>

      {/* 登录卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-8 animate-float">
          <div className="inline-flex items-center space-x-3 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500 blur-xl animate-pulse"></div>
              <Sparkles className="w-6 h-6 text-cyan-400 relative z-10" />
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-purple-500 blur-xl animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <Heart className="w-6 h-6 text-purple-400 relative z-10" />
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-pink-500 blur-xl animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              <Star className="w-6 h-6 text-pink-400 relative z-10" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white whitespace-nowrap drop-shadow-lg">
            进入灵值元宇宙
          </h1>
          <p className="text-sm text-cyan-300 mt-2 drop-shadow-md">
            沉浸体验·全息交互·无限可能
          </p>
        </div>

        {/* 登录表单 - 玻璃拟态 */}
        <div className={`${vrStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/20 backdrop-blur-xl ${vrStyle.glow}`}>
          <form onSubmit={handleLoginSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-cyan-300 mb-2">用户名</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-cyan-400" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入用户名"
                  required
                />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-cyan-300 mb-2">密码</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-cyan-400" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-10 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入密码"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              </div>
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg px-4 py-2 text-red-300 text-sm backdrop-blur-sm">
                {error}
              </div>
            )}

            {/* 登录按钮组 */}
            <div className="grid grid-cols-2 gap-4 pt-2">
              <button
                type="submit"
                disabled={loading}
                className={`relative py-3 px-4 bg-gradient-to-r ${vrStyle.buttonBg} text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 overflow-hidden group ${loading ? 'opacity-70' : ''}`}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Lock className="w-5 h-5" />}
                <span className="ml-2 text-sm">登录</span>
              </button>
              <button
                type="button"
                onClick={handleWechatLogin}
                className="relative py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <MessageCircle className="w-5 h-5" />
                <span className="ml-2 text-sm">微信</span>
              </button>
            </div>
          </form>

          {/* 其他选项 */}
          <div className="mt-6 pt-4 border-t border-white/10">
            <div className="flex justify-center space-x-6 text-sm">
              <button
                onClick={() => navigate('/register-full')}
                className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
              >
                注册账号
              </button>
              <span className="text-white/30">|</span>
              <button
                onClick={() => navigate('/forgot-password')}
                className="text-gray-400 hover:text-gray-300 transition-colors"
              >
                忘记密码？
              </button>
            </div>
          </div>
        </div>

        {/* VR特点 - 底部 */}
        <div className="mt-6">
          <div className={`${vrStyle.cardBg} rounded-2xl p-4 shadow-lg border border-white/20 backdrop-blur-xl ${vrStyle.glow} overflow-hidden relative`}>
            <div className="relative z-10 flex items-center justify-around">
              {vrFeatures.map((feature, idx) => (
                <div key={idx} className={`flex flex-col items-center transition-all duration-500 ${featureIndex === idx ? 'opacity-100 transform scale-110' : 'opacity-50'}`}>
                  <div className={`relative mb-2`}>
                    <div className={`absolute inset-0 ${vrStyle.buttonBg} rounded-full blur-lg opacity-50`}></div>
                    <div className={`w-12 h-12 ${vrStyle.buttonBg} rounded-full flex items-center justify-center relative z-10 shadow-lg`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className={`text-xl font-bold text-white drop-shadow-lg`}>{feature.title}</div>
                  <div className="text-xs text-cyan-300">{feature.subtitle}</div>
                </div>
              ))}
            </div>
            {/* 光扫效果 */}
            <div className="absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-transparent via-white/30 to-transparent transition-all duration-300" style={{ left: `${featureIndex * 33.33}%` }}></div>
          </div>
        </div>
      </div>

      {/* 添加自定义动画样式 */}
      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        @keyframes twinkle {
          0%, 100% {
            opacity: 0;
            transform: scale(0.5);
          }
          50% {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}

export default LoginFull
