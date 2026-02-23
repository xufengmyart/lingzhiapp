import { useState, useEffect } from 'react'
import { Users, TrendingUp, Calendar, Search, Filter, UserPlus, Activity, Shield, Star, Award, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react'

interface UserActivity {
  id: number
  username: string
  avatar?: string
  action: string
  description: string
  type: 'register' | 'active' | 'upgrade' | 'achievement' | 'consume' | 'contribution'
  createdAt: string
  lingzhi: number
}

interface PaginationInfo {
  page: number
  page_size: number
  total: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

const CompanyUsers = () => {
  const [activities, setActivities] = useState<UserActivity[]>([])
  const [pagination, setPagination] = useState<PaginationInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const [isRealtime, setIsRealtime] = useState(false)
  const [newActivityCount, setNewActivityCount] = useState(0)

  // 加载用户活动
  useEffect(() => {
    loadActivities(currentPage)
  }, [currentPage, selectedType])

  // 连接WebSocket
  useEffect(() => {
    let socket: WebSocket | null = null

    if (isRealtime) {
      try {
        // 连接WebSocket - 使用相对路径或环境变量
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsHost = window.location.host
        socket = new WebSocket(`${wsProtocol}//${wsHost}/socket.io/?transport=websocket`)

        socket.onopen = () => {
          console.log('WebSocket已连接')
        }

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data[0] === 'new_activity') {
              setNewActivityCount(prev => prev + 1)
              console.log('收到新活动:', data[1])
            }
          } catch (e) {
            console.error('解析WebSocket消息失败:', e)
          }
        }

        socket.onerror = (error) => {
          console.error('WebSocket错误:', error)
        }

        socket.onclose = () => {
          console.log('WebSocket已断开')
        }
      } catch (error) {
        console.error('WebSocket连接失败:', error)
        setIsRealtime(false)
      }
    }

    return () => {
      if (socket) {
        socket.close()
      }
    }
  }, [isRealtime])

  const loadActivities = async (page: number = 1) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      })

      if (selectedType !== 'all') {
        params.append('type', selectedType)
      }

      if (searchQuery) {
        params.append('username', searchQuery)
      }

      const response = await fetch(`/api/company/users/activities?${params.toString()}`);
      const result = await response.json();

      if (result.success && result.data) {
        setActivities(result.data)
        setPagination(result.pagination)
        setNewActivityCount(0) // 重置新活动计数
      } else {
        // 降级到模拟数据
        const mockData: UserActivity[] = [
          {
            id: 1,
            username: '管理员',
            action: '注册加入',
            description: '新用户注册，获得新人奖励100灵值',
            type: 'register',
            createdAt: '2026-02-18 05:57:36',
            lingzhi: 110
          },
          {
            id: 2,
            username: 'te***',
            action: '注册加入',
            description: '新用户注册，获得新人奖励110灵值',
            type: 'register',
            createdAt: '2026-02-14 00:04:08',
            lingzhi: 110
          },
          {
            id: 3,
            username: 'pa***',
            action: '活跃用户',
            description: '完善个人资料，获得20灵值',
            type: 'active',
            createdAt: '2026-02-18 16:34:00',
            lingzhi: 20
          },
          {
            id: 4,
            username: 'ad***',
            action: '活跃用户',
            description: '完善个人资料，获得20灵值',
            type: 'active',
            createdAt: '2026-02-18 16:45:49',
            lingzhi: 20
          },
          {
            id: 5,
            username: 'te***',
            action: '完成签到',
            description: '每日签到，获得10灵值',
            type: 'achievement',
            createdAt: '2026-02-20 10:30:00',
            lingzhi: 10
          },
          {
            id: 6,
            username: 'pa***',
            action: '完成签到',
            description: '每日签到，获得10灵值',
            type: 'achievement',
            createdAt: '2026-02-20 11:15:00',
            lingzhi: 10
          },
          {
            id: 7,
            username: 'ad***',
            action: '完成签到',
            description: '每日签到，获得10灵值',
            type: 'achievement',
            createdAt: '2026-02-20 12:00:00',
            lingzhi: 10
          },
          {
            id: 8,
            username: '管理员',
            action: '活跃用户',
            description: '管理系统配置',
            type: 'active',
            createdAt: '2026-02-20 13:00:00',
            lingzhi: 0
          },
          {
            id: 9,
            username: '用户8',
            action: '注册加入',
            description: '新用户注册，获得新人奖励120灵值',
            type: 'register',
            createdAt: '2026-02-18 20:17:46',
            lingzhi: 120
          },
          {
            id: 10,
            username: '用户9',
            action: '添加私有资源',
            description: '添加政府招商引资资源',
            type: 'active',
            createdAt: '2026-02-20 13:59:30',
            lingzhi: 50
          }
        ]
        setActivities(mockData)
        setPagination({
          page: 1,
          page_size: pageSize,
          total: mockData.length,
          total_pages: 1,
          has_next: false,
          has_prev: false
        })
      }
    } catch (error) {
      console.error('Failed to load user activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setCurrentPage(1)
    loadActivities(1)
  }

  const handleTypeChange = (type: string) => {
    setSelectedType(type)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const typeConfig = {
    all: { label: '全部', icon: Filter, color: 'text-white', bg: 'bg-white/10' },
    register: { label: '注册', icon: UserPlus, color: 'text-[#00FF88]', bg: 'bg-[#00FF88]/10' },
    active: { label: '活跃', icon: Activity, color: 'text-[#00C3FF]', bg: 'bg-[#00C3FF]/10' },
    upgrade: { label: '升级', icon: Award, color: 'text-[#FFB800]', bg: 'bg-[#FFB800]/10' },
    achievement: { label: '成就', icon: Star, color: 'text-[#FF6B6B]', bg: 'bg-[#FF6B6B]/10' },
    consume: { label: '消费', icon: TrendingUp, color: 'text-[#FFA07A]', bg: 'bg-[#FFA07A]/10' },
    contribution: { label: '贡献', icon: Shield, color: 'text-[#DDA0DD]', bg: 'bg-[#DDA0DD]/10' }
  }

  const filteredActivities = activities.filter(activity => {
    const matchesSearch = 
      activity.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.type?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'all' || activity.type === selectedType
    return matchesSearch && matchesType
  })

  // 获取当前页的活动
  const paginatedActivities = filteredActivities.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  return (
    <div className="min-h-screen bg-[#0A0D18]">
      {/* 头部 */}
      <div className="bg-[#121A2F] border-b border-[#00C3FF]/20">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">用户活动</h1>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00FF88]/20 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-[#00FF88]" />
              </div>
              <span className="text-[#B4C7E7]">总用户</span>
            </div>
            <div className="text-3xl font-bold text-[#00FF88]">{activities.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00C3FF]/20 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-[#00C3FF]" />
              </div>
              <span className="text-[#B4C7E7]">活跃用户</span>
            </div>
            <div className="text-3xl font-bold text-[#00C3FF]">
              {activities.filter(a => a.type === 'active').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#FF6B6B]/20 rounded-lg flex items-center justify-center">
                <Award className="w-5 h-5 text-[#FF6B6B]" />
              </div>
              <span className="text-[#B4C7E7]">灵值流动</span>
            </div>
            <div className="text-3xl font-bold text-[#FF6B6B]">{totalLingzhi.toLocaleString()}</div>
          </div>
        </div>

        {/* 筛选栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索用户或动态..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setSelectedType('all')}
                className={`px-4 py-2.5 rounded-lg transition-all ${
                  selectedType === 'all'
                    ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]'
                    : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20'
                }`}
              >
                全部
              </button>
              {Object.entries(typeConfig).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => setSelectedType(key)}
                  className={`px-4 py-2.5 rounded-lg transition-all ${
                    selectedType === key
                      ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]'
                      : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20'
                  }`}
                >
                  {config.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 动态列表 */}
        <div className="space-y-4">
          {filteredActivities.map(item => {
            const config = typeConfig[item.type]
            const Icon = config.icon
            return (
              <div key={item.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#00C3FF] to-[#00E0FF] rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {(item?.username || "?").charAt(0)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 bg-[#00C3FF]/10 text-[#00C3FF] rounded text-xs font-medium">
                            {item.username}
                          </span>
                          <div className={`flex items-center gap-1 px-2 py-0.5 ${config.bg} ${config.color} rounded text-xs`}>
                            <Icon className="w-3 h-3" />
                            <span>{config.label}</span>
                          </div>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-1">{item.action}</h3>
                      </div>
                    </div>
                    <p className="text-[#B4C7E7] text-sm mb-3">{item.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-xs text-[#B4C7E7]/60">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(item.createdAt).toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Award className="w-4 h-4 text-[#FFB800]" />
                          <span className="text-[#FFB800]">+{item.lingzhi} 灵值</span>
                        </div>
                      </div>
                      <button className="text-[#00C3FF] text-xs hover:underline">查看用户</button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default CompanyUsers
