/**
 * 科幻主题配置 - 科技蓝配色方案
 * 用于统一整个应用的科幻风格设计
 */

export const vrTheme = {
  // 背景渐变 - 科技蓝
  bgGradient: 'bg-gradient-to-br from-[#0A0D18] via-[#121A2F]/40 to-[#0A0D18]',

  // 玻璃拟态
  glass: {
    bg: 'bg-[#121A2F]/40',
    blur: 'backdrop-blur-xl',
    border: 'border border-[#00C3FF]/30',
    shadow: 'shadow-[0_0_30px_rgba(0,195,255,0.3)]',
  },

  // 主色调 - 科技蓝
  colors: {
    primary: {
      DEFAULT: '[#00C3FF]',   // 高亮主蓝
      hover: '[#00E0FF]',     // 能量光效蓝
      gradient: 'from-[#00C3FF] to-[#00E0FF]',
    },
    secondary: {
      DEFAULT: '[#47D1FF]',   // 半透浅蓝
      hover: '[#00E0FF]',     // 能量光效蓝
      gradient: 'from-[#47D1FF] to-[#00E0FF]',
    },
    accent: {
      DEFAULT: '[#00E0FF]',   // 能量光效蓝
      hover: '[#00C3FF]',     // 高亮主蓝
      gradient: 'from-[#00E0FF] to-[#00C3FF]',
    },
    border: {
      DEFAULT: '[#007ACC]',   // 深邃蓝边
      hover: '[#00C3FF]',     // 高亮主蓝
    },
    background: {
      dark: '[#0A0D18]',      // 深邃黑
      light: '[#121A2F]',     // 深灰蓝调
      card: '[#2D3A59]',      // 深灰
    },
    text: {
      primary: '[#FFFFFF]',       // 纯白
      secondary: '[#B4C7E7]',     // 浅灰蓝
      muted: '[#B4C7E7]/50',      // 浅灰蓝半透明
    },
    warm: {
      orange: '[#FF9E7A]',    // 暖橙粉
      yellow: '[#FFDC9E]',    // 浅暖黄
    },
  },

  // 按钮样式
  button: {
    gradient: 'bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00E0FF]',
    gradientHover: 'from-[#47D1FF] via-[#00E0FF] to-[#00C3FF]',
    glow: 'shadow-[0_0_20px_rgba(0,195,255,0.5)]',
  },

  // 卡片样式
  card: {
    bg: 'bg-[#2D3A59]/60',
    border: 'border border-[#007ACC]/20',
    hover: 'hover:bg-[#00C3FF]/20 hover:border-[#47D1FF]/30',
    glow: 'hover:shadow-[0_0_20px_rgba(0,195,255,0.3)]',
  },

  // 文本颜色
  text: {
    primary: 'text-[#FFFFFF]',
    secondary: 'text-[#B4C7E7]/80',
    accent: 'text-[#00C3FF]',
    muted: 'text-[#B4C7E7]/50',
  },

  // 发光效果
  glow: {
    cyan: 'shadow-[0_0_20px_rgba(0,195,255,0.5)]',
    light: 'shadow-[0_0_20px_rgba(71,209,255,0.5)]',
    energy: 'shadow-[0_0_20px_rgba(0,224,255,0.5)]',
    border: 'shadow-[0_0_20px_rgba(0,122,204,0.5)]',
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
    gradient: 'bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00E0FF]',
    track: 'bg-[#2D3A59]/40',
  },
}

// 科幻风格的特色展示项
export const vrFeatures = [
  {
    icon: '🌐',
    title: '沉浸体验',
    subtitle: '全息交互',
    color: 'from-[#00C3FF] to-[#47D1FF]',
  },
  {
    icon: '⚡',
    title: '即时响应',
    subtitle: '秒级处理',
    color: 'from-[#47D1FF] to-[#00E0FF]',
  },
  {
    icon: '🔒',
    title: '量子加密',
    subtitle: '安全可靠',
    color: 'from-[#00E0FF] to-[#00C3FF]',
  },
]

// 科幻风格的统计卡片配置
export const vrCardStyles = {
  total_lingzhi: {
    icon: '📈',
    color: 'from-[#00C3FF] to-[#47D1FF]',
    glow: 'shadow-[0_0_20px_rgba(0,195,255,0.5)]',
  },
  todayCheckIn: {
    icon: '📅',
    color: 'from-[#47D1FF] to-[#00E0FF]',
    glow: 'shadow-[0_0_20px_rgba(71,209,255,0.5)]',
  },
  milestone: {
    icon: '🎯',
    color: 'from-[#00E0FF] to-[#00C3FF]',
    glow: 'shadow-[0_0_20px_rgba(0,224,255,0.5)]',
  },
  partner: {
    icon: '🏆',
    color: 'from-[#FF9E7A] to-[#FFDC9E]',
    glow: 'shadow-[0_0_20px_rgba(255,158,122,0.5)]',
  },
}
