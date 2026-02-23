import { useState, useEffect } from 'react'
import { Bell, Search, Filter, AlertTriangle, Info, CheckCircle, XCircle, Clock, Zap } from 'lucide-react'

interface InfoItem {
  id: number
  title: string
  content: string
  type: 'urgent' | 'info' | 'success' | 'error'
  priority: 'high' | 'medium' | 'low'
  created_at: string
  is_read: boolean
}

const CompanyInfo = () => {
  const [infos, setInfos] = useState<InfoItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedPriority, setSelectedPriority] = useState('all')

  useEffect(() => {
    loadInfos()
  }, [])

  const loadInfos = async () => {
    try {
      // TODO: 从API获取信息动态
      const mockData: InfoItem[] = [
        {
          id: 1,
          title: '系统维护通知',
          content: '系统将于2026年2月10日02:00-04:00进行例行维护，届时服务将暂停。请提前做好准备，感谢理解。',
          type: 'urgent',
          priority: 'high',
          created_at: '2026-02-07 09:00:00',
          is_read: false
        },
        {
          id: 2,
          title: '新功能上线公告',
          content: '数字生态模块已正式上线！现在您可以访问文化知识库、文化转译和文化项目页面，体验全新的数字文化服务。',
          type: 'success',
          priority: 'medium',
          created_at: '2026-02-06 10:00:00',
          is_read: false
        },
        {
          id: 3,
          title: '安全提醒',
          content: '近期发现部分用户账户存在异常登录行为。请定期修改密码，并开启二次验证以确保账户安全。',
          type: 'error',
          priority: 'high',
          created_at: '2026-02-05 14:30:00',
          is_read: true
        },
        {
          id: 4,
          title: '活动通知：新人注册送灵值',
          content: '新用户注册即送100灵值，邀请好友再送50灵值！活动时间：2026年2月1日-2月28日。',
          type: 'info',
          priority: 'low',
          created_at: '2026-02-01 10:00:00',
          is_read: true
        }
      ]
      setInfos(mockData)
    } catch (error) {
      console.error('Failed to load infos:', error)
    }
  }

  const typeConfig = {
    urgent: { label: '紧急', icon: AlertTriangle, color: 'text-[#FF6B6B]', bg: 'bg-[#FF6B6B]/10' },
    info: { label: '通知', icon: Info, color: 'text-[#00C3FF]', bg: 'bg-[#00C3FF]/10' },
    success: { label: '成功', icon: CheckCircle, color: 'text-[#00FF88]', bg: 'bg-[#00FF88]/10' },
    error: { label: '错误', icon: XCircle, color: 'text-[#FF6B6B]', bg: 'bg-[#FF6B6B]/10' }
  }

  const priorityConfig = {
    high: { label: '高', color: 'text-[#FF6B6B]' },
    medium: { label: '中', color: 'text-[#FFB800]' },
    low: { label: '低', color: 'text-[#00C3FF]' }
  }

  const filteredInfos = infos.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'all' || item.type === selectedType
    const matchesPriority = selectedPriority === 'all' || item.priority === selectedPriority
    return matchesSearch && matchesType && matchesPriority
  })

  const unreadCount = infos.filter(i => !i.is_read).length

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        {/* 头部 */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
              信息动态
            </h1>
            <p className="text-[#B4C7E7]">获取最新的系统通知和重要信息</p>
          </div>
          {unreadCount > 0 && (
            <div className="flex items-center gap-2 bg-[#FF6B6B]/20 text-[#FF6B6B] px-4 py-2 rounded-lg">
              <Zap className="w-4 h-4" />
              <span className="text-sm font-medium">{unreadCount} 条未读</span>
            </div>
          )}
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00C3FF]/20 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-[#00C3FF]" />
              </div>
              <span className="text-[#B4C7E7]">总信息数</span>
            </div>
            <div className="text-3xl font-bold text-white">{infos.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#FF6B6B]/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-[#FF6B6B]" />
              </div>
              <span className="text-[#B4C7E7]">紧急信息</span>
            </div>
            <div className="text-3xl font-bold text-[#FF6B6B]">
              {infos.filter(i => i.type === 'urgent').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00FF88]/20 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-[#00FF88]" />
              </div>
              <span className="text-[#B4C7E7]">已读</span>
            </div>
            <div className="text-3xl font-bold text-[#00FF88]">
              {infos.filter(i => i.is_read).length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00C3FF]/20 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-[#00C3FF]" />
              </div>
              <span className="text-[#B4C7E7]">未读</span>
            </div>
            <div className="text-3xl font-bold text-[#00C3FF]">
              {infos.filter(i => !i.is_read).length}
            </div>
          </div>
        </div>

        {/* 筛选栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索信息..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
              >
                <option value="all" className="bg-[#121A2F]">全部类型</option>
                {Object.entries(typeConfig).map(([key, config]) => (
                  <option key={key} value={key} className="bg-[#121A2F]">{config.label}</option>
                ))}
              </select>
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
              >
                <option value="all" className="bg-[#121A2F]">全部优先级</option>
                {Object.entries(priorityConfig).map(([key, config]) => (
                  <option key={key} value={key} className="bg-[#121A2F]">{config.label}优先级</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 信息列表 */}
        <div className="space-y-4">
          {filteredInfos.map(item => {
            const config = typeConfig[item.type]
            const Icon = config.icon
            return (
              <div key={item.id} className={`bg-[#121A2F] border ${item.is_read ? 'border-[#00C3FF]/20' : 'border-[#00C3FF]/50'} rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 ${config.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-6 h-6 ${config.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 ${config.bg} ${config.color} rounded text-xs font-medium`}>
                            {config.label}
                          </span>
                          <span className={`text-xs ${priorityConfig[item.priority].color}`}>
                            {priorityConfig[item.priority].label}优先级
                          </span>
                          {!item.is_read && (
                            <span className="w-2 h-2 bg-[#FF6B6B] rounded-full" />
                          )}
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                      </div>
                    </div>
                    <p className="text-[#B4C7E7] text-sm mb-3">{item.content}</p>
                    <div className="flex items-center gap-4 text-xs text-[#B4C7E7]/60">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{new Date(item.created_at).toLocaleString()}</span>
                      </div>
                      <span className={item.is_read ? 'text-[#B4C7E7]/40' : 'text-[#00C3FF]'}>
                        {item.is_read ? '已读' : '未读'}
                      </span>
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

export default CompanyInfo
