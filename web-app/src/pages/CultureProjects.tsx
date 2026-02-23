import { useState, useEffect } from 'react'
import { Layers, Search, Filter, TrendingUp, Users, Calendar, Award, ArrowRight, MapPin, Camera, Sparkles } from 'lucide-react'

interface CultureProject {
  id: number
  title: string
  description: string
  category: string
  budget: number
  lingzhi_reward: number
  deadline: string
  participants: number
  status: 'open' | 'ongoing' | 'completed'
  tags: string[]
  location?: string
}

const CultureProjects = () => {
  const [projects, setProjects] = useState<CultureProject[]>([])
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    // 模拟数据加载
    setProjects([
      {
        id: 2,
        title: '西安美学侦探',
        description: '探索城市美学，发现西安之美。通过摄影、文字等方式记录城市文化美学，分享独特视角。项目旨在将西安的文化美学元素数字化，转化为可分享和交易的数字资产。',
        category: 'design',
        budget: 8000,
        lingzhi_reward: 400,
        deadline: '2025-12-31',
        participants: 12,
        status: 'open',
        tags: ['摄影', '美学', '文化转译', '数字资产'],
        location: '西安市',
      },
      {
        id: 3,
        title: '文化基因解码计划',
        description: '对西安文化基因进行系统解码，建立文化基因图谱。通过大数据分析和AI技术，深度挖掘文化内涵。',
        category: 'research',
        budget: 12000,
        lingzhi_reward: 600,
        deadline: '2025-12-31',
        participants: 8,
        status: 'open',
        tags: ['文化研究', 'AI解码', '基因图谱'],
      },
      {
        id: 4,
        title: '古城墙数字化保护',
        description: '利用3D扫描和VR技术，对西安古城墙进行数字化建模和保存，为文化传承提供技术支持。',
        category: 'technology',
        budget: 15000,
        lingzhi_reward: 750,
        deadline: '2025-06-30',
        participants: 25,
        status: 'ongoing',
        tags: ['3D扫描', 'VR技术', '数字保护'],
        location: '西安市城墙景区',
      },
      {
        id: 5,
        title: '大雁塔文化解读',
        description: '深入解读大雁塔的历史文化背景，挖掘佛教文化在西安的传承与发展。',
        category: 'history',
        budget: 6000,
        lingzhi_reward: 300,
        deadline: '2025-12-31',
        participants: 0,
        status: 'open',
        tags: ['历史研究', '佛教文化', '文化遗产'],
      },
      {
        id: 6,
        title: '秦岭文化生态调研',
        description: '对秦岭地区的文化生态进行全面调研，记录传统文化和民俗风情。',
        category: 'research',
        budget: 10000,
        lingzhi_reward: 500,
        deadline: '2025-10-31',
        participants: 15,
        status: 'ongoing',
        tags: ['生态调研', '民俗文化', '秦岭文化'],
        location: '秦岭山脉',
      },
      {
        id: 7,
        title: '丝绸之路文化地图',
        description: '绘制丝绸之路文化地图，标注重要文化节点和历史遗迹，展示文化交流的脉络。',
        category: 'design',
        budget: 20000,
        lingzhi_reward: 1000,
        deadline: '2025-09-30',
        participants: 30,
        status: 'ongoing',
        tags: ['地图设计', '丝绸之路', '文化交流'],
      },
      {
        id: 8,
        title: '唐诗词文化数字展',
        description: '将唐代诗词数字化展示，通过AR技术让用户沉浸式体验诗词意境。',
        category: 'technology',
        budget: 25000,
        lingzhi_reward: 1250,
        deadline: '2025-11-30',
        participants: 18,
        status: 'open',
        tags: ['AR技术', '唐诗', '数字化展示'],
      },
      {
        id: 9,
        title: '陕西非遗传承计划',
        description: '记录和传承陕西非物质文化遗产，包括皮影戏、秦腔、剪纸等传统艺术形式。',
        category: 'culture',
        budget: 18000,
        lingzhi_reward: 900,
        deadline: '2026-03-31',
        participants: 22,
        status: 'open',
        tags: ['非遗传承', '皮影戏', '秦腔', '剪纸'],
        location: '陕西省',
      },
    ])
  }, [])

  const statusOptions = [
    { id: 'all', name: '全部状态' },
    { id: 'open', name: '招募中' },
    { id: 'ongoing', name: '进行中' },
    { id: 'completed', name: '已完成' },
  ]

  const filteredProjects = projects.filter((project) => {
    const matchStatus = selectedStatus === 'all' || project.status === selectedStatus
    const matchSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        project.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchStatus && matchSearch
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'ongoing':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'completed':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open':
        return '招募中'
      case 'ongoing':
        return '进行中'
      case 'completed':
        return '已完成'
      default:
        return status
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0D18] via-[#121A2F] to-[#0A0D18]">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0A0D18] via-[#1A2332] to-[#0A0D18] border-b border-[#00C3FF]/20 pt-20 pb-8">
        <div className="container mx-auto px-4">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] flex items-center justify-center">
                <Layers className="w-6 h-6 text-white" />
              </div>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
              文化项目
            </h1>
            <p className="text-[#B4C7E7] text-lg">
              参与文化项目，推动文化数字化转译
            </p>
          </div>

          {/* Search and Filter */}
          <div className="max-w-3xl mx-auto">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#B4C7E7]/50" />
                <input
                  type="text"
                  placeholder="搜索项目..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg text-white placeholder-[#B4C7E7]/50 focus:outline-none focus:border-[#00C3FF]"
                />
              </div>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-4 py-3 bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg text-white focus:outline-none focus:border-[#00C3FF]"
              >
                {statusOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">项目总数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {projects.length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">招募中</div>
            <div className="text-2xl font-bold text-green-400">
              {projects.filter(p => p.status === 'open').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总预算</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {projects.reduce((sum, p) => sum + p.budget, 0).toLocaleString()}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">灵值奖励</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {projects.reduce((sum, p) => sum + p.lingzhi_reward, 0)}
            </div>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl overflow-hidden hover:border-[#00C3FF]/50 transition-all group"
            >
              {/* Project Header */}
              <div className="bg-gradient-to-r from-[#00C3FF]/10 to-[#00E0FF]/5 border-b border-[#00C3FF]/10 p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-white font-bold text-xl mb-2 group-hover:text-[#00C3FF] transition-colors">
                      {project.title}
                    </h3>
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(project.status)}`}>
                      {getStatusText(project.status)}
                    </span>
                  </div>
                  {project.location && (
                    <div className="flex items-center gap-1 text-[#B4C7E7] text-sm">
                      <MapPin className="w-4 h-4" />
                      {project.location}
                    </div>
                  )}
                </div>

                <p className="text-[#B4C7E7] text-sm leading-relaxed">
                  {project.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mt-4">
                  {project.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="text-xs text-[#00C3FF] bg-[#00C3FF]/10 px-2 py-1 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Project Stats */}
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <TrendingUp className="w-5 h-5 text-[#00C3FF] mx-auto mb-1" />
                    <div className="text-white font-semibold">{project.budget.toLocaleString()}</div>
                    <div className="text-[#B4C7E7] text-xs">灵值预算</div>
                  </div>
                  <div className="text-center">
                    <Award className="w-5 h-5 text-[#00C3FF] mx-auto mb-1" />
                    <div className="text-white font-semibold">{project.lingzhi_reward}</div>
                    <div className="text-[#B4C7E7] text-xs">参与奖励</div>
                  </div>
                  <div className="text-center">
                    <Users className="w-5 h-5 text-[#00C3FF] mx-auto mb-1" />
                    <div className="text-white font-semibold">{project.participants}</div>
                    <div className="text-[#B4C7E7] text-xs">参与人数</div>
                  </div>
                  <div className="text-center">
                    <Calendar className="w-5 h-5 text-[#00C3FF] mx-auto mb-1" />
                    <div className="text-white font-semibold text-sm">
                      {project.deadline.split('-')[1]}-{project.deadline.split('-')[2]}
                    </div>
                    <div className="text-[#B4C7E7] text-xs">截止日期</div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button className="flex-1 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-[#0A0D18] font-semibold py-2.5 px-4 rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    开始转译
                  </button>
                  <button className="flex items-center gap-2 text-[#00C3FF] hover:text-[#00E0FF] border border-[#00C3FF]/30 px-4 py-2.5 rounded-lg hover:border-[#00C3FF] transition-all">
                    查看详情
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-12 text-center">
            <Layers className="w-16 h-16 text-[#B4C7E7]/30 mx-auto mb-4" />
            <h3 className="text-white text-lg font-semibold mb-2">暂无匹配的项目</h3>
            <p className="text-[#B4C7E7]">尝试调整搜索条件或选择其他状态</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CultureProjects
