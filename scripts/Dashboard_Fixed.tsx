import { useState, useEffect } from 'react'
import { Calendar, Award, Users, Clock, Star, CheckCircle, TrendingUp, Gift, Sparkles, User, Flame, Zap, Target, Trophy, Book, FolderOpen, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface DashboardStats {
  totalUsers: number
  totalAgents: number
  totalKnowledgeBaseItems: number
  todayActiveUsers: number
  todayActiveAgents: number
  todayKnowledgeBaseItems: number
  companyNews: number
  companyAnnouncements: number
  totalLingzhi: number
}

interface TodayCheckInStatus {
  status: 'checked_in' | 'not_checked_in'
  lingzhi: number
  streak: number
  timestamp: string | null
}

// 辅助函数：调用API
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  }

  const response = await fetch(`${endpoint}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`)
  }

  return await response.json()
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, updateUser, loading: authLoading } = useAuth()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [checkInStatus, setCheckInStatus] = useState<TodayCheckInStatus | null>(null)
  const [checkInLoading, setCheckInLoading] = useState(false)
  const [checkInAnimation, setCheckInAnimation] = useState(false)

  const isAuthenticated = !!user && !authLoading

  // 加载用户信息
  const loadUserInfo = async () => {
    if (!isAuthenticated) return

    try {
      const res = await apiCall('/api/user/info')
      if (res.success && res.data) {
        const userData = {
          id: res.data.id || user?.id,
          username: res.data.username || user?.username || '',
          email: res.data.email || user?.email || '',
          phone: res.data.phone || user?.phone || '',
          totalLingzhi: res.data.totalLingzhi || user?.totalLingzhi || 0,
          currentStage: res.data.currentStage || user?.currentStage || '探索者',
          participationLevel: res.data.participationLevel || user?.participationLevel || '普通用户',
          createdAt: res.data.createdAt || user?.createdAt || '',
        }
        updateUser(userData)
      }
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  }

  // 加载今日签到状态
  const loadCheckInStatus = async () => {
    try {
      const res = await apiCall('/api/check-in/today-status')
      if (res.success && res.data) {
        setCheckInStatus(res.data)
      }
    } catch (error) {
      console.error('加载签到状态失败:', error)
    }
  }

  // 加载统计数据
  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const statsRes = await apiCall('/api/stats')
      if (statsRes.success) {
        setStats(statsRes.data)
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 初始化数据
  const initDashboard = async () => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    await Promise.all([
      loadDashboardData(),
      loadUserInfo()
    ])
    await loadCheckInStatus()
  }

  useEffect(() => {
    initDashboard()
  }, [isAuthenticated, navigate])

  const handleCheckIn = async () => {
    setCheckInLoading(true)
    try {
      const checkInRes = await apiCall('/api/checkin', { method: 'POST' })
      if (checkInRes.success) {
        await loadCheckInStatus()
        await loadUserInfo()
        await loadDashboardData()
        setCheckInAnimation(true)
        setTimeout(() => setCheckInAnimation(false), 3000)
      }
    } catch (error) {
      console.error('签到失败:', error)
    } finally {
      setCheckInLoading(false)
    }
  }

  if (loading || !stats || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  const statsCards = [
    { icon: Users, label: '用户总数', value: stats.totalUsers, color: 'bg-blue-500' },
    { icon: FolderOpen, label: '项目总数', value: stats.totalAgents, color: 'bg-purple-500' },
    { icon: Book, label: '知识库条目', value: stats.totalKnowledgeBaseItems, color: 'bg-green-500' },
    { icon: Calendar, label: '今日活跃用户', value: stats.todayActiveUsers, color: 'bg-orange-500' },
    { icon: Zap, label: '今日活跃项目', value: stats.todayActiveAgents, color: 'bg-yellow-500' },
    { icon: TrendingUp, label: '今日新增知识', value: stats.todayKnowledgeBaseItems, color: 'bg-pink-500' },
    { icon: Star, label: '公司动态', value: stats.companyNews, color: 'bg-indigo-500' },
    { icon: Trophy, label: '系统公告', value: stats.companyAnnouncements, color: 'bg-teal-500' }
  ]

  const guideSteps = [
    {
      icon: Gift,
      label: '每日签到',
      desc: '获取灵值奖励',
      onClick: () => {}
    },
    {
      icon: FolderOpen,
      label: '项目库',
      desc: '探索所有项目',
      onClick: () => navigate('/projects')
    },
    {
      icon: Book,
      label: '知识库',
      desc: '管理知识内容',
      onClick: () => navigate('/knowledge-base')
    },
    {
      icon: Star,
      label: '公司动态',
      desc: '了解最新资讯',
      onClick: () => navigate('/company-news')
    },
    {
      icon: TrendingUp,
      label: '经济模型',
      desc: '查看收入预测',
      onClick: () => navigate('/economy')
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* 顶部欢迎区域 */}
        <div className="mb-8 bg-gradient-to-r from-emerald-600 to-teal-500 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {user.username && user.username.length > 0 && user.username !== '请填写'
                  ? `欢迎回来，${user.username}！`
                  : '欢迎回来！'}
              </h1>
              <p className="text-emerald-100">开始探索灵值生态园的奇妙世界吧</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2">
                <Flame className="w-8 h-8 text-yellow-300" />
                <div>
                  <div className="text-sm text-emerald-100">当前灵值</div>
                  <div className="text-4xl font-bold">{user.totalLingzhi || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 项目导引 */}
        <div className="mt-8 bg-gradient-to-br from-emerald-600 to-teal-500 rounded-2xl p-8 shadow-2xl text-white">
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
              <Target className="w-7 h-7" />
              新手导引
            </h2>
            <p className="text-emerald-100 text-lg">快速了解灵值生态园，开启您的探索之旅</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {guideSteps.map((step, index) => (
              <div
                key={index}
                onClick={step.onClick}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-4 hover:bg-white/20 transition-all cursor-pointer"
              >
                <div className="flex flex-col items-center text-center">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mb-3">
                    <span className="text-2xl font-bold text-emerald-600">{index + 1}</span>
                  </div>
                  <step.icon className="w-8 h-8 mb-2 text-yellow-300" />
                  <h4 className="font-semibold mb-1">{step.label}</h4>
                  <p className="text-sm text-emerald-100">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 签到卡片 */}
        <div className="mt-8 bg-white rounded-xl p-6 shadow-lg relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-4 rounded-full ${checkInStatus?.status === 'checked_in' ? 'bg-green-100' : 'bg-gradient-to-r from-emerald-500 to-teal-500'}`}>
                {checkInStatus?.status === 'checked_in' ? (
                  <CheckCircle className="w-8 h-8 text-green-600" />
                ) : (
                  <Target className="w-8 h-8 text-white" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800">
                  {checkInStatus?.status === 'checked_in' ? '今日已签到' : '今日签到'}
                </h3>
                <p className="text-gray-600">
                  {checkInStatus?.status === 'checked_in'
                    ? `已获得 ${checkInStatus.lingzhi} 灵值，连续签到 ${checkInStatus.streak} 天`
                    : `签到即可获得灵值奖励`}
                </p>
              </div>
            </div>
            {checkInStatus?.status !== 'checked_in' && (
              <button
                onClick={handleCheckIn}
                disabled={checkInLoading}
                className={`px-8 py-4 rounded-xl font-semibold text-white shadow-lg transform transition-all duration-300 ${
                  checkInLoading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:scale-105 hover:shadow-xl active:scale-95'
                }`}
              >
                {checkInLoading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    签到中...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Gift className="w-5 h-5" />
                    立即签到
                  </span>
                )}
              </button>
            )}
          </div>

          {/* 签到动画 */}
          {checkInAnimation && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-xl z-10">
              <div className="text-center text-white">
                <div className="animate-bounce mb-4">
                  <Sparkles className="w-16 h-16 mx-auto text-yellow-400" />
                </div>
                <div className="text-3xl font-bold mb-2">签到成功！</div>
                <div className="text-xl">+{checkInStatus?.lingzhi || 10} 灵值</div>
              </div>
            </div>
          )}
        </div>

        {/* 统计卡片 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsCards.map((stat, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4">
                <div className={`${stat.color} p-4 rounded-lg flex-shrink-0`}>
                  <stat.icon className="w-8 h-8 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-600 truncate whitespace-nowrap">{stat.label}</div>
                  <div className="text-2xl font-bold text-gray-800 truncate whitespace-nowrap">{stat.value}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 快捷操作 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            onClick={() => navigate('/projects')}
            className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer hover:scale-105 group"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-purple-500 p-3 rounded-lg flex-shrink-0">
                <FolderOpen className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 truncate whitespace-nowrap flex-1">项目库</h3>
              <ArrowRight className="w-5 h-5 text-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <p className="text-gray-600 text-sm truncate">探索灵值生态园的所有项目和功能</p>
          </div>

          <div
            onClick={() => navigate('/knowledge-base')}
            className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer hover:scale-105 group"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-green-500 p-3 rounded-lg flex-shrink-0">
                <Book className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 truncate whitespace-nowrap flex-1">知识库管理</h3>
              <ArrowRight className="w-5 h-5 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <p className="text-gray-600 text-sm truncate">管理知识库内容和检索知识</p>
          </div>

          <div
            onClick={() => navigate('/company-news')}
            className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer hover:scale-105 group"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-indigo-500 p-3 rounded-lg flex-shrink-0">
                <Star className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 truncate whitespace-nowrap flex-1">公司动态</h3>
              <ArrowRight className="w-5 h-5 text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <p className="text-gray-600 text-sm truncate">查看公司最新动态和公告</p>
          </div>
        </div>

        {/* 用户信息 */}
        <div className="mt-8 bg-white rounded-xl p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            用户信息
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center gap-3">
              <Award className="w-5 h-5 text-purple-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm text-gray-600 truncate whitespace-nowrap">当前阶段</div>
                <div className="font-semibold text-gray-800 truncate whitespace-nowrap">{user.currentStage || '探索者'}</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-blue-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm text-gray-600 truncate whitespace-nowrap">参与等级</div>
                <div className="font-semibold text-gray-800 truncate whitespace-nowrap">{user.participationLevel || '普通用户'}</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-teal-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm text-gray-600 truncate whitespace-nowrap">加入时间</div>
                <div className="font-semibold text-gray-800 truncate whitespace-nowrap">
                  {user.createdAt ? new Date(user.createdAt).toLocaleDateString('zh-CN') : '未知'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
