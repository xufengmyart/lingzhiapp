/**
 * 科幻主题配置
 * 用于统一整个应用的科幻风格设计
 */

export const vrTheme = {
  // 背景渐变
  bgGradient: 'bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]',

  // 玻璃拟态
  glass: {
    bg: 'bg-[#091422]/40',
    blur: 'backdrop-blur-xl',
    border: 'border border-[#3e8bb6]/30',
    shadow: 'shadow-[0_0_30px_rgba(62,139,182,0.3)]',
  },

  // 主色调
  colors: {
    cyan: {
      DEFAULT: '[#3e8bb6]',
      hover: '[#b5cbdb]',
      gradient: 'from-[#3e8bb6] to-[#b5cbdb]',
    },
    purple: {
      DEFAULT: '[#b5cbdb]',
      hover: '[#22d3ee]',
      gradient: 'from-[#b5cbdb] to-[#22d3ee]',
    },
    pink: {
      DEFAULT: '[#22d3ee]',
      hover: '[#3e8bb6]',
      gradient: 'from-[#22d3ee] to-[#3e8bb6]',
    },
  },

  // 按钮样式
  button: {
    gradient: 'bg-gradient-to-r from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    gradientHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
    glow: 'shadow-[0_0_20px_rgba(62,139,182,0.5)]',
  },

  // 卡片样式
  card: {
    bg: 'bg-[#091422]/60',
    border: 'border border-[#3e8bb6]/20',
    hover: 'hover:bg-[#3e8bb6]/20 hover:border-[#b5cbdb]/30',
    glow: 'hover:shadow-[0_0_20px_rgba(62,139,182,0.3)]',
  },

  // 文本颜色
  text: {
    primary: 'text-white',
    secondary: 'text-[#b5cbdb]/80',
    accent: 'text-[#3e8bb6]',
    muted: 'text-[#b5cbdb]/50',
  },

  // 发光效果
  glow: {
    cyan: 'shadow-[0_0_20px_rgba(62,139,182,0.5)]',
    purple: 'shadow-[0_0_20px_rgba(181,203,219,0.5)]',
    pink: 'shadow-[0_0_20px_rgba(34,211,238,0.5)]',
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
    gradient: 'bg-gradient-to-r from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    track: 'bg-[#091422]/40',
  },
}

// 科幻风格的特色展示项
export const vrFeatures = [
  {
    icon: '🌐',
    title: '沉浸体验',
    subtitle: '全息交互',
    color: 'from-[#3e8bb6] to-[#b5cbdb]',
  },
  {
    icon: '⚡',
    title: '即时响应',
    subtitle: '秒级处理',
    color: 'from-[#b5cbdb] to-[#22d3ee]',
  },
  {
    icon: '🔒',
    title: '量子加密',
    subtitle: '安全可靠',
    color: 'from-[#22d3ee] to-[#3e8bb6]',
  },
]

// 科幻风格的统计卡片配置
export const vrCardStyles = {
  totalLingzhi: {
    icon: '📈',
    color: 'from-[#3e8bb6] to-[#b5cbdb]',
    glow: 'shadow-[0_0_20px_rgba(62,139,182,0.5)]',
  },
  todayCheckIn: {
    icon: '📅',
    color: 'from-[#b5cbdb] to-[#22d3ee]',
    glow: 'shadow-[0_0_20px_rgba(181,203,219,0.5)]',
  },
  milestone: {
    icon: '🎯',
    color: 'from-[#22d3ee] to-[#3e8bb6]',
    glow: 'shadow-[0_0_20px_rgba(34,211,238,0.5)]',
  },
  partner: {
    icon: '🏆',
    color: 'from-amber-400 to-amber-500',
    glow: 'shadow-[0_0_20px_rgba(251,191,36,0.5)]',
  },
}
