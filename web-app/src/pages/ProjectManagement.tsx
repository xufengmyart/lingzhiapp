import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Edit, Eye, Search, Filter, ArrowLeft, Star, Clock, DollarSign } from 'lucide-react'
import api from '../services/api'

interface Project {
  id: number
  name: string
  description: string
  category: string
  status: string
  budget: number
  progress: number
  priority: string
  startDate: string
  endDate: string
  userId: number
  userName: string
  createdAt: string
  updatedAt: string
}

const ProjectManagement = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  
  // 筛选和搜索
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'design',
    status: 'planning',
    budget: 0,
    progress: 0,
    priority: 'medium',
    startDate: '',
    endDate: ''
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await api.get('/projects')
      if (response.data.success) {
        setProjects(response.data.data || [])
      }
    } catch (err) {
      setError('获取项目列表失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus
    const matchesPriority = filterPriority === 'all' || project.priority === filterPriority
    return matchesSearch && matchesStatus && matchesPriority
  })

  const handleCreate = () => {
    setIsCreating(true)
    setIsEditing(false)
    setFormData({
      name: '',
      description: '',
      category: 'design',
      status: 'planning',
      budget: 0,
      progress: 0,
      priority: 'medium',
      startDate: '',
      endDate: ''
    })
    setSelectedProject(null)
  }

  const handleEdit = (project: Project) => {
    setSelectedProject(project)
    setIsCreating(false)
    setIsEditing(true)
    setFormData({
      name: project.name,
      description: project.description,
      category: project.category,
      status: project.status,
      budget: project.budget,
      progress: project.progress,
      priority: project.priority,
      startDate: project.startDate ? project.startDate.split('T')[0] : '',
      endDate: project.endDate ? project.endDate.split('T')[0] : ''
    })
  }

  const handleView = (project: Project) => {
    setSelectedProject(project)
    setIsCreating(false)
    setIsEditing(false)
  }

  const handleDelete = async (projectId: number) => {
    if (!confirm('确定要删除这个项目吗？')) {
      return
    }

    try {
      const response = await api.delete(`/projects/${projectId}`)
      if (response.data.success) {
        setMessage('项目删除成功')
        fetchProjects()
        if (selectedProject?.id === projectId) {
          setSelectedProject(null)
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
        const response = await api.post('/projects', formData)
        if (response.data.success) {
          setMessage('项目创建成功')
          setIsCreating(false)
          fetchProjects()
        } else {
          setError(response.data.message || '创建失败')
        }
      } else if (isEditing && selectedProject) {
        const response = await api.put(`/projects/${selectedProject.id}`, formData)
        if (response.data.success) {
          setMessage('项目更新成功')
          setIsEditing(false)
          fetchProjects()
          if (selectedProject.id) {
            handleView(selectedProject)
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
      planning: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-green-100 text-green-800',
      completed: 'bg-gray-100 text-gray-800',
      on_hold: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (priority: string) => {
    const colors: { [key: string]: string } = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
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
                <h1 className="text-2xl font-bold text-gray-900">项目管理</h1>
                <p className="text-sm text-gray-600">管理和跟踪文化项目进度</p>
              </div>
            </div>
            <button
              onClick={handleCreate}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建项目
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
                placeholder="搜索项目..."
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
              <option value="planning">规划中</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
              <option value="on_hold">暂停</option>
              <option value="cancelled">已取消</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">所有优先级</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>
        </div>

        <div className="flex gap-6">
          {/* 左侧列表 */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  项目列表 ({filteredProjects.length})
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">加载中...</div>
                ) : filteredProjects.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    暂无项目
                  </div>
                ) : (
                  filteredProjects.map((project) => (
                    <div
                      key={project.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedProject?.id === project.id ? 'bg-indigo-50' : ''
                      }`}
                      onClick={() => handleView(project)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg font-semibold text-gray-900">
                              {project.name}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(project.status)}`}>
                              {project.status}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(project.priority)}`}>
                              {project.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {project.description}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>预算: {project.budget} 灵值</span>
                            <span>进度: {project.progress}%</span>
                            {project.startDate && (
                              <span>开始: {new Date(project.startDate).toLocaleDateString('zh-CN')}</span>
                            )}
                            {project.endDate && (
                              <span>结束: {new Date(project.endDate).toLocaleDateString('zh-CN')}</span>
                            )}
                          </div>
                          {/* 进度条 */}
                          <div className="mt-2">
                            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                              <span>进度</span>
                              <span>{project.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  project.progress === 100 ? 'bg-green-600' :
                                  project.progress > 50 ? 'bg-blue-600' :
                                  'bg-yellow-600'
                                }`}
                                style={{ width: `${project.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleEdit(project)
                            }}
                            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(project.id)
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
                  {isCreating ? '新建项目' : '编辑项目'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      项目名称 *
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
                  <div className="grid grid-cols-2 gap-4">
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
                        <option value="design">设计</option>
                        <option value="culture">文化</option>
                        <option value="art">艺术</option>
                        <option value="technology">科技</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        优先级 *
                      </label>
                      <select
                        required
                        value={formData.priority}
                        onChange={(e) => setFormData({...formData, priority: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="high">高</option>
                        <option value="medium">中</option>
                        <option value="low">低</option>
                      </select>
                    </div>
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
                      <option value="planning">规划中</option>
                      <option value="in_progress">进行中</option>
                      <option value="completed">已完成</option>
                      <option value="on_hold">暂停</option>
                      <option value="cancelled">已取消</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        预算 (灵值)
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={formData.budget}
                        onChange={(e) => setFormData({...formData, budget: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        进度 (%)
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={formData.progress}
                        onChange={(e) => setFormData({...formData, progress: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        开始日期
                      </label>
                      <input
                        type="date"
                        value={formData.startDate}
                        onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        结束日期
                      </label>
                      <input
                        type="date"
                        value={formData.endDate}
                        onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setIsCreating(false)
                        setIsEditing(false)
                        setSelectedProject(null)
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
            ) : selectedProject ? (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">项目详情</h2>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">名称</label>
                    <p className="text-gray-900 mt-1">{selectedProject.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">描述</label>
                    <p className="text-gray-900 mt-1">{selectedProject.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">状态</label>
                      <p className="mt-1"><span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedProject.status)}`}>{selectedProject.status}</span></p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">优先级</label>
                      <p className="mt-1"><span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(selectedProject.priority)}`}>{selectedProject.priority}</span></p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">预算</label>
                      <p className="text-gray-900 mt-1">{selectedProject.budget} 灵值</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">进度</label>
                      <p className="text-gray-900 mt-1">{selectedProject.progress}%</p>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      进度
                    </label>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          selectedProject.progress === 100 ? 'bg-green-600' :
                          selectedProject.progress > 50 ? 'bg-blue-600' :
                          'bg-yellow-600'
                        }`}
                        style={{ width: `${selectedProject.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">开始日期</label>
                      <p className="text-gray-900 mt-1">
                        {selectedProject.startDate ? new Date(selectedProject.startDate).toLocaleDateString('zh-CN') : '未设置'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">结束日期</label>
                      <p className="text-gray-900 mt-1">
                        {selectedProject.endDate ? new Date(selectedProject.endDate).toLocaleDateString('zh-CN') : '未设置'}
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建者</label>
                    <p className="text-gray-900 mt-1">{selectedProject.userName || `用户${selectedProject.userId}`}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">创建时间</label>
                    <p className="text-gray-900 mt-1">{new Date(selectedProject.createdAt).toLocaleString('zh-CN')}</p>
                  </div>
                  <div className="flex space-x-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(selectedProject)}
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
                <p>选择一个项目查看详情</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProjectManagement
