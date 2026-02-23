import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Edit, Eye, Upload, Download, Search, Filter, ArrowLeft } from 'lucide-react'
import api from '../services/api'

interface Resource {
  id: number
  name: string
  description: string
  type: string
  category: string
  price: number
  status: string
  downloadCount: number
  viewCount: number
  userId: number
  userName: string
  createdAt: string
  updatedAt: string
}

const ResourceManagement = () => {
  const navigate = useNavigate()
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  
  // 筛选和搜索
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'document',
    category: 'general',
    price: 0,
    status: 'active'
  })

  useEffect(() => {
    fetchResources()
  }, [])

  const fetchResources = async () => {
    try {
      setLoading(true)
      const response = await api.get('/user-resources')
      if (response.data.success) {
        setResources(response.data.data || [])
      }
    } catch (err) {
      setError('获取资源列表失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || resource.type === filterType
    const matchesStatus = filterStatus === 'all' || resource.status === filterStatus
    return matchesSearch && matchesType && matchesStatus
  })

  const handleCreate = () => {
    setIsCreating(true)
    setIsEditing(false)
    setFormData({
      name: '',
      description: '',
      type: 'document',
      category: 'general',
      price: 0,
      status: 'active'
    })
    setSelectedResource(null)
  }

  const handleEdit = (resource: Resource) => {
    setSelectedResource(resource)
    setIsCreating(false)
    setIsEditing(true)
    setFormData({
      name: resource.name,
      description: resource.description,
      type: resource.type,
      category: resource.category,
      price: resource.price,
      status: resource.status
    })
  }

  const handleView = (resource: Resource) => {
    setSelectedResource(resource)
    setIsCreating(false)
    setIsEditing(false)
  }

  const handleDelete = async (resourceId: number) => {
    if (!confirm('确定要删除这个资源吗？')) {
      return
    }

    try {
      const response = await api.delete(`/user-resources/${resourceId}`)
      if (response.data.success) {
        setMessage('资源删除成功')
        fetchResources()
        if (selectedResource?.id === resourceId) {
          setSelectedResource(null)
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
        const response = await api.post('/user-resources', formData)
        if (response.data.success) {
          setMessage('资源创建成功')
          setIsCreating(false)
          fetchResources()
        } else {
          setError(response.data.message || '创建失败')
        }
      } else if (isEditing && selectedResource) {
        const response = await api.put(`/user-resources/${selectedResource.id}`, formData)
        if (response.data.success) {
          setMessage('资源更新成功')
          setIsEditing(false)
          fetchResources()
          if (selectedResource.id) {
            handleView(selectedResource)
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
                <h1 className="text-2xl font-bold text-gray-900">资源管理</h1>
                <p className="text-sm text-gray-600">管理用户资源和私有资源</p>
              </div>
            </div>
            <button
              onClick={handleCreate}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建资源
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
                placeholder="搜索资源..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有类型</option>
              <option value="document">文档</option>
              <option value="image">图片</option>
              <option value="video">视频</option>
              <option value="audio">音频</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有状态</option>
              <option value="active">启用</option>
              <option value="inactive">禁用</option>
              <option value="pending">审核中</option>
            </select>
          </div>
        </div>

        <div className="flex gap-6">
          {/* 左侧列表 */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  资源列表 ({filteredResources.length})
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">加载中...</div>
                ) : filteredResources.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    暂无资源
                  </div>
                ) : (
                  filteredResources.map((resource) => (
                    <div
                      key={resource.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedResource?.id === resource.id ? 'bg-indigo-50' : ''
                      }`}
                      onClick={() => handleView(resource)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg font-semibold text-gray-900">
                              {resource.name}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              resource.status === 'active' ? 'bg-green-100 text-green-800' :
                              resource.status === 'inactive' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {resource.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {resource.description}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>类型: {resource.type}</span>
                            <span>价格: {resource.price} 灵值</span>
                            <span>下载: {resource.downloadCount}</span>
                            <span>浏览: {resource.viewCount}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleEdit(resource)
                            }}
                            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(resource.id)
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
                  {isCreating ? '新建资源' : '编辑资源'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      资源名称 *
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
                      类型 *
                    </label>
                    <select
                      required
                      value={formData.type}
                      onChange={(e) => setFormData({...formData, type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="document">文档</option>
                      <option value="image">图片</option>
                      <option value="video">视频</option>
                      <option value="audio">音频</option>
                    </select>
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
                      <option value="general">通用</option>
                      <option value="culture">文化</option>
                      <option value="design">设计</option>
                      <option value="business">商业</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      价格 (灵值)
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.price}
                      onChange={(e) => setFormData({...formData, price: parseInt(e.target.value)})}
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
                      <option value="inactive">禁用</option>
                      <option value="pending">审核中</option>
                    </select>
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setIsCreating(false)
                        setIsEditing(false)
                        setSelectedResource(null)
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
            ) : selectedResource ? (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">资源详情</h2>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">名称</label>
                    <p className="text-gray-900 mt-1">{selectedResource.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">描述</label>
                    <p className="text-gray-900 mt-1">{selectedResource.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">类型</label>
                      <p className="text-gray-900 mt-1">{selectedResource.type}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">分类</label>
                      <p className="text-gray-900 mt-1">{selectedResource.category}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">价格</label>
                      <p className="text-gray-900 mt-1">{selectedResource.price} 灵值</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">状态</label>
                      <p className="text-gray-900 mt-1">{selectedResource.status}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">下载次数</label>
                      <p className="text-gray-900 mt-1">{selectedResource.downloadCount}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">浏览次数</label>
                      <p className="text-gray-900 mt-1">{selectedResource.viewCount}</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建者</label>
                    <p className="text-gray-900 mt-1">{selectedResource.userName || `用户${selectedResource.userId}`}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建时间</label>
                    <p className="text-gray-900 mt-1">{new Date(selectedResource.createdAt).toLocaleString('zh-CN')}</p>
                  </div>
                  <div className="flex space-x-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(selectedResource)}
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
                <p>选择一个资源查看详情</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResourceManagement
