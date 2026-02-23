import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Building2,
  MapPin,
  Phone,
  Mail,
  Globe,
  Star,
  Shield,
  Calendar,
  Users,
  DollarSign,
  CheckCircle,
  AlertCircle,
  Clock,
  Heart,
  MessageSquare,
  Send,
  X,
  ThumbsUp,
  Tag,
  Award,
  TrendingUp,
  BarChart3,
  PieChart,
  ArrowLeft,
  Share2
} from 'lucide-react'

interface Merchant {
  id: number
  name: string
  description: string
  category: string
  logo: string
  rating: number
  review_count: number
  location: string
  phone: string
  email: string
  website: string
  business_license: string
  verified: boolean
  established_year: number
  services: string[]
  tags: string[]
  status: string
  joined_date: string
  lingzhi_points: number
  total_deals: number
  reviews: any[]
}

interface Review {
  id: number
  rating: number
  review: string
  created_at: string
  username: string
}

const MerchantDetail = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [merchant, setMerchant] = useState<Merchant | null>(null)
  const [loading, setLoading] = useState(true)
  const [isFavorited, setIsFavorited] = useState(false)
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [showCollabModal, setShowCollabModal] = useState(false)
  const [reviewForm, setReviewForm] = useState({ rating: 5, review: '' })
  const [collabForm, setCollabForm] = useState({
    project_title: '',
    project_description: '',
    budget: '',
    contact_method: ''
  })
  const [analytics, setAnalytics] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'info' | 'reviews' | 'analytics'>('info')

  useEffect(() => {
    if (id) {
      loadMerchant()
      loadAnalytics()
    }
  }, [id])

  const loadMerchant = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/merchants/${id}`)
      if (response.ok) {
        const data = await response.json()
        setMerchant(data)
      }
    } catch (error) {
      console.error('Failed to load merchant:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${apiBase}/merchants/analytics`)
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
    }
  }

  const handleFavorite = async () => {
    if (!user) {
      alert('请先登录')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${apiBase}/merchants/${id}/favorite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setIsFavorited(data.favorited)
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }

  const handleSubmitReview = async () => {
    if (!user) {
      alert('请先登录')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${apiBase}/merchants/${id}/reviews`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reviewForm)
      })
      if (response.ok) {
        setShowReviewModal(false)
        setReviewForm({ rating: 5, review: '' })
        loadMerchant()
        alert('评价成功')
      }
    } catch (error) {
      console.error('Failed to submit review:', error)
    }
  }

  const handleSubmitCollab = async () => {
    if (!user) {
      alert('请先登录')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${apiBase}/merchants/${id}/collaborations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...collabForm,
          budget: parseFloat(collabForm.budget) || 0
        })
      })
      if (response.ok) {
        setShowCollabModal(false)
        setCollabForm({
          project_title: '',
          project_description: '',
          budget: '',
          contact_method: ''
        })
        alert('合作申请已提交')
      }
    } catch (error) {
      console.error('Failed to submit collaboration:', error)
    }
  }

  const renderStars = (rating: number, interactive = false) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={20}
            className={`cursor-pointer transition-colors ${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
            onClick={() => {
              if (interactive) {
                setReviewForm({ ...reviewForm, rating: star })
              }
            }}
          />
        ))}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (!merchant) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">商家不存在</h3>
          <button
            onClick={() => navigate('/merchant-pool')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回商家列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/merchant-pool')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-6 h-6 text-gray-600" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{merchant.name}</h1>
                <p className="text-sm text-gray-600">{merchant.category}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleFavorite}
                className={`p-2 rounded-lg transition-colors ${
                  isFavorited
                    ? 'bg-red-50 text-red-600'
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
              >
                <Heart
                  className={`w-6 h-6 ${isFavorited ? 'fill-current' : ''}`}
                />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-600">
                <Share2 className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Merchant Info */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-start gap-6 mb-6">
            <div className="w-24 h-24 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Building2 className="w-12 h-12 text-gray-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-gray-900">{merchant.name}</h2>
                {merchant.verified && (
                  <div className="flex items-center gap-1 text-blue-600">
                    <Shield size={16} />
                    <span className="text-sm">已认证</span>
                  </div>
                )}
              </div>
              <p className="text-gray-600 mb-4">{merchant.description}</p>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Star size={16} className="fill-yellow-400 text-yellow-400" />
                  <span className="font-medium">{merchant.rating}</span>
                  <span>({merchant.review_count}条评价)</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users size={16} />
                  <span>{merchant.total_deals}笔交易</span>
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign size={16} />
                  <span>{merchant.lingzhi_points}灵值</span>
                </div>
              </div>
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-6">
            {merchant.tags.map((tag, index) => (
              <span key={index} className="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
                <Tag size={12} />
                {tag}
              </span>
            ))}
          </div>

          {/* Contact Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin size={16} />
              <span>{merchant.location}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar size={16} />
              <span>{merchant.established_year}年创立</span>
            </div>
            {merchant.phone && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Phone size={16} />
                <a href={`tel:${merchant.phone}`} className="hover:text-blue-600">
                  {merchant.phone}
                </a>
              </div>
            )}
            {merchant.email && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Mail size={16} />
                <a href={`mailto:${merchant.email}`} className="hover:text-blue-600">
                  {merchant.email}
                </a>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowCollabModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Send size={20} />
              发起合作
            </button>
            {merchant.website && (
              <a
                href={merchant.website}
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <Globe size={20} />
                访问官网
              </a>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <div className="flex">
              {[
                { id: 'info', label: '详细信息', icon: MessageSquare },
                { id: 'reviews', label: '用户评价', icon: ThumbsUp },
                { id: 'analytics', label: '数据分析', icon: BarChart3 }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-6 py-4 transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <tab.icon size={20} />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'info' && (
              <div className="space-y-6">
                {/* Services */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">主营服务</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {merchant.services.map((service, index) => (
                      <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                        <CheckCircle size={16} className="text-green-600" />
                        <span className="text-gray-700">{service}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* License Info */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">营业执照</h3>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 font-mono text-sm">
                      {merchant.business_license}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="space-y-6">
                {/* Write Review */}
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">用户评价</h3>
                  <button
                    onClick={() => setShowReviewModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <MessageSquare size={18} />
                    写评价
                  </button>
                </div>

                {/* Reviews List */}
                {merchant.reviews && merchant.reviews.length > 0 ? (
                  <div className="space-y-4">
                    {merchant.reviews.map((review: Review) => (
                      <div key={review.id} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 font-semibold">
                                {review.username?.[0]?.toUpperCase() || 'U'}
                              </span>
                            </div>
                            <span className="font-medium text-gray-900">
                              {review.username || '匿名用户'}
                            </span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {new Date(review.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              size={16}
                              className={`${
                                star <= review.rating
                                  ? 'fill-yellow-400 text-yellow-400'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <p className="text-gray-700">{review.review}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">暂无评价</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="space-y-6">
                {analytics && (
                  <>
                    {/* Overall Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">总商家数</span>
                          <Building2 className="w-5 h-5 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">
                          {analytics.overall?.total_merchants || 0}
                        </p>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">活跃商家</span>
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">
                          {analytics.overall?.active_merchants || 0}
                        </p>
                      </div>
                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">总交易额</span>
                          <DollarSign className="w-5 h-5 text-purple-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">
                          {analytics.overall?.total_deals || 0}
                        </p>
                      </div>
                      <div className="p-4 bg-yellow-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">平均评分</span>
                          <Star className="w-5 h-5 text-yellow-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">
                          {(analytics.overall?.avg_rating || 0).toFixed(1)}
                        </p>
                      </div>
                    </div>

                    {/* Category Stats */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">类别分布</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {analytics.by_category?.map((cat: any) => (
                          <div key={cat.category} className="p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium text-gray-900">{cat.category}</span>
                              <span className="text-sm text-gray-600">{cat.count}家</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Star size={14} className="fill-yellow-400 text-yellow-400" />
                              <span className="text-sm text-gray-600">{cat.avg_rating.toFixed(1)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Top Merchants */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">热门商家</h3>
                      <div className="space-y-3">
                        {analytics.top_merchants?.slice(0, 5).map((m: any) => (
                          <div
                            key={m.id}
                            onClick={() => navigate(`/merchant-detail/${m.id}`)}
                            className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                          >
                            <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                              <Building2 className="w-6 h-6 text-gray-400" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">{m.name}</h4>
                              <p className="text-sm text-gray-600">{m.category}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Star size={16} className="fill-yellow-400 text-yellow-400" />
                              <span className="font-medium">{m.rating}</span>
                              <span className="text-sm text-gray-600">({m.review_count})</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">写评价</h3>
              <button
                onClick={() => setShowReviewModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  评分
                </label>
                <div className="flex gap-2">
                  {renderStars(reviewForm.rating, true)}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  评价内容
                </label>
                <textarea
                  value={reviewForm.review}
                  onChange={(e) => setReviewForm({ ...reviewForm, review: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="分享您的体验..."
                />
              </div>
              <button
                onClick={handleSubmitReview}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                提交评价
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Collaboration Modal */}
      {showCollabModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">发起合作申请</h3>
              <button
                onClick={() => setShowCollabModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  项目标题 *
                </label>
                <input
                  type="text"
                  value={collabForm.project_title}
                  onChange={(e) =>
                    setCollabForm({ ...collabForm, project_title: e.target.value })
                  }
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="简要描述项目名称"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  项目描述 *
                </label>
                <textarea
                  value={collabForm.project_description}
                  onChange={(e) =>
                    setCollabForm({ ...collabForm, project_description: e.target.value })
                  }
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="详细描述项目内容和需求"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  预算（元）
                </label>
                <input
                  type="number"
                  value={collabForm.budget}
                  onChange={(e) =>
                    setCollabForm({ ...collabForm, budget: e.target.value })
                  }
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="项目预算"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  联系方式 *
                </label>
                <input
                  type="text"
                  value={collabForm.contact_method}
                  onChange={(e) =>
                    setCollabForm({ ...collabForm, contact_method: e.target.value })
                  }
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="手机号或邮箱"
                />
              </div>
              <button
                onClick={handleSubmitCollab}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                提交申请
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MerchantDetail
