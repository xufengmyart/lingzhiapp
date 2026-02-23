import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  TrendingUp,
  Calendar,
  Target,
  Award,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  Star,
  Sparkles,
  Globe,
  Zap,
  Shield,
  BookOpen
} from 'lucide-react'
import { checkInApi, userApi } from '../services/api'
import { clearCheckInCache, requestCache, generateCacheKey } from '../services/cache'
import { vrTheme, vrCardStyles, vrFeatures } from '../utils/vr-theme'
import InstallPrompt from '../components/InstallPrompt'
import DocModal from '../components/DocModal'
import NewsSectionComplete from '../components/NewsSectionComplete'

interface DashboardStats {
  todayLingzhi: number
  checkedIn: boolean
  streak: number
  nextMilestone: number
  progress: number
  rewards: number[]  // 奖励列表
}

// 用户名脱敏函数（定义在组件外部）
const maskUsername = (username: string): string => {
  if (!username) return '?'
  const name = username.trim()
  if (name.length <= 2) {
    return name.charAt(0) + '*'
  } else {
    return name.charAt(0) + '*'.repeat(name.length - 2) + name.charAt(name.length - 1)
  }
}

const Dashboard = () => {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats>({
    todayLingzhi: 0,
    checkedIn: false,
    streak: 0,
    nextMilestone: 100,
    progress: 0,
    rewards: [10, 12, 15, 20, 25, 30, 40, 50]  // 默认奖励列表
  })
  const [loading, setLoading] = useState(true)
  const [checkInLoading, setCheckInLoading] = useState(false)
  const [showInstallPrompt, setShowInstallPrompt] = useState(false)
  const [hasDismissedInstall, setHasDismissedInstall] = useState(false)
  const [showDocModal, setShowDocModal] = useState(false)
  const [currentDocSlug, setCurrentDocSlug] = useState<string>('user-guide') // 默认显示用户指南

  useEffect(() => {
    console.log('Dashboard useEffect - 当前用户:', user)
    if (!user) {
      console.log('Dashboard useEffect - 用户不存在，跳转到登录页')
      navigate('/')
      return
    }
    loadDashboardData()
    checkInstallPrompt()
  }, []) // 只在组件挂载时加载一次

  const checkInstallPrompt = () => {
    // 检查是否已经关闭过安装提示
    const dismissed = localStorage.getItem('installPromptDismissed')
    if (dismissed) {
      const dismissedTime = parseInt(dismissed)
      const oneWeek = 7 * 24 * 60 * 60 * 1000
      if (Date.now() - dismissedTime < oneWeek) {
        return // 一周内不再显示
      }
    }

    // 检查是否已经安装
    const isInstalled = window.matchMedia('(display-mode: standalone)').matches ||
                       (window.navigator as any).standalone === true

    if (!isInstalled && !hasDismissedInstall) {
      // 延迟 3 秒后显示
      setTimeout(() => {
        setShowInstallPrompt(true)
      }, 3000)
    }
  }

  const handleCloseInstallPrompt = () => {
    setShowInstallPrompt(false)
    localStorage.setItem('installPromptDismissed', Date.now().toString())
    setHasDismissedInstall(true)
  }

  const handleInstallSuccess = () => {
    setShowInstallPrompt(false)
    // 可以添加庆祝动画或其他反馈
  }

  // 辅助函数：获取用户灵值（兼容两种字段名格式）
  const getUserLingzhi = (): number => {
    return user?.totalLingzhi ?? user?.total_lingzhi ?? 0
  }

  const loadDashboardData = async (useCache: boolean = true) => {
    if (!user) {
      console.log('Dashboard loadDashboardData - 用户不存在，跳转到登录页')
      navigate('/')
      return
    }

    try {
      setLoading(true)

      // 尝试刷新用户信息（如果API不存在则跳过）
      try {
        const userInfo = await userApi.getUserInfo(false)
        let currentUser = user
        if (userInfo.success && userInfo.data) {
          console.log('刷新后的用户信息:', userInfo.data)
          updateUser(userInfo.data)
          currentUser = userInfo.data
        }
      } catch (apiError) {
        console.log('用户信息API不存在或失败，使用当前用户信息:', apiError)
        // 继续执行，使用当前用户信息
      }

      // 获取签到状态
      const checkInRes = await checkInApi.getTodayStatus(useCache)
      console.log('签到状态响应:', checkInRes)

      // 计算下一个里程碑（使用最新的用户数据）
      // 支持两种字段名：totalLingzhi（camelCase）和 total_lingzhi（snake_case）
      const userLingzhi = user?.totalLingzhi || user?.total_lingzhi || 0
      const milestones = [10, 100, 500, 1000, 5000, 10000]
      const nextMilestone = milestones.find(m => m > userLingzhi) || milestones[milestones.length - 1]
      const prevMilestone = milestones.filter(m => m < userLingzhi).pop() || 0
      const progress = ((userLingzhi - prevMilestone) / (nextMilestone - prevMilestone)) * 100

      console.log('统计数据:', {
        todayLingzhi: checkInRes.data.todayLingzhi,
        checkedIn: checkInRes.data.checkedIn,
        nextMilestone,
        progress,
        rewards: checkInRes.data.rewards
      })

      setStats({
        todayLingzhi: checkInRes.data.todayLingzhi || 0,
        checkedIn: checkInRes.data.checkedIn,
        streak: checkInRes.data.streak || 0,  // 使用后端返回的连续签到天数
        nextMilestone,
        progress,
        rewards: checkInRes.data.rewards || [10, 12, 15, 20, 25, 30, 40, 50]  // 使用后端返回的奖励列表
      })
    } catch (error) {
      console.error('加载仪表盘数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckIn = async () => {
    if (stats.checkedIn || checkInLoading) {
      return
    }

    setCheckInLoading(true)
    try {
      console.log('开始签到...')
      const result = await checkInApi.checkIn()
      console.log('签到结果:', result)
      console.log('签到数据详情:', result.data)

      if (result.success) {
        // 清除签到缓存，确保获取最新数据
        clearCheckInCache()
        
        // 显示成功提示（使用后端返回的详细消息）
        alert(result.message || `🎉 签到成功！连续签到 ${result.data.streak} 天`)

        // 立即更新用户信息
        if (user) {
          // 计算新的总灵值：签到接口应该返回 total_lingzhi，如果没有则使用当前灵值 + 今日获得的灵值
          const newTotalLingzhi = result.data.total_lingzhi !== undefined 
            ? result.data.total_lingzhi
            : (user.total_lingzhi || user.totalLingzhi || 0) + (result.data.todayLingzhi || 0)
          
          console.log('计算后的新总灵值:', newTotalLingzhi, {
            原始total_lingzhi: result.data.total_lingzhi,
            当前灵值: user.total_lingzhi || user.totalLingzhi,
            今日获得: result.data.todayLingzhi
          })

          const updatedUser = {
            ...user,
            total_lingzhi: newTotalLingzhi,
            totalLingzhi: newTotalLingzhi
          }
          console.log('立即更新用户信息:', updatedUser)
          updateUser(updatedUser)
          
          // 立即更新统计数据（使用最新的灵值）
          const milestones = [10, 100, 500, 1000, 5000, 10000]
          const nextMilestone = milestones.find(m => m > newTotalLingzhi) || milestones[milestones.length - 1]
          const prevMilestone = milestones.filter(m => m < newTotalLingzhi).pop() || 0
          const progress = ((newTotalLingzhi - prevMilestone) / (nextMilestone - prevMilestone)) * 100

          setStats(prev => ({
            ...prev,
            checkedIn: true,
            todayLingzhi: result.data.todayLingzhi || prev.todayLingzhi,
            streak: result.data.streak || prev.streak,
            nextMilestone,
            progress
          }))
        }
      } else {
        alert(result.message || '签到失败，请稍后重试')
      }
    } catch (error: any) {
      console.error('签到失败:', error)
      // 根据错误类型显示不同的提示
      if (error.response?.status === 401) {
        alert('请先登录后再进行签到')
      } else if (error.response?.status === 429) {
        alert('操作过于频繁，请稍后再试')
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        alert('网络连接失败，请检查网络后重试')
      } else {
        alert(error.response?.data?.message || '签到失败，请稍后重试')
      }
    } finally {
      setCheckInLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={`min-h-screen ${vrTheme.bgGradient} flex items-center justify-center`}>
        <div className="relative">
          <div className="w-20 h-20 border-4 border-cyan-400/30 rounded-full"></div>
          <div className="w-20 h-20 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0"></div>
          <div className="w-20 h-20 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen ${vrTheme.bgGradient} pb-8`}>
      {/* 科幻主题背景装饰 - 科技蓝配色 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00C3FF]/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#47D1FF]/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#00E0FF]/10 rounded-full blur-[200px]"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10 pt-20">
        {/* 系统通知 - 智能化排版 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} rounded-2xl p-4 mb-6`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#00C3FF] to-[#00E0FF] rounded-lg flex items-center justify-center flex-shrink-0">
              <Star className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-white font-semibold text-sm sm:text-base mb-1">系统通知</h3>
              <p className="text-sm text-gray-300 break-words text-xs sm:text-sm leading-relaxed">
                🎉 VR 2.0 全新升级！沉浸式体验即将开启
              </p>
            </div>
            <button 
              onClick={() => navigate('/company/news')}
              className="text-[#00C3FF] text-sm hover:text-[#00E0FF] transition-colors flex-shrink-0 whitespace-nowrap"
            >
              查看更多
            </button>
          </div>
        </div>

        {/* 欢迎消息 - VR风格，智能化排版 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} rounded-3xl p-6 sm:p-8 mb-6`}>
          <div className="flex items-center gap-2 sm:gap-3 mb-3 flex-wrap">
            <div className="relative flex-shrink-0">
              <div className="absolute inset-0 bg-[#00C3FF] blur-xl animate-pulse"></div>
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-[#00E0FF] relative z-10" />
            </div>
            <Globe className="w-5 h-5 sm:w-6 sm:h-6 text-[#00C3FF] flex-shrink-0" />
            <Zap className="w-5 h-5 sm:w-6 sm:h-6 text-[#47D1FF] flex-shrink-0" />
            <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-[#00C3FF] flex-shrink-0" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2 drop-shadow-lg leading-tight">
            欢迎来到灵值元宇宙
          </h1>
          <p className="text-sm sm:text-base text-[#B4C7E7] opacity-90 leading-relaxed break-words">
            创造者 {user?.username}，您的 {getUserLingzhi()} 灵值正在创造无限可能
          </p>
        </div>

        {/* VR特色展示 */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {vrFeatures.map((feature, idx) => (
            <div key={idx} className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} rounded-2xl p-4 text-center transition-all hover:scale-105`}>
              <div className="text-3xl mb-2">{feature.icon}</div>
              <div className="text-[#FFFFFF] font-semibold">{feature.title}</div>
              <div className="text-sm text-[#B4C7E7]">{feature.subtitle}</div>
            </div>
          ))}
        </div>

        {/* 核心数据卡片 - VR风格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* 总灵值 */}
          <div className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 transition-all group`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${vrCardStyles.total_lingzhi.color} rounded-xl flex items-center justify-center ${vrCardStyles.total_lingzhi.glow}`}>
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center text-green-400 text-sm font-semibold">
                <ArrowUpRight className="w-4 h-4 mr-1" />
                <span>+{((getUserLingzhi()) * 0.012).toFixed(1)}%</span>
              </div>
            </div>
            <div className="text-3xl font-bold text-[#FFFFFF] mb-1">{getUserLingzhi()}</div>
            <div className="text-[#B4C7E7] text-sm">总灵值</div>
            <div className="text-[#00C3FF] font-semibold mt-2">
              {((getUserLingzhi()) * 0.1).toFixed(1)} 元
            </div>
          </div>

          {/* 今日签到 */}
          <div className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 transition-all group`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${vrCardStyles.todayCheckIn.color} rounded-xl flex items-center justify-center ${vrCardStyles.todayCheckIn.glow}`}>
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center text-[#00C3FF] text-sm font-semibold">
                <Clock className="w-4 h-4 mr-1" />
                <span>连续 {stats.streak} 天</span>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stats.todayLingzhi}</div>
            <div className="text-gray-400 text-sm">今日灵值</div>
            <button
              onClick={handleCheckIn}
              disabled={stats.checkedIn || checkInLoading}
              className={`mt-4 w-full py-2.5 rounded-xl font-semibold transition-all ${
                stats.checkedIn
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50 cursor-default'
                  : `${vrTheme.button.gradient} ${vrTheme.button.glow} text-white hover:scale-105`
              }`}
            >
              {stats.checkedIn ? (
                <span className="flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  已签到
                </span>
              ) : checkInLoading ? (
                '签到中...'
              ) : (
                `立即签到 (+${stats.rewards[stats.streak] || 10}灵值)`
              )}
            </button>
          </div>

          {/* 下一个里程碑 */}
          <div className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 transition-all group`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${vrCardStyles.milestone.color} rounded-xl flex items-center justify-center ${vrCardStyles.milestone.glow}`}>
                <Target className="w-6 h-6 text-white" />
              </div>
              <div className="text-xs bg-[#FF9E7A]/20 text-[#FF9E7A] px-2 py-1 rounded-full font-semibold">
                目标
              </div>
            </div>
            <div className="text-3xl font-bold text-[#FFFFFF] mb-1">{stats.nextMilestone}</div>
            <div className="text-[#B4C7E7] text-sm">下一个里程碑</div>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-[#B4C7E7] mb-2">
                <span>进度</span>
                <span>{stats.progress.toFixed(0)}%</span>
              </div>
              <div className={`w-full ${vrTheme.progress.track} rounded-full h-2 overflow-hidden`}>
                <div 
                  className={`${vrTheme.progress.gradient} h-2 rounded-full transition-all`}
                  style={{ width: `${stats.progress}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* 合伙人资格 */}
          <div className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 transition-all group`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${vrCardStyles.partner.color} rounded-xl flex items-center justify-center ${vrCardStyles.partner.glow}`}>
                <Award className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center text-amber-400 text-sm font-semibold">
                <Star className="w-4 h-4 mr-1" />
                <span>{getUserLingzhi() >= 10000 ? '已达成' : '进行中'}</span>
              </div>
            </div>
            <div className="text-3xl font-bold text-[#FFFFFF] mb-1">{10000}</div>
            <div className="text-[#B4C7E7] text-sm">合伙人资格要求</div>
            <div className="mt-4 text-sm">
              <span className="text-[#B4C7E7]">距离资格还差：</span>
              <span className="text-[#00C3FF] font-semibold">
                {Math.max(0, 10000 - getUserLingzhi())} 灵值
              </span>
            </div>
          </div>
        </div>

        {/* 项目入口 - VR风格 */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-[#FFFFFF] mb-4 flex items-center">
            <Sparkles className="w-6 h-6 mr-2 text-[#00C3FF]" />
            元宇宙项目入口
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div
              onClick={() => window.location.href = '/medium-video'}
              className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-red-500/10"></div>
              <div className="text-4xl mb-3 relative z-10">🎬</div>
              <h3 className="text-lg font-semibold text-orange-400 mb-2 relative z-10">中视频项目</h3>
              <p className="text-gray-400 text-sm relative z-10">创作 1-30 分钟视频，获取播放收益</p>
              <div className="absolute top-0 right-0 w-24 h-24 bg-orange-500/20 rounded-full blur-2xl"></div>
            </div>

            <div
              onClick={() => window.location.href = '/xian-aesthetics'}
              className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-[#3e8bb6]/10"></div>
              <div className="text-4xl mb-3 relative z-10">🔍</div>
              <h3 className="text-lg font-semibold text-cyan-400 mb-2 relative z-10">西安美学侦探</h3>
              <p className="text-gray-400 text-sm relative z-10">探索城市美学，发现西安之美</p>
              <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/20 rounded-full blur-2xl"></div>
            </div>

            <div
              onClick={() => window.location.href = '/partner'}
              className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 to-yellow-500/10"></div>
              <div className="text-4xl mb-3 relative z-10">🏆</div>
              <h3 className="text-lg font-semibold text-amber-400 mb-2 relative z-10">合伙人计划</h3>
              <p className="text-gray-400 text-sm relative z-10">成为合伙人，享受更高收益</p>
              <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/20 rounded-full blur-2xl"></div>
            </div>
          </div>
        </div>

        {/* 动态资讯（完整版） */}
        <div className="mb-6">
          <NewsSectionComplete limit={5} showMore={false} featured={true} showSearch={true} showFilters={true} />
        </div>
      </div>

      {/* 快速入口 - VR风格 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
          <Zap className="w-6 h-6 mr-2 text-pink-400" />
          快速入口
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            onClick={() => {
              setCurrentDocSlug('user-guide')
              setShowDocModal(true)
            }}
            className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 to-orange-500/10"></div>
            <div className="text-4xl mb-3 relative z-10">📖</div>
            <h3 className="text-lg font-semibold text-amber-400 mb-2 relative z-10">用户指南</h3>
            <p className="text-gray-400 text-sm relative z-10">快速入门，了解平台功能</p>
            <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/20 rounded-full blur-2xl"></div>
          </div>

          <div
            onClick={() => window.location.href = '/chat'}
            className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-[#3e8bb6]/10"></div>
            <div className="text-4xl mb-3 relative z-10">💬</div>
            <h3 className="text-lg font-semibold text-cyan-400 mb-2 relative z-10">智能对话</h3>
            <p className="text-gray-400 text-sm relative z-10">与智能体对话，探索文化价值</p>
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/20 rounded-full blur-2xl"></div>
          </div>

          <div
            onClick={() => window.location.href = '/economy'}
            className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 to-green-500/10"></div>
            <div className="text-4xl mb-3 relative z-10">💰</div>
            <h3 className="text-lg font-semibold text-teal-400 mb-2 relative z-10">经济模型</h3>
            <p className="text-gray-400 text-sm relative z-10">查看收入预测，规划财富增长</p>
            <div className="absolute top-0 right-0 w-24 h-24 bg-teal-500/20 rounded-full blur-2xl"></div>
          </div>

          <div
            onClick={() => window.location.href = '/user-learning'}
            className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 cursor-pointer transition-all hover:scale-105 group relative overflow-hidden`}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10"></div>
            <div className="text-4xl mb-3 relative z-10">📚</div>
            <h3 className="text-lg font-semibold text-purple-400 mb-2 relative z-10">用户学习</h3>
            <p className="text-gray-400 text-sm relative z-10">修行记录，开始学习之旅</p>
            <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/20 rounded-full blur-2xl"></div>
          </div>
        </div>
      </div>

      {/* 用户动态 - VR风格 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
          <Globe className="w-6 h-6 mr-2 text-cyan-400" />
          用户动态
        </h2>
        <div className={`${vrTheme.card.bg} ${vrTheme.card.border} rounded-2xl p-6`}>
          <UserActivityFeed />
        </div>
      </div>

      {/* 安装提示 */}
      {showInstallPrompt && (
        <InstallPrompt
          onClose={handleCloseInstallPrompt}
          onInstall={handleInstallSuccess}
        />
      )}

      {/* 文档模态框 */}
      {showDocModal && (
        <DocModal
          slug={currentDocSlug}
          onClose={() => setShowDocModal(false)}
        />
      )}
    </div>
  )
}

// 用户动态组件
const UserActivityFeed = () => {
  const [recentUsers, setRecentUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRecentUsers()
  }, [])

  const loadRecentUsers = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/public/users/recent?limit=20`)
      const data = await response.json()
      if (data.success) {
        setRecentUsers(data.data)
      }
    } catch (error) {
      console.error('加载用户动态失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-cyan-400/30 rounded-full"></div>
          <div className="w-12 h-12 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {recentUsers.map((user) => (
          <div
            key={user.id}
            className={`flex items-center space-x-4 p-4 ${vrTheme.card.bg} rounded-xl hover:bg-white/10 transition-colors`}
          >
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-[#3e8bb6] rounded-full flex items-center justify-center text-white font-bold">
              {(user?.username || "?").charAt(0)}
            </div>
            <div className="flex-1">
              <div className="text-sm font-semibold text-white">
                {maskUsername(user.username)} 加入了灵值元宇宙
              </div>
              <div className="text-xs text-gray-400">
                {new Date(user.created_at).toLocaleString('zh-CN', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
            <div className={`px-3 py-1 text-xs ${vrTheme.button.gradient} rounded-full text-white`}>
              新用户
            </div>
          </div>
        ))}
        {recentUsers.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            暂无用户动态
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
