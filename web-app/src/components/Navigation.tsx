import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, MessageSquare, TrendingUp, Award, User, LogOut, Wallet, Sparkles, Globe, Zap, Shield, HelpCircle, MessageCircle } from 'lucide-react'
import { vrTheme } from '../utils/vr-theme'

const Navigation = () => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', icon: Home, label: '首页', glow: 'shadow-[0_0_15px_rgba(34,211,238,0.3)]' },
    { path: '/chat', icon: MessageSquare, label: '智能对话', glow: 'shadow-[0_0_15px_rgba(168,85,247,0.3)]' },
    { path: '/economy', icon: TrendingUp, label: '经济模型', glow: 'shadow-[0_0_15px_rgba(244,114,182,0.3)]' },
    { path: '/partner', icon: Award, label: '合伙人', glow: 'shadow-[0_0_15px_rgba(251,191,36,0.3)]' },
    { path: '/recharge', icon: Wallet, label: '购买灵值', glow: 'shadow-[0_0_15px_rgba(52,211,153,0.3)]' },
    { path: '/profile', icon: User, label: '个人中心', glow: 'shadow-[0_0_15px_rgba(239,68,68,0.3)]' },
  ]

  const navItemsRight = [
    { path: '/value-guide', icon: HelpCircle, label: '价值指南', glow: 'shadow-[0_0_15px_rgba(34,211,238,0.3)]' },
    { path: '/feedback', icon: MessageCircle, label: '反馈', glow: 'shadow-[0_0_15px_rgba(168,85,247,0.3)]' },
  ]

  const isActive = (path: string) => location.pathname === path

  const handleLogout = () => {
    logout()
  }

  return (
    <nav className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} sticky top-0 z-[999999]`}>
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            to="/dashboard"
            className="flex items-center space-x-3 group hover:opacity-90 transition-opacity"
          >
            <div className={`w-10 h-10 ${vrTheme.button.gradient} rounded-lg flex items-center justify-center ${vrTheme.button.glow} transition-all group-hover:scale-110`}>
              <Wallet className="w-5 h-5 text-white" />
              <div className="absolute inset-0 bg-white/20 rounded-lg animate-pulse pointer-events-none"></div>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                灵值元宇宙
              </span>
            </div>
          </Link>

          {/* 导航链接 */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all hover:opacity-90 ${
                  isActive(item.path)
                    ? `bg-white/20 text-white ${item.glow}`
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="no-wrap">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* 帮助和反馈 */}
          <div className="hidden md:flex items-center space-x-1 border-l border-white/10 pl-4">
            {navItemsRight.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all hover:opacity-90 ${
                  isActive(item.path)
                    ? `bg-white/20 text-white ${item.glow}`
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="text-sm no-wrap">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* 用户信息和登出 */}
          <div className="flex items-center space-x-4">
            {user && (
              <div className={`hidden sm:flex items-center space-x-2 ${vrTheme.button.gradient} ${vrTheme.button.glow} text-white px-4 py-2 rounded-full`}>
                <Wallet className="w-4 h-4" />
                <span className="font-semibold no-wrap">{user.totalLingzhi} 灵值</span>
                <span className="text-xs opacity-80 no-wrap">({(user.totalLingzhi * 0.1).toFixed(1)}元)</span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-pink-400 hover:bg-white/10 rounded-lg transition-all hover:text-pink-300"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline no-wrap">退出</span>
            </button>
          </div>
        </div>

        {/* 移动端导航 */}
        <div className="md:hidden flex justify-around py-3 border-t border-white/10">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center space-y-1 px-4 py-1 rounded-lg transition-all hover:opacity-90 ${
                isActive(item.path) ? 'text-cyan-400' : 'text-gray-400'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-xs">{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navigation
