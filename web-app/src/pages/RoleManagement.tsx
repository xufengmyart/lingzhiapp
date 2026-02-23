import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Shield,
  Plus,
  Edit2,
  Trash2,
  CheckSquare,
  Square,
  X,
  Users,
  Key,
  ChevronDown,
  ChevronUp,
  ArrowLeft
} from 'lucide-react'

interface Permission {
  id: number
  name: string
  display_name: string
  description: string
  module: string
}

interface Role {
  id: number
  name: string
  display_name: string
  description: string
  level: number
  is_system: number
  permission_count: number
}

interface RoleDetail extends Role {
  permissions?: Permission[]
  user_count: number
}

const RoleManagement = () => {
  const navigate = useNavigate()
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isPermissionModalOpen, setIsPermissionModalOpen] = useState(false)
  const [currentRole, setCurrentRole] = useState<RoleDetail | null>(null)
  const [expandedRoles, setExpandedRoles] = useState<Set<number>>(new Set())
  const [message, setMessage] = useState({ type: '', text: '' })

  const [roleForm, setRoleForm] = useState({
    name: '',
    display_name: '',
    description: '',
    level: 10
  })

  useEffect(() => {
    loadRoles()
    loadPermissions()
  }, [])

  const loadRoles = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/roles', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setRoles(data.data)
      }
    } catch (error) {
      console.error('加载角色列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadPermissions = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/permissions', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setPermissions(data.data)
      }
    } catch (error) {
      console.error('加载权限列表失败:', error)
    }
  }

  const loadRoleDetail = async (roleId: number) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/roles/${roleId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        return data.data
      }
    } catch (error) {
      console.error('加载角色详情失败:', error)
    }
    return null
  }

  const handleCreateRole = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/roles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(roleForm)
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '角色创建成功' })
        setIsCreateModalOpen(false)
        setRoleForm({ name: '', display_name: '', description: '', level: 10 })
        loadRoles()
      } else {
        setMessage({ type: 'error', text: data.message || '创建失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleEditRole = async () => {
    if (!currentRole) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/roles/${currentRole.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(roleForm)
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '角色更新成功' })
        setIsEditModalOpen(false)
        setCurrentRole(null)
        loadRoles()
      } else {
        setMessage({ type: 'error', text: data.message || '更新失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleDeleteRole = async (role: Role) => {
    if (!window.confirm(`确定要删除角色 "${role.display_name}" 吗？此操作不可恢复。`)) {
      return
    }

    if (role.is_system) {
      setMessage({ type: 'error', text: '系统角色不允许删除' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/roles/${role.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '角色删除成功' })
        loadRoles()
      } else {
        setMessage({ type: 'error', text: data.message || '删除失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleOpenEdit = async (role: Role) => {
    const detail = await loadRoleDetail(role.id)
    if (detail) {
      setCurrentRole(detail)
      setRoleForm({
        name: role.name,
        display_name: role.display_name,
        description: role.description,
        level: role.level
      })
      setIsEditModalOpen(true)
    }
  }

  const handleOpenPermissions = async (role: Role) => {
    const detail = await loadRoleDetail(role.id)
    if (detail) {
      setCurrentRole(detail)
      setIsPermissionModalOpen(true)
    }
  }

  const handleSavePermissions = async () => {
    if (!currentRole) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/roles/${currentRole.id}/permissions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ permission_ids: currentRole.permissions?.map(p => p.id) || [] })
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '权限分配成功' })
        setIsPermissionModalOpen(false)
        setCurrentRole(null)
        loadRoles()
      } else {
        setMessage({ type: 'error', text: data.message || '分配失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const togglePermission = (permission: Permission) => {
    if (!currentRole) return

    const updatedPermissions = currentRole.permissions || []
    const exists = updatedPermissions.find(p => p.id === permission.id)

    if (exists) {
      setCurrentRole({
        ...currentRole,
        permissions: updatedPermissions.filter(p => p.id !== permission.id)
      })
    } else {
      setCurrentRole({
        ...currentRole,
        permissions: [...updatedPermissions, permission]
      })
    }
  }

  const toggleExpand = (roleId: number) => {
    const newExpanded = new Set(expandedRoles)
    if (newExpanded.has(roleId)) {
      newExpanded.delete(roleId)
    } else {
      newExpanded.add(roleId)
    }
    setExpandedRoles(newExpanded)
  }

  const groupPermissionsByModule = (perms: Permission[]) => {
    const grouped: { [key: string]: Permission[] } = {}
    perms.forEach(perm => {
      if (!grouped[perm.module]) {
        grouped[perm.module] = []
      }
      grouped[perm.module].push(perm)
    })
    return grouped
  }

  const getModuleDisplayName = (module: string) => {
    const moduleNames: { [key: string]: string } = {
      'user': '用户管理',
      'role': '角色管理',
      'content': '内容管理',
      'agent': '智能体管理',
      'knowledge': '知识库管理',
      'system': '系统管理',
      'finance': '财务管理',
      'stats': '统计分析'
    }
    return moduleNames[module] || module
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
            <h1 className="text-2xl font-bold text-gray-900">角色权限管理</h1>
            <p className="text-gray-600 mt-1">管理系统角色和权限分配</p>
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
            <Shield className="w-5 h-5" />
            <span>共 {roles.length} 个角色</span>
          </div>
        </div>
        <button
          onClick={() => {
            setRoleForm({ name: '', display_name: '', description: '', level: 10 })
            setIsCreateModalOpen(true)
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          创建角色
        </button>
      </div>

      {/* 角色列表 */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
            加载中...
          </div>
        ) : roles.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
            暂无角色数据
          </div>
        ) : (
          roles.map((role) => (
            <div key={role.id} className="bg-white rounded-xl shadow-sm border border-gray-200">
              {/* 角色头部 */}
              <div className="p-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold text-gray-900">{role.display_name}</h3>
                      {role.is_system && (
                        <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">系统</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{role.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-500">
                    <span className="font-medium">{role.permission_count}</span> 个权限
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleExpand(role.id)}
                      className="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors"
                    >
                      {expandedRoles.has(role.id) ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                    <button
                      onClick={() => handleOpenPermissions(role)}
                      className="p-2 rounded hover:bg-blue-100 text-blue-600 transition-colors"
                      title="管理权限"
                    >
                      <Key className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleOpenEdit(role)}
                      className="p-2 rounded hover:bg-blue-100 text-blue-600 transition-colors"
                      title="编辑"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    {!role.is_system && (
                      <button
                        onClick={() => handleDeleteRole(role)}
                        className="p-2 rounded hover:bg-red-100 text-red-600 transition-colors"
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* 展开的详情 */}
              {expandedRoles.has(role.id) && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">角色代码:</span>
                      <span className="ml-2 font-mono text-gray-900">{role.name}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">权限等级:</span>
                      <span className="ml-2 text-gray-900">{role.level}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">用户数量:</span>
                      <span className="ml-2 text-gray-900">{currentRole?.user_count || 0}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* 创建角色模态框 */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">创建角色</h2>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">角色代码</label>
                <input
                  type="text"
                  value={roleForm.name}
                  onChange={(e) => setRoleForm({ ...roleForm, name: e.target.value })}
                  placeholder="例如: content_manager"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">显示名称</label>
                <input
                  type="text"
                  value={roleForm.display_name}
                  onChange={(e) => setRoleForm({ ...roleForm, display_name: e.target.value })}
                  placeholder="例如: 内容管理员"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
                <textarea
                  value={roleForm.description}
                  onChange={(e) => setRoleForm({ ...roleForm, description: e.target.value })}
                  placeholder="角色描述"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">权限等级</label>
                <input
                  type="number"
                  value={roleForm.level}
                  onChange={(e) => setRoleForm({ ...roleForm, level: parseInt(e.target.value) })}
                  placeholder="10-100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
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
                onClick={handleCreateRole}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 编辑角色模态框 */}
      {isEditModalOpen && currentRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">编辑角色</h2>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">角色代码</label>
                <input
                  type="text"
                  value={roleForm.name}
                  disabled={!!currentRole.is_system}
                  onChange={(e) => setRoleForm({ ...roleForm, name: e.target.value })}
                  className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${currentRole.is_system ? 'bg-gray-100' : ''}`}
                />
                {currentRole.is_system && <p className="text-xs text-gray-500 mt-1">系统角色代码不可修改</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">显示名称</label>
                <input
                  type="text"
                  value={roleForm.display_name}
                  onChange={(e) => setRoleForm({ ...roleForm, display_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
                <textarea
                  value={roleForm.description}
                  onChange={(e) => setRoleForm({ ...roleForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">权限等级</label>
                <input
                  type="number"
                  value={roleForm.level}
                  onChange={(e) => setRoleForm({ ...roleForm, level: parseInt(e.target.value) })}
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
                onClick={handleEditRole}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 权限分配模态框 */}
      {isPermissionModalOpen && currentRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {currentRole.display_name} - 权限配置
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  已选择 {currentRole.permissions?.length || 0} / {permissions.length} 个权限
                </p>
              </div>
              <button
                onClick={() => setIsPermissionModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto" style={{ maxHeight: '60vh' }}>
              <div className="space-y-6">
                {Object.entries(groupPermissionsByModule(permissions)).map(([module, perms]) => (
                  <div key={module}>
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">
                      {getModuleDisplayName(module)}
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                      {perms.map((perm) => {
                        const isChecked = currentRole.permissions?.find(p => p.id === perm.id)
                        return (
                          <label
                            key={perm.id}
                            className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                              isChecked ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200 hover:bg-gray-50'
                            }`}
                          >
                            <div className="pt-0.5">
                              {isChecked ? (
                                <CheckSquare className="w-5 h-5 text-blue-600" />
                              ) : (
                                <Square className="w-5 h-5 text-gray-400" />
                              )}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-900">{perm.display_name}</div>
                              <div className="text-xs text-gray-500">{perm.name}</div>
                            </div>
                            <input
                              type="checkbox"
                              checked={!!isChecked}
                              onChange={() => togglePermission(perm)}
                              className="hidden"
                            />
                          </label>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => setIsPermissionModalOpen(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSavePermissions}
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

export default RoleManagement
