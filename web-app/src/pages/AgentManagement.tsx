import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Edit, Trash2, Power, PowerOff, Bot, ArrowLeft, Save, X } from 'lucide-react'
import MobileRichEditor from '../components/MobileRichEditor'
import api from '../services/api'

interface Agent {
  id: number
  name: string
  description: string
  system_prompt: string
  model_config: string
  tools: string
  status: string
  avatar_url: string
  created_at: string
  updated_at: string
}

const AgentManagement = () => {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model_config: '',
    tools: '[]',
    avatar_url: '',
    status: 'active'
  })

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/admin/agents')
      if (response.data.success) {
        setAgents(response.data.data)
      }
    } catch (err) {
      setError('获取智能体列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setIsCreating(true)
    setFormData({
      name: '',
      description: '',
      system_prompt: '',
      model_config: '',
      tools: '[]',
      avatar_url: '',
      status: 'active'
    })
    setEditingAgent(null)
  }

  const handleEdit = (agent: Agent) => {
    setIsCreating(false)
    setEditingAgent(agent)
    setFormData({
      name: agent.name,
      description: agent.description || '',
      system_prompt: agent.system_prompt || '',
      model_config: agent.model_config || '',
      tools: agent.tools || '[]',
      avatar_url: agent.avatar_url || '',
      status: agent.status
    })
  }

  const handleDelete = async (agentId: number) => {
    if (!confirm('确定要删除这个智能体吗？')) {
      return
    }

    try {
      const response = await api.delete(`/api/admin/agents/${agentId}`)
      if (response.data.success) {
        setMessage('智能体删除成功')
        fetchAgents()
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleToggleStatus = async (agent: Agent) => {
    const newStatus = agent.status === 'active' ? 'inactive' : 'active'
    try {
      const response = await api.put(`/api/admin/agents/${agent.id}`, {
        status: newStatus
      })
      if (response.data.success) {
        setMessage(newStatus === 'active' ? '智能体已激活' : '智能体已停用')
        fetchAgents()
      }
    } catch (err) {
      setError('状态更新失败')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const payload = {
        ...formData,
        model_config: typeof formData.model_config === 'string' 
          ? JSON.parse(formData.model_config || '{}') 
          : formData.model_config,
        tools: typeof formData.tools === 'string' 
          ? JSON.parse(formData.tools || '[]') 
          : formData.tools
      }

      let response
      if (isCreating) {
        response = await api.post('/api/admin/agents', payload)
      } else if (editingAgent) {
        response = await api.put(`/api/admin/agents/${editingAgent.id}`, payload)
      }

      if (response && response.data.success) {
        setMessage(isCreating ? '智能体创建成功' : '智能体更新成功')
        setIsCreating(false)
        setEditingAgent(null)
        fetchAgents()
      } else if (response) {
        setError(response.data.message || '操作失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setIsCreating(false)
    setEditingAgent(null)
    setError('')
    setMessage('')
  }

  if (loading && agents.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/admin')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回后台
          </button>
          <h1 className="text-xl font-bold text-gray-900">智能体管理</h1>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            创建智能体
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* 提示信息 */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {error}
          </div>
        )}
        {message && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-600">
            {message}
          </div>
        )}

        {/* 编辑表单 */}
        {(isCreating || editingAgent) && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                {isCreating ? '创建智能体' : '编辑智能体'}
              </h2>
              <button
                onClick={handleCancel}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  智能体名称 *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入智能体名称"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入智能体描述"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  系统提示词（System Prompt）
                </label>
                <MobileRichEditor
                  value={formData.system_prompt}
                  onChange={(value) => setFormData({ ...formData, system_prompt: value })}
                  placeholder="定义智能体的角色、任务和约束..."
                  height="200px"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  模型配置（JSON）
                </label>
                <textarea
                  value={formData.model_config}
                  onChange={(e) => setFormData({ ...formData, model_config: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  placeholder='{"model": "doubao-seed-1-6-251015", "temperature": 0.7}'
                  rows={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  状态
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="active">激活</option>
                  <option value="inactive">停用</option>
                </select>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Save className="w-5 h-5 mr-2" />
                  {loading ? '保存中...' : (isCreating ? '创建' : '保存')}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300"
                >
                  取消
                </button>
              </div>
            </form>
          </div>
        )}

        {/* 智能体列表 */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              智能体列表 ({agents.length})
            </h2>
          </div>

          {agents.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">暂无智能体</p>
              <p className="text-sm">点击上方"创建智能体"开始</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {agents.map((agent) => (
                <div key={agent.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {agent.name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          agent.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {agent.status === 'active' ? '激活' : '停用'}
                        </span>
                      </div>
                      {agent.description && (
                        <p className="text-gray-600 text-sm mb-2">{agent.description}</p>
                      )}
                      <p className="text-gray-400 text-xs">
                        创建时间: {new Date(agent.created_at).toLocaleString('zh-CN')}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleToggleStatus(agent)}
                        className={`p-2 rounded-lg hover:opacity-80 ${
                          agent.status === 'active'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                        title={agent.status === 'active' ? '停用' : '激活'}
                      >
                        {agent.status === 'active' ? (
                          <Power className="w-4 h-4" />
                        ) : (
                          <PowerOff className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleEdit(agent)}
                        className="p-2 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-200"
                        title="编辑"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(agent.id)}
                        className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200"
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgentManagement
