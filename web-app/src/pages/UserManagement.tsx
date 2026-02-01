import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Users,
  Search,
  Edit2,
  Trash2,
  Plus,
  ChevronLeft,
  ChevronRight,
  X
} from 'lucide-react'

interface User {
  id: number
  username: string
  email: string
  phone: string
  total_lingzhi: number
  created_at: string
}

const UserManagement = () => {
  const navigate = useNavigate()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<User | null>(null)
  const [editForm, setEditForm] = useState({
    username: '',
    email: '',
    phone: '',
    total_lingzhi: 0
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    loadUsers()
  }, [currentPage, searchTerm])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('adminToken')
      const response = await fetch(`/api/admin/users?page=${currentPage}&limit=10&search=${searchTerm}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setUsers(data.data.users || [])
        setTotalPages(data.data.totalPages || 1)
      }
    } catch (error) {
      console.error('加载用户列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    setEditForm({
      username: user.username,
      email: user.email || '',
      phone: user.phone || '',
      total_lingzhi: user.total_lingzhi
    })
    setIsEditModalOpen(true)
  }

  const handleSaveEdit = async () => {
    if (!editingUser) return

    try {
      const token = localStorage.getItem('adminToken')
      const response = await fetch(`/api/admin/users/${editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(editForm)
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户信息更新成功' })
        setIsEditModalOpen(false)
        loadUsers()
      } else {
        setMessage({ type: 'error', text: data.message || '更新失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleDelete = async (user: User) => {
    if (!window.confirm(`确定要删除用户 "${user.username}" 吗？此操作不可恢复。`)) {
      return
    }

    try {
      const token = localStorage.getItem('adminToken')
      const response = await fetch(`/api/admin/users/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户删除成功' })
        loadUsers()
      } else {
        setMessage({ type: 'error', text: data.message || '删除失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
        <p className="text-gray-600 mt-1">管理系统中的所有用户</p>
      </div>

      {/* 消息提示 */}
      {message.text && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* 搜索栏 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索用户名、邮箱或手机号..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* 用户列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">手机号</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">灵值</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">加载中...</td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">暂无用户数据</td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{user.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.phone || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{user.total_lingzhi}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(user.created_at)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(user)}
                        className="p-2 rounded hover:bg-blue-100 text-blue-600 transition-colors"
                        title="编辑"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(user)}
                        className="p-2 rounded hover:bg-red-100 text-red-600 transition-colors"
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* 分页 */}
        {totalPages > 1 && (
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              第 {currentPage} / {totalPages} 页
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 编辑用户模态框 */}
      {isEditModalOpen && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">编辑用户</h2>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                <input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                <input
                  type="tel"
                  value={editForm.phone}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">灵值</label>
                <input
                  type="number"
                  value={editForm.total_lingzhi}
                  onChange={(e) => setEditForm({ ...editForm, total_lingzhi: parseInt(e.target.value) || 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 p-6 border-t">
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
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

export default UserManagement
