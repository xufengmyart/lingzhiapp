/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 科技蓝配色方案
        'tech-primary': '#00C3FF',   // 高亮主蓝
        'tech-secondary': '#47D1FF', // 半透浅蓝
        'tech-accent': '#00E0FF',    // 能量光效蓝
        'tech-border': '#007ACC',    // 深邃蓝边
        'tech-dark-bg': '#0A0D18',   // 深邃黑
        'tech-light-bg': '#121A2F',  // 深灰蓝调
        'tech-card-bg': '#2D3A59',   // 深灰
        'tech-text-primary': '#FFFFFF',    // 纯白
        'tech-text-secondary': '#B4C7E7',  // 浅灰蓝
        'tech-warm-orange': '#FF9E7A',     // 暖橙粉
        'tech-warm-yellow': '#FFDC9E',     // 浅暖黄

        // 旧配色保持兼容
        primary: {
          50: '#fef3f2',
          100: '#fee4e2',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',
          600: '#e11d48',
          700: '#be123c',
          800: '#9f1239',
          900: '#881337',
        },
        secondary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-slow': 'bounce 2s infinite',
        'gradient-x': 'gradientX 3s ease infinite',
        'shake': 'shake 0.5s ease-in-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        gradientX: {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-5px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(5px)' },
        },
      },
    },
  },
  plugins: [],
}
