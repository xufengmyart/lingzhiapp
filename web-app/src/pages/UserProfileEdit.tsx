import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  User,
  Save,
  X,
  ArrowLeft,
  MapPin,
  Phone,
  Mail,
  Globe,
  Tag,
  Award,
  Heart,
  Plus,
  Trash2,
  CheckCircle,
  AlertCircle,
  Edit3,
  Lock
} from 'lucide-react'

interface UserField {
  name: string
  label: string
  type: 'text' | 'email' | 'tel' | 'url' | 'select' | 'textarea' | 'tags' | 'object'
  editable: boolean
  required?: boolean
  placeholder?: string
  maxLength?: number
  options?: { value: string; label: string }[]
  fields?: UserField[]
  sensitive?: boolean
  adminOnly?: boolean
  description?: string
}

interface FieldGroup {
  title: string
  fields: UserField[]
}

interface UserProfile {
  id: number
  username: string
  email?: string
  phone?: string
  password_hash?: string
  total_lingzhi: number
  status: string
  last_login_at?: string
  avatar_url?: string
  real_name?: string
  is_verified?: boolean
  login_type?: string
  wechat_openid?: string
  wechat_unionid?: string
  wechat_nickname?: string
  wechat_avatar?: string
  created_at: string
  updated_at: string
  referrer_id?: number
  referee_id?: number
  referral_code?: string
  level?: number
  total_contribution?: number
  cumulative_contribution?: number
  current_stage?: string
  journey_progress?: number
  account_status?: string
  verification_status?: string
  wechat_bound?: boolean
  phone_bound?: boolean
  require_phone_verification?: boolean
  single_login_enabled?: boolean
  sys_platform?: string
  uuid?: string
  bstudio_create_time?: string
  my_cczd?: boolean
  my_userid?: number
  gender?: string
  title?: string
  position?: string
  checkintime?: string
  permission?: string
  consumervalue?: number
  remaining?: number
  participate?: string
  complete?: string
  obtainvalue?: number
  lead_name?: string
  my_sfzh?: string
  my_wxh?: string
  user_type_id?: number
  user_type?: any
  my_sfzh_masked?: string
  cultural_interests?: string[]
  participated_projects?: string[]
  skill_tags?: string[]
  location?: string
  service_area?: string
  bio?: string
  social_links?: Record<string, string>
  contribution_details?: any
  achievement_badges?: any
}

const UserProfileEdit = () => {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [activeSection, setActiveSection] = useState('basic')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    loadUserProfile()
    loadSchema()
    checkAdminRole()
  }, [userId])

  const loadUserProfile = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setMessage({ type: 'error', text: '请先登录' })
        navigate('/admin/login')
        return
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.status === 401) {
        setMessage({ type: 'error', text: '登录已过期，请重新登录' })
        localStorage.removeItem('token')
        navigate('/admin/login')
        return
      }

      if (!response.ok) {
        throw new Error(`获取用户资料失败 (${response.status})`)
      }

      // 检查响应内容类型
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('服务器返回了非JSON格式的响应')
      }

      const result = await response.json()
      if (!result.success) {
        throw new Error(result.message || '获取用户资料失败')
      }
      
      setUser(result.user)
      setFormData(result.user)
    } catch (error) {
      console.error('加载用户资料失败:', error)
      const errorMessage = error instanceof Error ? error.message : '加载用户资料失败，请稍后重试'
      setMessage({ type: 'error', text: errorMessage })
    } finally {
      setLoading(false)
    }
  }

  const loadSchema = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('未找到 token，跳过加载字段定义')
        return
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}/profile/schema`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.status === 401) {
        console.warn('Token 已过期，跳过加载字段定义')
        return
      }

      if (!response.ok) {
        console.warn('加载字段定义失败:', response.status)
        return
      }

      // 检查响应内容类型
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        console.warn('服务器返回了非JSON格式的响应')
        return
      }

      const result = await response.json()
      // 可以使用schema来生成动态表单
    } catch (error) {
      console.error('加载字段定义失败:', error)
      // schema加载失败不影响主要功能，只记录日志
    }
  }

  const checkAdminRole = () => {
    const role = localStorage.getItem('adminRole')
    setIsAdmin(role === 'admin' || role === 'superadmin')
  }

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: '请上传图片文件' })
      return
    }

    // 验证文件大小 (最大5MB)
    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: '图片大小不能超过5MB' })
      return
    }

    try {
      setSaving(true)
      const token = localStorage.getItem('token')

      // 创建FormData
      const formData = new FormData()
      formData.append('avatar', file)

      // 上传头像（注意：不要使用 VITE_API_BASE_URL，直接使用 /api 前缀）
      const response = await fetch(`/api/admin/users/${userId}/avatar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '上传头像失败')
      }

      const result = await response.json()
      if (result.success) {
        // 更新用户头像
        setUser(prev => prev ? { ...prev, avatar_url: result.data.avatar_url } : null)
        setMessage({ type: 'success', text: '头像上传成功' })
        
        // 刷新用户信息
        await loadUserProfile()
        
        // 3秒后清除消息
        setTimeout(() => setMessage(null), 3000)
      } else {
        throw new Error(result.message || '上传头像失败')
      }
    } catch (error) {
      console.error('上传头像失败:', error)
      setMessage({ type: 'error', text: error instanceof Error ? error.message : '上传头像失败' })
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleTagAdd = (field: string) => {
    const inputValue = (document.getElementById(`tag-input-${field}`) as HTMLInputElement)?.value
    if (!inputValue || !inputValue.trim()) return

    const currentTags = formData[field] || []
    if (!currentTags.includes(inputValue.trim())) {
      handleChange(field, [...currentTags, inputValue.trim()])
    }

    const inputEl = document.getElementById(`tag-input-${field}`) as HTMLInputElement
    if (inputEl) inputEl.value = ''
  }

  const handleTagRemove = (field: string, tagToRemove: string) => {
    const currentTags = formData[field] || []
    handleChange(field, currentTags.filter((tag: string) => tag !== tagToRemove))
  }

  const handleSocialLinkChange = (platform: string, value: string) => {
    const currentLinks = formData['social_links'] || {}
    handleChange('social_links', {
      ...currentLinks,
      [platform]: value
    })
  }

  const handleSubmit = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setMessage({ type: 'error', text: '请先登录' })
        navigate('/admin/login')
        return
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.status === 401) {
        setMessage({ type: 'error', text: '登录已过期，请重新登录' })
        localStorage.removeItem('token')
        navigate('/admin/login')
        return
      }

      if (!response.ok) {
        // 检查响应内容类型
        const contentType = response.headers.get('content-type')
        if (!contentType || !contentType.includes('application/json')) {
          const text = await response.text()
          throw new Error(`服务器返回了非JSON格式的响应 (HTTP ${response.status}): ${text.substring(0, 200)}`)
        }

        const error = await response.json()
        throw new Error(error.error || error.message || '保存失败')
      }

      const result = await response.json()
      if (!result.success) {
        throw new Error(result.message || result.error || '保存失败')
      }

      setMessage({ type: 'success', text: '用户资料保存成功' })
      setTimeout(() => {
        setMessage(null)
      }, 3000)

      // 重新加载用户数据
      loadUserProfile()
    } catch (error: any) {
      console.error('保存失败:', error)
      const errorMessage = error.message || '保存失败，请稍后重试'
      setMessage({ type: 'error', text: errorMessage })
    } finally {
      setSaving(false)
    }
  }

  const sections = [
    {
      id: 'basic',
      label: '基本信息',
      icon: <User className="w-5 h-5" />
    },
    {
      id: 'identity',
      label: '身份信息',
      icon: <Edit3 className="w-5 h-5" />
    },
    {
      id: 'cultural',
      label: '文化信息',
      icon: <Heart className="w-5 h-5" />
    },
    {
      id: 'location',
      label: '位置信息',
      icon: <MapPin className="w-5 h-5" />
    },
    {
      id: 'social',
      label: '社交媒体',
      icon: <Globe className="w-5 h-5" />
    },
    {
      id: 'contribution',
      label: '贡献值（只读）',
      icon: <Award className="w-5 h-5" />
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
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
                onClick={() => navigate('/admin/users')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">用户资料编辑</h1>
                <p className="text-sm text-gray-600">
                  {user?.username || user?.phone || `用户 #${userId}`}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/admin/users')}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSubmit}
                disabled={saving}
                className="flex items-center px-4 py-2 text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    保存
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`max-w-7xl mx-auto px-4 mt-4`}>
          <div className={`p-4 rounded-lg flex items-center ${
            message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-2" />
            )}
            {message.text}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* 左侧导航 */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <nav className="space-y-1">
                {sections.map(section => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center px-3 py-2 rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {section.icon}
                    <span className="ml-3">{section.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* 用户基本信息卡片 */}
            <div className="bg-white rounded-lg shadow-sm p-4 mt-4">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt="头像"
                      className="w-20 h-20 rounded-full object-cover border-2 border-indigo-200"
                    />
                  ) : (
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center border-2 border-indigo-200">
                      <User className="w-10 h-10 text-indigo-600" />
                    </div>
                  )}
                  <label className="absolute bottom-0 right-0 w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-indigo-700 transition-colors shadow-md">
                    <Plus className="w-4 h-4 text-white" />
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleAvatarUpload}
                    />
                  </label>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 text-lg">{user?.username}</p>
                  <p className="text-sm text-gray-600">{user?.real_name || '未设置姓名'}</p>
                  <p className="text-xs text-gray-500 mt-1">ID: {user?.id}</p>
                  <p className="text-xs text-gray-400 mt-1">点击右上角 + 上传头像</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">注册时间</span>
                  <span className="text-gray-900">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('zh-CN') : '-'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧表单内容 */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm p-6">
              {activeSection === 'basic' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">基本信息</h2>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                      <input
                        type="text"
                        value={formData.username || ''}
                        disabled
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                      <input
                        type="email"
                        value={formData.email || ''}
                        onChange={(e) => handleChange('email', e.target.value)}
                        placeholder="请输入邮箱"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                      <input
                        type="tel"
                        value={formData.phone || ''}
                        onChange={(e) => handleChange('phone', e.target.value)}
                        placeholder="请输入手机号"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">真实姓名</label>
                      <input
                        type="text"
                        value={formData.real_name || ''}
                        onChange={(e) => handleChange('real_name', e.target.value)}
                        placeholder="请输入真实姓名"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">性别</label>
                      <select
                        value={formData.gender || ''}
                        onChange={(e) => handleChange('gender', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="">请选择</option>
                        <option value="男">男</option>
                        <option value="女">女</option>
                      </select>
                    </div>
                  </div>

                  {/* 个人简介 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
                    <textarea
                      value={formData.bio || ''}
                      onChange={(e) => handleChange('bio', e.target.value)}
                      placeholder="请输入个人简介（最多500字）"
                      maxLength={500}
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {(formData.bio || '').length} / 500
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'identity' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">身份信息</h2>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">头衔</label>
                      <input
                        type="text"
                        value={formData.title || ''}
                        onChange={(e) => handleChange('title', e.target.value)}
                        placeholder="请输入头衔"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">职位</label>
                      <input
                        type="text"
                        value={formData.position || ''}
                        onChange={(e) => handleChange('position', e.target.value)}
                        placeholder="请输入职位"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    {isAdmin && (
                      <div>
                        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                          <Lock className="w-4 h-4 mr-1 text-gray-400" />
                          证件号
                        </label>
                        <input
                          type="text"
                          value={formData.my_sfzh || ''}
                          onChange={(e) => handleChange('my_sfzh', e.target.value)}
                          placeholder="请输入证件号（仅管理员可见）"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">微信号</label>
                      <input
                        type="text"
                        value={formData.my_wxh || ''}
                        onChange={(e) => handleChange('my_wxh', e.target.value)}
                        placeholder="请输入微信号"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">负责人</label>
                      <input
                        type="text"
                        value={formData.lead_name || ''}
                        onChange={(e) => handleChange('lead_name', e.target.value)}
                        placeholder="请输入负责人"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    {/* 新增：身份证号、银行账号、开户行 */}
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        身份证号
                      </label>
                      <input
                        type="text"
                        value={formData.id_card || ''}
                        onChange={(e) => handleChange('id_card', e.target.value)}
                        placeholder="请输入身份证号（选填，用于提现验证）"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      {formData.id_card_masked && !formData.id_card && (
                        <p className="text-xs text-gray-500 mt-1">
                          已填写：{formData.id_card_masked}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        开户银行
                      </label>
                      <input
                        type="text"
                        value={formData.bank_name || ''}
                        onChange={(e) => handleChange('bank_name', e.target.value)}
                        placeholder="请输入开户银行"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        银行账号
                      </label>
                      <input
                        type="text"
                        value={formData.bank_account || ''}
                        onChange={(e) => handleChange('bank_account', e.target.value)}
                        placeholder="请输入银行账号"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      {formData.bank_account_masked && !formData.bank_account && (
                        <p className="text-xs text-gray-500 mt-1">
                          已填写：{formData.bank_account_masked}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeSection === 'cultural' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">文化相关信息</h2>

                  {/* 文化兴趣标签 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Tag className="w-4 h-4 inline mr-1" />
                      文化兴趣标签
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {(formData.cultural_interests || []).map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                        >
                          {tag}
                          <button
                            onClick={() => handleTagRemove('cultural_interests', tag)}
                            className="ml-2 hover:text-indigo-900"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        id="tag-input-cultural_interests"
                        type="text"
                        placeholder="添加文化兴趣标签"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleTagAdd('cultural_interests')}
                      />
                      <button
                        onClick={() => handleTagAdd('cultural_interests')}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* 参与项目 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      参与项目
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {(formData.participated_projects || []).map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                        >
                          {tag}
                          <button
                            onClick={() => handleTagRemove('participated_projects', tag)}
                            className="ml-2 hover:text-green-900"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        id="tag-input-participated_projects"
                        type="text"
                        placeholder="添加参与项目"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleTagAdd('participated_projects')}
                      />
                      <button
                        onClick={() => handleTagAdd('participated_projects')}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* 技能标签 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      技能标签
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {(formData.skill_tags || []).map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                        >
                          {tag}
                          <button
                            onClick={() => handleTagRemove('skill_tags', tag)}
                            className="ml-2 hover:text-purple-900"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        id="tag-input-skill_tags"
                        type="text"
                        placeholder="添加技能标签"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleTagAdd('skill_tags')}
                      />
                      <button
                        onClick={() => handleTagAdd('skill_tags')}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">服务区域</label>
                    <input
                      type="text"
                      value={formData.service_area || ''}
                      onChange={(e) => handleChange('service_area', e.target.value)}
                      placeholder="请输入服务区域"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              {activeSection === 'location' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">位置信息</h2>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <MapPin className="w-4 h-4 inline mr-1" />
                      地理位置
                    </label>
                    <input
                      type="text"
                      value={formData.location || ''}
                      onChange={(e) => handleChange('location', e.target.value)}
                      placeholder="如：北京市朝阳区"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              {activeSection === 'social' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">社交媒体</h2>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">微博</label>
                      <input
                        type="url"
                        value={formData.social_links?.weibo || ''}
                        onChange={(e) => handleSocialLinkChange('weibo', e.target.value)}
                        placeholder="https://weibo.com/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">抖音</label>
                      <input
                        type="url"
                        value={formData.social_links?.douyin || ''}
                        onChange={(e) => handleSocialLinkChange('douyin', e.target.value)}
                        placeholder="https://douyin.com/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">其他链接</label>
                      <input
                        type="url"
                        value={formData.social_links?.other || ''}
                        onChange={(e) => handleSocialLinkChange('other', e.target.value)}
                        placeholder="https://..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeSection === 'contribution' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">贡献值信息（只读）</h2>

                  <div className="grid grid-cols-3 gap-6">
                    <div className="bg-indigo-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-2">总灵值</p>
                      <p className="text-2xl font-bold text-indigo-700">{formData.total_lingzhi || 0}</p>
                    </div>

                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-2">总贡献值</p>
                      <p className="text-2xl font-bold text-green-700">{formData.total_contribution || 0}</p>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-2">累计贡献值</p>
                      <p className="text-2xl font-bold text-purple-700">{formData.cumulative_contribution || 0}</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4 mt-4">
                    <p className="text-sm text-gray-600">
                      <Award className="w-4 h-4 inline mr-1" />
                      贡献值由系统自动计算，如需调整请联系管理员
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserProfileEdit
