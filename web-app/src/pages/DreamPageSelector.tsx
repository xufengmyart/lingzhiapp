import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Heart, Star, ArrowRight, User, Lock } from 'lucide-react'

// 梦幻式设计风格配置
const dreamStyles = {
  aurora: {
    bg: 'bg-gradient-to-br from-rose-100 via-purple-100 to-blue-100',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-rose-500 to-purple-500',
    buttonHover: 'from-rose-600 to-purple-600',
    accent: 'text-rose-600',
    decorColors: ['bg-rose-300', 'bg-purple-300', 'bg-blue-300'],
    name: '极光之梦',
    description: '绚丽、梦幻、多彩',
    icon: '🌈',
  },
  sakura: {
    bg: 'bg-gradient-to-br from-pink-50 via-rose-50 to-fuchsia-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-pink-400 to-fuchsia-400',
    buttonHover: 'from-pink-500 to-fuchsia-500',
    accent: 'text-pink-500',
    decorColors: ['bg-pink-200', 'bg-rose-200', 'bg-fuchsia-200'],
    name: '樱花之梦',
    description: '浪漫、柔美、优雅',
    icon: '🌸',
  },
  ocean: {
    bg: 'bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-cyan-500 to-blue-500',
    buttonHover: 'from-cyan-600 to-blue-600',
    accent: 'text-cyan-600',
    decorColors: ['bg-cyan-300', 'bg-blue-300', 'bg-indigo-300'],
    name: '海洋之梦',
    description: '宁静、深邃、自由',
    icon: '🌊',
  },
  ecosystem: {
    bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-amber-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-emerald-500 to-amber-500',
    buttonHover: 'from-emerald-600 to-amber-600',
    accent: 'text-emerald-600',
    decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-amber-300'],
    name: '生态之梦',
    description: '资源匹配、价值生态',
    icon: '🌿',
  },
}

const DreamPageSelector = () => {
  const navigate = useNavigate()
  const [selectedStyle, setSelectedStyle] = useState<keyof typeof dreamStyles>('ecosystem')
  const currentStyle = dreamStyles[selectedStyle]

  const handleGoToPage = (page: 'login' | 'register') => {
    navigate(`/${page}-full`)
  }

  return (
    <div className={`min-h-screen relative overflow-hidden ${currentStyle.bg}`}>

      {/* 装饰性背景元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* 顶部装饰 */}
        <div className={`absolute top-20 left-20 w-32 h-32 ${currentStyle.decorColors[0]} rounded-full blur-3xl opacity-30 animate-pulse`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${currentStyle.decorColors[1]} rounded-full blur-3xl opacity-30 animate-pulse delay-1000`}></div>

        {/* 中部装饰 */}
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${currentStyle.decorColors[2]} rounded-full blur-3xl opacity-20 animate-pulse delay-500`}></div>

        {/* 底部装饰 */}
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

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* 头部 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 mb-4">
            <Sparkles className="w-6 h-6 text-yellow-500 animate-pulse" />
            <Heart className="w-6 h-6 text-red-400 animate-pulse delay-300" />
            <Star className="w-6 h-6 text-purple-500 animate-pulse delay-700" />
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">选择你的梦幻风格</h1>
          <p className="text-gray-600">挑选你喜欢的风格，开启梦幻之旅</p>
        </div>

        {/* 风格选择器 */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className={`${currentStyle.cardBg} rounded-2xl shadow-xl p-6 border border-white/50 backdrop-blur-xl`}>
            <h2 className="text-xl font-semibold text-gray-800 mb-4 text-center">
              4种梦幻风格任你选择
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(dreamStyles).map(([key, style]) => (
                <button
                  key={key}
                  onClick={() => setSelectedStyle(key as keyof typeof dreamStyles)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedStyle === key
                      ? 'border-primary-500 bg-primary-50 shadow-lg transform scale-105'
                      : 'border-transparent hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className={`w-full h-20 rounded-lg ${style.bg} mb-2 flex items-center justify-center text-3xl`}>
                    {style.icon}
                  </div>
                  <div className="font-semibold text-gray-800 text-sm">{style.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{style.description}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 页面选择 */}
        <div className="max-w-4xl mx-auto">
          <div className={`${currentStyle.cardBg} rounded-2xl shadow-xl p-8 border border-white/50 backdrop-blur-xl`}>
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              你要做什么？
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 登录卡片 */}
              <button
                onClick={() => handleGoToPage('login')}
                className="group relative p-8 rounded-2xl border-2 border-gray-200 hover:border-pink-400 transition-all hover:shadow-xl hover:-translate-y-1"
              >
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ArrowRight className="w-6 h-6 text-pink-500" />
                </div>
                <div className={`w-16 h-16 ${currentStyle.buttonBg} rounded-2xl flex items-center justify-center mb-4 mx-auto`}>
                  <Lock className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">登录账户</h3>
                <p className="text-gray-600 text-sm">
                  已有账户？登录进入你的梦幻空间
                </p>
                <div className={`mt-4 text-sm ${currentStyle.accent} font-semibold`}>
                  进入登录 →
                </div>
              </button>

              {/* 注册卡片 */}
              <button
                onClick={() => handleGoToPage('register')}
                className="group relative p-8 rounded-2xl border-2 border-gray-200 hover:border-pink-400 transition-all hover:shadow-xl hover:-translate-y-1"
              >
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ArrowRight className="w-6 h-6 text-pink-500" />
                </div>
                <div className={`w-16 h-16 ${currentStyle.buttonBg} rounded-2xl flex items-center justify-center mb-4 mx-auto`}>
                  <User className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">创建账户</h3>
                <p className="text-gray-600 text-sm">
                  新用户？注册开启你的梦幻之旅
                </p>
                <div className={`mt-4 text-sm ${currentStyle.accent} font-semibold`}>
                  开始注册 →
                </div>
              </button>
            </div>

            {/* 提示 */}
            <div className="mt-8 text-center">
              <p className="text-sm text-gray-500">
                💡 提示：选择风格后，你可以在登录/注册页面随时切换其他风格
              </p>
            </div>
          </div>
        </div>

        {/* 返回传统版 */}
        <div className="text-center mt-8">
          <a
            href="/login"
            className="text-sm text-gray-600 hover:text-gray-800 transition-colors inline-flex items-center space-x-2"
          >
            <span>返回传统版登录页面</span>
          </a>
        </div>
      </div>
    </div>
  )
}

export default DreamPageSelector
