/**
 * 增强版对话界面样式配置
 * 提升视觉美感和科技感
 */

export const chatTheme = {
  // 消息气泡样式
  bubble: {
    // 用户消息气泡
    user: {
      bg: 'bg-gradient-to-br from-[#00C3FF]/20 via-[#47D1FF]/30 to-[#00E0FF]/20',
      border: 'border border-[#00C3FF]/40',
      shadow: 'shadow-[0_4px_20px_rgba(0,195,255,0.3)]',
      glow: 'hover:shadow-[0_0_30px_rgba(0,195,255,0.5)]',
      text: 'text-white',
    },
    // 助手消息气泡
    assistant: {
      bg: 'bg-gradient-to-br from-[#2D3A59]/60 via-[#1E283D]/70 to-[#2D3A59]/60',
      border: 'border border-[#47D1FF]/20',
      shadow: 'shadow-[0_4px_20px_rgba(0,0,0,0.3)]',
      glow: 'hover:shadow-[0_0_20px_rgba(71,209,255,0.2)]',
      text: 'text-[#B4C7E7]',
    },
    // 思考过程气泡
    thinking: {
      bg: 'bg-gradient-to-br from-purple-500/10 via-purple-600/15 to-purple-500/10',
      border: 'border border-purple-400/40',
      shadow: 'shadow-[0_4px_20px_rgba(168,85,247,0.2)]',
      glow: 'shadow-[0_0_20px_rgba(168,85,247,0.3)]',
      text: 'text-purple-200',
    },
    // 错误消息气泡
    error: {
      bg: 'bg-gradient-to-br from-red-500/20 via-red-600/25 to-red-500/20',
      border: 'border border-red-400/40',
      shadow: 'shadow-[0_4px_20px_rgba(239,68,68,0.2)]',
      text: 'text-red-200',
    },
  },

  // 头像样式
  avatar: {
    // 用户头像
    user: {
      bg: 'bg-gradient-to-br from-[#00C3FF] via-[#47D1FF] to-[#00E0FF]',
      shadow: 'shadow-[0_0_20px_rgba(0,195,255,0.6)]',
      ring: 'ring-2 ring-[#00C3FF]/50',
    },
    // 助手头像
    assistant: {
      bg: 'bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700',
      shadow: 'shadow-[0_0_20px_rgba(168,85,247,0.6)]',
      ring: 'ring-2 ring-purple-500/50',
      pulse: 'animate-pulse-glow',
    },
  },

  // 加载动画
  loading: {
    dots: [
      'bg-[#00C3FF]',
      'bg-[#47D1FF]',
      'bg-[#00E0FF]',
    ],
    glow: 'shadow-[0_0_15px_rgba(0,195,255,0.5)]',
  },

  // 输入框样式
  input: {
    bg: 'bg-[#2D3A59]/40',
    border: 'border border-[#007ACC]/30',
    focus: 'focus:border-[#00C3FF]/60 focus:shadow-[0_0_20px_rgba(0,195,255,0.3)]',
    placeholder: 'text-[#B4C7E7]/50',
    text: 'text-white',
  },

  // 深度思考开关
  thinkingToggle: {
    active: 'bg-gradient-to-r from-cyan-500 to-cyan-600',
    inactive: 'bg-[#2D3A59]/60',
    thumb: 'bg-white',
    glow: 'shadow-[0_0_20px_rgba(0,195,255,0.5)]',
  },

  // 反馈按钮
  feedback: {
    bg: 'bg-[#2D3A59]/40',
    hover: 'hover:bg-[#00C3FF]/20',
    border: 'border border-[#007ACC]/20',
    text: 'text-[#B4C7E7]/70',
    hoverText: 'hover:text-[#00C3FF]',
  },

  // 动画效果
  animations: {
    messageIn: 'animate-message-slide-in',
    typingIndicator: 'animate-typing',
    thinkingGlow: 'animate-thinking-glow',
  },
}

// 动画关键帧（需要添加到全局CSS）
export const animationKeyframes = `
@keyframes message-slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

@keyframes thinking-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(168, 85, 247, 0.5);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
  }
  50% {
    box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
  }
}

.animate-message-slide-in {
  animation: message-slide-in 0.3s ease-out;
}

.animate-typing {
  animation: typing 1.4s ease-in-out infinite;
}

.animate-thinking-glow {
  animation: thinking-glow 2s ease-in-out infinite;
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
`
