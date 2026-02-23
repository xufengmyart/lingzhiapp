import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, MessageSquare, TrendingUp, Award, User, LogOut, Wallet, Sparkles, HelpCircle, MessageCircle, Database, Box, Trophy, ChevronDown, BookOpen, LayoutGrid, Palette, Layers, Wand2, Sparkles as SparklesIcon, Building2, FileText, Info, Users, DollarSign, Gem, Target, Map, GraduationCap, Coins, Briefcase, Wrench, Bot, Globe, Newspaper, Compass, Brain, Flower2, Route, Star, ArrowLeft, Receipt, Lock } from 'lucide-react'
import { useState, useEffect } from 'react'
import DocModal from './DocModal'

const Navigation = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [history, setHistory] = useState<string[]>([])
  const [showDocModal, setShowDocModal] = useState(false)
  const [currentDocSlug, setCurrentDocSlug] = useState<string>('user-guide')

  // 根据当前路径自动展开对应的下拉菜单
  useEffect(() => {
    const activeGroup = mainNav.find(group =>
      group.items.some(item => location.pathname === item.path)
    )
    if (activeGroup) {
      setActiveDropdown(activeGroup.id)
    }
  }, [location.pathname])

  // 管理历史记录
  useEffect(() => {
    // 如果不是从登录页面来的，则添加到历史记录
    if (location.pathname !== '/' && location.pathname !== '/login-full' && location.pathname !== '/admin/login') {
      setHistory(prev => {
        // 避免重复添加相同的路径
        if (prev.length > 0 && prev[prev.length - 1] === location.pathname) {
          return prev
        }
        // 最多保留10条历史记录
        return [...prev.slice(-9), location.pathname]
      })
    }
  }, [location.pathname])

  const handleGoBack = () => {
    if (history.length > 1) {
      const previousPath = history[history.length - 2]
      navigate(previousPath)
      // 移除最后一条记录（当前路径）
      setHistory(prev => prev.slice(0, -1))
    } else {
      // 如果没有历史记录，返回到dashboard
      navigate('/dashboard')
    }
  }

  const toggleDropdown = (id: string) => {
    if (activeDropdown === id) {
      setActiveDropdown(null)
    } else {
      setActiveDropdown(id)
    }
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const handleMobileSubmenuClick = (groupId: string) => {
    if (activeDropdown === groupId) {
      setActiveDropdown(null)
    } else {
      setActiveDropdown(groupId)
    }
  }

  // 优化后的主导航结构 - 5大核心分类
  const mainNav = [
    {
      id: 'ai-assistant',
      label: '智能助手',
      icon: Bot,
      description: 'AI驱动的核心功能',
      items: [
        { path: '/chat', label: '智能对话', icon: MessageSquare, highlight: true },
        { path: '/knowledge', label: '知识之库', icon: BookOpen },
        { path: '/culture-translation', label: '文化转译', icon: Wand2 },
        { path: '/culture-projects', label: '文化项目', icon: Layers },
      ]
    },
    {
      id: 'resource-hub',
      label: '资源广场',
      icon: Globe,
      description: '资源匹配与交易',
      items: [
        { path: '/user-resources', label: '用户资源', icon: Users },
        { path: '/project-pool', label: '项目资源', icon: Box },
        { path: '/merchant-pool', label: '商家资源', icon: Building2 },
        { path: '/bounty-hunter', label: '赏金任务', icon: Trophy },
        {
          path: '/private-resources',
          label: '私有资源',
          icon: Sparkles,
          highlight: true,
          submenu: [
            { path: '/private-resources', label: '资源管理', icon: Sparkles },
            { path: '/project-recommendations', label: '项目推荐', icon: Target },
            { path: '/project-workflow', label: '项目流程', icon: Route },
          ]
        },
      ]
    },
    {
      id: 'asset-value',
      label: '资产价值',
      icon: Gem,
      description: '资产管理与价值实现',
      items: [
        { path: '/assets', label: '数字资产', icon: Gem, highlight: true },
        { path: '/asset-management', label: '资产管理', icon: Coins },
        { path: '/dividend-pool', label: '分红殿堂', icon: DollarSign, highlight: true },
        { path: '/sacred-sites', label: '文化圣地', icon: Map },
        { path: '/partner', label: '合伙人计划', icon: Award },
      ]
    },
    {
      id: 'cultural-creation',
      label: '文化创作',
      icon: Palette,
      description: '文化内容创作与管理',
      items: [
        { path: '/journey', label: '用户旅程', icon: Route },
        { path: '/user-learning', label: '修行记录', icon: GraduationCap },
        { path: '/economy', label: '经济模型', icon: TrendingUp },
        { path: '/recharge', label: '购买灵值', icon: Wallet },
        { path: '/recharge-history', label: '充值记录', icon: Receipt },
      ]
    },
    {
      id: 'news-updates',
      label: '动态资讯',
      icon: Newspaper,
      description: '平台最新动态',
      items: [
        { path: '/news', label: '系统新闻', icon: Newspaper, highlight: true },
        { path: '/notifications', label: '我的通知', icon: MessageCircle, highlight: true },
        { path: '/company/news', label: '公司动态', icon: FileText },
        { path: '/company/projects', label: '项目动态', icon: Box },
        { path: '/company/info', label: '平台信息', icon: Info },
        { path: '/company/users', label: '数据统计', icon: Target },
      ]
    },
  ]

  // 工作台 - 根据用户角色动态显示
  const getWorkbenchItems = () => {
    const userRole = localStorage.getItem('userRole')
    const items = []
    
    if (userRole === 'merchant' || userRole === 'admin') {
      items.push({ path: '/merchant-workbench', label: '商家工作台', icon: Briefcase })
    }
    if (userRole === 'expert' || userRole === 'admin') {
      items.push({ path: '/expert-workbench', label: '专家工作台', icon: Wrench })
    }
    
    return items
  }

  const workbenchItems = getWorkbenchItems()

  // 右侧功能区
  const navItemsRight = [
    ...workbenchItems,
    { path: '/docs', icon: HelpCircle, label: '帮助' },
    { path: '/value-guide', icon: Compass, label: '指南' },
    { path: '/profile', icon: User, label: '个人' },
    { path: '/change-password', icon: Lock, label: '密码' },
    { path: '/feedback', icon: MessageCircle, label: '反馈' },
    // 管理员入口
    ...(user && (user as any).role && ['admin', 'super_admin'].includes((user as any).role)
      ? [{ path: '/admin/analytics', icon: Target, label: '分析' }]
      : []),
  ]

  const isActive = (path: string) => location.pathname === path
  const isActiveGroup = (items: any[]) => items.some(item => isActive(item.path))

  return (
    <nav className="fixed top-0 left-0 right-0 bg-gradient-to-r from-[#0A0D18] via-[#121A2F] to-[#0A0D18] border-b border-[#00C3FF]/30 shadow-2xl z-[999999]">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* 返回按钮 - 只在有历史记录时显示 */}
          {history.length > 0 && (
            <button
              onClick={handleGoBack}
              className="flex items-center gap-1.5 px-3 py-2 text-[#B4C7E7] hover:bg-[#00C3FF]/20 rounded-lg transition-all hover:text-white mr-2"
              title="返回"
            >
              <ArrowLeft className="w-4 h-4 flex-shrink-0" />
              <span className="hidden sm:inline whitespace-nowrap text-sm">返回</span>
            </button>
          )}

          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2 sm:gap-3 group flex-shrink-0">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] rounded-lg flex items-center justify-center shadow-lg">
              <Wallet className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#47D1FF] flex-shrink-0" />
              <span className="text-base sm:text-xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent hidden sm:block truncate">
                灵值元宇宙
              </span>
            </div>
          </Link>

          {/* 主导航 - 桌面端 */}
          <div className="hidden xl:flex items-center gap-1">
            {mainNav.map((group) => {
              const Icon = group.icon
              const isGroupActive = isActiveGroup(group.items)
              return (
                <div
                  key={group.id}
                  className="relative group"
                  onMouseEnter={() => setActiveDropdown(group.id)}
                  onMouseLeave={() => setActiveDropdown(null)}
                >
                  <button
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all hover:bg-[#00C3FF]/20 ${
                      isGroupActive || activeDropdown === group.id 
                        ? 'bg-[#00C3FF]/30 text-white' 
                        : 'text-[#B4C7E7] hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span className="whitespace-nowrap text-sm font-medium">{group.label}</span>
                    <ChevronDown className={`w-3 h-3 flex-shrink-0 transition-transform ${activeDropdown === group.id ? 'rotate-180' : ''}`} />
                  </button>

                  {/* 下拉菜单 */}
                  {activeDropdown === group.id && (
                    <div className="absolute top-full left-0 mt-1 bg-[#121A2F] border border-[#00C3FF]/30 rounded-lg shadow-2xl min-w-[240px] py-2 z-[999999]">
                      {/* 分类标题 */}
                      <div className="px-4 py-2 border-b border-[#00C3FF]/10">
                        <div className="text-xs text-[#47D1FF] font-medium mb-0.5">{group.description}</div>
                      </div>
                      {/* 菜单项 */}
                      {group.items.map((item) => {
                        const ItemIcon = item.icon
                        return (
                          <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center gap-3 px-4 py-2.5 transition-all ${
                              isActive(item.path)
                                ? 'bg-[#00C3FF]/30 text-white'
                                : 'text-[#B4C7E7] hover:bg-[#00C3FF]/20 hover:text-white'
                            }`}
                          >
                            <ItemIcon className="w-4 h-4 flex-shrink-0" />
                            <span className="whitespace-nowrap text-sm flex-1">{item.label}</span>
                            {item.highlight && <Star className="w-3.5 h-3.5 text-[#FFD700] flex-shrink-0" />}
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* 大屏右侧功能区 */}
          <div className="hidden xl:flex items-center gap-1 border-l border-[#00C3FF]/10 pl-3 sm:pl-4">
            {navItemsRight.map((item) => {
              const Icon = item.icon
              const isHelpItem = item.path === '/docs'
              
              if (isHelpItem) {
                // 帮助按钮 - 打开文档模态框
                return (
                  <button
                    key={item.path}
                    onClick={() => {
                      setCurrentDocSlug('user-guide')
                      setShowDocModal(true)
                    }}
                    className={`flex items-center gap-2 px-2 sm:px-3 py-2 rounded-lg transition-all hover:bg-[#00C3FF]/20 ${
                      isActive(item.path) ? 'bg-[#00C3FF]/30 text-white' : 'text-[#B4C7E7] hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span className="text-xs sm:text-sm whitespace-nowrap">{item.label}</span>
                  </button>
                )
              }
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-2 sm:px-3 py-2 rounded-lg transition-all hover:bg-[#00C3FF]/20 ${
                    isActive(item.path) ? 'bg-[#00C3FF]/30 text-white' : 'text-[#B4C7E7] hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs sm:text-sm whitespace-nowrap">{item.label}</span>
                </Link>
              )
            })}

            {/* 用户信息和登出 */}
            {user && (
              <>
                <div className="hidden md:flex items-center gap-2 bg-gradient-to-r from-[#00C3FF]/20 to-[#00E0FF]/20 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-full border border-[#00C3FF]/30 flex-shrink-0 mx-2">
                  <Wallet className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  <span className="font-semibold text-sm sm:text-base whitespace-nowrap">{user.total_lingzhi} 灵值</span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 sm:gap-2 px-3 py-2 text-[#B4C7E7] hover:bg-[#00C3FF]/20 rounded-lg transition-all hover:text-white"
                >
                  <LogOut className="w-4 h-4 flex-shrink-0" />
                  <span className="hidden sm:inline whitespace-nowrap text-sm">退出</span>
                </button>
              </>
            )}
          </div>

          {/* 移动端菜单按钮 */}
          <button
            onClick={toggleMobileMenu}
            className="xl:hidden flex flex-col items-center justify-center gap-1.5 p-2 text-[#B4C7E7] hover:text-white hover:bg-[#00C3FF]/20 rounded-lg transition-all z-[999999]"
            aria-label="打开菜单"
          >
            <div className={`w-6 h-0.5 bg-current transition-all ${isMobileMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></div>
            <div className={`w-6 h-0.5 bg-current transition-all ${isMobileMenuOpen ? 'opacity-0' : ''}`}></div>
            <div className={`w-6 h-0.5 bg-current transition-all ${isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></div>
          </button>
        </div>

        {/* 移动端导航菜单 */}
        {isMobileMenuOpen && (
          <div className="xl:hidden pb-4 border-t border-[#00C3FF]/10 pt-4 bg-[#0A0D18] z-40 relative">
            <div className="max-h-[calc(100vh-8rem)] overflow-y-auto">
              {/* 五大生态导航 */}
              <div className="grid grid-cols-5 gap-2 mb-4">
                {mainNav.map((group) => {
                  const Icon = group.icon
                  const isGroupActive = isActiveGroup(group.items)
                  return (
                    <button
                      key={group.id}
                      onClick={() => handleMobileSubmenuClick(group.id)}
                      className={`flex flex-col items-center gap-1.5 px-2 py-3 rounded-lg transition-all ${
                        isGroupActive || activeDropdown === group.id 
                          ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]' 
                          : 'bg-[#121A2F] text-[#B4C7E7]/60 border border-[#00C3FF]/10'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-[10px] font-medium whitespace-nowrap">{group.label}</span>
                    </button>
                  )
                })}
              </div>

              {/* 子菜单 */}
              {activeDropdown && activeDropdown !== 'mobile' && (
                <div className="bg-[#121A2F] border border-[#00C3FF]/30 rounded-lg p-2 mb-4">
                  <div className="px-3 py-2 mb-2">
                    <div className="text-xs text-[#47D1FF]">
                      {mainNav.find(g => g.id === activeDropdown)?.description}
                    </div>
                  </div>
                  {mainNav.find(g => g.id === activeDropdown)?.items.map((item) => {
                    const ItemIcon = item.icon
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={() => {
                          setActiveDropdown(null)
                          setIsMobileMenuOpen(false)
                        }}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                          isActive(item.path) ? 'bg-[#00C3FF]/30 text-white' : 'text-[#B4C7E7] hover:bg-[#00C3FF]/20'
                        }`}
                      >
                        <ItemIcon className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm flex-1">{item.label}</span>
                        {item.highlight && <Star className="w-3.5 h-3.5 text-[#FFD700] flex-shrink-0" />}
                      </Link>
                    )
                  })}
                </div>
              )}

              {/* 工作台快捷入口 */}
              {workbenchItems.length > 0 && (
                <div className="bg-gradient-to-r from-[#00C3FF]/10 to-[#00E0FF]/10 border border-[#00C3FF]/20 rounded-lg p-2 mb-4">
                  <div className="text-xs text-[#47D1FF] px-3 py-2 mb-2">工作台</div>
                  {workbenchItems.map((item) => {
                    const ItemIcon = item.icon
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                          isActive(item.path) ? 'bg-[#00C3FF]/30 text-white' : 'text-[#B4C7E7] hover:bg-[#00C3FF]/20'
                        }`}
                      >
                        <ItemIcon className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm">{item.label}</span>
                      </Link>
                    )
                  })}
                </div>
              )}

              {/* 用户信息 */}
              {user && (
                <div className="flex items-center justify-between bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg px-4 py-3 mb-4">
                  <div className="flex items-center gap-2">
                    <Wallet className="w-5 h-5 text-[#00C3FF]" />
                    <span className="text-sm text-white font-medium">{user.total_lingzhi} 灵值</span>
                  </div>
                  <button
                    onClick={logout}
                    className="p-2 text-[#B4C7E7] hover:text-white hover:bg-[#00C3FF]/20 rounded-lg transition-all"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              )}

              {/* 快捷入口 */}
              <div className="grid grid-cols-4 gap-2">
                {navItemsRight.filter(item => !workbenchItems.find(wi => wi.path === item.path)).map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex flex-col items-center justify-center gap-1 px-2 py-3 rounded-lg transition-all ${
                        isActive(item.path) ? 'bg-[#00C3FF]/30 text-white' : 'bg-[#121A2F] text-[#B4C7E7] border border-[#00C3FF]/10'
                      }`}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      <span className="text-[10px] whitespace-nowrap">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 文档模态框 */}
      {showDocModal && (
        <DocModal
          slug={currentDocSlug}
          onClose={() => setShowDocModal(false)}
        />
      )}
    </nav>
  )
}

export default Navigation
