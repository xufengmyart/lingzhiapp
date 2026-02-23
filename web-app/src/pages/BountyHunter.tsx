import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Target, Search, Filter, Trophy, Clock, CheckCircle, AlertCircle, DollarSign, Users, TrendingUp, Award, Zap } from 'lucide-react'

interface BountyTask {
  id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  reward: number
  deadline: string
  status: 'open' | 'claimed' | 'completed' | 'expired'
  participants: number
  completions: number
  tags: string[]
}

// 模拟赏金任务数据
const MOCK_BOUNTIES: BountyTask[] = [
  {
    id: '1',
    title: '关注并转发灵值生态园官方Twitter',
    description: '关注@LingzhiPark并转发置顶推文，评论分享您的灵值生态园体验',
    difficulty: 'easy',
    reward: 100,
    deadline: '2024-02-29',
    status: 'open',
    participants: 156,
    completions: 89,
    tags: ['社交媒体', '宣传', '新手任务']
  },
  {
    id: '2',
    title: '创作灵值生态园推广视频',
    description: '制作一段1-3分钟的推广视频，介绍灵值生态园的核心功能和使用体验',
    difficulty: 'medium',
    reward: 500,
    deadline: '2024-03-15',
    status: 'open',
    participants: 45,
    completions: 12,
    tags: ['内容创作', '视频', '推广']
  },
  {
    id: '3',
    title: '发现并报告智能合约漏洞',
    description: '在灵值生态园智能合约中发现安全漏洞并提供详细报告和修复建议',
    difficulty: 'hard',
    reward: 5000,
    deadline: '2024-04-30',
    status: 'open',
    participants: 8,
    completions: 2,
    tags: ['安全', '技术', '漏洞挖掘']
  },
  {
    id: '4',
    title: '翻译灵值生态园白皮书',
    description: '将灵值生态园白皮书翻译成英语、日语或韩语版本',
    difficulty: 'medium',
    reward: 300,
    deadline: '2024-03-31',
    status: 'open',
    participants: 23,
    completions: 7,
    tags: ['翻译', '文档', '本地化']
  },
  {
    id: '5',
    title: '参与社区治理投票',
    description: '参与本周DAO治理提案投票，贡献您的决策意见',
    difficulty: 'easy',
    reward: 50,
    deadline: '2024-02-20',
    status: 'open',
    participants: 342,
    completions: 189,
    tags: ['治理', '投票', '社区']
  },
  {
    id: '6',
    title: '撰写技术分析文章',
    description: '撰写一篇关于灵值生态园技术架构或通证经济模型的深度分析文章',
    difficulty: 'hard',
    reward: 800,
    deadline: '2024-03-31',
    status: 'open',
    participants: 15,
    completions: 4,
    tags: ['写作', '技术', '分析']
  }
]

