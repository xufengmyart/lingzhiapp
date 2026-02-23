import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Plus,
  Edit2,
  Trash2,
  Save,
  X,
  Search,
  Bot,
  MessageSquare,
  Settings,
  Code,
  Zap
} from 'lucide-react'

interface Agent {
  id: number
  name: string
  type: string
  description: string
  status: string
  avatar: string
  createdAt: string
  updatedAt: string
}

const AgentManagement = () => {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    type: 'chat',
    description: '',
    system_prompt: '',
    status: 'active',
    avatar: ''
  })

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/agents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) throw new Error('获取智能体列表失败')

      const result = await response.json()
      if (result.success) {
        setAgents(result.data || [])
      }
    } catch (error) {
      console.error('加载智能体列表失败:', error)
      setMessage({ type: 'error', text: '加载智能体列表失败' })
    } finally {
      setLoading(false)
    }
  }

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreate = () => {
    setIsCreating(true)
    setIsEditing(false)
    setSelectedAgent(null)
    setFormData({
      name: '',
      type: 'chat',
      description: '',
      system_prompt: '',
      status: 'active',
      avatar: ''
    })
  }

  const handleEdit = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsCreating(false)
    setIsEditing(true)
    setFormData({
      name: agent.name,
      type: agent.type,
      description: agent.description,
      system_prompt: '',
      status: agent.status,
      avatar: agent.avatar
    })
  }

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('token')
      const method = isCreating ? 'POST' : 'PUT'
      const url = isCreating
        ? `${import.meta.env.VITE_API_URL}/admin/agents`
        : `${import.meta.env.VITE_API_URL}/admin/agents/${selectedAgent?.id}`

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) throw new Error('保存失败')

      setMessage({ type: 'success', text: isCreating ? '智能体创建成功' : '智能体更新成功' })
      fetchAgents()
      setIsCreating(false)
      setIsEditing(false)
      setSelectedAgent(null)
    } catch (error) {
      console.error('保存失败:', error)
      setMessage({ type: 'error', text: '保存失败' })
    }
  }

  const handleDelete = async (agentId: number) => {
    if (!confirm('确定要删除这个智能体吗？')) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/agents/${agentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) throw new Error('删除失败')

      setMessage({ type: 'success', text: '智能体删除成功' })
      fetchAgents()
      if (selectedAgent?.id === agentId) {
        setSelectedAgent(null)
      }
    } catch (error) {
      console.error('删除失败:', error)
      setMessage({ type: 'error', text: '删除失败' })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200 fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/admin')}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 mr-4"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold text-gray-900">智能体管理</h1>
            </div>
            <button
              onClick={handleCreate}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建智能体
            </button>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 消息提示 */}
          {message && (
            <div
              className={`mb-6 p-4 rounded-md ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              {message.text}
              <button
                onClick={() => setMessage(null)}
                className="float-right text-gray-500 hover:text-gray-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="flex gap-6">
            {/* 左侧列表 */}
            <div className="w-80 flex-shrink-0">
              <div className="bg-white rounded-lg shadow-sm">
                {/* 搜索框 */}
                <div className="p-4 border-b border-gray-200">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="搜索智能体..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* 智能体列表 */}
                <div className="overflow-y-auto max-h-[calc(100vh-250px)]">
                  {loading ? (
                    <div className="p-4 text-center text-gray-500">加载中...</div>
                  ) : filteredAgents.length === 0 ? (
                    <div className="p-4 text-center text-gray-500">暂无智能体</div>
                  ) : (
                    <div className="divide-y divide-gray-100">
                      {filteredAgents.map((agent) => (
                        <div
                          key={agent.id}
                          onClick={() => handleEdit(agent)}
                          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                            selectedAgent?.id === agent.id ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                          }`}
                        >
                          <div className="flex items-start">
                            <div className="flex-shrink-0 w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                              <Bot className="w-5 h-5 text-indigo-600" />
                            </div>
                            <div className="ml-3 flex-1">
                              <div className="flex items-center justify-between">
                                <h3 className="font-medium text-gray-900">{agent.name}</h3>
                                <span
                                  className={`text-xs px-2 py-1 rounded-full ${
                                    agent.status === 'active'
                                      ? 'bg-green-100 text-green-700'
                                      : 'bg-gray-100 text-gray-700'
                                  }`}
                                >
                                  {agent.status === 'active' ? '活跃' : '禁用'}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                {agent.description || '暂无描述'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 右侧编辑区 */}
            <div className="flex-1">
              <div className="bg-white rounded-lg shadow-sm">
                {isCreating || selectedAgent ? (
                  <>
                    {/* 标题栏 */}
                    <div className="px-6 py-4 border-b border-gray-200">
                      <h2 className="text-lg font-semibold text-gray-900">
                        {isCreating ? '新建智能体' : '编辑智能体'}
                      </h2>
                    </div>

                    {/* 编辑表单 */}
                    <div className="p-6">
                      <div className="space-y-6">
                        {/* 名称 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            智能体名称
                          </label>
                          <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="请输入智能体名称"
                          />
                        </div>

                        {/* 类型 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            智能体类型
                          </label>
                          <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="chat">对话助手</option>
                            <option value="task">任务执行</option>
                            <option value="analysis">数据分析</option>
                            <option value="creative">创意生成</option>
                          </select>
                        </div>

                        {/* 描述 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            描述
                          </label>
                          <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            rows={4}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="请输入智能体描述"
                          />
                        </div>

                        {/* 系统提示词 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            系统提示词
                          </label>
                          <textarea
                            value={formData.system_prompt}
                            onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                            rows={8}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm"
                            placeholder="请输入系统提示词"
                          />
                        </div>

                        {/* 状态 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            状态
                          </label>
                          <select
                            value={formData.status}
                            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="active">活跃</option>
                            <option value="inactive">禁用</option>
                          </select>
                        </div>

                        {/* 头像 */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            头像 URL
                          </label>
                          <input
                            type="text"
                            value={formData.avatar}
                            onChange={(e) => setFormData({ ...formData, avatar: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="请输入头像 URL"
                          />
                        </div>

                        {/* 操作按钮 */}
                        <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                          <button
                            onClick={handleSave}
                            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                          >
                            <Save className="w-4 h-4 mr-2" />
                            保存
                          </button>
                          <button
                            onClick={() => {
                              setIsCreating(false)
                              setIsEditing(false)
                              setSelectedAgent(null)
                            }}
                            className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                          >
                            <X className="w-4 h-4 mr-2" />
                            取消
                          </button>
                          {!isCreating && selectedAgent && (
                            <button
                              onClick={() => selectedAgent && handleDelete(selectedAgent.id)}
                              className="flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors ml-auto"
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              删除
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    {/* 空状态 */}
                    <div className="flex flex-col items-center justify-center h-96 text-center">
                    <Bot className="w-16 h-16 text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">选择一个智能体</h3>
                    <p className="text-gray-500 mb-4">点击左侧列表中的智能体进行编辑，或新建智能体</p>
                    <button
                      onClick={handleCreate}
                      className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      新建智能体
                    </button>
                  </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default AgentManagement
