import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Search, Plus, BookOpen, FileText, Star, Clock, Download, Trash2, Edit, Filter, Grid, List, BrainCircuit, Lightbulb, BookMarked, FolderOpen, Tag, Eye, Folder, MoreVertical, X } from 'lucide-react'

interface KnowledgeItem {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
  created_at: string
  updated_at: string
  is_favorite: boolean
  source?: string
  access_count?: number
  file_url?: string
  file_type?: string
  document_count?: number
}

interface Category {
  id: string
  name: string
  icon: any
  count: number
  description: string
}

// 文档分类定义
const CATEGORIES: Category[] = [
  { id: 'all', name: '全部文档', icon: FolderOpen, count: 0, description: '所有类型文档' },
  { id: 'general', name: '通用知识', icon: BookOpen, count: 0, description: '通用知识和使用指南' },
  { id: 'tech', name: '技术文档', icon: BrainCircuit, count: 0, description: 'API文档、开发指南' },
  { id: 'business', name: '商业文档', icon: FileText, count: 0, description: '商业计划、合同协议' },
  { id: 'design', name: '设计资源', icon: Lightbulb, count: 0, description: '设计稿、品牌规范' },
  { id: 'culture', name: '文化知识', icon: BookMarked, count: 0, description: '传统文化、文化知识' },
  { id: 'policy', name: '政策法规', icon: BookMarked, count: 0, description: '政策、法规文件' },
]

// 预设的文化知识库
const PRESET_CULTURE_KNOWLEDGE: KnowledgeItem[] = [
  {
    id: 'culture-1',
    title: '西安文化关键词库',
    content: '110个西安文化关键词及转译提示，涵盖历史、建筑、美食、民俗等各个方面。包括大雁塔、兵马俑、城墙等标志性文化元素的深度解析。',
    category: 'culture',
    tags: ['西安', '文化', '关键词', '转译'],
    created_at: '2026-02-01T00:00:00',
    updated_at: '2026-02-01T00:00:00',
    is_favorite: false,
    document_count: 110
  },
  {
    id: 'culture-2',
    title: '西安文化基因库',
    content: '文化基因分类和解码方法，包含12大类文化基因库。系统性整理西安文化的核心基因，为文化转译提供理论基础。',
    category: 'culture',
    tags: ['西安', '文化基因', '转译理论'],
    created_at: '2026-02-02T00:00:00',
    updated_at: '2026-02-02T00:00:00',
    is_favorite: false,
    document_count: 43
  },
  {
    id: 'culture-3',
    title: '转译商业案例库',
    content: '文化商业转译的六大方法及成功案例。展示如何将传统文化元素转化为现代商业价值。',
    category: 'culture',
    tags: ['文化转译', '商业案例', '价值转化'],
    created_at: '2026-02-03T00:00:00',
    updated_at: '2026-02-03T00:00:00',
    is_favorite: false,
    document_count: 28
  },
  {
    id: 'culture-4',
    title: '关中文化民俗库',
    content: '关中地区民俗文化、传统技艺、节庆活动等文化资源的系统整理。',
    category: 'culture',
    tags: ['关中', '民俗文化', '传统技艺'],
    created_at: '2026-02-04T00:00:00',
    updated_at: '2026-02-04T00:00:00',
    is_favorite: false,
    document_count: 67
  },
  {
    id: 'culture-5',
    title: '丝路文化传承库',
    content: '丝绸之路沿线文化遗产、文化交流历史、传承技艺等。',
    category: 'culture',
    tags: ['丝路文化', '文化遗产', '传承技艺'],
    created_at: '2026-02-05T00:00:00',
    updated_at: '2026-02-05T00:00:00',
    is_favorite: false,
    document_count: 89
  }
]

