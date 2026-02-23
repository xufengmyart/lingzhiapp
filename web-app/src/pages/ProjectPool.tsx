import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Search, Filter, Plus, Eye, Calendar, DollarSign, Users, Clock, CheckCircle, AlertCircle } from 'lucide-react'

interface Project {
  id: string
  title: string
  description: string
  category: string
  budget: number
  deadline: string
  participants: number
  status: 'open' | 'in_progress' | 'completed'
  lingzhi_reward: number
  requirements: string[]
}

// 模拟项目数据
const MOCK_PROJECTS: Project[] = [
  {
    id: '1',
    title: '灵值生态园官网设计升级',
    description: '对灵值生态园官方网站进行全面UI/UX升级，提升用户体验和视觉吸引力',
    category: 'design',
    budget: 50000,
    deadline: '2024-03-15',
    participants: 12,
    status: 'in_progress',
    lingzhi_reward: 1000,
    requirements: ['3年以上设计经验', '熟悉Web3设计', '提供作品集']
  },
  {
    id: '2',
    title: '智能合约审计服务',
    description: '对灵值通证（LYZ）和SBT合约进行安全审计，确保系统安全性',
    category: 'development',
    budget: 80000,
    deadline: '2024-02-28',
    participants: 5,
    status: 'open',
    lingzhi_reward: 1500,
    requirements: ['有智能合约审计经验', '熟悉Solidity', '提供过往审计报告']
  },
  {
    id: '3',
    title: '社区内容创作激励计划',
    description: '创作高质量的灵值生态园相关内容，包括文章、视频、社交媒体内容',
    category: 'content',
    budget: 30000,
    deadline: '2024-04-01',
    participants: 28,
    status: 'open',
    lingzhi_reward: 500,
    requirements: ['具备内容创作能力', '熟悉区块链文化', '有自媒体运营经验者优先']
  },
  {
    id: '4',
    title: '全球化市场推广策略研究',
    description: '研究灵值生态园在海外市场的推广策略和本地化方案',
    category: 'marketing',
    budget: 60000,
    deadline: '2024-03-30',
    participants: 8,
    status: 'in_progress',
    lingzhi_reward: 1200,
    requirements: ['有海外市场推广经验', '了解区块链行业', '具备双语能力']
  },
  {
    id: '5',
    title: 'DAO治理机制优化研究',
    description: '研究并设计更高效的DAO治理机制，提升社区参与度和决策效率',
    category: 'research',
    budget: 40000,
    deadline: '2024-05-01',
    participants: 15,
    status: 'open',
    lingzhi_reward: 800,
    requirements: ['了解DAO治理机制', '有Web3社区运营经验', '具备研究分析能力']
  },
  {
    id: '6',
    title: '移动端App开发',
    description: '开发灵值生态园移动端应用，支持iOS和Android平台',
    category: 'development',
    budget: 120000,
    deadline: '2024-06-30',
    participants: 20,
    status: 'open',
    lingzhi_reward: 2000,
    requirements: ['有移动端开发经验', '熟悉React Native或Flutter', '有完整项目经验']
  },
  {
    id: '7',
    title: '中视频创作项目',
    description: '基于灵值生态园的中视频内容创作，打造高质量、有深度的视频内容，提升品牌影响力',
    category: 'content',
    budget: 100000,
    deadline: '2024-04-30',
    participants: 35,
    status: 'in_progress',
    lingzhi_reward: 1800,
    requirements: ['有视频创作经验', '熟悉短视频/中视频平台', '具备内容策划能力', '有账号运营经验']
  },
  {
    id: '8',
    title: '西安美学侦探项目',
    description: '深入挖掘西安美学文化，探索传统与现代的融合，打造具有地域特色的美学内容IP',
    category: 'research',
    budget: 80000,
    deadline: '2024-05-15',
    participants: 18,
    status: 'open',
    lingzhi_reward: 1500,
    requirements: ['对西安文化有深入了解', '具备美学理论素养', '有内容创作能力', '擅长摄影或视频制作']
  },
  {
    id: '9',
    title: '合伙人计划',
    description: '招募生态合伙人，共同建设灵值生态园，共享生态发展红利，实现合作共赢',
    category: 'business',
    budget: 200000,
    deadline: '2024-06-01',
    participants: 50,
    status: 'open',
    lingzhi_reward: 3000,
    requirements: ['认同灵值生态园理念', '有相关行业资源', '具备团队管理能力', '有创业或合作经验']
  },
  {
    id: '10',
    title: '智能体生态建设',
    description: '构建灵值生态园智能体系统，实现智能对话、智能推荐、智能分析等功能，提升用户体验',
    category: 'development',
    budget: 150000,
    deadline: '2024-07-15',
    participants: 25,
    status: 'in_progress',
    lingzhi_reward: 2500,
    requirements: ['熟悉AI和NLP技术', '有智能体开发经验', '具备系统架构能力', '了解区块链和Web3']
  }
]

