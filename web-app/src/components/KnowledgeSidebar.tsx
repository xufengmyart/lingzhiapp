import { useState, useEffect } from 'react'
import { BookOpen, ChevronDown, ChevronRight, Sparkles, Search } from 'lucide-react'
import api from '../services/api'

interface KnowledgeItem {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
}

interface KnowledgeCategory {
  name: string
  icon: string
  color: string
  items: KnowledgeItem[]
}

const KNOWLEDGE_CATEGORIES = [
  { name: '新手必读', icon: '🎯', color: 'from-green-400 to-emerald-500' },
  { name: '灵值系统', icon: '💰', color: 'from-yellow-400 to-orange-500' },
  { name: '数字资产', icon: '🎨', color: 'from-purple-400 to-pink-500' },
  { name: '技术开发', icon: '🔧', color: 'from-blue-400 to-cyan-500' },
  { name: '设计规范', icon: '🎭', color: 'from-pink-400 to-rose-500' },
  { name: '商业运营', icon: '📊', color: 'from-indigo-400 to-violet-500' },
  { name: 'general', icon: '📖', color: 'from-gray-400 to-gray-500' },
  { name: 'tech', icon: '⚡', color: 'from-blue-400 to-indigo-500' },
  { name: 'business', icon: '💼', color: 'from-amber-400 to-orange-500' },
  { name: 'culture', icon: '🏛️', color: 'from-red-400 to-rose-500' },
  { name: 'policy', icon: '📜', color: 'from-teal-400 to-cyan-500' },
]

// 默认知识库数据（当API不可用时使用）
const DEFAULT_KNOWLEDGE: KnowledgeCategory[] = [
  {
    name: '新手必读',
    icon: '🎯',
    color: 'from-green-400 to-emerald-500',
    items: [
      { id: '1', title: '什么是灵值？', content: '灵值是灵值生态园的核心价值单位，代表用户在生态中的贡献和影响力。', category: '新手必读', tags: ['基础', '入门'] },
      { id: '2', title: '如何获得灵值？', content: '通过签到、参与项目、贡献内容、推荐用户等方式获得灵值。', category: '新手必读', tags: ['获取', '奖励'] },
      { id: '3', title: '灵值有什么用？', content: '灵值可以兑换现金、参与分红池、解锁高级功能等。', category: '新手必读', tags: ['用途', '权益'] },
    ]
  },
  {
    name: '灵值系统',
    icon: '💰',
    color: 'from-yellow-400 to-orange-500',
    items: [
      { id: '4', title: '灵值获取规则', content: '每日签到可获得灵值，连续签到天数越多，奖励越高。', category: '灵值系统', tags: ['签到', '规则'] },
      { id: '5', title: '灵值兑换汇率', content: '灵值可以按照当前汇率兑换成现金，汇率会根据市场变化。', category: '灵值系统', tags: ['兑换', '汇率'] },
    ]
  },
  {
    name: '数字资产',
    icon: '🎨',
    color: 'from-purple-400 to-pink-500',
    items: [
      { id: '6', title: '什么是数字资产？', content: '数字资产是基于区块链技术的数字化商品，具有唯一性和不可替代性。', category: '数字资产', tags: ['概念', 'NFT'] },
      { id: '7', title: '如何创建数字资产？', content: '通过文化转译工作流，将文化元素数字化，生成可交易的数字资产。', category: '数字资产', tags: ['创建', '流程'] },
    ]
  }
]

interface KnowledgeSidebarProps {
  onKnowledgeSelect?: (item: KnowledgeItem) => void
}

