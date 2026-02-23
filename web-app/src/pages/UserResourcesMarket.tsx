import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Search, Filter, BookOpen, BrainCircuit, Clock, Star, DollarSign, Lock, Eye, ShoppingBag, Upload, X, CheckCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface Resource {
  id: number
  title: string
  resource_type: string
  resource_level: string
  brief_description: string
  detailed_description?: string
  implementation_guide?: string
  required_resources?: string
  expected_benefits?: string
  risk_assessment?: string
  price_lingzhi: number
  view_count: number
  purchase_count: number
  owner_id: number
  owner_name: string
  created_at: string
  access_level: 'full_access' | 'brief_only'
  requires_approval: boolean
  status?: string
  visibility?: string
}

interface Category {
  id: number
  name: string
  description: string
  icon: string
  sort_order: number
}

export default function UserResources() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'market' | 'my'>('market')
  const [resources, setResources] = useState<Resource[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('全部')
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingDetail, setLoadingDetail] = useState(false)
  
  // 创建资源表单
  const [formData, setFormData] = useState({
    title: '',
    resource_type: '文化资源',
    resource_level: 'normal',
    brief_description: '',
    detailed_description: '',
    implementation_guide: '',
    required_resources: '',
    expected_benefits: '',
    risk_assessment: '',
    visibility: 'public',
    requires_approval: true
  })

  useEffect(() => {
    loadCategories()
    loadResources()
  }, [activeTab])

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/resources/market/categories')
      const data = await response.json()
      if (data.success) {
        setCategories(data.data.categories)
      }
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const loadResources = async () => {
    setLoading(true)
    try {
      const url = activeTab === 'my' 
        ? '/api/resources/market/my'
        : '/api/resources/market/list'
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (data.success) {
        setResources(data.data.resources)
      }
    } catch (error) {
      console.error('加载资源失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadResourceDetail = async (resourceId: number) => {
    setLoadingDetail(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/resources/market/${resourceId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      
      if (data.success) {
        setSelectedResource(data.data)
      }
    } catch (error) {
      console.error('加载资源详情失败:', error)
    } finally {
      setLoadingDetail(false)
    }
  }

  const handlePurchase = async (resourceId: number) => {
    if (!user) {
      alert('请先登录')
      return
    }

    if (!confirm('确定要购买此资源吗？')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/resources/market/${resourceId}/purchase`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: '我想购买此资源'
        })
      })
      const data = await response.json()

      if (data.success) {
        alert(data.message)
        if (!data.data.requires_approval) {
          // 刷新资源详情
          loadResourceDetail(resourceId)
        }
      } else {
        alert(data.message)
      }
    } catch (error) {
      console.error('购买失败:', error)
      alert('购买失败，请稍后重试')
    }
  }

  const handleCreateResource = async () => {
    if (!user) {
      alert('请先登录')
      return
    }

    // 验证必填字段
    if (!formData.title || !formData.brief_description || !formData.detailed_description) {
      alert('请填写标题、简介和详细描述')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/resources/market/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      const data = await response.json()

      if (data.success) {
        alert('资源创建成功！')
        setShowCreateModal(false)
        setFormData({
          title: '',
          resource_type: '文化资源',
          resource_level: 'normal',
          brief_description: '',
          detailed_description: '',
          implementation_guide: '',
          required_resources: '',
          expected_benefits: '',
          risk_assessment: '',
          visibility: 'public',
          requires_approval: true
        })
        loadResources()
      } else {
        alert(data.message)
      }
    } catch (error) {
      console.error('创建失败:', error)
      alert('创建失败，请稍后重试')
    }
  }

  const filteredResources = resources.filter(resource => {
    const matchCategory = selectedCategory === '全部' || resource.resource_type === selectedCategory
    const matchSearch = resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       resource.brief_description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  const resourceTypes = ['全部', ...categories.map(c => c.name)]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">资源市场</h1>
          <p className="text-gray-600">发现和共享优质的落地资源</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">总资源数</p>
                <p className="text-2xl font-bold text-gray-900">{resources.length}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">我的资源</p>
                <p className="text-2xl font-bold text-gray-900">
                  {activeTab === 'my' ? resources.length : resources.filter(r => r.owner_id === user?.id).length}
                </p>
              </div>
              <Upload className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">我的灵值</p>
                <p className="text-2xl font-bold text-gray-900">{user?.balance || 0}</p>
              </div>
              <DollarSign className="w-8 h-8 text-yellow-500" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">我的贡献值</p>
                <p className="text-2xl font-bold text-gray-900">{user?.contribution_value || 0}</p>
              </div>
              <BrainCircuit className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* 选项卡 */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('market')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'market'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                资源市场
              </button>
              <button
                onClick={() => setActiveTab('my')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'my'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                我的资源
              </button>
            </nav>
          </div>
        </div>

        {/* 搜索和筛选 */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="搜索资源..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
              {resourceTypes.map(type => (
                <button
                  key={type}
                  onClick={() => setSelectedCategory(type)}
                  className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                    selectedCategory === type
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
            {activeTab === 'my' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 whitespace-nowrap"
              >
                <Plus className="w-5 h-5" />
                创建资源
              </button>
            )}
          </div>
        </div>

        {/* 资源列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              加载中...
            </div>
          ) : filteredResources.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              暂无资源
            </div>
          ) : (
            filteredResources.map(resource => (
              <div
                key={resource.id}
                className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => loadResourceDetail(resource.id)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{resource.title}</h3>
                      <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                        resource.resource_level === 'key' 
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {resource.resource_level === 'key' ? '关键资源' : '普通资源'}
                      </span>
                    </div>
                    {resource.access_level === 'brief_only' && (
                      <Lock className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {resource.brief_description}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {resource.view_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <ShoppingBag className="w-4 h-4" />
                      {resource.purchase_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      {resource.price_lingzhi}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      by {resource.owner_name}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(resource.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* 资源详情模态框 */}
        {selectedResource && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">{selectedResource.title}</h2>
                <button
                  onClick={() => setSelectedResource(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[70vh]">
                {loadingDetail ? (
                  <div className="text-center py-8">加载中...</div>
                ) : selectedResource.access_level === 'full_access' ? (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">资源简介</h3>
                      <p className="text-gray-700">{selectedResource.brief_description}</p>
                    </div>
                    
                    {selectedResource.detailed_description && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">详细描述</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{selectedResource.detailed_description}</p>
                      </div>
                    )}
                    
                    {selectedResource.implementation_guide && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">落地实施指南</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{selectedResource.implementation_guide}</p>
                      </div>
                    )}
                    
                    {selectedResource.required_resources && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">所需资源</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{selectedResource.required_resources}</p>
                      </div>
                    )}
                    
                    {selectedResource.expected_benefits && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">预期收益</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{selectedResource.expected_benefits}</p>
                      </div>
                    )}
                    
                    {selectedResource.risk_assessment && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">风险评估</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{selectedResource.risk_assessment}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">资源简介</h3>
                      <p className="text-gray-700">{selectedResource.brief_description}</p>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Lock className="w-5 h-5 text-gray-500" />
                        <span className="font-semibold text-gray-700">此资源需要购买才能查看详细内容</span>
                      </div>
                      <p className="text-gray-600 mb-4">
                        价格: <span className="text-2xl font-bold text-blue-600">{selectedResource.price_lingzhi}</span> 灵值
                      </p>
                      {selectedResource.requires_approval && (
                        <p className="text-sm text-orange-600">
                          注意: 此资源需要所有者审批后才能查看
                        </p>
                      )}
                    </div>
                    
                    {selectedResource.owner_id !== user?.id && (
                      <button
                        onClick={() => handlePurchase(selectedResource.id)}
                        className="w-full py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-semibold"
                      >
                        购买资源
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 创建资源模态框 */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">创建资源</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[70vh]">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      资源标题 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="输入资源标题"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      资源类型 <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.resource_type}
                      onChange={(e) => setFormData({...formData, resource_type: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      {categories.map(cat => (
                        <option key={cat.id} value={cat.name}>{cat.icon} {cat.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      资源级别 <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.resource_level}
                      onChange={(e) => setFormData({...formData, resource_level: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="normal">普通资源（500灵值）</option>
                      <option value="key">关键资源（20000灵值）</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      资源简介 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={formData.brief_description}
                      onChange={(e) => setFormData({...formData, brief_description: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="简短描述资源内容（所有用户可见）"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      详细描述 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={formData.detailed_description}
                      onChange={(e) => setFormData({...formData, detailed_description: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={5}
                      placeholder="详细描述资源内容（付费后可见）"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      落地实施指南
                    </label>
                    <textarea
                      value={formData.implementation_guide}
                      onChange={(e) => setFormData({...formData, implementation_guide: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={4}
                      placeholder="提供具体的实施步骤和方法"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      所需资源
                    </label>
                    <textarea
                      value={formData.required_resources}
                      onChange={(e) => setFormData({...formData, required_resources: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="列出实施所需的人力、物力、财力等资源"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      预期收益
                    </label>
                    <textarea
                      value={formData.expected_benefits}
                      onChange={(e) => setFormData({...formData, expected_benefits: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="描述预期可获得的经济或社会收益"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      风险评估
                    </label>
                    <textarea
                      value={formData.risk_assessment}
                      onChange={(e) => setFormData({...formData, risk_assessment: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="分析可能存在的风险和应对措施"
                    />
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.visibility === 'public'}
                        onChange={(e) => setFormData({...formData, visibility: e.target.checked ? 'public' : 'private'})}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-sm text-gray-700">公开显示（其他用户可看到简介）</span>
                    </label>
                    
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.requires_approval}
                        onChange={(e) => setFormData({...formData, requires_approval: e.target.checked})}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-sm text-gray-700">需要审批（购买者需获得您的批准才能查看）</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div className="p-6 border-t bg-gray-50 flex justify-end gap-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100"
                >
                  取消
                </button>
                <button
                  onClick={handleCreateResource}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  创建资源
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
