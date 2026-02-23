import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Upload, Download, Trash2, Search, FileText, Image, Video, Music, File, FolderPlus, Grid, List, Star, Share2, MoreHorizontal, BookOpen, BrainCircuit, Clock } from 'lucide-react'

interface ResourceFile {
  id: string
  name: string
  type: 'image' | 'video' | 'audio' | 'document' | 'other'
  size: number
  url: string
  created_at: string
  is_favorite: boolean
}

interface KnowledgeItem {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
  created_at: string
  updated_at: string
  is_favorite: boolean
}

// 模拟资源文件数据
const MOCK_RESOURCES: ResourceFile[] = [
  {
    id: '1',
    name: '灵值生态园设计稿.png',
    type: 'image',
    size: 2540000,
    url: '/assets/mock/design.png',
    created_at: '2024-01-15',
    is_favorite: true
  },
  {
    id: '2',
    name: '项目演示视频.mp4',
    type: 'video',
    size: 45200000,
    url: '/assets/mock/demo.mp4',
    created_at: '2024-01-18',
    is_favorite: false
  },
  {
    id: '3',
    name: '白皮书V2.0.pdf',
    type: 'document',
    size: 1250000,
    url: '/assets/mock/whitepaper.pdf',
    created_at: '2024-01-20',
    is_favorite: true
  },
  {
    id: '4',
    name: '品牌Logo.svg',
    type: 'image',
    size: 45000,
    url: '/assets/mock/logo.svg',
    created_at: '2024-01-10',
    is_favorite: true
  },
  {
    id: '5',
    name: '系统架构图.png',
    type: 'image',
    size: 1890000,
    url: '/assets/mock/architecture.png',
    created_at: '2024-01-22',
    is_favorite: false
  },
  {
    id: '6',
    name: '用户手册.docx',
    type: 'document',
    size: 890000,
    url: '/assets/mock/manual.docx',
    created_at: '2024-01-25',
    is_favorite: false
  }
]

// 模拟知识库数据
const MOCK_KNOWLEDGE: KnowledgeItem[] = [
  {
    id: '1',
    title: '灵值通证经济模型详解',
    content: '灵值生态园采用双代币模型：LYZ（灵值通证）作为治理代币和主要交易媒介，SBT（灵魂绑定通证）用于身份认证和权益绑定。',
    category: '通证',
    tags: ['代币', '经济模型', '治理'],
    created_at: '2024-01-15',
    updated_at: '2024-01-20',
    is_favorite: true
  },
  {
    id: '2',
    title: '圣地贡献机制说明',
    content: '用户可以通过参与圣地建设、贡献内容、完成任务等方式获得圣地贡献积分，积分可兑换相应权益和奖励。',
    category: '圣地',
    tags: ['贡献', '积分', '奖励'],
    created_at: '2024-01-18',
    updated_at: '2024-01-18',
    is_favorite: true
  },
  {
    id: '3',
    title: 'DAO治理流程',
    content: '灵值生态园采用去中心化自治组织（DAO）模式，持有LYZ通证的用户可以参与提案和投票，共同决定生态发展方向。',
    category: '治理',
    tags: ['DAO', '投票', '治理'],
    created_at: '2024-01-20',
    updated_at: '2024-01-22',
    is_favorite: false
  },
  {
    id: '4',
    title: '智能合约安全审计报告',
    content: '灵值生态园智能合约已完成第三方安全审计，未发现严重漏洞。合约代码已开源，接受社区监督。',
    category: '技术',
    tags: ['智能合约', '安全', '审计'],
    created_at: '2024-01-22',
    updated_at: '2024-01-22',
    is_favorite: false
  },
  {
    id: '5',
    title: '社区运营指南',
    content: '欢迎加入灵值生态园社区！本指南将帮助您快速了解如何参与社区活动、获取奖励、贡献价值。',
    category: '社区',
    tags: ['社区', '运营', '指南'],
    created_at: '2024-01-25',
    updated_at: '2024-01-26',
    is_favorite: true
  }
]