const KnowledgeSidebar = ({ onKnowledgeSelect }: KnowledgeSidebarProps) => {
  const [knowledgeData, setKnowledgeData] = useState<KnowledgeCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadKnowledge()
  }, [])

  const loadKnowledge = async () => {
    try {
      console.log('[KnowledgeSidebar] 开始加载知识库...')
      // 优先使用 /api/knowledge API（这是专门为用户知识库设计的）
      const response = await api.get('/knowledge')
      console.log('[KnowledgeSidebar] API响应:', response.data)

      if (response.data.success && response.data.data) {
        const items = response.data.data || []

        // 将API返回的category映射到 KNOWLEDGE_CATEGORIES 的 name
        const itemsWithMappedCategory = items.map((item: any) => {
          // 确保每个条目都有必要的字段
          const normalizedItem = {
            id: item.id || item._id || String(Math.random()),
            title: item.title || item.name || '未命名',
            content: item.content || item.description || item.text || '暂无内容',
            category: item.category || 'general',
            tags: item.tags || [],
            ...item // 保留其他字段
          }

          // 如果 category 已经是 KNOWLEDGE_CATEGORIES 中的 name，直接使用
          if (KNOWLEDGE_CATEGORIES.some(cat => cat.name === item.category)) {
            return { ...normalizedItem, mappedCategory: item.category }
          }
          // 否则，根据 category 映射到对应的分类
          let mappedCategory = normalizedItem.category
          if (normalizedItem.category === 'general') mappedCategory = '新手必读'
          else if (normalizedItem.category === 'tech') mappedCategory = '技术开发'
          else if (normalizedItem.category === 'business') mappedCategory = '商业运营'
          else if (normalizedItem.category === 'culture') mappedCategory = '设计规范'
          else mappedCategory = '新手必读'
          return { ...normalizedItem, mappedCategory }
        })

        // 按分类组织数据
        const categories: KnowledgeCategory[] = KNOWLEDGE_CATEGORIES.map(cat => ({
          ...cat,
          items: itemsWithMappedCategory.filter((item: any) => item.mappedCategory === cat.name)
        }))

        // 过滤掉没有项目的分类
        const filteredCategories = categories.filter(cat => cat.items.length > 0)

        console.log('[KnowledgeSidebar] 加载成功，分类数量:', filteredCategories.length, '项目总数:', items.length)

        if (filteredCategories.length > 0) {
          setKnowledgeData(filteredCategories)
          setExpandedCategories(new Set([filteredCategories[0].name]))
        } else {
          // 如果没有数据，使用默认数据
          console.log('[KnowledgeSidebar] 没有数据，使用默认数据')
          setKnowledgeData(DEFAULT_KNOWLEDGE)
          setExpandedCategories(new Set([DEFAULT_KNOWLEDGE[0].name]))
        }
      } else {
        // API返回失败，使用默认数据
        console.log('[KnowledgeSidebar] API返回失败，使用默认数据')
        setKnowledgeData(DEFAULT_KNOWLEDGE)
        setExpandedCategories(new Set([DEFAULT_KNOWLEDGE[0].name]))
      }
    } catch (error) {
      console.error('[KnowledgeSidebar] 加载知识库失败，使用默认数据:', error)
      // API调用失败，使用默认数据
      setKnowledgeData(DEFAULT_KNOWLEDGE)
      setExpandedCategories(new Set([DEFAULT_KNOWLEDGE[0].name]))
    } finally {
      setLoading(false)
    }
  }

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev)
      if (newSet.has(categoryName)) {
        newSet.delete(categoryName)
      } else {
        newSet.add(categoryName)
      }
      return newSet
    })
  }

  const handleItemClick = (item: KnowledgeItem) => {
    if (onKnowledgeSelect) {
      onKnowledgeSelect(item)
    }
  }

  // 过滤分类和项目
  const filteredCategories = knowledgeData.map(cat => ({
    ...cat,
    items: searchQuery
      ? cat.items.filter(item =>
          (item.title && item.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (item.content && item.content.toLowerCase().includes(searchQuery.toLowerCase()))
        )
      : cat.items
  })).filter(cat => !searchQuery || cat.items.length > 0)

  if (loading) {
    return (
      <div className="w-80 bg-[#0A0D18]/95 backdrop-blur-xl border-r border-[#00C3FF]/20 p-4 overflow-y-auto">
        <div className="flex items-center justify-center h-64 text-[#B4C7E7]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00C3FF]"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-80 bg-[#0A0D18]/95 backdrop-blur-xl border-r border-[#00C3FF]/20 flex flex-col">
      {/* 头部 */}
      <div className="p-4 border-b border-[#00C3FF]/20">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-5 h-5 text-[#00C3FF]" />
          <h2 className="text-lg font-bold text-white">知识库</h2>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B4C7E7]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索知识..."
            className="w-full pl-10 pr-4 py-2 bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg text-sm text-white placeholder-[#B4C7E7] focus:outline-none focus:border-[#00C3FF]/50"
          />
        </div>
      </div>

      {/* 知识库内容 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {filteredCategories.length === 0 ? (
          <div className="text-center text-[#B4C7E7] text-sm py-8">
            没有找到相关知识
          </div>
        ) : (
          filteredCategories.map((category) => {
            const isExpanded = expandedCategories.has(category.name)

            return (
              <div key={category.name} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg overflow-hidden">
                {/* 分类标题 */}
                <button
                  onClick={() => toggleCategory(category.name)}
                  className="w-full flex items-center justify-between p-3 hover:bg-[#00C3FF]/10 transition-all"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{category.icon}</span>
                    <span className="text-sm font-semibold text-white">{category.name}</span>
                    <span className="text-xs text-[#B4C7E7] bg-[#00C3FF]/20 px-2 py-0.5 rounded-full">
                      {category.items.length}
                    </span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-[#B4C7E7]" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-[#B4C7E7]" />
                  )}
                </button>

                {/* 分类内容 */}
                {isExpanded && category.items.length > 0 && (
                  <div className="border-t border-[#00C3FF]/10">
                    {category.items.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleItemClick(item)}
                        className="w-full flex items-start gap-2 p-3 hover:bg-[#00C3FF]/10 transition-all border-l-2 border-transparent hover:border-[#00C3FF] text-left"
                      >
                        <Sparkles className="w-4 h-4 text-[#00C3FF] flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white font-medium line-clamp-2">
                            {item.title || '未命名'}
                          </p>
                          {item.tags && Array.isArray(item.tags) && item.tags.length > 0 && (
                            <div className="flex gap-1 mt-1 flex-wrap">
                              {item.tags.slice(0, 2).map((tag, idx) => (
                                <span
                                  key={`${item.id}-tag-${idx}`}
                                  className="text-xs text-[#B4C7E7] bg-[#121A2F] px-1.5 py-0.5 rounded"
                                >
                                  {String(tag)}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* 底部提示 */}
      <div className="p-4 border-t border-[#00C3FF]/20">
        <p className="text-xs text-[#B4C7E7] text-center">
          共 {filteredCategories.reduce((sum, cat) => sum + cat.items.length, 0)} 条知识
        </p>
      </div>
    </div>
  )
}

export default KnowledgeSidebar