const ProjectPool = () => {
  const { user } = useAuth()
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')

  useEffect(() => {
    // TODO: 从API获取项目数据
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await fetch('/api/projects', {
        signal: AbortSignal.timeout(5000) // 5秒超时
      })
      if (response.ok) {
        const data = await response.json()
        if (Array.isArray(data) && data.length > 0) {
          console.log('✅ 从API加载项目数据:', data.length, '个项目')
          setProjects(data)
        } else {
          console.log('⚠️ API返回空数据，使用模拟数据')
          setProjects(MOCK_PROJECTS)
        }
      } else {
        console.log('⚠️ API请求失败，使用模拟数据')
        setProjects(MOCK_PROJECTS)
      }
    } catch (error) {
      console.log('⚠️ API调用异常，使用模拟数据:', error)
      setProjects(MOCK_PROJECTS)
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || project.category === selectedCategory
    const matchesStatus = selectedStatus === 'all' || project.status === selectedStatus
    return matchesSearch && matchesCategory && matchesStatus
  })

  const categories = ['all', 'design', 'development', 'content', 'marketing', 'research', 'business']
  const statusMap = {
    open: { label: '招募中', icon: AlertCircle, color: 'text-[#00C3FF]' },
    in_progress: { label: '进行中', icon: Clock, color: 'text-[#FFB800]' },
    completed: { label: '已完成', icon: CheckCircle, color: 'text-[#00FF88]' }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-16">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            项目资源池
          </h1>
          <p className="text-[#B4C7E7] text-sm sm:text-base">发现并参与优质项目，与团队共创价值</p>
        </div>

        {/* 搜索和筛选 */}
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
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
            >
              {categories.map(cat => (
                <option key={cat} value={cat} className="bg-[#121A2F]">
                  {cat === 'all' ? '所有类别' : cat}
                </option>
              ))}
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
            >
              {Object.entries(statusMap).map(([key, val]) => (
                <option key={key} value={key} className="bg-[#121A2F]">
                  {val.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 项目统计 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总项目数</div>
            <div className="text-2xl font-bold text-white">{projects.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">招募中</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {projects.filter(p => p.status === 'open').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总预算</div>
            <div className="text-2xl font-bold text-[#00FF88]">
              {projects.reduce((sum, p) => sum + p.budget, 0).toLocaleString()} 灵值
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">参与人数</div>
            <div className="text-2xl font-bold text-[#FFB800]">
              {projects.reduce((sum, p) => sum + p.participants, 0)}
            </div>
          </div>
        </div>

        {/* 项目列表 */}
        <div className="space-y-4">
          {filteredProjects.map(project => {
            const statusInfo = statusMap[project.status]
            const StatusIcon = statusInfo.icon
            return (
              <div key={project.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-xl font-bold text-white">{project.title}</h3>
                      <span className={`flex items-center gap-1.5 text-sm font-medium ${statusInfo.color} flex-shrink-0`}>
                        <StatusIcon className="w-4 h-4" />
                        {statusInfo.label}
                      </span>
                    </div>
                    <p className="text-[#B4C7E7] mb-4">{project.description}</p>

                    {/* 项目信息 */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <DollarSign className="w-4 h-4 text-[#00FF88]" />
                        <span>{project.budget.toLocaleString()} 灵值</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <Users className="w-4 h-4 text-[#FFB800]" />
                        <span>{project.participants} 人参与</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <Calendar className="w-4 h-4 text-[#00C3FF]" />
                        <span>{new Date(project.deadline).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <AlertCircle className="w-4 h-4 text-[#FF6B9D]" />
                        <span>{project.lingzhi_reward} 灵值奖励</span>
                      </div>
                    </div>

                    {/* 需求标签 */}
                    <div className="flex flex-wrap gap-2">
                      {project.requirements.map((req, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded-full text-xs font-medium"
                        >
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex sm:flex-col gap-2">
                    <button className="flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all font-medium">
                      <Eye className="w-4 h-4" />
                      查看详情
                    </button>
                    {project.status === 'open' && (
                      <button className="flex items-center justify-center gap-2 px-4 py-2 bg-[#00FF88]/20 text-[#00FF88] border border-[#00FF88]/50 rounded-lg hover:bg-[#00FF88]/30 transition-all font-medium">
                        <Plus className="w-4 h-4" />
                        申请加入
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}

          {filteredProjects.length === 0 && (
            <div className="text-center py-12 text-[#B4C7E7]">
              <Filter className="w-12 h-12 mx-auto mb-4 text-[#B4C7E7]/40" />
              <p className="text-lg">没有找到匹配的项目</p>
              <p className="text-sm mt-2">尝试调整筛选条件或搜索关键词</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProjectPool