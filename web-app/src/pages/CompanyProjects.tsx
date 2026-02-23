import { useState, useEffect } from 'react'
import { FolderKanban, GitBranch, Calendar, Users, TrendingUp, Search, Filter, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface Project {
  id: number
  name: string
  description: string
  status: 'planning' | 'in_progress' | 'completed' | 'paused'
  progress: number
  participants: number
  created_at: string
  updated_at: string
}

const CompanyProjects = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('all')

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      // TODO: 从API获取项目动态
      const mockData: Project[] = [
        {
          id: 1,
          name: '西安美学侦探',
          description: '将传统文化与现代科技相结合，打造独特的数字文化体验项目。用户可以通过互动方式探索西安的美学文化。',
          status: 'in_progress',
          progress: 65,
          participants: 23,
          created_at: '2026-02-01 10:00:00',
          updated_at: '2026-02-07 09:30:00'
        },
        {
          id: 2,
          name: '中视频平台',
          description: '打造中短视频内容生态，支持创作者发布和管理优质内容，构建完善的内容变现机制。',
          status: 'in_progress',
          progress: 80,
          participants: 45,
          created_at: '2026-01-15 14:00:00',
          updated_at: '2026-02-06 16:20:00'
        },
        {
          id: 3,
          name: '合伙人计划2.0',
          description: '升级合伙人体系，引入更多权益和激励机制，为合伙人创造更多收益机会。',
          status: 'completed',
          progress: 100,
          participants: 156,
          created_at: '2026-01-01 09:00:00',
          updated_at: '2026-02-05 11:00:00'
        },
        {
          id: 4,
          name: '智能体生态建设',
          description: '构建完整的智能体生态系统，包括智能体创建、训练、部署和商业化全链路服务。',
          status: 'planning',
          progress: 15,
          participants: 8,
          created_at: '2026-02-05 10:00:00',
          updated_at: '2026-02-07 08:00:00'
        }
      ]
      setProjects(mockData)
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const statusConfig = {
    planning: { label: '规划中', icon: Clock, color: 'text-[#FFB800]', bg: 'bg-[#FFB800]/10' },
    in_progress: { label: '进行中', icon: TrendingUp, color: 'text-[#00C3FF]', bg: 'bg-[#00C3FF]/10' },
    completed: { label: '已完成', icon: CheckCircle, color: 'text-[#00FF88]', bg: 'bg-[#00FF88]/10' },
    paused: { label: '已暂停', icon: AlertCircle, color: 'text-[#FF6B6B]', bg: 'bg-[#FF6B6B]/10' }
  }

  const filteredProjects = projects.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || item.status === selectedStatus
    return matchesSearch && matchesStatus
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            项目动态
          </h1>
          <p className="text-[#B4C7E7]">跟踪公司项目进展，了解最新开发动态</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总项目数</div>
            <div className="text-2xl font-bold text-white">{projects.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">进行中</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {projects.filter(p => p.status === 'in_progress').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">已完成</div>
            <div className="text-2xl font-bold text-[#00FF88]">
              {projects.filter(p => p.status === 'completed').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">参与人数</div>
            <div className="text-2xl font-bold text-[#FFB800]">
              {projects.reduce((sum, p) => sum + p.participants, 0)}
            </div>
          </div>
        </div>

        {/* 筛选栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索项目..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setSelectedStatus('all')}
                className={`px-4 py-2.5 rounded-lg transition-all ${
                  selectedStatus === 'all'
                    ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]'
                    : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20'
                }`}
              >
                全部
              </button>
              {Object.entries(statusConfig).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => setSelectedStatus(key)}
                  className={`px-4 py-2.5 rounded-lg transition-all ${
                    selectedStatus === key
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

        {/* 项目列表 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProjects.map(item => {
            const config = statusConfig[item.status]
            const Icon = config.icon
            return (
              <div key={item.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-8 h-8 ${config.bg} rounded-lg flex items-center justify-center`}>
                        <Icon className={`w-4 h-4 ${config.color}`} />
                      </div>
                      <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{item.name}</h3>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-[#00C3FF]">{item.progress}%</div>
                    <div className="text-xs text-[#B4C7E7]">完成度</div>
                  </div>
                </div>

                <p className="text-[#B4C7E7] text-sm mb-4 line-clamp-2">{item.description}</p>

                {/* 进度条 */}
                <div className="mb-4">
                  <div className="w-full bg-[#0A0D18] rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] h-full transition-all duration-500"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>

                {/* 项目信息 */}
                <div className="flex items-center justify-between text-xs text-[#B4C7E7]/60">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>{item.participants} 人</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(item.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button className="text-[#00C3FF] hover:underline">查看详情</button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default CompanyProjects
