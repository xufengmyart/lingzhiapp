import { useState, useEffect } from 'react'
import { BookOpen, Search, Filter, ChevronRight, Database, Sparkles, Lock, Unlock, Building2, Package, Wrench, Users2, Target, FileText } from 'lucide-react'

interface CompanyKnowledgeBase {
  id: number
  name: string
  description: string
  category: string
  document_count: number
  is_public: boolean
  created_at: string
  icon: React.ReactNode
}

const CompanyKnowledge = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<CompanyKnowledgeBase[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  const loadKnowledgeBases = async () => {
    // 模拟数据：5个公司介绍相关的知识库
    const mockData: CompanyKnowledgeBase[] = [
      {
        id: 1,
        name: '公司介绍',
        description: '了解我们的公司历史、愿景、使命和核心价值观',
        category: 'company',
        document_count: 15,
        is_public: true,
        created_at: '2026-01-01',
        icon: <Building2 className="w-6 h-6" />
      },
      {
        id: 2,
        name: '产品介绍',
        description: '探索我们的产品线、功能特性和使用指南',
        category: 'product',
        document_count: 28,
        is_public: true,
        created_at: '2026-01-15',
        icon: <Package className="w-6 h-6" />
      },
      {
        id: 3,
        name: '服务介绍',
        description: '了解我们提供的各项服务和解决方案',
        category: 'service',
        document_count: 22,
        is_public: true,
        created_at: '2026-01-20',
        icon: <Sparkles className="w-6 h-6" />
      },
      {
        id: 4,
        name: '技术介绍',
        description: '深入我们的技术架构、开发流程和技术创新',
        category: 'technology',
        document_count: 35,
        is_public: true,
        created_at: '2026-02-01',
        icon: <Wrench className="w-6 h-6" />
      },
      {
        id: 5,
        name: '团队介绍',
        description: '认识我们的团队成员和组织架构',
        category: 'team',
        document_count: 18,
        is_public: true,
        created_at: '2026-02-05',
        icon: <Users2 className="w-6 h-6" />
      }
    ]
    setKnowledgeBases(mockData)
  }

  const categories = [
    { id: 'all', name: '全部' },
    { id: 'company', name: '公司' },
    { id: 'product', name: '产品' },
    { id: 'service', name: '服务' },
    { id: 'technology', name: '技术' },
    { id: 'team', name: '团队' }
  ]

  const filteredKBs = knowledgeBases.filter((kb) => {
    const matchCategory = selectedCategory === 'all' || kb.category === selectedCategory
    const matchSearch = kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       kb.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  const categoryColors = {
    company: 'from-[#00C3FF] to-[#47D1FF]',
    product: 'from-[#00FF88] to-[#00E0FF]',
    service: 'from-[#FFB800] to-[#FFA500]',
    technology: 'from-[#FF6B6B] to-[#FF8E53]',
    team: 'from-[#A855F7] to-[#7C3AED]'
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            公司介绍知识库
          </h1>
          <p className="text-[#B4C7E7]">深入了解我们的公司、产品、服务、技术和团队</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">知识库总数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {knowledgeBases.length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">文档总数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {knowledgeBases.reduce((sum, kb) => sum + kb.document_count, 0)}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">公开库</div>
            <div className="text-2xl font-bold text-green-400">
              {knowledgeBases.filter(kb => kb.is_public).length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">分类数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {new Set(knowledgeBases.map(kb => kb.category)).size}
            </div>
          </div>
        </div>

        {/* 搜索和筛选 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索知识库..."
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
                <option key={cat.id} value={cat.id} className="bg-[#121A2F]">{cat.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Knowledge Bases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKBs.map((kb) => {
            const gradientColor = categoryColors[kb.category as keyof typeof categoryColors]
            return (
              <div
                key={kb.id}
                className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all hover:shadow-lg hover:shadow-[#00C3FF]/10 group cursor-pointer"
              >
                {/* 图标和标题 */}
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-r ${gradientColor} rounded-lg flex items-center justify-center shadow-lg`}>
                    {kb.icon}
                  </div>
                  {kb.is_public ? (
                    <Unlock className="w-5 h-5 text-green-400" />
                  ) : (
                    <Lock className="w-5 h-5 text-[#FFB800]" />
                  )}
                </div>

                {/* 标题和描述 */}
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-[#00C3FF] transition-colors">
                  {kb.name}
                </h3>
                <p className="text-[#B4C7E7] text-sm mb-4 line-clamp-2">
                  {kb.description}
                </p>

                {/* 统计信息 */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#B4C7E7]" />
                    <span className="text-[#B4C7E7] text-sm">{kb.document_count} 文档</span>
                  </div>
                  <div className="text-[#B4C7E7]/60 text-xs">
                    {kb.created_at}
                  </div>
                </div>

                {/* 查看按钮 */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#00C3FF] bg-[#00C3FF]/10 px-2 py-1 rounded-full">
                    {categories.find(c => c.id === kb.category)?.name}
                  </span>
                  <div className="flex items-center gap-2 text-[#00C3FF] text-sm font-medium group-hover:gap-3 transition-all">
                    查看详情
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* 空状态 */}
        {filteredKBs.length === 0 && (
          <div className="text-center py-16">
            <Database className="w-16 h-16 mx-auto mb-4 text-[#B4C7E7]/30" />
            <p className="text-[#B4C7E7]">未找到匹配的知识库</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CompanyKnowledge
