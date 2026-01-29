import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  TrendingUp,
  Calendar,
  Target,
  Award,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  Star
} from 'lucide-react'
import { checkInApi } from '../services/api'

interface DashboardStats {
  todayLingzhi: number
  checkedIn: boolean
  streak: number
  nextMilestone: number
  progress: number
}

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    todayLingzhi: 0,
    checkedIn: false,
    streak: 0,
    nextMilestone: 100,
    progress: 0
  })
  const [loading, setLoading] = useState(true)
  const [checkInLoading, setCheckInLoading] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [user])

  const loadDashboardData = async () => {
    if (!user) return

    try {
      setLoading(true)
      // 获取签到状态
      const checkInRes = await checkInApi.getTodayStatus()
      
      // 计算下一个里程碑
      const milestones = [10, 100, 500, 1000, 5000, 10000]
      const nextMilestone = milestones.find(m => m > user.totalLingzhi) || milestones[milestones.length - 1]
      const prevMilestone = milestones.filter(m => m < user.totalLingzhi).pop() || 0
      const progress = ((user.totalLingzhi - prevMilestone) / (nextMilestone - prevMilestone)) * 100

      setStats({
        todayLingzhi: checkInRes.data.lingzhi || 0,
        checkedIn: checkInRes.data.checkedIn,
        streak: Math.floor(Math.random() * 10) + 1, // 模拟数据
        nextMilestone,
        progress
      })
    } catch (error) {
      console.error('加载仪表盘数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckIn = async () => {
    if (!stats.checkedIn) {
      setCheckInLoading(true)
      try {
        await checkInApi.checkIn()
        await loadDashboardData()
      } catch (error) {
        console.error('签到失败:', error)
      } finally {
        setCheckInLoading(false)
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 欢迎消息 */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-8 text-white shadow-xl">
        <h1 className="text-3xl font-bold mb-2">
          欢迎回来，{user?.username}！
        </h1>
        <p className="opacity-90">
          今天也是创造价值的一天，{user?.totalLingzhi} 灵值正在增长中
        </p>
      </div>

      {/* 核心数据卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 总灵值 */}
        <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex items-center text-green-500 text-sm font-semibold">
              <ArrowUpRight className="w-4 h-4 mr-1" />
              <span>+{((user?.totalLingzhi || 0) * 0.012).toFixed(1)}%</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900">{user?.totalLingzhi || 0}</div>
          <div className="text-gray-500 text-sm mt-1">总灵值</div>
          <div className="text-primary-600 font-semibold mt-2">
            {((user?.totalLingzhi || 0) * 0.1).toFixed(1)} 元
          </div>
        </div>

        {/* 今日签到 */}
        <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-secondary-600" />
            </div>
            <div className="flex items-center text-green-500 text-sm font-semibold">
              <Clock className="w-4 h-4 mr-1" />
              <span>连续 {stats.streak} 天</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900">{stats.todayLingzhi}</div>
          <div className="text-gray-500 text-sm mt-1">今日灵值</div>
          <button
            onClick={handleCheckIn}
            disabled={stats.checkedIn || checkInLoading}
            className={`mt-4 w-full py-2 rounded-lg font-semibold transition-all ${
              stats.checkedIn
                ? 'bg-green-100 text-green-700 cursor-default'
                : 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white hover:from-primary-600 hover:to-secondary-600'
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
              '立即签到 (+10灵值)'
            )}
          </button>
        </div>

        {/* 下一个里程碑 */}
        <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full font-semibold">
              目标
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900">{stats.nextMilestone}</div>
          <div className="text-gray-500 text-sm mt-1">下一个里程碑</div>
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>进度</span>
              <span>{stats.progress.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full transition-all"
                style={{ width: `${stats.progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* 合伙人资格 */}
        <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex items-center text-purple-500 text-sm font-semibold">
              <Star className="w-4 h-4 mr-1" />
              <span>{user?.totalLingzhi! >= 10000 ? '已达成' : '进行中'}</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900">{10000}</div>
          <div className="text-gray-500 text-sm mt-1">合伙人资格要求</div>
          <div className="mt-4 text-sm">
            <span className="text-gray-600">距离资格还差：</span>
            <span className="text-primary-600 font-semibold">
              {Math.max(0, 10000 - user!.totalLingzhi)} 灵值
            </span>
          </div>
        </div>
      </div>

      {/* 快速入口 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl p-6 border border-pink-200 hover:shadow-lg transition-shadow cursor-pointer">
          <h3 className="text-lg font-semibold text-pink-800 mb-2">💬 开始对话</h3>
          <p className="text-pink-600 text-sm">与智能体对话，探索文化价值，获得灵值</p>
        </div>

        <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-6 border border-teal-200 hover:shadow-lg transition-shadow cursor-pointer">
          <h3 className="text-lg font-semibold text-teal-800 mb-2">💰 经济模型</h3>
          <p className="text-teal-600 text-sm">查看收入预测，规划财富增长路径</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200 hover:shadow-lg transition-shadow cursor-pointer">
          <h3 className="text-lg font-semibold text-purple-800 mb-2">🏆 合伙人计划</h3>
          <p className="text-purple-600 text-sm">了解合伙人权益，申请成为合伙人</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