const BountyHunter = () => {
  const { user } = useAuth()
  const [bounties, setBounties] = useState<BountyTask[]>(MOCK_BOUNTIES)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')

  useEffect(() => {
    loadBounties()
  }, [])

  const loadBounties = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/bounty/tasks`)
      if (response.ok) {
        const data = await response.json()
        setBounties(data.length > 0 ? data : MOCK_BOUNTIES)
      } else {
        setBounties(MOCK_BOUNTIES)
      }
    } catch (error) {
      console.error('Failed to load bounties:', error)
      setBounties(MOCK_BOUNTIES)
    }
  }

  const claimBounty = async (bountyId: string) => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/bounty/${bountyId}/claim`, {
        method: 'POST'
      })
      if (response.ok) {
        loadBounties()
      }
    } catch (error) {
      console.error('Failed to claim bounty:', error)
    }
  }

  const filteredBounties = bounties.filter(bounty => {
    const matchesSearch = bounty.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         bounty.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesDifficulty = selectedDifficulty === 'all' || bounty.difficulty === selectedDifficulty
    const matchesStatus = selectedStatus === 'all' || bounty.status === selectedStatus
    return matchesSearch && matchesDifficulty && matchesStatus
  })

  const difficultyMap = {
    easy: { label: '简单', color: 'bg-[#00FF88]', icon: Zap },
    medium: { label: '中等', color: 'bg-[#FFB800]', icon: Target },
    hard: { label: '困难', color: 'bg-[#FF6B9D]', icon: Award }
  }

  const statusMap = {
    open: { label: '招募中', icon: AlertCircle, color: 'text-[#00C3FF]' },
    claimed: { label: '已接取', icon: Clock, color: 'text-[#FFB800]' },
    completed: { label: '已完成', icon: CheckCircle, color: 'text-[#00FF88]' },
    expired: { label: '已过期', icon: Clock, color: 'text-[#FF6B9D]' }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18]">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2 leading-tight">
            赏金资源池
          </h1>
          <p className="text-[#B4C7E7] text-sm sm:text-base">完成赏金任务，赚取丰厚灵值奖励</p>
        </div>

        {/* 筛选栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索赏金任务..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
            >
              <option value="all" className="bg-[#121A2F]">所有难度</option>
              <option value="easy" className="bg-[#121A2F]">简单</option>
              <option value="medium" className="bg-[#121A2F]">中等</option>
              <option value="hard" className="bg-[#121A2F]">困难</option>
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
            >
              <option value="all" className="bg-[#121A2F]">所有状态</option>
              {Object.entries(statusMap).map(([key, val]) => (
                <option key={key} value={key} className="bg-[#121A2F]">{val.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总任务数</div>
            <div className="text-2xl font-bold text-white">{bounties.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">招募中</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {bounties.filter(b => b.status === 'open').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总赏金</div>
            <div className="text-2xl font-bold text-[#00FF88]">
              {bounties.reduce((sum, b) => sum + b.reward, 0).toLocaleString()} 灵值
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">完成数</div>
            <div className="text-2xl font-bold text-[#FFB800]">
              {bounties.reduce((sum, b) => sum + b.completions, 0)}
            </div>
          </div>
        </div>

        {/* 排行榜 */}
        <div className="bg-gradient-to-r from-[#00C3FF]/10 to-[#00E0FF]/10 border border-[#00C3FF]/30 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Trophy className="w-6 h-6 text-[#FFB800]" />
            <h2 className="text-xl font-bold text-white">本周排行榜</h2>
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map(rank => (
              <div key={rank} className="flex items-center gap-4 bg-[#0A0D18] rounded-lg p-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                  rank === 1 ? 'bg-[#FFB800]' : rank === 2 ? 'bg-[#C0C0C0]' : 'bg-[#CD7F32]'
                }`}>
                  {rank}
                </div>
                <div className="flex-1">
                  <div className="text-white font-medium">用户{rank}</div>
                  <div className="text-xs text-[#B4C7E7]">完成 {10 - rank * 2} 个任务</div>
                </div>
                <div className="text-[#00FF88] font-bold">{(1000 - rank * 200).toLocaleString()} 灵值</div>
              </div>
            ))}
          </div>
        </div>

        {/* 任务列表 */}
        <div className="space-y-4">
          {filteredBounties.map(bounty => {
            const difficultyInfo = difficultyMap[bounty.difficulty]
            const DifficultyIcon = difficultyInfo.icon
            const statusInfo = statusMap[bounty.status]
            const StatusIcon = statusInfo.icon

            return (
              <div key={bounty.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1">
                    {/* 标题和标签 */}
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-xl font-bold text-white">{bounty.title}</h3>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {/* 难度标签 */}
                        <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${difficultyInfo.color} text-white`}>
                          <DifficultyIcon className="w-3.5 h-3.5" />
                          {difficultyInfo.label}
                        </span>
                        {/* 状态标签 */}
                        <span className={`flex items-center gap-1.5 text-sm font-medium ${statusInfo.color}`}>
                          <StatusIcon className="w-4 h-4" />
                          {statusInfo.label}
                        </span>
                      </div>
                    </div>

                    <p className="text-[#B4C7E7] mb-4">{bounty.description}</p>

                    {/* 信息栏 */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <DollarSign className="w-4 h-4 text-[#00FF88]" />
                        <span className="text-white font-semibold">{bounty.reward.toLocaleString()} 灵值</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <Users className="w-4 h-4 text-[#FFB800]" />
                        <span>{bounty.participants} 人接取</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <CheckCircle className="w-4 h-4 text-[#00C3FF]" />
                        <span>{bounty.completions} 次完成</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#B4C7E7] text-sm">
                        <Clock className="w-4 h-4 text-[#FF6B9D]" />
                        <span>{new Date(bounty.deadline).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* 标签 */}
                    <div className="flex flex-wrap gap-2">
                      {bounty.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded-full text-xs font-medium"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  {bounty.status === 'open' && (
                    <button
                      onClick={() => claimBounty(bounty.id)}
                      className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-[#00FF88] to-[#00C3FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00FF88]/30 transition-all font-bold whitespace-nowrap"
                    >
                      <Target className="w-5 h-5" />
                      接取任务
                    </button>
                  )}
                </div>
              </div>
            )
          })}

          {filteredBounties.length === 0 && (
            <div className="text-center py-12 text-[#B4C7E7]">
              <Target className="w-12 h-12 mx-auto mb-4 text-[#B4C7E7]/40" />
              <p className="text-lg">没有找到匹配的任务</p>
              <p className="text-sm mt-2">尝试调整筛选条件或搜索关键词</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default BountyHunter