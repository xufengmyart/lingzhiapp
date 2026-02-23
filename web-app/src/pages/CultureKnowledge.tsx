import { useState, useEffect } from 'react'
import { BookOpen, Search, Filter, ChevronRight, Database, Sparkles, Lock, Unlock } from 'lucide-react'

interface CultureKnowledgeBase {
  id: number
  name: string
  description: string
  category: string
  document_count: number
  is_public: boolean
  created_at: string
}

const CultureKnowledge = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<CultureKnowledgeBase[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    // 模拟数据加载
    setKnowledgeBases([
      {
        id: 1,
        name: '西安文化关键词库',
        description: '110个西安文化关键词及转译提示，涵盖历史、建筑、美食、民俗等各个方面。包括大雁塔、兵马俑、城墙等标志性文化元素的深度解析。',
        category: 'keywords',
        document_count: 110,
        is_public: true,
        created_at: '2026-02-01',
      },
      {
        id: 2,
        name: '西安文化基因库',
        description: '文化基因分类和解码方法，包含12大类文化基因库。系统性整理西安文化的核心基因，为文化转译提供理论基础。',
        category: 'genes',
        document_count: 43,
        is_public: true,
        created_at: '2026-02-02',
      },
      {
        id: 3,
        name: '转译商业案例库',
        description: '文化商业转译的六大方法及成功案例。展示如何将传统文化元素转化为现代商业价值。',
        category: 'cases',
        document_count: 28,
        is_public: true,
        created_at: '2026-02-03',
      },
      {
        id: 4,
        name: '关中文化民俗库',
        description: '关中地区民俗文化、传统技艺、节庆活动等文化资源的系统整理。',
        category: 'folk',
        document_count: 67,
        is_public: true,
        created_at: '2026-02-04',
      },
      {
        id: 5,
        name: '丝路文化传承库',
        description: '丝绸之路沿线文化遗产、文化交流历史、传承技艺等。',
        category: 'silkroad',
        document_count: 89,
        is_public: true,
        created_at: '2026-02-05',
      },
    ])
  }, [])

  const categories = [
    { id: 'all', name: '全部' },
    { id: 'keywords', name: '关键词' },
    { id: 'genes', name: '文化基因' },
    { id: 'cases', name: '商业案例' },
    { id: 'folk', name: '民俗' },
    { id: 'silkroad', name: '丝路文化' },
  ]

  const filteredKBs = knowledgeBases.filter((kb) => {
    const matchCategory = selectedCategory === 'all' || kb.category === selectedCategory
    const matchSearch = kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        kb.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0D18] via-[#121A2F] to-[#0A0D18]">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0A0D18] via-[#1A2332] to-[#0A0D18] border-b border-[#00C3FF]/20 pt-20 pb-8">
        <div className="container mx-auto px-4">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
              文化知识库
            </h1>
            <p className="text-[#B4C7E7] text-lg">
              丰富的文化资源，为文化转译提供坚实基础
            </p>
          </div>

          {/* Search and Filter */}
          <div className="max-w-3xl mx-auto">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#B4C7E7]/50" />
                <input
                  type="text"
                  placeholder="搜索知识库..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg text-white placeholder-[#B4C7E7]/50 focus:outline-none focus:border-[#00C3FF]"
                />
              </div>
              <div className="flex items-center gap-2 bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg px-3 py-2 overflow-x-auto">
                {categories.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-all ${
                      selectedCategory === cat.id
                        ? 'bg-[#00C3FF] text-[#0A0D18]'
                        : 'text-[#B4C7E7] hover:text-white'
                    }`}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">知识库总数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {knowledgeBases.length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">文档总数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {knowledgeBases.reduce((sum, kb) => sum + kb.document_count, 0)}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">公开库</div>
            <div className="text-2xl font-bold text-green-400">
              {knowledgeBases.filter(kb => kb.is_public).length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">类别数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {categories.length - 1}
            </div>
          </div>
        </div>

        {/* Knowledge Bases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKBs.map((kb) => (
            <div
              key={kb.id}
              className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] flex items-center justify-center flex-shrink-0">
                  <Database className="w-6 h-6 text-white" />
                </div>
                {kb.is_public ? (
                  <div className="flex items-center gap-1 text-green-400 bg-green-400/10 px-2 py-1 rounded-full">
                    <Unlock className="w-3 h-3" />
                    <span className="text-xs">公开</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-[#B4C7E7] bg-[#B4C7E7]/10 px-2 py-1 rounded-full">
                    <Lock className="w-3 h-3" />
                    <span className="text-xs">私密</span>
                  </div>
                )}
              </div>

              <h3 className="text-white font-bold text-lg mb-2 group-hover:text-[#00C3FF] transition-colors">
                {kb.name}
              </h3>

              <p className="text-[#B4C7E7] text-sm mb-4 line-clamp-2">
                {kb.description}
              </p>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-[#00C3FF]">{kb.document_count}</span>
                  <span className="text-[#B4C7E7]">文档</span>
                </div>
                <button className="text-[#00C3FF] hover:text-[#00E0FF] flex items-center gap-1 transition-colors">
                  查看详情
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 pt-4 border-t border-[#00C3FF]/10 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#00C3FF]" />
                <span className="text-xs text-[#B4C7E7]">可参与文化转译</span>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredKBs.length === 0 && (
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-12 text-center">
            <Database className="w-16 h-16 text-[#B4C7E7]/30 mx-auto mb-4" />
            <h3 className="text-white text-lg font-semibold mb-2">暂无匹配的知识库</h3>
            <p className="text-[#B4C7E7]">尝试调整搜索条件或选择其他类别</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CultureKnowledge
