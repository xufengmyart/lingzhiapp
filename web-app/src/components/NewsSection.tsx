import { useState, useEffect } from 'react'
import { Clock, Eye, Tag, TrendingUp, ArrowRight, Calendar } from 'lucide-react'
import api from '../services/api'
import { formatAuthorName } from '../utils/userDisplayName'

export interface NewsArticle {
  id: number
  title: string
  content: string
  category: string
  tags: string[]
  image_url?: string
  is_featured: boolean
  view_count: number
  created_at: string
  published_at: string
  author: string
}

interface NewsSectionProps {
  limit?: number
  showMore?: boolean
  category?: string
  featured?: boolean
}

const NewsSection: React.FC<NewsSectionProps> = ({
  limit = 5,
  showMore = true,
  category,
  featured
}) => {
  const [articles, setArticles] = useState<NewsArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedArticle, setExpandedArticle] = useState<number | null>(null)

  useEffect(() => {
    loadNews()
  }, [category, featured])

  const loadNews = async () => {
    try {
      setLoading(true)
      const params: any = { limit }
      if (category) params.category = category
      if (featured !== undefined) params.featured = featured ? 1 : 0

      const response = await api.get('/api/v9/news/articles', { params })
      if (response.data.success) {
        setArticles(response.data.data)
      }
    } catch (error) {
      console.error('加载动态资讯失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      general: 'from-blue-500 to-cyan-500',
      feature: 'from-purple-500 to-pink-500',
      update: 'from-green-500 to-emerald-500',
      announcement: 'from-orange-500 to-red-500',
      event: 'from-yellow-500 to-orange-500'
    }
    return colors[category] || 'from-gray-500 to-gray-600'
  }

  const getCategoryName = (category: string) => {
    const names: Record<string, string> = {
      general: '通用',
      feature: '新功能',
      update: '更新',
      announcement: '公告',
      event: '活动'
    }
    return names[category] || category
  }

  const toggleExpand = (articleId: number) => {
    setExpandedArticle(expandedArticle === articleId ? null : articleId)
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="h-4 bg-gray-700/50 rounded w-3/4"></div>
              <div className="h-3 bg-gray-700/30 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (articles.length === 0) {
    return (
      <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <div className="text-center py-8 text-gray-400">
          <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无动态资讯</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
      {/* 标题栏 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="relative">
            <TrendingUp className="w-6 h-6 text-cyan-400" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
          </div>
          <h2 className="text-xl font-bold text-white">动态资讯</h2>
        </div>
        {showMore && (
          <button className="text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 text-sm">
            查看更多
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 资讯列表 */}
      <div className="space-y-4">
        {articles.map((article) => (
          <div
            key={article.id}
            className={`
              group bg-gray-800/40 rounded-xl p-4 border border-gray-700/50 
              hover:border-cyan-500/50 hover:bg-gray-800/60 transition-all duration-300
              cursor-pointer
              ${article.is_featured ? 'ring-1 ring-purple-500/30' : ''}
            `}
            onClick={() => toggleExpand(article.id)}
          >
            {/* 精选标识 */}
            {article.is_featured && (
              <div className="absolute top-2 right-2">
                <span className="px-2 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs rounded-full font-medium">
                  精选
                </span>
              </div>
            )}

            {/* 标题和时间 */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="flex-1 text-white font-medium group-hover:text-cyan-400 transition-colors line-clamp-2">
                {article.title}
              </h3>
            </div>

            {/* 元数据 */}
            <div className="flex items-center gap-4 text-xs text-gray-400">
              {/* 分类标签 */}
              <span className={`
                px-2 py-0.5 rounded-full text-white font-medium
                bg-gradient-to-r ${getCategoryColor(article.category)}
              `}>
                {getCategoryName(article.category)}
              </span>

              {/* 时间 */}
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(article.published_at || article.created_at)}
              </span>

              {/* 浏览量 */}
              <span className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                {article.view_count}
              </span>

              {/* 标签 */}
              {article.tags && article.tags.length > 0 && (
                <span className="flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  {article.tags[0]}
                </span>
              )}
            </div>

            {/* 展开内容 */}
            {expandedArticle === article.id && (
              <div className="mt-4 pt-4 border-t border-gray-700/50">
                <div
                  className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: article.content }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 更多按钮 */}
      {showMore && articles.length >= limit && (
        <button className="w-full mt-6 py-3 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/30 transition-all flex items-center justify-center gap-2 group">
          加载更多
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      )}
    </div>
  )
}

export default NewsSection
