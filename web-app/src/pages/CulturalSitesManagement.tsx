import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Edit, Eye, Search, Filter, ArrowLeft, MapPin, Star, Clock } from 'lucide-react'
import api from '../services/api'

interface CulturalSite {
  id: number
  name: string
  description: string
  location: string
  type: string
  status: string
  rating: number
  visitCount: number
  images: string[]
  openingHours: string
  admissionFee: number
  userId: number
  userName: string
  createdAt: string
  updatedAt: string
}

const CulturalSitesManagement = () => {
  const navigate = useNavigate()
  const [sites, setSites] = useState<CulturalSite[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSite, setSelectedSite] = useState<CulturalSite | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  
  // 筛选和搜索
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterType, setFilterType] = useState('all')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location: '',
    type: 'museum',
    status: 'active',
    rating: 5,
    openingHours: '',
    admissionFee: 0,
    images: []
  })

  useEffect(() => {
    fetchSites()
  }, [])

  const fetchSites = async () => {
    try {
      setLoading(true)
      const response = await api.get('/cultural-sites')
      if (response.data.success) {
        setSites(response.data.data || [])
      }
    } catch (err) {
      setError('获取文化圣地列表失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredSites = sites.filter(site => {
    const matchesSearch = site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         site.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         site.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || site.status === filterStatus
    const matchesType = filterType === 'all' || site.type === filterType
    return matchesSearch && matchesStatus && matchesType
  })

  const handleCreate = () => {
    setIsCreating(true)
    setIsEditing(false)
    setFormData({
      name: '',
      description: '',
      location: '',
      type: 'museum',
      status: 'active',
      rating: 5,
      openingHours: '',
      admissionFee: 0,
      images: []
    })
    setSelectedSite(null)
  }

  const handleEdit = (site: CulturalSite) => {
    setSelectedSite(site)
    setIsCreating(false)
    setIsEditing(true)
    setFormData({
      name: site.name,
      description: site.description,
      location: site.location,
      type: site.type,
      status: site.status,
      rating: site.rating,
      openingHours: site.openingHours || '',
      admissionFee: site.admissionFee || 0,
      images: site.images || []
    })
  }

  const handleView = (site: CulturalSite) => {
    setSelectedSite(site)
    setIsCreating(false)
    setIsEditing(false)
  }

  const handleDelete = async (siteId: number) => {
    if (!confirm('确定要删除这个文化圣地吗？')) {
      return
    }

    try {
      const response = await api.delete(`/cultural-sites/${siteId}`)
      if (response.data.success) {
        setMessage('文化圣地删除成功')
        fetchSites()
        if (selectedSite?.id === siteId) {
          setSelectedSite(null)
        }
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      if (isCreating) {
        const response = await api.post('/cultural-sites', formData)
        if (response.data.success) {
          setMessage('文化圣地创建成功')
          setIsCreating(false)
          fetchSites()
        } else {
          setError(response.data.message || '创建失败')
        }
      } else if (isEditing && selectedSite) {
        const response = await api.put(`/cultural-sites/${selectedSite.id}`, formData)
        if (response.data.success) {
          setMessage('文化圣地更新成功')
          setIsEditing(false)
          fetchSites()
          if (selectedSite.id) {
            handleView(selectedSite)
          }
        } else {
          setError(response.data.message || '更新失败')
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      active: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      inactive: 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/admin/modules')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">文化圣地管理</h1>
                <p className="text-sm text-gray-600">管理平台文化圣地和文化内容</p>
              </div>
            </div>
            <button
              onClick={handleCreate}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建文化圣地
            </button>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-green-50 text-green-800 px-4 py-3 rounded-lg">
            {message}
          </div>
        </div>
      )}
      {error && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-red-50 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* 筛选和搜索 */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="搜索文化圣地..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有状态</option>
              <option value="active">启用</option>
              <option value="pending">待审核</option>
              <option value="inactive">禁用</option>
            </select>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有类型</option>
              <option value="museum">博物馆</option>
              <option value="temple">寺庙</option>
              <option value="historical_site">历史古迹</option>
              <option value="park">公园</option>
            </select>
          </div>
        </div>

        <div className="flex gap-6">
          {/* 左侧列表 */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  文化圣地列表 ({filteredSites.length})
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">加载中...</div>
                ) : filteredSites.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    暂无文化圣地
                  </div>
                ) : (
                  filteredSites.map((site) => (
                    <div
                      key={site.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedSite?.id === site.id ? 'bg-indigo-50' : ''
                      }`}
                      onClick={() => handleView(site)}
                    >
                      <div className="flex items-start space-x-4">
                        {site.images && site.images.length > 0 && (
                          <img
                            src={site.images[0]}
                            alt={site.name}
                            className="w-20 h-20 rounded-lg object-cover"
                          />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <span className="text-lg font-semibold text-gray-900">
                                {site.name}
                              </span>
                              <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(site.status)}`}>
                                {site.status}
                              </span>
                            </div>
                            {renderStars(site.rating)}
                          </div>
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                            {site.description}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span className="flex items-center">
                              <MapPin className="w-3 h-3 mr-1" />
                              {site.location}
                            </span>
                            <span>类型: {site.type}</span>
                            <span>访问: {site.visitCount}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleEdit(site)
                            }}
                            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(site.id)
                            }}
                            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* 右侧详情/表单 */}
          <div className="w-96">
            {(isCreating || isEditing) ? (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  {isCreating ? '新建文化圣地' : '编辑文化圣地'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      名称 *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      描述 *
                    </label>
                    <textarea
                      required
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      位置 *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      类型 *
                    </label>
                    <select
                      required
                      value={formData.type}
                      onChange={(e) => setFormData({...formData, type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="museum">博物馆</option>
                      <option value="temple">寺庙</option>
                      <option value="historical_site">历史古迹</option>
                      <option value="park">公园</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        评分 (1-5)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={formData.rating}
                        onChange={(e) => setFormData({...formData, rating: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        门票 (灵值)
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={formData.admissionFee}
                        onChange={(e) => setFormData({...formData, admissionFee: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      开放时间
                    </label>
                    <input
                      type="text"
                      placeholder="例如: 9:00-17:00"
                      value={formData.openingHours}
                      onChange={(e) => setFormData({...formData, openingHours: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      状态 *
                    </label>
                    <select
                      required
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="active">启用</option>
                      <option value="pending">待审核</option>
                      <option value="inactive">禁用</option>
                    </select>
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setIsCreating(false)
                        setIsEditing(false)
                        setSelectedSite(null)
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                    >
                      {loading ? '保存中...' : '保存'}
                    </button>
                  </div>
                </form>
              </div>
            ) : selectedSite ? (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">文化圣地详情</h2>
                <div className="space-y-4">
                  {selectedSite.images && selectedSite.images.length > 0 && (
                    <div className="flex justify-center">
                      <img
                        src={selectedSite.images[0]}
                        alt={selectedSite.name}
                        className="w-24 h-24 rounded-lg object-cover"
                      />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium text-gray-700">名称</label>
                    <p className="text-gray-900 mt-1">{selectedSite.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">描述</label>
                    <p className="text-gray-900 mt-1">{selectedSite.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700">位置:</label>
                    <p className="text-gray-900 mt-1 flex items-center">
                      <MapPin className="w-4 h-4 mr-1 text-gray-500" />
                      {selectedSite.location}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">类型</label>
                      <p className="text-gray-900 mt-1">{selectedSite.type}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">状态</label>
                      <p className="mt-1"><span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedSite.status)}`}>{selectedSite.status}</span></p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">评分</label>
                      <div className="mt-1">{renderStars(selectedSite.rating)}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">访问次数</label>
                      <p className="text-gray-900 mt-1">{selectedSite.visitCount}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">开放时间</label>
                      <p className="text-gray-900 mt-1 flex items-center">
                        <Clock className="w-4 h-4 mr-1 text-gray-500" />
                        {selectedSite.openingHours || '未设置'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">门票</label>
                      <p className="text-gray-900 mt-1">{selectedSite.admissionFee || 0} 灵值</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建者</label>
                    <p className="text-gray-900 mt-1">{selectedSite.userName || `用户${selectedSite.userId}`}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建时间</label>
                    <p className="text-gray-900 mt-1">{new Date(selectedSite.createdAt).toLocaleString('zh-CN')}</p>
                  </div>
                  <div className="flex space-x-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(selectedSite)}
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <Edit className="w-4 h-4 mr-2 inline" />
                      编辑
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-6 text-center text-gray-500">
                <Eye className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>选择一个文化圣地查看详情</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CulturalSitesManagement
