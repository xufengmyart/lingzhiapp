/**
 * VR沉浸式主题配置
 * 用于统一整个应用的VR风格设计
 */

export const vrTheme = {
  // 背景渐变
  bgGradient: 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900',

  // 玻璃拟态
  glass: {
    bg: 'bg-white/10',
    blur: 'backdrop-blur-xl',
    border: 'border border-white/20',
    shadow: 'shadow-[0_0_30px_rgba(168,85,247,0.3)]',
  },

  // 主色调
  colors: {
    cyan: {
      DEFAULT: 'cyan-400',
      hover: 'cyan-300',
      gradient: 'from-cyan-400 to-cyan-500',
    },
    purple: {
      DEFAULT: 'purple-400',
      hover: 'purple-300',
      gradient: 'from-purple-400 to-purple-500',
    },
    pink: {
      DEFAULT: 'pink-400',
      hover: 'pink-300',
      gradient: 'from-pink-400 to-pink-500',
    },
  },

  // 按钮样式
  button: {
    gradient: 'bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400',
    gradientHover: 'from-cyan-300 via-purple-300 to-pink-300',
    glow: 'shadow-[0_0_20px_rgba(168,85,247,0.5)]',
  },

  // 卡片样式
  card: {
    bg: 'bg-white/5',
    border: 'border border-white/10',
    hover: 'hover:bg-white/10 hover:border-white/20',
    glow: 'hover:shadow-[0_0_20px_rgba(168,85,247,0.3)]',
  },

  // 文本颜色
  text: {
    primary: 'text-white',
    secondary: 'text-gray-300',
    accent: 'text-cyan-400',
    muted: 'text-gray-500',
  },

  // 发光效果
  glow: {
    cyan: 'shadow-[0_0_20px_rgba(34,211,238,0.5)]',
    purple: 'shadow-[0_0_20px_rgba(168,85,247,0.5)]',
    pink: 'shadow-[0_0_20px_rgba(244,114,182,0.5)]',
  },

  // 动画
  animation: {
    float: 'animate-float',
    pulse: 'animate-pulse',
    fadeIn: 'animate-fade-in',
    slideIn: 'animate-slide-in',
  },

  // 进度条
  progress: {
    gradient: 'bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400',
    track: 'bg-white/10',
  },
}

// VR风格的特色展示项
export const vrFeatures = [
  {
    icon: '🌐',
    title: '沉浸体验',
    subtitle: '全息交互',
    color: 'from-cyan-400 to-cyan-500',
  },
  {
    icon: '⚡',
    title: '即时响应',
    subtitle: '秒级处理',
    color: 'from-purple-400 to-purple-500',
  },
  {
    icon: '🔒',
    title: '量子加密',
    subtitle: '安全可靠',
    color: 'from-pink-400 to-pink-500',
  },
]

// VR风格的统计卡片配置
export const vrCardStyles = {
  totalLingzhi: {
    icon: '📈',
    color: 'from-cyan-400 to-cyan-500',
    glow: 'shadow-[0_0_20px_rgba(34,211,238,0.5)]',
  },
  todayCheckIn: {
    icon: '📅',
    color: 'from-purple-400 to-purple-500',
    glow: 'shadow-[0_0_20px_rgba(168,85,247,0.5)]',
  },
  milestone: {
    icon: '🎯',
    color: 'from-pink-400 to-pink-500',
    glow: 'shadow-[0_0_20px_rgba(244,114,182,0.5)]',
  },
  partner: {
    icon: '🏆',
    color: 'from-amber-400 to-amber-500',
    glow: 'shadow-[0_0_20px_rgba(251,191,36,0.5)]',
  },
}
