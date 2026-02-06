import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, MessageSquare, TrendingUp, Award, User, LogOut, Wallet } from 'lucide-react'

const Navigation = () => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: '首页' },
    { path: '/chat', icon: MessageSquare, label: '智能对话' },
    { path: '/economy', icon: TrendingUp, label: '经济模型' },
    { path: '/partner', icon: Award, label: '合伙人' },
    { path: '/recharge', icon: Wallet, label: '购买灵值' },
    { path: '/profile', icon: User, label: '个人中心' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <Wallet className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent no-wrap">
              灵值生态园
            </span>
          </Link>

          {/* 导航链接 */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isActive(item.path)
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="no-wrap">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* 用户信息和登出 */}
          <div className="flex items-center space-x-4">
            {user && (
              <div className="hidden sm:flex items-center space-x-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-4 py-2 rounded-full">
                <Wallet className="w-4 h-4" />
                <span className="font-semibold no-wrap">{user.totalLingzhi} 灵值</span>
                <span className="text-xs opacity-80 no-wrap">({(user.totalLingzhi * 0.1).toFixed(1)}元)</span>
              </div>
            )}
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline no-wrap">退出</span>
            </button>
          </div>
        </div>

        {/* 移动端导航 */}
        <div className="md:hidden flex justify-around py-2 border-t">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center space-y-1 px-3 py-1 rounded-lg transition-all ${
                isActive(item.path) ? 'text-primary-600' : 'text-gray-500'
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