const Knowledge = () => {
  const { user, updateUser } = useAuth()
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<KnowledgeItem | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [viewingLoading, setViewingLoading] = useState(false)
  const [viewingError, setViewingError] = useState('')
  const [newItem, setNewItem] = useState<{ title: string; content: string; category: string; tags: string[] }>({ title: '', content: '', category: 'general', tags: [] })
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [statistics, setStatistics] = useState({ total: 0, favorites: 0, recent: 0 })

  useEffect(() => {
    loadKnowledge()
  }, [selectedCategory, searchQuery])

  useEffect(() => {
    updateStatistics()
  }, [knowledgeItems])

  const updateStatistics = () => {
    setStatistics({
      total: knowledgeItems.length,
      favorites: knowledgeItems.filter(item => item.is_favorite).length,
      recent: knowledgeItems.filter(item => {
        const createdAt = new Date(item.created_at)
        const weekAgo = new Date()
        weekAgo.setDate(weekAgo.getDate() - 7)
        return createdAt > weekAgo
      }).length
    })

    // 更新分类计数
    CATEGORIES.forEach(cat => {
      if (cat.id === 'all') {
        cat.count = knowledgeItems.length
      } else {
        cat.count = knowledgeItems.filter(item => item.category === cat.id).length
      }
    })
  }

  const loadKnowledge = async () => {
    console.log('[Knowledge] 开始加载知识库...')
    try {
      const token = localStorage.getItem('token')
      console.log('[Knowledge] Token:', token ? '存在' : '不存在')
      
      // 使用用户资源池的知识库API
      const response = await fetch('/api/knowledge', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        }
      })
      
      console.log('[Knowledge] 响应状态:', response.status)

      if (response.ok) {
        const result = await response.json()
        console.log('[Knowledge] 返回的数据:', result)

        // 后端返回格式: { success: true, data: [...] }
        const data = result.data || result
        const items = Array.isArray(data) ? data : []
        
        // 将预设的文化知识库添加到列表中
        const allItems = [...PRESET_CULTURE_KNOWLEDGE, ...items]
        setKnowledgeItems(allItems)
        console.log('[Knowledge] 已加载知识库列表，总计数量:', allItems.length, '(预设:', PRESET_CULTURE_KNOWLEDGE.length, ', API:', items.length, ')')
      } else {
        console.error('[Knowledge] API 请求失败:', response.status, response.statusText)
        // API 失败时，显示预设的文化知识库
        const presetCultureKnowledge: KnowledgeItem[] = [
          {
            id: '1',
            title: '西安文化关键词库',
            content: '110个西安文化关键词及转译提示，涵盖历史、建筑、美食、民俗等各个方面。包括大雁塔、兵马俑、城墙等标志性文化元素的深度解析。',
            category: 'culture',
            tags: ['西安', '文化', '关键词', '转译'],
            created_at: '2026-02-01T00:00:00',
            updated_at: '2026-02-01T00:00:00',
            is_favorite: false,
            document_count: 110
          },
          {
            id: '2',
            title: '西安文化基因库',
            content: '文化基因分类和解码方法，包含12大类文化基因库。系统性整理西安文化的核心基因，为文化转译提供理论基础。',
            category: 'culture',
            tags: ['西安', '文化基因', '转译理论'],
            created_at: '2026-02-02T00:00:00',
            updated_at: '2026-02-02T00:00:00',
            is_favorite: false,
            document_count: 43
          },
          {
            id: '3',
            title: '转译商业案例库',
            content: '文化商业转译的六大方法及成功案例。展示如何将传统文化元素转化为现代商业价值。',
            category: 'culture',
            tags: ['文化转译', '商业案例', '价值转化'],
            created_at: '2026-02-03T00:00:00',
            updated_at: '2026-02-03T00:00:00',
            is_favorite: false,
            document_count: 28
          },
          {
            id: '4',
            title: '关中文化民俗库',
            content: '关中地区民俗文化、传统技艺、节庆活动等文化资源的系统整理。',
            category: 'culture',
            tags: ['关中', '民俗文化', '传统技艺'],
            created_at: '2026-02-04T00:00:00',
            updated_at: '2026-02-04T00:00:00',
            is_favorite: false,
            document_count: 67
          },
          {
            id: '5',
            title: '丝路文化传承库',
            content: '丝绸之路沿线文化遗产、文化交流历史、传承技艺等。',
            category: 'culture',
            tags: ['丝路文化', '文化遗产', '传承技艺'],
            created_at: '2026-02-05T00:00:00',
            updated_at: '2026-02-05T00:00:00',
            is_favorite: false,
            document_count: 89
          }
        ]
        setKnowledgeItems(presetCultureKnowledge)
        console.log('[Knowledge] API 失败，已设置预设文化知识库，数量:', presetCultureKnowledge.length)
      }
    } catch (error) {
      console.error('[Knowledge] 加载知识库失败:', error)
      // 异常时，显示预设的文化知识库
      const presetCultureKnowledge: KnowledgeItem[] = [
        {
          id: '1',
          title: '西安文化关键词库',
          content: '110个西安文化关键词及转译提示，涵盖历史、建筑、美食、民俗等各个方面。包括大雁塔、兵马俑、城墙等标志性文化元素的深度解析。',
          category: 'culture',
          tags: ['西安', '文化', '关键词', '转译'],
          created_at: '2026-02-01T00:00:00',
          updated_at: '2026-02-01T00:00:00',
          is_favorite: false,
          document_count: 110
        },
        {
          id: '2',
          title: '西安文化基因库',
          content: '文化基因分类和解码方法，包含12大类文化基因库。系统性整理西安文化的核心基因，为文化转译提供理论基础。',
          category: 'culture',
          tags: ['西安', '文化基因', '转译理论'],
          created_at: '2026-02-02T00:00:00',
          updated_at: '2026-02-02T00:00:00',
          is_favorite: false,
          document_count: 43
        },
        {
          id: '3',
          title: '转译商业案例库',
          content: '文化商业转译的六大方法及成功案例。展示如何将传统文化元素转化为现代商业价值。',
          category: 'culture',
          tags: ['文化转译', '商业案例', '价值转化'],
          created_at: '2026-02-03T00:00:00',
          updated_at: '2026-02-03T00:00:00',
          is_favorite: false,
          document_count: 28
        },
        {
          id: '4',
          title: '关中文化民俗库',
          content: '关中地区民俗文化、传统技艺、节庆活动等文化资源的系统整理。',
          category: 'culture',
          tags: ['关中', '民俗文化', '传统技艺'],
          created_at: '2026-02-04T00:00:00',
          updated_at: '2026-02-04T00:00:00',
          is_favorite: false,
          document_count: 67
        },
        {
          id: '5',
          title: '丝路文化传承库',
          content: '丝绸之路沿线文化遗产、文化交流历史、传承技艺等。',
          category: 'culture',
          tags: ['丝路文化', '文化遗产', '传承技艺'],
          created_at: '2026-02-05T00:00:00',
          updated_at: '2026-02-05T00:00:00',
          is_favorite: false,
          document_count: 89
        }
      ]
      setKnowledgeItems(presetCultureKnowledge)
      console.log('[Knowledge] 加载异常，已设置预设文化知识库，数量:', presetCultureKnowledge.length)
    }
  }

  const handleAddItem = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/knowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(newItem)
      })

      if (response.ok) {
        loadKnowledge()
        setShowAddModal(false)
        setNewItem({ title: '', content: '', category: 'general', tags: [] })
      }
    } catch (error) {
      console.error('Failed to add knowledge item:', error)
    }
  }

  const toggleFavorite = async (id: string) => {
    try {
      const token = localStorage.getItem('token')
      await fetch(`/api/knowledge/${id}/favorite`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        }
      })
      loadKnowledge()
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }

  const deleteItem = async (id: string) => {
    if (!confirm('确定要删除这条知识吗？')) return
    try {
      const token = localStorage.getItem('token')
      await fetch(`/api/knowledge/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        }
      })
      loadKnowledge()
    } catch (error) {
      console.error('Failed to delete knowledge item:', error)
    }
  }

  const handleViewItem = async (item: KnowledgeItem) => {
    try {
      setViewingLoading(true)
      setViewingError('')
      
      const token = localStorage.getItem('token')
      if (!token) {
        setViewingError('请先登录')
        setViewingLoading(false)
        return
      }
      
      const response = await fetch(`/api/v9/knowledge/items/${item.id}/view`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      const result = await response.json()
      
      if (result.success) {
        setSelectedItem(result.data.item)
        setShowDetailModal(true)
        
        // 如果使用了灵值，更新用户信息
        if (result.data.consumed > 0 && user) {
          updateUser({
            ...user,
            total_lingzhi: result.data.user_lingzhi
          })
        }
      } else {
        setViewingError(result.message || '浏览失败')
      }
    } catch (error) {
      console.error('浏览知识库失败:', error)
      setViewingError('网络错误，请重试')
    } finally {
      setViewingLoading(false)
    }
  }

  const filteredItems = knowledgeItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = [
    { id: 'all', label: '全部', icon: BookOpen },
    { id: 'tech', label: '技术', icon: BrainCircuit },
    { id: 'design', label: '设计', icon: Lightbulb },
    { id: 'business', label: '商业', icon: BookMarked },
    { id: 'culture', label: '文化', icon: BookMarked },
    { id: 'general', label: '通用', icon: FileText }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-16">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            知识库
          </h1>
          <p className="text-[#B4C7E7] text-sm sm:text-base">构建个人知识体系，让智能体更懂你</p>
        </div>

        {/* 操作栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* 搜索 */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索知识..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  loadKnowledge()
                }}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>

            {/* 分类筛选 */}
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value)
                loadKnowledge()
              }}
              className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id} className="bg-[#121A2F]">{cat.label}</option>
              ))}
            </select>

            {/* 右侧操作 */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                className="p-2.5 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
              >
                {viewMode === 'grid' ? <List className="w-5 h-5 text-[#B4C7E7]" /> : <Grid className="w-5 h-5 text-[#B4C7E7]" />}
              </button>
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all font-medium"
              >
                <Plus className="w-4 h-4" />
                添加知识
              </button>
            </div>
          </div>
        </div>

        {/* 分类标签 */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {categories.map(cat => {
            const Icon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${
                  selectedCategory === cat.id
                    ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]'
                    : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20 hover:border-[#00C3FF]/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{cat.label}</span>
              </button>
            )
          })}
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总知识数</div>
            <div className="text-2xl font-bold text-white">{knowledgeItems.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">收藏数</div>
            <div className="text-2xl font-bold text-[#FFB800]">
              {knowledgeItems.filter(i => i.is_favorite).length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">分类数</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {new Set(knowledgeItems.map(i => i.category)).size}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">标签数</div>
            <div className="text-2xl font-bold text-[#00FF88]">
              {new Set(knowledgeItems.flatMap(i => i.tags)).size}
            </div>
          </div>
        </div>

        {/* 知识展示 */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map(item => (
              <div key={item.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-5 hover:border-[#00C3FF]/50 transition-all group cursor-pointer" onClick={() => handleViewItem(item)}>
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-white flex-1">{item.title}</h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(item.id)
                    }}
                    className="flex-shrink-0 ml-2"
                  >
                    <Star className={`w-5 h-5 ${item.is_favorite ? 'text-[#FFB800] fill-[#FFB800]' : 'text-[#B4C7E7]'}`} />
                  </button>
                </div>
                <p className="text-[#B4C7E7] text-sm mb-4 line-clamp-3">{item.content}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {item.tags.slice(0, 3).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                  {item.tags.length > 3 && (
                    <span className="px-2 py-1 bg-[#0A0D18] text-[#B4C7E7] rounded text-xs">
                      +{item.tags.length - 3}
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between text-xs text-[#B4C7E7]">
                  <span>{new Date(item.updated_at).toLocaleDateString()}</span>
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all">
                    <button className="p-1 hover:text-white transition-all">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="p-1 hover:text-red-400 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredItems.map(item => (
              <div key={item.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4 hover:border-[#00C3FF]/50 transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-bold text-white">{item.title}</h3>
                      <button
                        onClick={() => toggleFavorite(item.id)}
                      >
                        <Star className={`w-4 h-4 ${item.is_favorite ? 'text-[#FFB800] fill-[#FFB800]' : 'text-[#B4C7E7]'}`} />
                      </button>
                    </div>
                    <p className="text-[#B4C7E7] text-sm mb-2 line-clamp-2">{item.content}</p>
                    <div className="flex flex-wrap gap-2">
                      {item.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-xs text-[#B4C7E7] whitespace-nowrap">
                    {new Date(item.updated_at).toLocaleDateString()}
                  </div>
                  <div className="flex gap-2">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation()
                        // TODO: 实现编辑功能
                      }}
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
                    >
                      <Edit className="w-4 h-4 text-[#B4C7E7]" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteItem(item.id)
                      }}
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-red-600/20 transition-all"
                    >
                      <Trash2 className="w-4 h-4 text-[#B4C7E7]" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredItems.length === 0 && (
          <div className="text-center py-12 text-[#B4C7E7]">
            <BookOpen className="w-12 h-12 mx-auto mb-4 text-[#B4C7E7]/40" />
            <p className="text-lg">暂无知识</p>
            <p className="text-sm mt-2">点击"添加知识"开始构建您的知识库</p>
          </div>
        )}

        {/* 添加知识模态框 */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#121A2F] border border-[#00C3FF]/30 rounded-xl p-6 w-full max-w-2xl">
              <h2 className="text-2xl font-bold text-white mb-4">添加知识</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-[#B4C7E7] mb-2">标题</label>
                  <input
                    type="text"
                    value={newItem.title}
                    onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                    className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
                    placeholder="输入知识标题"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#B4C7E7] mb-2">内容</label>
                  <textarea
                    value={newItem.content}
                    onChange={(e) => setNewItem({ ...newItem, content: e.target.value })}
                    className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF] h-32 resize-none"
                    placeholder="输入知识内容"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#B4C7E7] mb-2">分类</label>
                  <select
                    value={newItem.category}
                    onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                    className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
                  >
                    {categories.filter(c => c.id !== 'all').map(cat => (
                      <option key={cat.id} value={cat.id} className="bg-[#121A2F]">{cat.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-[#B4C7E7] mb-2">标签（用逗号分隔）</label>
                  <input
                    type="text"
                    value={newItem.tags.join(', ')}
                    onChange={(e) => setNewItem({ ...newItem, tags: e.target.value.split(',').map(t => t.trim()).filter(t => t) })}
                    className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
                    placeholder="例如: 技术, React, JavaScript"
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2.5 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg text-[#B4C7E7] hover:bg-[#00C3FF]/20 transition-all"
                >
                  取消
                </button>
                <button
                  onClick={handleAddItem}
                  className="flex-1 px-4 py-2.5 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all font-medium"
                >
                  添加
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 知识详情模态框 */}
        {showDetailModal && selectedItem && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#121A2F] border border-[#00C3FF]/30 rounded-xl p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
              {viewingLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#00C3FF]"></div>
                  <p className="text-[#B4C7E7] mt-4">正在加载...</p>
                </div>
              ) : viewingError ? (
                <div className="text-center py-8">
                  <div className="text-red-400 text-4xl mb-4">⚠️</div>
                  <p className="text-[#B4C7E7] mb-4">{viewingError}</p>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="px-6 py-2 bg-[#00C3FF] text-white rounded-lg hover:bg-[#00E0FF] transition-all"
                  >
                    关闭
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-4">
                    <h2 className="text-2xl font-bold text-white">{selectedItem.title}</h2>
                    <button
                      onClick={() => setShowDetailModal(false)}
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
                    >
                      ✕
                    </button>
                  </div>
                  
                  <div className="flex items-center gap-4 mb-6 text-sm text-[#B4C7E7]">
                    <span className="px-2 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded">
                      {selectedItem.category}
                    </span>
                    <span>•</span>
                    <span>来源: {selectedItem.source}</span>
                    <span>•</span>
                    <span>浏览次数: {selectedItem.access_count || 0}</span>
                  </div>
                  
                  <div className="bg-[#0A0D18] border border-[#00C3FF]/20 rounded-lg p-4 mb-6">
                    <pre className="whitespace-pre-wrap text-[#B4C7E7] font-sans text-sm leading-relaxed">
                      {selectedItem.content}
                    </pre>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mb-6">
                    {selectedItem.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowDetailModal(false)}
                      className="flex-1 px-4 py-2.5 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg text-[#B4C7E7] hover:bg-[#00C3FF]/20 transition-all"
                    >
                      关闭
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Knowledge