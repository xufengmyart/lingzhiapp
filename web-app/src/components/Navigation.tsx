import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, MessageSquare, TrendingUp, Award, User, LogOut, Wallet, Sparkles, HelpCircle, MessageCircle } from 'lucide-react'

const Navigation = () => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', icon: Home, label: '首页' },
    { path: '/chat', icon: MessageSquare, label: '智能对话' },
    { path: '/economy', icon: TrendingUp, label: '经济模型' },
    { path: '/partner', icon: Award, label: '合伙人' },
    { path: '/recharge', icon: Wallet, label: '购买灵值' },
    { path: '/profile', icon: User, label: '个人中心' },
  ]

  const navItemsRight = [
    { path: '/value-guide', icon: HelpCircle, label: '价值指南' },
    { path: '/feedback', icon: MessageCircle, label: '反馈' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="fixed top-0 left-0 right-0 bg-[#2a4559] border-b border-[#b5cbdb]/30 shadow-2xl z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-r from-[#3e8bb6] to-[#b5cbdb] rounded-lg flex items-center justify-center shadow-lg">
              <Wallet className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-[#b5cbdb]" />
              <span className="text-xl font-bold bg-gradient-to-r from-[#3e8bb6] via-[#b5cbdb] to-[#3e8bb6] bg-clip-text text-transparent">
                灵值生态园
              </span>
            </div>
          </Link>

          {/* 导航链接 */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all hover:bg-[#3e8bb6]/20 ${
                    isActive(item.path) ? 'bg-[#3e8bb6]/30 text-white' : 'text-[#b5cbdb] hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="whitespace-nowrap">{item.label}</span>
                </Link>
              )
            })}
          </div>

          {/* 帮助和反馈 */}
          <div className="hidden md:flex items-center space-x-1 border-l border-[#b5cbdb]/10 pl-4">
            {navItemsRight.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all hover:bg-[#3e8bb6]/20 ${
                    isActive(item.path) ? 'bg-[#3e8bb6]/30 text-white' : 'text-[#b5cbdb] hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm whitespace-nowrap">{item.label}</span>
                </Link>
              )
            })}
          </div>

          {/* 用户信息和登出 */}
          <div className="flex items-center space-x-4">
            {user && (
              <div className="hidden sm:flex items-center space-x-2 bg-gradient-to-r from-[#3e8bb6] to-[#b5cbdb] text-white px-4 py-2 rounded-full shadow-lg">
                <Wallet className="w-4 h-4" />
                <span className="font-semibold whitespace-nowrap">{user.totalLingzhi} 灵值</span>
                <span className="text-xs opacity-80 whitespace-nowrap">({(user.totalLingzhi * 0.1).toFixed(1)}元)</span>
              </div>
            )}
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 text-[#b5cbdb] hover:bg-[#3e8bb6]/20 rounded-lg transition-all hover:text-white"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline whitespace-nowrap">退出</span>
            </button>
          </div>
        </div>

        {/* 移动端导航 */}
        <div className="md:hidden flex justify-around py-3 border-t border-[#b5cbdb]/10">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center space-y-1 px-4 py-1 rounded-lg transition-all ${
                  isActive(item.path) ? 'text-[#3e8bb6]' : 'text-[#b5cbdb]/60'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

export default Navigation
