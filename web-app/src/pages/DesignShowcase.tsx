import { useState } from 'react'
import { RefreshCw, Sparkles, Heart, Star, CheckCircle, ArrowRight } from 'lucide-react'

// 梦幻式设计风格配置
const dreamStyles = {
  dawn: {
    bg: 'bg-gradient-to-br from-pink-100 via-purple-50 to-orange-50',
    cardBg: 'bg-white/80 backdrop-blur-lg',
    buttonBg: 'from-pink-500 to-orange-400',
    buttonHover: 'from-pink-600 to-orange-500',
    accent: 'text-pink-600',
    decorColors: ['bg-pink-300', 'bg-purple-300', 'bg-orange-300'],
    name: '晨曦之梦',
    description: '温暖、活力、希望',
    icon: '🌅',
  },
  galaxy: {
    bg: 'bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900',
    cardBg: 'bg-white/90 backdrop-blur-lg',
    buttonBg: 'from-indigo-500 to-purple-500',
    buttonHover: 'from-indigo-600 to-purple-600',
    accent: 'text-indigo-600',
    decorColors: ['bg-indigo-400', 'bg-purple-400', 'bg-blue-400'],
    name: '星空梦境',
    description: '深邃、神秘、宁静',
    icon: '🌌',
  },
  forest: {
    bg: 'bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50',
    cardBg: 'bg-white/85 backdrop-blur-lg',
    buttonBg: 'from-emerald-500 to-teal-500',
    buttonHover: 'from-emerald-600 to-teal-600',
    accent: 'text-emerald-600',
    decorColors: ['bg-emerald-300', 'bg-teal-300', 'bg-cyan-300'],
    name: '森林之梦',
    description: '自然、清新、放松',
    icon: '🌿',
  },
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
}

const DesignShowcase = () => {
  const [styleKey, setStyleKey] = useState<keyof typeof dreamStyles>('dawn')
  const currentStyle = dreamStyles[styleKey]

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
          <h1 className="text-4xl font-bold text-gray-800 mb-2">梦幻式设计风格展示</h1>
          <p className="text-gray-600">为灵值生态园精心打造的4种梦幻UI风格</p>
        </div>

        {/* 风格选择器 */}
        <div className="mb-12">
          <div className={`${currentStyle.cardBg} rounded-2xl shadow-xl p-6 border border-white/50 backdrop-blur-xl max-w-4xl mx-auto`}>
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <RefreshCw className="w-5 h-5" />
              <span>选择预览风格</span>
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(dreamStyles).map(([key, style]) => (
                <button
                  key={key}
                  onClick={() => setStyleKey(key as keyof typeof dreamStyles)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    styleKey === key
                      ? 'border-primary-500 bg-primary-50 shadow-lg'
                      : 'border-transparent hover:border-gray-300'
                  }`}
                >
                  <div className={`w-full h-16 rounded-lg ${style.bg} mb-2 flex items-center justify-center text-2xl`}>
                    {style.icon}
                  </div>
                  <div className="font-semibold text-gray-800">{style.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{style.description}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 登录页面预览 */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">登录页面预览</h2>
          <div className="max-w-md mx-auto">
            <div className={`${currentStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
              {/* 顶部 Logo */}
              <div className="text-center mb-6">
                <div className={`relative inline-block mb-3`}>
                  <div className={`w-16 h-16 bg-gradient-to-br ${currentStyle.buttonBg} rounded-xl flex items-center justify-center mx-auto transform rotate-3 hover:rotate-6 transition-transform duration-300 shadow-xl`}>
                    <span className="text-2xl">{currentStyle.icon}</span>
                  </div>
                  <div className={`absolute inset-0 bg-gradient-to-br ${currentStyle.buttonBg} rounded-xl blur-xl opacity-50`}></div>
                </div>
                <div className="text-xl font-bold text-gray-800">
                  {currentStyle.name}
                </div>
                <div className={`text-sm ${currentStyle.accent} font-medium mt-1`}>
                  {currentStyle.description}
                </div>
              </div>

              {/* 模拟表单 */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    用户名 / 邮箱
                  </label>
                  <div className="relative">
                    <div className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${currentStyle.accent}`}>👤</div>
                    <div className={`w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 bg-white/50 backdrop-blur text-gray-400`}>
                      示例：user@example.com
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    密码
                  </label>
                  <div className="relative">
                    <div className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${currentStyle.accent}`}>🔒</div>
                    <div className={`w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 bg-white/50 backdrop-blur text-gray-400`}>
                      ••••••••
                    </div>
                  </div>
                </div>

                <button
                  className={`w-full bg-gradient-to-r ${currentStyle.buttonBg} text-white py-3 rounded-xl font-semibold hover:${currentStyle.buttonHover} transition-all shadow-lg transform hover:scale-[1.02] flex items-center justify-center space-x-2`}
                >
                  <span>登录</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>

              {/* 微信登录 */}
              <div className="mt-4">
                <div className="flex items-center mb-4">
                  <div className="flex-1 border-t border-gray-200"></div>
                  <div className="px-4 text-sm text-gray-500">或</div>
                  <div className="flex-1 border-t border-gray-200"></div>
                </div>
                <button className="w-full bg-[#07c160] text-white py-3 rounded-xl font-semibold hover:bg-[#06ad56] transition-all flex items-center justify-center space-x-2 shadow-lg">
                  <span>💬</span>
                  <span>微信登录</span>
                </button>
              </div>

              <div className="mt-6 text-center space-y-2">
                <a href="#" className={`text-sm ${currentStyle.accent} hover:underline block`}>
                  忘记密码？
                </a>
                <p className="text-sm text-gray-600">
                  还没有账户？{' '}
                  <a href="#" className={`font-semibold ${currentStyle.accent} hover:underline`}>
                    立即创建
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 特性说明 */}
        <div className="max-w-4xl mx-auto">
          <div className={`${currentStyle.cardBg} rounded-2xl shadow-xl p-8 border border-white/50 backdrop-blur-xl`}>
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center space-x-2">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <span>设计特性</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">✨</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">梦幻毛玻璃效果</h3>
                  <p className="text-sm text-gray-600 mt-1">使用 backdrop-blur 营造梦幻感</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">🎨</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">渐变色彩搭配</h3>
                  <p className="text-sm text-gray-600 mt-1">精心调配的渐变配色方案</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">🌟</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">动态装饰元素</h3>
                  <p className="text-sm text-gray-600 mt-1">飘动的星星和浮动装饰块</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">💫</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">平滑交互动画</h3>
                  <p className="text-sm text-gray-600 mt-1">悬停缩放和平滑过渡效果</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">💚</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">舒适性优先</h3>
                  <p className="text-sm text-gray-600 mt-1">柔和色彩，保护用户视力</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`w-10 h-10 ${currentStyle.buttonBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <span className="text-white">🎯</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">90%满意度目标</h3>
                  <p className="text-sm text-gray-600 mt-1">精心设计，确保绝大多数用户舒适</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 返回按钮 */}
        <div className="text-center mt-12">
          <a
            href="/"
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowRight className="w-5 h-5 rotate-180" />
            <span>返回首页</span>
          </a>
        </div>
      </div>
    </div>
  )
}

export default DesignShowcase
