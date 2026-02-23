import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, BookOpen, Building2, Package, HelpCircle, MessageCircle, Clock, Search, ChevronRight, Grid, List } from 'lucide-react'

interface DocItem {
  id: number
  title: string
  slug: string
  category: string
  description: string
  icon: string
  is_published: boolean
  created_at: string
  updated_at: string
}

interface DocDetail extends DocItem {
  content: string
}

const DocViewer = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const [doc, setDoc] = useState<DocDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (slug) {
      loadDoc(slug)
    }
  }, [slug])

  const loadDoc = async (docSlug: string) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/docs/${docSlug}`)
      const data = await response.json()

      if (data.success) {
        setDoc(data.data)
        setError(null)
      } else {
        setError(data.message || '加载文档失败')
      }
    } catch (err) {
      setError('网络错误，请稍后重试')
      console.error('加载文档失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const renderMarkdown = (content: string) => {
    // 简单的Markdown渲染
    return content
      .replace(/^# (.*)/gm, '<h1 class="text-3xl font-bold text-white mb-6 mt-8">$1</h1>')
      .replace(/^## (.*)/gm, '<h2 class="text-2xl font-bold text-cyan-400 mb-4 mt-6">$1</h2>')
      .replace(/^### (.*)/gm, '<h3 class="text-xl font-bold text-[#47D1FF] mb-3 mt-4">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="bg-[#00C3FF]/20 text-cyan-300 px-2 py-1 rounded text-sm">$1</code>')
      .replace(/^- (.*)/gm, '<li class="text-gray-300 ml-4 mb-2">$1</li>')
      .replace(/^(\d+)\. (.*)/gm, '<li class="text-gray-300 ml-4 mb-2">$2</li>')
      .replace(/\n\n/g, '<br/><br/>')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-cyan-400/30 rounded-full"></div>
              <div className="w-16 h-16 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !doc) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <button
              onClick={() => navigate('/docs')}
              className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 mb-8 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              返回文档列表
            </button>

            <div className={`${doc ? 'hidden' : 'block'} bg-red-500/10 border border-red-500/50 rounded-2xl p-8 text-center`}>
              <HelpCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-red-400 mb-2">加载失败</h2>
              <p className="text-gray-400">{error || '文档不存在'}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* 返回按钮 */}
          <button
            onClick={() => navigate('/docs')}
            className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 mb-8 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            返回文档列表
          </button>

          {/* 文档标题 */}
          <div className="bg-gradient-to-r from-[#0A0D18] to-[#121A2F] border border-[#00C3FF]/30 rounded-2xl p-8 mb-6">
            <div className="flex items-start gap-4">
              <div className="text-5xl">{doc.icon}</div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-3">{doc.title}</h1>
                <p className="text-gray-400 mb-4">{doc.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>更新于 {new Date(doc.updated_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 文档内容 */}
          <div className="bg-[#0A0D18]/50 backdrop-blur-xl border border-[#00C3FF]/20 rounded-2xl p-8 prose prose-invert max-w-none">
            <div
              className="text-gray-300 leading-relaxed"
              dangerouslySetInnerHTML={{
                __html: renderMarkdown(doc.content)
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

const DocsList = () => {
  const navigate = useNavigate()
  const [docs, setDocs] = useState<DocItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    loadDocs()
  }, [])

  const loadDocs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/docs')
      const data = await response.json()

      if (data.success) {
        setDocs(data.data)
      }
    } catch (err) {
      console.error('加载文档列表失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const categories = [
    { id: 'all', name: '全部', icon: Grid },
    { id: 'company', name: '公司介绍', icon: Building2 },
    { id: 'product', name: '产品介绍', icon: Package },
    { id: 'guide', name: '使用指南', icon: BookOpen },
    { id: 'support', name: '支持服务', icon: HelpCircle },
  ]

  const categoryIcons: Record<string, string> = {
    company: '🏢',
    product: '📦',
    guide: '📖',
    support: '💬',
  }

  const filteredDocs = docs.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            帮助中心
          </h1>
          <p className="text-gray-400">查找您需要的信息和帮助</p>
        </div>

        {/* 搜索栏 */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
            <input
              type="text"
              placeholder="搜索文档..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#0A0D18]/50 backdrop-blur-xl border border-[#00C3FF]/30 rounded-xl pl-12 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#00C3FF] transition-colors"
            />
          </div>
        </div>

        {/* 分类筛选 */}
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map(category => {
            const Icon = category.icon
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  selectedCategory === category.id
                    ? 'bg-[#00C3FF]/20 text-[#00C3FF] border border-[#00C3FF]/50'
                    : 'bg-[#0A0D18]/50 text-gray-400 border border-[#00C3FF]/20 hover:border-[#00C3FF]/50 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm">{category.name}</span>
              </button>
            )
          })}
        </div>

        {/* 视图切换 */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-400 text-sm">
            找到 {filteredDocs.length} 个文档
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-all ${
                viewMode === 'grid'
                  ? 'bg-[#00C3FF]/20 text-[#00C3FF]'
                  : 'bg-[#0A0D18]/50 text-gray-400 hover:text-white'
              }`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-all ${
                viewMode === 'list'
                  ? 'bg-[#00C3FF]/20 text-[#00C3FF]'
                  : 'bg-[#0A0D18]/50 text-gray-400 hover:text-white'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 文档列表 */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-cyan-400/30 rounded-full"></div>
              <div className="w-16 h-16 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0"></div>
            </div>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center py-20">
            <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">没有找到文档</h3>
            <p className="text-gray-500">请尝试其他搜索条件</p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDocs.map(doc => (
              <div
                key={doc.id}
                onClick={() => navigate(`/docs/${doc.slug}`)}
                className="bg-[#0A0D18]/50 backdrop-blur-xl border border-[#00C3FF]/20 rounded-2xl p-6 cursor-pointer transition-all hover:border-[#00C3FF]/50 hover:scale-105 group"
              >
                <div className="text-4xl mb-4">{doc.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                  {doc.title}
                </h3>
                <p className="text-gray-400 text-sm mb-4 line-clamp-2">{doc.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(doc.updated_at).toLocaleDateString('zh-CN')}
                  </span>
                  <ChevronRight className="w-4 h-4 text-cyan-400 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredDocs.map(doc => (
              <div
                key={doc.id}
                onClick={() => navigate(`/docs/${doc.slug}`)}
                className="bg-[#0A0D18]/50 backdrop-blur-xl border border-[#00C3FF]/20 rounded-xl p-6 cursor-pointer transition-all hover:border-[#00C3FF]/50 hover:scale-[1.02] group"
              >
                <div className="flex items-center gap-4">
                  <div className="text-4xl flex-shrink-0">{doc.icon}</div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                      {doc.title}
                    </h3>
                    <p className="text-gray-400 text-sm line-clamp-1">{doc.description}</p>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <span className="text-xs text-gray-500">
                      {new Date(doc.updated_at).toLocaleDateString('zh-CN')}
                    </span>
                    <ChevronRight className="w-5 h-5 text-cyan-400 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// 根据是否有slug参数决定显示哪个组件
const Docs = () => {
  const { slug } = useParams<{ slug?: string }>()

  if (slug) {
    return <DocViewer />
  }

  return <DocsList />
}

export default Docs
