import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Users,
  Search,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  X,
  Eye,
  Plus,
  Minus,
  ShieldCheck,
  ShieldX,
  Download,
  CheckSquare,
  Square,
  Filter,
  Upload,
  Key,
  ArrowLeft
} from 'lucide-react'

interface User {
  id: number
  username: string
  email: string
  phone: string
  totalLingzhi: number
  status: string
  createdAt: string
  referrerId: number | null
  referralCode: string | null
  level: number | null
  avatarUrl?: string
  realName?: string
  isVerified?: boolean
  lastLoginAt?: string
}

interface UserDetail extends User {
  stats?: {
    checkin_count: number
    recharge_count: number
    recharge_amount: number
    consumption_count: number
    consumption_lingzhi: number
  }
}

const UserManagementEnhanced = () => {
  const navigate = useNavigate()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedUsers, setSelectedUsers] = useState<number[]>([])
  const [viewingUser, setViewingUser] = useState<UserDetail | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isLingzhiModalOpen, setIsLingzhiModalOpen] = useState(false)
  const [lingzhiAmount, setLingzhiAmount] = useState('')
  const [lingzhiReason, setLingzhiReason] = useState('')
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState({ type: '', text: '' })
  const [activeTab, setActiveTab] = useState<'basic' | 'referrals' | 'recharges' | 'consumptions' | 'devices' | 'checkins'>('basic')
  const [detailData, setDetailData] = useState<any>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailPage, setDetailPage] = useState(1)
  const [detailTotalPages, setDetailTotalPages] = useState(1)

  // 高级筛选状态
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [filters, setFilters] = useState({
    status: '',
    user_type_id: '',
    min_lingzhi: '',
    max_lingzhi: '',
    start_date: '',
    end_date: '',
    sort_by: 'id',
    sort_order: 'DESC'
  })

  // 批量操作状态
  const [batchAction, setBatchAction] = useState('')
  const [batchValue, setBatchValue] = useState('')

  // 导入功能状态
  const [isImportModalOpen, setIsImportModalOpen] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [currentPage, searchTerm])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')

      // 构建查询参数
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '10',
        search: searchTerm,
        ...filters
      })

      const response = await fetch(`/api/admin/users?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setUsers(data.data.users || [])
        setTotalPages(data.data.totalPages || 1)
      }
    } catch (error) {
      console.error('加载用户列表失败:', error)
      setMessage({ type: 'error', text: '加载用户列表失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleView = async (user: User) => {
    setViewingUser(user)
    setActiveTab('basic')
    setIsDetailModalOpen(true)
    await loadUserDetail(user.id)
  }

  const loadUserDetail = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载用户详情失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const loadUserReferrals = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/referrals?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载推荐列表失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const loadUserRecharges = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/recharges?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载充值记录失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const loadUserConsumptions = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/consumptions?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载消费记录失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const loadUserDevices = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/devices?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载设备列表失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const loadUserCheckins = async (userId: number, page = 1) => {
    setDetailLoading(true)
    setDetailPage(page)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/checkins?page=${page}&limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setDetailData(data.data)
        setDetailTotalPages(data.data.total_pages || 1)
      }
    } catch (error) {
      console.error('加载签到记录失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const handleTabChange = async (tab: typeof activeTab) => {
    setActiveTab(tab)
    setDetailPage(1)  // 重置分页页码
    if (!viewingUser) return

    switch (tab) {
      case 'basic':
        await loadUserDetail(viewingUser.id, 1)
        break
      case 'referrals':
        await loadUserReferrals(viewingUser.id, 1)
        break
      case 'recharges':
        await loadUserRecharges(viewingUser.id, 1)
        break
      case 'consumptions':
        await loadUserConsumptions(viewingUser.id, 1)
        break
      case 'devices':
        await loadUserDevices(viewingUser.id, 1)
        break
      case 'checkins':
        await loadUserCheckins(viewingUser.id, 1)
        break
    }
  }

  const handleUpdateStatus = async (userId: number, status: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户状态更新成功' })
        loadUsers()
        if (viewingUser) {
          loadUserDetail(viewingUser.id)
        }
      } else {
        setMessage({ type: 'error', text: data.message || '更新失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handlePasswordChange = async () => {
    if (!editingUser) return

    // 验证密码
    if (!newPassword || newPassword.length < 6) {
      setMessage({ type: 'error', text: '密码长度至少为6位' })
      return
    }

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: '两次输入的密码不一致' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${editingUser.id}/password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          password: newPassword
        })
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '密码修改成功' })
        setIsPasswordModalOpen(false)
        setNewPassword('')
        setConfirmPassword('')
      } else {
        setMessage({ type: 'error', text: data.message || '修改失败' })
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
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${user.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: '用户删除成功' })
        setIsDetailModalOpen(false)
        loadUsers()
      } else {
        setMessage({ type: 'error', text: data.message || '删除失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleBatchExecute = async () => {
    if (selectedUsers.length === 0) {
      setMessage({ type: 'error', text: '请先选择用户' })
      return
    }

    if (!batchAction) {
      setMessage({ type: 'error', text: '请选择批量操作' })
      return
    }

    // 映射操作类型
    const actionMap: Record<string, { action: string; value?: string }> = {
      'set_status_active': { action: 'status', value: 'active' },
      'set_status_inactive': { action: 'status', value: 'inactive' },
      'set_status_banned': { action: 'status', value: 'banned' },
      'delete': { action: 'delete' }
    }

    const mapped = actionMap[batchAction]
    if (!mapped) {
      setMessage({ type: 'error', text: '不支持的操作' })
      return
    }

    // 二次确认删除操作
    if (mapped.action === 'delete') {
      if (!window.confirm(`确定要删除选中的 ${selectedUsers.length} 个用户吗？此操作不可恢复。`)) {
        return
      }
    } else if (!mapped.value) {
      setMessage({ type: 'error', text: '请选择操作值' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/users/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_ids: selectedUsers,
          action: mapped.action,
          value: mapped.value
        })
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: data.message })
        setSelectedUsers([])
        setBatchAction('')
        setBatchValue('')
        loadUsers()
      } else {
        setMessage({ type: 'error', text: data.message || '操作失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/users/export', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `users_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        setMessage({ type: 'success', text: '用户列表导出成功' })
      } else {
        setMessage({ type: 'error', text: '导出失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    }
  }

  const handleImport = async () => {
    if (!importFile) {
      setMessage({ type: 'error', text: '请选择要导入的CSV文件' })
      return
    }

    setImporting(true)
    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('file', importFile)

      const response = await fetch('/api/admin/users/import', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: data.message })
        setIsImportModalOpen(false)
        setImportFile(null)
        loadUsers()
      } else {
        setMessage({ type: 'error', text: data.message || '导入失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    } finally {
      setImporting(false)
    }
  }

  const handleAdjustLingzhi = async () => {
    if (!editingUser || !lingzhiAmount) return

    const amount = parseInt(lingzhiAmount)
    if (isNaN(amount)) {
      setMessage({ type: 'error', text: '请输入有效的金额' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${editingUser.id}/lingzhi`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: amount,
          reason: lingzhiReason || '管理员调整'
        })
      })
      const data = await response.json()
      if (data.success) {
        setMessage({ type: 'success', text: `灵值调整成功: ${amount > 0 ? '+' : ''}${amount}` })
        setIsLingzhiModalOpen(false)
        setLingzhiAmount('')
        setLingzhiReason('')
        loadUsers()
        if (viewingUser) {
          loadUserDetail(viewingUser.id)
        }
      } else {
        setMessage({ type: 'error', text: data.message || '调整失败' })
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

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { bg: 'bg-green-100', text: 'text-green-700', label: '正常' },
      inactive: { bg: 'bg-gray-100', text: 'text-gray-700', label: '未激活' },
      banned: { bg: 'bg-red-100', text: 'text-red-700', label: '已封禁' }
    }
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active
    return <span className={`px-2 py-1 text-xs rounded ${config.bg} ${config.text}`}>{config.label}</span>
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
            <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
            <p className="text-gray-600 mt-1">管理系统中的所有用户</p>
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

      {/* 搜索和操作栏 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="space-y-4">
          {/* 第一行：搜索和基本操作 */}
          <div className="flex items-center justify-between space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="搜索用户名、邮箱、手机号或真实姓名..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setCurrentPage(1)
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsFilterOpen(!isFilterOpen)}
                className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                  isFilterOpen
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Filter className="w-4 h-4 mr-2" />
                高级筛选
              </button>
              <button
                onClick={() => setIsImportModalOpen(true)}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Upload className="w-4 h-4 mr-2" />
                导入
              </button>
              <button
                onClick={handleExport}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                导出
              </button>
              {selectedUsers.length > 0 && (
                <span className="text-sm text-gray-600">
                  已选择 {selectedUsers.length} 个用户
                </span>
              )}
            </div>
          </div>

          {/* 高级筛选区域 */}
          {isFilterOpen && (
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部</option>
                    <option value="active">活跃</option>
                    <option value="inactive">未激活</option>
                    <option value="banned">已封禁</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">用户类型</label>
                  <select
                    value={filters.user_type_id}
                    onChange={(e) => setFilters({ ...filters, user_type_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部</option>
                    <option value="1">一般用户</option>
                    <option value="2">项目总经理</option>
                    <option value="3">公司总经理</option>
                    <option value="4">初级合伙人</option>
                    <option value="5">中级合伙人</option>
                    <option value="6">高级合伙人</option>
                    <option value="7">股东</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">最小灵值</label>
                  <input
                    type="number"
                    value={filters.min_lingzhi}
                    onChange={(e) => setFilters({ ...filters, min_lingzhi: e.target.value })}
                    placeholder="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">最大灵值</label>
                  <input
                    type="number"
                    value={filters.max_lingzhi}
                    onChange={(e) => setFilters({ ...filters, max_lingzhi: e.target.value })}
                    placeholder="无限制"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">注册开始日期</label>
                  <input
                    type="date"
                    value={filters.start_date}
                    onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">注册结束日期</label>
                  <input
                    type="date"
                    value={filters.end_date}
                    onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">排序字段</label>
                  <select
                    value={filters.sort_by}
                    onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="id">ID</option>
                    <option value="username">用户名</option>
                    <option value="total_lingzhi">灵值</option>
                    <option value="created_at">注册时间</option>
                    <option value="last_login_at">最后登录</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">排序方式</label>
                  <select
                    value={filters.sort_order}
                    onChange={(e) => setFilters({ ...filters, sort_order: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="DESC">降序</option>
                    <option value="ASC">升序</option>
                  </select>
                </div>
              </div>
              <div className="mt-4 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setFilters({
                      status: '',
                      user_type_id: '',
                      min_lingzhi: '',
                      max_lingzhi: '',
                      start_date: '',
                      end_date: '',
                      sort_by: 'id',
                      sort_order: 'DESC'
                    })
                    setCurrentPage(1)
                    loadUsers()
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  重置筛选
                </button>
                <button
                  onClick={() => {
                    setCurrentPage(1)
                    loadUsers()
                  }}
                  className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  应用筛选
                </button>
              </div>
            </div>
          )}

          {/* 第二行：批量操作（当选中用户时显示） */}
          {selectedUsers.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sm text-gray-700">
                  <span>已选择 <strong>{selectedUsers.length}</strong> 个用户</span>
                </div>
                <div className="flex items-center space-x-2">
                  <select
                    value={batchAction}
                    onChange={(e) => setBatchAction(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">批量操作...</option>
                    <option value="set_status_active">批量启用</option>
                    <option value="set_status_inactive">批量禁用</option>
                    <option value="set_status_banned">批量封禁</option>
                    <option value="delete">批量删除</option>
                  </select>
                  {batchAction && (
                    <>
                      {batchAction.includes('set_status') && (
                        <select
                          value={batchValue}
                          onChange={(e) => setBatchValue(e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">选择状态...</option>
                          <option value="active">活跃</option>
                          <option value="inactive">未激活</option>
                          <option value="banned">已封禁</option>
                        </select>
                      )}
                      <button
                        onClick={() => handleBatchExecute()}
                        className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                      >
                        执行操作
                      </button>
                      <button
                        onClick={() => {
                          setBatchAction('')
                          setBatchValue('')
                        }}
                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                      >
                        取消
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 用户列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10">
                <input
                  type="checkbox"
                  checked={selectedUsers.length === users.length && users.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedUsers(users.map(u => u.id))
                    } else {
                      setSelectedUsers([])
                    }
                  }}
                  className="rounded"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">手机号</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">灵值</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center text-gray-500">加载中...</td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center text-gray-500">暂无用户数据</td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedUsers([...selectedUsers, user.id])
                        } else {
                          setSelectedUsers(selectedUsers.filter(id => id !== user.id))
                        }
                      }}
                      className="rounded"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{user.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.phone || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{user.totalLingzhi}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(user.status)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(user.createdAt)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleView(user)}
                        className="p-2 rounded hover:bg-blue-100 text-blue-600 transition-colors"
                        title="查看详情"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => navigate(`/admin/users/${user.id}/edit`)}
                        className="p-2 rounded hover:bg-green-100 text-green-600 transition-colors"
                        title="编辑资料"
                      >
                        <Edit2 className="w-4 h-4" />
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
                onClick={() => {
                  if (currentPage > 1) {
                    setCurrentPage(currentPage - 1)
                  }
                }}
                disabled={currentPage === 1}
                className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  if (currentPage < totalPages) {
                    setCurrentPage(currentPage + 1)
                  }
                }}
                disabled={currentPage === totalPages}
                className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 用户详情模态框 */}
      {isDetailModalOpen && viewingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-6xl mx-4 max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  返回
                </button>
                <h2 className="text-lg font-semibold text-gray-900">用户详情 #{viewingUser.id}</h2>
              </div>
              <button
                onClick={() => setIsDetailModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 用户基本信息 */}
            <div className="p-6 bg-gray-50 border-b">
              <div className="flex items-start space-x-6">
                {viewingUser.avatarUrl && (
                  <img
                    src={viewingUser.avatarUrl}
                    alt={viewingUser.username}
                    className="w-20 h-20 rounded-full object-cover"
                  />
                )}
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-xl font-semibold text-gray-900">{viewingUser.username}</h3>
                    {getStatusBadge(viewingUser.status)}
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div><span className="font-medium">邮箱:</span> {viewingUser.email || '-'}</div>
                    <div><span className="font-medium">手机:</span> {viewingUser.phone || '-'}</div>
                    <div><span className="font-medium">灵值:</span> <span className="font-semibold text-gray-900">{viewingUser.totalLingzhi}</span></div>
                    <div><span className="font-medium">注册时间:</span> {formatDate(viewingUser.createdAt)}</div>
                    {viewingUser.lastLoginAt && (
                      <div><span className="font-medium">最后登录:</span> {formatDate(viewingUser.lastLoginAt)}</div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => { setEditingUser(viewingUser); setIsLingzhiModalOpen(true); }}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    调整灵值
                  </button>
                  <button
                    onClick={() => { setEditingUser(viewingUser); setIsPasswordModalOpen(true); }}
                    className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Key className="w-4 h-4 mr-2" />
                    修改密码
                  </button>
                  <div className="flex space-x-2">
                    {viewingUser.status !== 'active' && (
                      <button
                        onClick={() => handleUpdateStatus(viewingUser.id, 'active')}
                        className="flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <ShieldCheck className="w-4 h-4 mr-1" />
                        启用
                      </button>
                    )}
                    {viewingUser.status !== 'banned' && (
                      <button
                        onClick={() => handleUpdateStatus(viewingUser.id, 'banned')}
                        className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                      >
                        <ShieldX className="w-4 h-4 mr-1" />
                        封禁
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(viewingUser)}
                      className="flex items-center px-3 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* 选项卡 */}
            <div className="border-b">
              <div className="flex">
                {(['basic', 'referrals', 'recharges', 'consumptions', 'devices', 'checkins'] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => handleTabChange(tab)}
                    className={`px-6 py-3 text-sm font-medium ${
                      activeTab === tab
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {tab === 'basic' && '基本信息'}
                    {tab === 'referrals' && '推荐列表'}
                    {tab === 'recharges' && '充值记录'}
                    {tab === 'consumptions' && '消费记录'}
                    {tab === 'devices' && '设备管理'}
                    {tab === 'checkins' && '签到记录'}
                  </button>
                ))}
              </div>
            </div>

            {/* 内容区域 */}
            <div className="p-6 overflow-y-auto" style={{ maxHeight: '500px' }}>
              {detailLoading ? (
                <div className="text-center py-8 text-gray-500">加载中...</div>
              ) : activeTab === 'basic' && detailData?.stats ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">用户统计</h4>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg border">
                      <div className="text-2xl font-bold text-blue-600">{detailData.stats.checkin_count}</div>
                      <div className="text-sm text-gray-600">签到次数</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg border">
                      <div className="text-2xl font-bold text-green-600">{detailData.stats.recharge_count}</div>
                      <div className="text-sm text-gray-600">充值次数</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg border">
                      <div className="text-2xl font-bold text-purple-600">{detailData.stats.consumption_count}</div>
                      <div className="text-sm text-gray-600">消费次数</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg border">
                      <div className="text-2xl font-bold text-orange-600">{detailData.stats.recharge_amount}</div>
                      <div className="text-sm text-gray-600">累计充值</div>
                    </div>
                  </div>
                </div>
              ) : activeTab === 'referrals' && detailData?.referrals ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">
                    推荐列表 ({detailData.referral_count} 人)
                  </h4>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">用户名</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">灵值</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">注册时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.referrals.map((ref: any) => (
                        <tr key={ref.id} className="border-b">
                          <td className="px-4 py-2 text-sm">{ref.id}</td>
                          <td className="px-4 py-2 text-sm font-medium">{ref.username}</td>
                          <td className="px-4 py-2 text-sm">{ref.totalLingzhi}</td>
                          <td className="px-4 py-2 text-sm">{formatDate(ref.createdAt)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : activeTab === 'recharges' && detailData?.recharges ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">
                    充值记录 ({detailData.total} 条)
                  </h4>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">金额</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">状态</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.recharges.map((rec: any) => (
                        <tr key={rec.id} className="border-b">
                          <td className="px-4 py-2 text-sm">¥{rec.amount}</td>
                          <td className="px-4 py-2 text-sm">{rec.payment_status}</td>
                          <td className="px-4 py-2 text-sm">{formatDate(rec.createdAt)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : activeTab === 'consumptions' && detailData?.consumptions ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">
                    消费记录 ({detailData.total} 条)
                  </h4>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">灵值</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">类型</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.consumptions.map((cons: any) => (
                        <tr key={cons.id} className="border-b">
                          <td className="px-4 py-2 text-sm">{cons.lingzhi_amount}</td>
                          <td className="px-4 py-2 text-sm">{cons.consumption_type}</td>
                          <td className="px-4 py-2 text-sm">{formatDate(cons.createdAt)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : activeTab === 'devices' && detailData?.devices ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">
                    设备管理 ({detailData.devices.length} 个设备)
                  </h4>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">设备名称</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">设备类型</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">最后活跃</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.devices.map((dev: any) => (
                        <tr key={dev.id} className="border-b">
                          <td className="px-4 py-2 text-sm">{dev.device_name || '-'}</td>
                          <td className="px-4 py-2 text-sm">{dev.device_type || '-'}</td>
                          <td className="px-4 py-2 text-sm">{formatDate(dev.last_active_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : activeTab === 'checkins' && detailData?.checkins ? (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">
                    签到记录 ({detailData.total} 条)
                  </h4>
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">日期</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">奖励</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.checkins.map((check: any) => (
                        <tr key={check.id} className="border-b">
                          <td className="px-4 py-2 text-sm">{formatDate(check.checkin_date)}</td>
                          <td className="px-4 py-2 text-sm">{check.lingzhi_reward} 灵值</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">暂无数据</div>
              )}

              {/* 详情页翻页 */}
              {detailTotalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="text-sm text-gray-700">
                    第 {detailPage} / {detailTotalPages} 页
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        if (detailPage > 1) {
                          if (viewingUser) {
                            switch (activeTab) {
                              case 'basic':
                                loadUserDetail(viewingUser.id, detailPage - 1)
                                break
                              case 'referrals':
                                loadUserReferrals(viewingUser.id, detailPage - 1)
                                break
                              case 'recharges':
                                loadUserRecharges(viewingUser.id, detailPage - 1)
                                break
                              case 'consumptions':
                                loadUserConsumptions(viewingUser.id, detailPage - 1)
                                break
                              case 'devices':
                                loadUserDevices(viewingUser.id, detailPage - 1)
                                break
                              case 'checkins':
                                loadUserCheckins(viewingUser.id, detailPage - 1)
                                break
                            }
                          }
                        }
                      }}
                      disabled={detailPage === 1}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (detailPage < detailTotalPages && viewingUser) {
                          switch (activeTab) {
                            case 'basic':
                              loadUserDetail(viewingUser.id, detailPage + 1)
                              break
                            case 'referrals':
                              loadUserReferrals(viewingUser.id, detailPage + 1)
                              break
                            case 'recharges':
                              loadUserRecharges(viewingUser.id, detailPage + 1)
                              break
                            case 'consumptions':
                              loadUserConsumptions(viewingUser.id, detailPage + 1)
                              break
                            case 'devices':
                              loadUserDevices(viewingUser.id, detailPage + 1)
                              break
                            case 'checkins':
                              loadUserCheckins(viewingUser.id, detailPage + 1)
                              break
                          }
                        }
                      }}
                      disabled={detailPage === detailTotalPages}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 灵值调整模态框 */}
      {isLingzhiModalOpen && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">调整灵值</h2>
              <button
                onClick={() => setIsLingzhiModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  当前灵值
                </label>
                <div className="text-2xl font-bold text-gray-900">{editingUser.totalLingzhi}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  调整金额（正数增加，负数减少）
                </label>
                <input
                  type="number"
                  value={lingzhiAmount}
                  onChange={(e) => setLingzhiAmount(e.target.value)}
                  placeholder="输入调整金额"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  调整原因
                </label>
                <input
                  type="text"
                  value={lingzhiReason}
                  onChange={(e) => setLingzhiReason(e.target.value)}
                  placeholder="输入调整原因"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => setIsLingzhiModalOpen(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleAdjustLingzhi}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                确认调整
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 密码修改模态框 */}
      {isPasswordModalOpen && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">修改用户密码</h2>
              <button
                onClick={() => setIsPasswordModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  用户名
                </label>
                <div className="text-lg font-semibold text-gray-900">{editingUser.username}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  新密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="请输入新密码（至少6位）"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  确认密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="请再次输入新密码"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-yellow-800">
                  ⚠️ 注意：此操作将立即修改用户密码，请谨慎操作。修改后用户需要使用新密码登录。
                </p>
              </div>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => {
                  setIsPasswordModalOpen(false)
                  setNewPassword('')
                  setConfirmPassword('')
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handlePasswordChange}
                className="px-4 py-2 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                确认修改
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 用户导入模态框 */}
      {isImportModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">批量导入用户</h2>
              <button
                onClick={() => setIsImportModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">导入说明</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• 仅支持 CSV 格式文件</li>
                  <li>• 必须包含字段：username（用户名）、password（密码）</li>
                  <li>• 可选字段：email（邮箱）、phone（手机号）</li>
                  <li>• 用户名不能重复</li>
                  <li>• 密码会自动加密存储</li>
                </ul>
                <button
                  onClick={() => {
                    const csvContent = 'username,password,email,phone\nuser1,pass123,user1@example.com,\nuser2,pass456,,13800138000'
                    const blob = new Blob([csvContent], { type: 'text/csv' })
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = 'users_template.csv'
                    document.body.appendChild(a)
                    a.click()
                    window.URL.revokeObjectURL(url)
                    document.body.removeChild(a)
                  }}
                  className="mt-3 text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  下载导入模板
                </button>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  选择CSV文件
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) {
                      setImportFile(file)
                    }
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {importFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    已选择: {importFile.name} ({(importFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button
                onClick={() => {
                  setIsImportModalOpen(false)
                  setImportFile(null)
                }}
                disabled={importing}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                取消
              </button>
              <button
                onClick={handleImport}
                disabled={!importFile || importing}
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {importing ? '导入中...' : '开始导入'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserManagementEnhanced
