import { useState, useEffect } from 'react'
import {
  Clock, Eye, Tag, TrendingUp, ArrowRight, Calendar,
  Search, Share2, MessageCircle, Pin, Bell, ThumbsUp,
  Globe, Filter, Heart, BookmarkPlus
} from 'lucide-react'
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
  is_pinned: boolean
  view_count: number
  share_count: number
  language: string
  created_at: string
  published_at: string
  author: string
}

interface Comment {
  id: number
  user_id: number
  username: string
  content: string
  parent_id: number
  like_count: number
  created_at: string
}

interface Category {
  id: number
  code: string
  name: string
  description: string
  icon: string
  color: string
  sort_order: number
}

interface NewsSectionProps {
  limit?: number
  showMore?: boolean
  category?: string
  featured?: boolean
  showSearch?: boolean
  showFilters?: boolean
}

const NewsSectionComplete: React.FC<NewsSectionProps> = ({
  limit = 5,
  showMore = true,
  category,
  featured,
  showSearch = true,
  showFilters = true
}) => {
  const [articles, setArticles] = useState<NewsArticle[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedArticle, setExpandedArticle] = useState<number | null>(null)
  const [showComments, setShowComments] = useState<number | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>(category || 'all')
  const [showNotifications, setShowNotifications] = useState(false)
  const [notificationCount, setNotificationCount] = useState(0)
  const [recommendations, setRecommendations] = useState<NewsArticle[]>([])

  // 模拟用户ID（实际应从认证上下文获取）
  const userId = 1

  useEffect(() => {
    loadNews()
    loadCategories()
    loadRecommendations()
    loadNotifications()
  }, [category, featured, selectedCategory])

  const loadNews = async (keyword?: string) => {
    try {
      setLoading(true)
      const params: any = { limit }
      if (category && selectedCategory === 'all') params.category = category
      if (selectedCategory !== 'all') params.category = selectedCategory
      if (featured !== undefined) params.featured = featured ? 1 : 0

      const endpoint = keyword ? '/api/v9/news/articles/search' : '/api/v9/news/articles'
      const searchParams = keyword ? { ...params, keyword } : params

      const response = await api.get(endpoint, { params: searchParams })
      if (response.data.success) {
        setArticles(response.data.data)
      }
    } catch (error) {
      console.error('加载动态资讯失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await api.get('/api/v9/news/categories')
      if (response.data.success) {
        setCategories(response.data.data)
      }
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const loadComments = async (articleId: number) => {
    try {
      const response = await api.get(`/api/v9/news/articles/${articleId}/comments`)
      if (response.data.success) {
        setComments(response.data.data)
      }
    } catch (error) {
      console.error('加载评论失败:', error)
    }
  }

  const loadNotifications = async () => {
    try {
      const response = await api.get('/api/v9/news/notifications', {
        params: { user_id: userId }
      })
      if (response.data.success) {
        const unreadCount = response.data.data.filter((n: any) => !n.is_read).length
        setNotificationCount(unreadCount)
      }
    } catch (error) {
      console.error('加载通知失败:', error)
    }
  }

  const loadRecommendations = async () => {
    try {
      const response = await api.get(`/api/v9/news/recommendations/${userId}`)
      if (response.data.success) {
        setRecommendations(response.data.data)
      }
    } catch (error) {
      console.error('加载推荐失败:', error)
    }
  }

  const handleSearch = () => {
    if (searchKeyword.trim()) {
      loadNews(searchKeyword)
    }
  }

  const handleShare = async (articleId: number) => {
    try {
      await api.post(`/api/v9/news/articles/${articleId}/share`)
      alert('分享成功！链接已复制到剪贴板')
    } catch (error) {
      console.error('分享失败:', error)
    }
  }

  const handleLike = async (commentId: number) => {
    try {
      await api.post(`/api/v9/news/comments/${commentId}/like`, { user_id: userId })
      // 重新加载评论
      if (showComments) {
        loadComments(showComments)
      }
    } catch (error) {
      console.error('点赞失败:', error)
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

  const getCategoryColor = (categoryCode: string) => {
    const category = categories.find(c => c.code === categoryCode)
    return category?.color || 'from-gray-500 to-gray-600'
  }

  const getCategoryIcon = (categoryCode: string) => {
    const category = categories.find(c => c.code === categoryCode)
    return category?.icon || '📰'
  }

  const getCategoryName = (categoryCode: string) => {
    const category = categories.find(c => c.code === categoryCode)
    return category?.name || categoryCode
  }

  const toggleExpand = (articleId: number) => {
    setExpandedArticle(expandedArticle === articleId ? null : articleId)
  }

  const toggleComments = (articleId: number) => {
    if (showComments === articleId) {
      setShowComments(null)
    } else {
      setShowComments(articleId)
      loadComments(articleId)
    }
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
        <div className="flex items-center gap-3">
          {/* 通知按钮 */}
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <Bell className="w-5 h-5" />
            {notificationCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                {notificationCount}
              </span>
            )}
          </button>
          {showMore && (
            <button className="text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 text-sm">
              查看更多
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* 搜索和筛选 */}
      {(showSearch || showFilters) && (
        <div className="mb-6 space-y-4">
          {/* 搜索框 */}
          {showSearch && (
            <div className="relative">
              <input
                type="text"
                placeholder="搜索资讯..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full bg-gray-800/60 border border-gray-700/50 rounded-xl px-4 py-3 pl-12 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500/50 transition-colors"
              />
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                onClick={handleSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 px-4 py-1.5 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors text-sm"
              >
                搜索
              </button>
            </div>
          )}

          {/* 分类筛选 */}
          {showFilters && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedCategory === 'all'
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                    : 'bg-gray-800/60 text-gray-400 hover:bg-gray-700/60 border border-gray-700/50'
                }`}
              >
                <Filter className="w-4 h-4 inline mr-1" />
                全部
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.code}
                  onClick={() => setSelectedCategory(cat.code)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedCategory === cat.code
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'bg-gray-800/60 text-gray-400 hover:bg-gray-700/60 border border-gray-700/50'
                  }`}
                >
                  <span className="mr-1">{cat.icon}</span>
                  {cat.name}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 资讯列表 */}
      <div className="space-y-4">
        {articles.map((article) => (
          <div
            key={article.id}
            className={`
              group bg-gray-800/40 rounded-xl p-4 border border-gray-700/50
              hover:border-cyan-500/50 hover:bg-gray-800/60 transition-all duration-300
              cursor-pointer
              ${article.is_pinned ? 'ring-1 ring-yellow-500/30' : ''}
              ${article.is_featured ? 'ring-1 ring-purple-500/30' : ''}
            `}
          >
            {/* 顶部标识 */}
            <div className="flex items-center gap-2 mb-3">
              {article.is_pinned && (
                <span className="px-2 py-0.5 bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs rounded-full font-medium flex items-center gap-1">
                  <Pin className="w-3 h-3" />
                  置顶
                </span>
              )}
              {article.is_featured && (
                <span className="px-2 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs rounded-full font-medium">
                  精选
                </span>
              )}
            </div>

            {/* 图片展示 */}
            {article.image_url && (
              <div className="mb-3 rounded-lg overflow-hidden">
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-48 object-cover hover:scale-105 transition-transform duration-300"
                />
              </div>
            )}

            {/* 标题和时间 */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3
                onClick={() => toggleExpand(article.id)}
                className="flex-1 text-white font-medium group-hover:text-cyan-400 transition-colors line-clamp-2"
              >
                {article.title}
              </h3>
            </div>

            {/* 元数据 */}
            <div className="flex items-center flex-wrap gap-3 text-xs text-gray-400 mb-3">
              {/* 分类标签 */}
              <span className={`
                px-2 py-0.5 rounded-full text-white font-medium flex items-center gap-1
                bg-gradient-to-r ${getCategoryColor(article.category)}
              `}>
                <span>{getCategoryIcon(article.category)}</span>
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

              {/* 分享数 */}
              <span className="flex items-center gap-1">
                <Share2 className="w-3 h-3" />
                {article.share_count}
              </span>

              {/* 语言 */}
              {article.language && (
                <span className="flex items-center gap-1">
                  <Globe className="w-3 h-3" />
                  {article.language}
                </span>
              )}
            </div>

            {/* 操作按钮 */}
            <div className="flex items-center gap-2 border-t border-gray-700/50 pt-3">
              <button
                onClick={() => toggleExpand(article.id)}
                className="flex-1 py-2 px-4 bg-gray-700/30 hover:bg-gray-700/50 text-gray-300 hover:text-white rounded-lg transition-all text-xs flex items-center justify-center gap-1"
              >
                {expandedArticle === article.id ? '收起详情' : '查看详情'}
              </button>
              <button
                onClick={() => handleShare(article.id)}
                className="py-2 px-4 bg-gray-700/30 hover:bg-cyan-500/20 hover:text-cyan-400 text-gray-300 rounded-lg transition-all text-xs flex items-center justify-center gap-1"
              >
                <Share2 className="w-3 h-3" />
                分享
              </button>
              <button
                onClick={() => toggleComments(article.id)}
                className={`py-2 px-4 rounded-lg transition-all text-xs flex items-center justify-center gap-1 ${
                  showComments === article.id
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'bg-gray-700/30 text-gray-300 hover:bg-cyan-500/20 hover:text-cyan-400'
                }`}
              >
                <MessageCircle className="w-3 h-3" />
                评论
              </button>
              <button className="py-2 px-4 bg-gray-700/30 hover:bg-red-500/20 hover:text-red-400 text-gray-300 rounded-lg transition-all text-xs">
                <BookmarkPlus className="w-3 h-3" />
              </button>
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

            {/* 评论区 */}
            {showComments === article.id && (
              <div className="mt-4 pt-4 border-t border-gray-700/50">
                <div className="mb-4">
                  <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <MessageCircle className="w-4 h-4 text-cyan-400" />
                    评论 ({comments.length})
                  </h4>
                  {/* 评论输入框 */}
                  <textarea
                    placeholder="发表评论..."
                    className="w-full bg-gray-800/60 border border-gray-700/50 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500/50 transition-colors text-sm resize-none"
                    rows={3}
                  />
                  <button className="mt-2 px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors text-sm">
                    发表评论
                  </button>
                </div>
                {/* 评论列表 */}
                <div className="space-y-3">
                  {comments.map((comment) => (
                    <div key={comment.id} className="bg-gray-800/40 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium text-sm">
                          {formatAuthorName(comment.username)}
                        </span>
                        <span className="text-gray-400 text-xs">{formatDate(comment.created_at)}</span>
                      </div>
                      <p className="text-gray-300 text-sm mb-2">{comment.content}</p>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleLike(comment.id)}
                          className="text-xs text-gray-400 hover:text-cyan-400 flex items-center gap-1"
                        >
                          <ThumbsUp className="w-3 h-3" />
                          {comment.like_count}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 个性化推荐 */}
      {recommendations.length > 0 && (
        <div className="mt-8 pt-8 border-t border-gray-700/50">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Heart className="w-5 h-5 text-pink-400" />
            为您推荐
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((article) => (
              <div
                key={article.id}
                className="bg-gray-800/40 rounded-lg p-4 border border-gray-700/50 hover:border-cyan-500/50 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-0.5 rounded-full text-white text-xs bg-gradient-to-r ${getCategoryColor(article.category)}`}>
                    {getCategoryIcon(article.category)} {getCategoryName(article.category)}
                  </span>
                </div>
                <h4 className="text-white font-medium mb-2 line-clamp-2">{article.title}</h4>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Eye className="w-3 h-3" />
                    {article.view_count}
                  </span>
                  <span>{formatDate(article.published_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 加载更多 */}
      {showMore && articles.length >= limit && (
        <button className="w-full mt-6 py-3 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/30 transition-all flex items-center justify-center gap-2 group">
          加载更多
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      )}
    </div>
  )
}

export default NewsSectionComplete