const UserResources = () => {
  const { user } = useAuth()
  const [resources, setResources] = useState<ResourceFile[]>(MOCK_RESOURCES)
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>(MOCK_KNOWLEDGE)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedKnowledge, setSelectedKnowledge] = useState<KnowledgeItem | null>(null)
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false)

  useEffect(() => {
    loadResources()
    loadKnowledge()
  }, [])

  const loadResources = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/user/resources', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        }
      })
      if (response.ok) {
        const data = await response.json()
        setResources(data.resources && data.resources.length > 0 ? data.resources : MOCK_RESOURCES)
      } else {
        setResources(MOCK_RESOURCES)
      }
    } catch (error) {
      console.error('Failed to load resources:', error)
      setResources(MOCK_RESOURCES)
    }
  }

  const loadKnowledge = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/knowledge', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        }
      })
      if (response.ok) {
        const result = await response.json()
        // 后端返回格式: { success: true, data: [...] }
        const data = result.data || result
        const items = Array.isArray(data) ? data : []
        setKnowledgeItems(items.length > 0 ? items : MOCK_KNOWLEDGE)
      } else {
        setKnowledgeItems(MOCK_KNOWLEDGE)
      }
    } catch (error) {
      console.error('Failed to load knowledge:', error)
      setKnowledgeItems(MOCK_KNOWLEDGE)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/user/resources/upload', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        loadResources()
      }
    } catch (error) {
      console.error('Failed to upload file:', error)
    }
  }

  const toggleFavorite = async (resourceId: string) => {
    try {
      await fetch(`/api/user/resources/${resourceId}/favorite`, {
        method: 'POST'
      })
      loadResources()
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }

  const toggleKnowledgeFavorite = async (id: string) => {
    try {
      await fetch(`/api/knowledge/${id}/favorite`, { method: 'POST' })
      loadKnowledge()
    } catch (error) {
      console.error('Failed to toggle knowledge favorite:', error)
    }
  }

  const handleKnowledgeClick = (item: KnowledgeItem) => {
    setSelectedKnowledge(item)
    setShowKnowledgeModal(true)
  }

  const deleteResource = async (resourceId: string) => {
    if (!confirm('确定要删除这个资源吗？')) return

    try {
      await fetch(`/api/user/resources/${resourceId}`, {
        method: 'DELETE'
      })
      loadResources()
    } catch (error) {
      console.error('Failed to delete resource:', error)
    }
  }

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'all' || resource.type === selectedType
    return matchesSearch && matchesType
  })

  const typeIcons = {
    image: Image,
    video: Video,
    audio: Music,
    document: FileText,
    other: File
  }

  const typeLabels = {
    all: '全部',
    image: '图片',
    video: '视频',
    audio: '音频',
    document: '文档',
    other: '其他'
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18]">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2 leading-tight">
            用户资源池
          </h1>
          <p className="text-[#B4C7E7] text-sm sm:text-base">管理您的个人资源，随时调用</p>
        </div>

        {/* 操作栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex-1 flex gap-4 w-full sm:w-auto">
              {/* 搜索 */}
              <div className="relative flex-1 sm:flex-none sm:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
                <input
                  type="text"
                  placeholder="搜索资源..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
                />
              </div>

              {/* 类型筛选 */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#00C3FF]"
              >
                {Object.entries(typeLabels).map(([key, label]) => (
                  <option key={key} value={key} className="bg-[#121A2F]">{label}</option>
                ))}
              </select>
            </div>

            {/* 右侧操作 */}
            <div className="flex gap-2">
              {/* 视图切换 */}
              <button
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                className="p-2.5 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
              >
                {viewMode === 'grid' ? <List className="w-5 h-5 text-[#B4C7E7]" /> : <Grid className="w-5 h-5 text-[#B4C7E7]" />}
              </button>

              {/* 上传按钮 */}
              <label className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all font-medium cursor-pointer">
                <Upload className="w-4 h-4" />
                <span>上传资源</span>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                />
              </label>
            </div>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总资源数</div>
            <div className="text-2xl font-bold text-white">{resources.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">图片</div>
            <div className="text-2xl font-bold text-[#00C3FF]">
              {resources.filter(r => r.type === 'image').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">视频</div>
            <div className="text-2xl font-bold text-[#FFB800]">
              {resources.filter(r => r.type === 'video').length}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4">
            <div className="text-[#B4C7E7] text-sm mb-1">总大小</div>
            <div className="text-2xl font-bold text-[#00FF88]">
              {formatFileSize(resources.reduce((sum, r) => sum + r.size, 0))}
            </div>
          </div>
        </div>

        {/* 知识库区域 */}
        {knowledgeItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-[#00C3FF]" />
                知识库共享
              </h2>
              <span className="text-sm text-[#B4C7E7]">{knowledgeItems.length} 个知识库</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {knowledgeItems.map(item => {
                const categoryColors = {
                  'general': 'from-[#00C3FF] to-[#47D1FF]',
                  'tech': 'from-[#FFB800] to-[#FFC832]',
                  'business': 'from-[#00FF88] to-[#00CC6A]',
                  'design': 'from-[#FF6B9D] to-[#FF8FB1]'
                }
                const colorClass = categoryColors[item.category as keyof typeof categoryColors] || 'from-[#00C3FF] to-[#47D1FF]'
                
                return (
                  <div 
                    key={item.id} 
                    className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 hover:border-[#00C3FF]/50 transition-all group cursor-pointer"
                    onClick={() => handleKnowledgeClick(item)}
                  >
                    <div className="flex items-start gap-3 mb-3">
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClass} flex items-center justify-center flex-shrink-0`}>
                        <BookOpen className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-white truncate">{item.title}</div>
                        <div className="text-xs text-[#B4C7E7] mt-1 line-clamp-2">{item.content}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-1">
                        {item.tags.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className="text-xs px-2 py-0.5 bg-[#0A0D18] rounded text-[#B4C7E7]">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleKnowledgeFavorite(item.id)
                        }}
                        className="p-1 hover:bg-[#00C3FF]/20 rounded transition-all"
                      >
                        <Star className={`w-4 h-4 ${item.is_favorite ? 'text-[#FFB800] fill-[#FFB800]' : 'text-[#B4C7E7] hover:text-[#FFB800]'}`} />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* 资源展示 */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filteredResources.map(resource => {
              const TypeIcon = typeIcons[resource.type]
              return (
                <div key={resource.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4 hover:border-[#00C3FF]/50 transition-all group">
                  <div className="relative mb-3">
                    {/* 预览区 */}
                    <div className="aspect-square bg-[#0A0D18] rounded-lg flex items-center justify-center overflow-hidden">
                      {resource.type === 'image' ? (
                        <img src={resource.url} alt={resource.name} className="w-full h-full object-cover" />
                      ) : (
                        <TypeIcon className="w-12 h-12 text-[#B4C7E7]/50" />
                      )}
                    </div>

                    {/* 悬浮操作 */}
                    <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-all">
                      <button
                        onClick={() => toggleFavorite(resource.id)}
                        className="p-1.5 bg-black/60 rounded-lg hover:bg-black/80 transition-all"
                      >
                        <Star className={`w-4 h-4 ${resource.is_favorite ? 'text-[#FFB800] fill-[#FFB800]' : 'text-white'}`} />
                      </button>
                      <button
                        onClick={() => deleteResource(resource.id)}
                        className="p-1.5 bg-black/60 rounded-lg hover:bg-red-600/80 transition-all"
                      >
                        <Trash2 className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* 文件信息 */}
                  <div className="space-y-1">
                    <div className="text-sm font-medium text-white truncate">{resource.name}</div>
                    <div className="text-xs text-[#B4C7E7]">{formatFileSize(resource.size)}</div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredResources.map(resource => {
              const TypeIcon = typeIcons[resource.type]
              return (
                <div key={resource.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-4 hover:border-[#00C3FF]/50 transition-all flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#0A0D18] rounded-lg flex items-center justify-center flex-shrink-0">
                    {resource.type === 'image' ? (
                      <img src={resource.url} alt={resource.name} className="w-full h-full object-cover rounded-lg" />
                    ) : (
                      <TypeIcon className="w-6 h-6 text-[#B4C7E7]/50" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">{resource.name}</div>
                    <div className="text-xs text-[#B4C7E7]">{formatFileSize(resource.size)} · {new Date(resource.created_at).toLocaleString()}</div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleFavorite(resource.id)}
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
                    >
                      <Star className={`w-4 h-4 ${resource.is_favorite ? 'text-[#FFB800] fill-[#FFB800]' : 'text-[#B4C7E7]'}`} />
                    </button>
                    <a
                      href={resource.url}
                      download
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-[#00C3FF]/20 transition-all"
                    >
                      <Download className="w-4 h-4 text-[#B4C7E7]" />
                    </a>
                    <button
                      onClick={() => deleteResource(resource.id)}
                      className="p-2 bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg hover:bg-red-600/20 transition-all"
                    >
                      <Trash2 className="w-4 h-4 text-[#B4C7E7]" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {filteredResources.length === 0 && (
          <div className="text-center py-12 text-[#B4C7E7]">
            <File className="w-12 h-12 mx-auto mb-4 text-[#B4C7E7]/40" />
            <p className="text-lg">暂无资源</p>
            <p className="text-sm mt-2">点击"上传资源"开始添加您的文件</p>
          </div>
        )}
      </div>

      {/* 知识库详情模态框 */}
      {showKnowledgeModal && selectedKnowledge && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[999999] flex items-center justify-center p-4" onClick={() => setShowKnowledgeModal(false)}>
          <div className="bg-[#121A2F] border border-[#00C3FF]/30 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            {/* 标题栏 */}
            <div className="bg-gradient-to-r from-[#0A0D18] to-[#121A2F] border-b border-[#00C3FF]/30 p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#00C3FF] to-[#47D1FF] flex items-center justify-center flex-shrink-0">
                    <BookOpen className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-white mb-2">{selectedKnowledge.title}</h2>
                    <div className="flex items-center gap-4 text-sm text-[#B4C7E7]">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-[#00C3FF]/20 rounded text-[#00C3FF]">
                          {selectedKnowledge.category}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>更新于 {new Date(selectedKnowledge.updated_at).toLocaleDateString('zh-CN')}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowKnowledgeModal(false)}
                  className="p-2 hover:bg-[#00C3FF]/20 rounded-lg transition-all"
                >
                  <svg className="w-6 h-6 text-[#B4C7E7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* 内容区 */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {selectedKnowledge.content}
                </p>
              </div>

              {/* 标签 */}
              {selectedKnowledge.tags && selectedKnowledge.tags.length > 0 && (
                <div className="mt-6 pt-6 border-t border-[#00C3FF]/20">
                  <div className="flex flex-wrap gap-2">
                    {selectedKnowledge.tags.map((tag, idx) => (
                      <span key={idx} className="px-3 py-1 bg-[#0A0D18] rounded-full text-sm text-[#B4C7E7] border border-[#00C3FF]/20">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 操作栏 */}
            <div className="bg-gradient-to-r from-[#0A0D18] to-[#121A2F] border-t border-[#00C3FF]/30 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleKnowledgeFavorite(selectedKnowledge.id)
                      setShowKnowledgeModal(false)
                    }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      selectedKnowledge.is_favorite 
                        ? 'bg-[#FFB800]/20 text-[#FFB800] border border-[#FFB800]/30' 
                        : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20 hover:border-[#00C3FF]/50'
                    }`}
                  >
                    <Star className={`w-4 h-4 ${selectedKnowledge.is_favorite ? 'fill-[#FFB800]' : ''}`} />
                    <span>{selectedKnowledge.is_favorite ? '已收藏' : '收藏'}</span>
                  </button>
                </div>
                <button
                  onClick={() => setShowKnowledgeModal(false)}
                  className="px-6 py-2 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all font-medium"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserResources