import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Edit, Eye, Search, Filter, ArrowLeft, Check, X, Star } from 'lucide-react'
import api from '../services/api'

interface Merchant {
  id: number
  name: string
  description: string
  category: string
  status: string
  contact: string
  email: string
  phone: string
  address: string
  logo: string
  rating: number
  reviewCount: number
  userId: number
  userName: string
  createdAt: string
  updatedAt: string
}

const MerchantManagement = () => {
  const navigate = useNavigate()
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  
  // 筛选和搜索
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterCategory, setFilterCategory] = useState('all')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'culture',
    status: 'pending',
    contact: '',
    email: '',
    phone: '',
    address: '',
    logo: ''
  })

  useEffect(() => {
    fetchMerchants()
  }, [])

  const fetchMerchants = async () => {
    try {
      setLoading(true)
      const response = await api.get('/merchants')
      if (response.data.success) {
        setMerchants(response.data.data || [])
      }
    } catch (err) {
      setError('获取商家列表失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredMerchants = merchants.filter(merchant => {
    const matchesSearch = merchant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         merchant.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || merchant.status === filterStatus
    const matchesCategory = filterCategory === 'all' || merchant.category === filterCategory
    return matchesSearch && matchesStatus && matchesCategory
  })

  const handleCreate = () => {
    setIsCreating(true)
    setIsEditing(false)
    setFormData({
      name: '',
      description: '',
      category: 'culture',
      status: 'pending',
      contact: '',
      email: '',
      phone: '',
      address: '',
      logo: ''
    })
    setSelectedMerchant(null)
  }

  const handleEdit = (merchant: Merchant) => {
    setSelectedMerchant(merchant)
    setIsCreating(false)
    setIsEditing(true)
    setFormData({
      name: merchant.name,
      description: merchant.description,
      category: merchant.category,
      status: merchant.status,
      contact: merchant.contact,
      email: merchant.email,
      phone: merchant.phone,
      address: merchant.address,
      logo: merchant.logo
    })
  }

  const handleView = (merchant: Merchant) => {
    setSelectedMerchant(merchant)
    setIsCreating(false)
    setIsEditing(false)
  }

  const handleDelete = async (merchantId: number) => {
    if (!confirm('确定要删除这个商家吗？')) {
      return
    }

    try {
      const response = await api.delete(`/merchants/${merchantId}`)
      if (response.data.success) {
        setMessage('商家删除成功')
        fetchMerchants()
        if (selectedMerchant?.id === merchantId) {
          setSelectedMerchant(null)
        }
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleApprove = async (merchantId: number) => {
    if (!confirm('确定要批准这个商家吗？')) {
      return
    }

    try {
      const response = await api.put(`/merchants/${merchantId}`, { status: 'active' })
      if (response.data.success) {
        setMessage('商家已批准')
        fetchMerchants()
      } else {
        setError(response.data.message || '批准失败')
      }
    } catch (err) {
      setError('批准失败')
    }
  }

  const handleReject = async (merchantId: number) => {
    if (!confirm('确定要拒绝这个商家吗？')) {
      return
    }

    try {
      const response = await api.put(`/merchants/${merchantId}`, { status: 'rejected' })
      if (response.data.success) {
        setMessage('商家已拒绝')
        fetchMerchants()
      } else {
        setError(response.data.message || '拒绝失败')
      }
    } catch (err) {
      setError('拒绝失败')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      if (isCreating) {
        const response = await api.post('/merchants', formData)
        if (response.data.success) {
          setMessage('商家创建成功')
          setIsCreating(false)
          fetchMerchants()
        } else {
          setError(response.data.message || '创建失败')
        }
      } else if (isEditing && selectedMerchant) {
        const response = await api.put(`/merchants/${selectedMerchant.id}`, formData)
        if (response.data.success) {
          setMessage('商家更新成功')
          setIsEditing(false)
          fetchMerchants()
          if (selectedMerchant.id) {
            handleView(selectedMerchant)
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
      rejected: 'bg-red-100 text-red-800',
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
        <span className="text-sm text-gray-600 ml-1">({rating})</span>
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
                <h1 className="text-2xl font-bold text-gray-900">商家管理</h1>
                <p className="text-sm text-gray-600">管理平台商家和商家审核</p>
              </div>
            </div>
            <button
              onClick={handleCreate}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建商家
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
                placeholder="搜索商家..."
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
              <option value="active">已批准</option>
              <option value="pending">待审核</option>
              <option value="rejected">已拒绝</option>
              <option value="inactive">已禁用</option>
            </select>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有分类</option>
              <option value="culture">文化</option>
              <option value="art">艺术</option>
              <option value="design">设计</option>
              <option value="business">商业</option>
            </select>
          </div>
        </div>

        <div className="flex gap-6">
          {/* 左侧列表 */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  商家列表 ({filteredMerchants.length})
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">加载中...</div>
                ) : filteredMerchants.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    暂无商家
                  </div>
                ) : (
                  filteredMerchants.map((merchant) => (
                    <div
                      key={merchant.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedMerchant?.id === merchant.id ? 'bg-indigo-50' : ''
                      }`}
                      onClick={() => handleView(merchant)}
                    >
                      <div className="flex items-start space-x-4">
                        {merchant.logo && (
                          <img
                            src={merchant.logo}
                            alt={merchant.name}
                            className="w-16 h-16 rounded-lg object-cover"
                          />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <span className="text-lg font-semibold text-gray-900">
                                {merchant.name}
                              </span>
                              <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(merchant.status)}`}>
                                {merchant.status}
                              </span>
                            </div>
                            {merchant.status === 'pending' && (
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleApprove(merchant.id)
                                  }}
                                  className="p-1.5 hover:bg-green-100 rounded-lg transition-colors"
                                >
                                  <Check className="w-4 h-4 text-green-600" />
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleReject(merchant.id)
                                  }}
                                  className="p-1.5 hover:bg-red-100 rounded-lg transition-colors"
                                >
                                  <X className="w-4 h-4 text-red-600" />
                                </button>
                              </div>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                            {merchant.description}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>分类: {merchant.category}</span>
                            <span>联系人: {merchant.contact}</span>
                            {renderStars(merchant.rating)}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleEdit(merchant)
                            }}
                            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(merchant.id)
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
                  {isCreating ? '新建商家' : '编辑商家'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      商家名称 *
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
                      分类 *
                    </label>
                    <select
                      required
                      value={formData.category}
                      onChange={(e) => setFormData({...formData, category: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="culture">文化</option>
                      <option value="art">艺术</option>
                      <option value="design">设计</option>
                      <option value="business">商业</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      联系人
                    </label>
                    <input
                      type="text"
                      value={formData.contact}
                      onChange={(e) => setFormData({...formData, contact: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      邮箱
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      电话
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      地址
                    </label>
                    <textarea
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Logo URL
                    </label>
                    <input
                      type="url"
                      value={formData.logo}
                      onChange={(e) => setFormData({...formData, logo: e.target.value})}
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
                      <option value="pending">待审核</option>
                      <option value="active">已批准</option>
                      <option value="rejected">已拒绝</option>
                      <option value="inactive">已禁用</option>
                    </select>
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setIsCreating(false)
                        setIsEditing(false)
                        setSelectedMerchant(null)
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
            ) : selectedMerchant ? (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">商家详情</h2>
                <div className="space-y-4">
                  {selectedMerchant.logo && (
                    <div className="flex justify-center">
                      <img
                        src={selectedMerchant.logo}
                        alt={selectedMerchant.name}
                        className="w-24 h-24 rounded-lg object-cover"
                      />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium text-gray-700">名称</label>
                    <p className="text-gray-900 mt-1">{selectedMerchant.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">描述</label>
                    <p className="text-gray-900 mt-1">{selectedMerchant.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">分类</label>
                      <p className="text-gray-900 mt-1">{selectedMerchant.category}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">状态</label>
                      <p className="mt-1"><span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedMerchant.status)}`}>{selectedMerchant.status}</span></p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">联系人</label>
                    <p className="text-gray-900 mt-1">{selectedMerchant.contact || '未设置'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">邮箱</label>
                      <p className="text-gray-900 mt-1">{selectedMerchant.email || '未设置'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">电话</label>
                      <p className="text-gray-900 mt-1">{selectedMerchant.phone || '未设置'}</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">地址</label>
                    <p className="text-gray-900 mt-1">{selectedMerchant.address || '未设置'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">评分</label>
                      <div className="mt-1">{renderStars(selectedMerchant.rating)}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">评论数</label>
                      <p className="text-gray-900 mt-1">{selectedMerchant.reviewCount}</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建者</label>
                    <p className="text-gray-900 mt-1">{selectedMerchant.userName || `用户${selectedMerchant.userId}`}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建时间</label>
                    <p className="text-gray-900 mt-1">{new Date(selectedMerchant.createdAt).toLocaleString('zh-CN')}</p>
                  </div>
                  <div className="flex space-x-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(selectedMerchant)}
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
                <p>选择一个商家查看详情</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MerchantManagement
