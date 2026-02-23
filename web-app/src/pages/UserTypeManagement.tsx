import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  X,
  Crown,
  Star,
  Shield,
  ArrowLeft
} from 'lucide-react'

interface UserType {
  id: number
  name: string
  display_name: string
  description: string
  level: number
  is_system: number
  user_count: number
}

const UserTypeManagement = () => {
  const navigate = useNavigate()
  const [userTypes, setUserTypes] = useState<UserType[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [currentUserType, setCurrentUserType] = useState<UserType | null>(null)
  const [message, setMessage] = useState({ type: '', text: '' })

  const [userTypeForm, setUserTypeForm] = useState({
    name: '',
    display_name: '',
    description: '',
    level: 10
  })

  useEffect(() => {
    loadUserTypes()
  }, [])

  const loadUserTypes = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/user-types', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setUserTypes(data.data)
      } else {
        setMessage({ type: 'error', text: data.message || '加载失败' })
      }
    } catch (error) {
      console.error('加载用户类型失败:', error)
      setMessage({ type: 'error', text: '网络错误，请重试' })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUserType = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/user-types', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userTypeForm)
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户类型创建成功' })
        setIsCreateModalOpen(false)
        setUserTypeForm({ name: '', display_name: '', description: '', level: 10 })
        loadUserTypes()
      } else {
        setMessage({ type: 'error', text: data.message || '创建失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleEditUserType = async () => {
    if (!currentUserType) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/user-types/${currentUserType.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userTypeForm)
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户类型更新成功' })
        setIsEditModalOpen(false)
        setCurrentUserType(null)
        loadUserTypes()
      } else {
        setMessage({ type: 'error', text: data.message || '更新失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleDeleteUserType = async (userType: UserType) => {
    if (!window.confirm(`确定要删除用户类型 "${userType.display_name}" 吗？此操作不可恢复。`)) {
      return
    }

    if (userType.is_system) {
      setMessage({ type: 'error', text: '系统用户类型不允许删除' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/user-types/${userType.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户类型删除成功' })
        loadUserTypes()
      } else {
        setMessage({ type: 'error', text: data.message || '删除失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleOpenEdit = (userType: UserType) => {
    setCurrentUserType(userType)
    setUserTypeForm({
      name: userType.name,
      display_name: userType.display_name,
      description: userType.description,
      level: userType.level
    })
    setIsEditModalOpen(true)
  }

  const getLevelIcon = (level: number) => {
    if (level >= 90) return <Crown className="w-5 h-5 text-yellow-500" />
    if (level >= 70) return <Star className="w-5 h-5 text-orange-500" />
    if (level >= 50) return <Shield className="w-5 h-5 text-blue-500" />
    return <Users className="w-5 h-5 text-gray-500" />
  }

  const getLevelBadge = (level: number) => {
    if (level >= 90) return { bg: 'bg-yellow-100', text: 'text-yellow-700', label: '高级' }
    if (level >= 70) return { bg: 'bg-orange-100', text: 'text-orange-700', label: '高级' }
    if (level >= 50) return { bg: 'bg-blue-100', text: 'text-blue-700', label: '中级' }
    return { bg: 'bg-gray-100', text: 'text-gray-700', label: '普通' }
  }

  return (
    <div className="p-6">
      {/* 页面标题和返回按钮 */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/admin')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">用户类型管理</h1>
            <p className="text-gray-600 mt-1">管理系统中不同层级的用户类型</p>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message.text && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* 操作栏 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-gray-600">
            <Users className="w-5 h-5" />
            <span>共 {userTypes.length} 个用户类型</span>
          </div>
        </div>
        <button
          onClick={() => {
            setUserTypeForm({ name: '', display_name: '', description: '', level: 10 })
            setIsCreateModalOpen(true)
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          创建用户类型
        </button>
      </div>

      {/* 用户类型列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">图标</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型名称</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">描述</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">等级</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户数</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">加载中...</td>
              </tr>
            ) : userTypes.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">暂无用户类型</td>
              </tr>
            ) : (
              userTypes.map((userType) => {
                const badge = getLevelBadge(userType.level)
                return (
                  <tr key={userType.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getLevelIcon(userType.level)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">{userType.display_name}</span>
                        {userType.is_system && (
                          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">系统</span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">{userType.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{userType.description}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${badge.bg} ${badge.text}`}>
                        {badge.label} ({userType.level})
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {userType.user_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleOpenEdit(userType)}
                          className="p-2 rounded hover:bg-blue-100 text-blue-600 transition-colors"
                          title="编辑"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        {!userType.is_system && (
                          <button
                            onClick={() => handleDeleteUserType(userType)}
                            className="p-2 rounded hover:bg-red-100 text-red-600 transition-colors"
                            title="删除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* 创建用户类型模态框 */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">创建用户类型</h2>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">类型代码</label>
                <input
                  type="text"
                  value={userTypeForm.name}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, name: e.target.value })}
                  placeholder="例如: senior_partner"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">显示名称</label>
                <input
                  type="text"
                  value={userTypeForm.display_name}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, display_name: e.target.value })}
                  placeholder="例如: 高级合伙人"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
                <textarea
                  value={userTypeForm.description}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, description: e.target.value })}
                  placeholder="用户类型描述"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">等级 (1-100)</label>
                <input
                  type="number"
                  value={userTypeForm.level}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, level: parseInt(e.target.value) })}
                  placeholder="10-100"
                  min="1"
                  max="100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">等级越高，权限越大</p>
              </div>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleCreateUserType}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 编辑用户类型模态框 */}
      {isEditModalOpen && currentUserType && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">编辑用户类型</h2>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">类型代码</label>
                <input
                  type="text"
                  value={userTypeForm.name}
                  disabled={currentUserType.is_system === 1}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, name: e.target.value })}
                  className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${currentUserType.is_system === 1 ? 'bg-gray-100' : ''}`}
                />
                {currentUserType.is_system && <p className="text-xs text-gray-500 mt-1">系统类型代码不可修改</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">显示名称</label>
                <input
                  type="text"
                  value={userTypeForm.display_name}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, display_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
                <textarea
                  value={userTypeForm.description}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">等级 (1-100)</label>
                <input
                  type="number"
                  value={userTypeForm.level}
                  onChange={(e) => setUserTypeForm({ ...userTypeForm, level: parseInt(e.target.value) })}
                  min="1"
                  max="100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleEditUserType}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserTypeManagement
