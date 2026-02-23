import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userApi } from '../services/api'
import { Mail, Phone, Calendar, Wallet, Target, Settings, LogOut, Lock, Key, Shield, Globe, MapPin, Upload, Camera, UserPlus } from 'lucide-react'

const Profile = () => {
  const { user, logout, updateUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [referrerInfo, setReferrerInfo] = useState<{ id: number; username: string; realName: string } | null>(null)
  const [loadingReferrer, setLoadingReferrer] = useState(false)
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
    realName: user?.realName || '',
    avatarUrl: user?.avatarUrl || '',
    title: user?.title || '',
    position: user?.position || '',
    gender: user?.gender || '',
    bio: user?.bio || '',
    location: user?.location || '',
    website: user?.website || '',
    referralCode: user?.referralCode || '',
    idCard: (user as any).idCard || '',
    bankAccount: (user as any).bankAccount || '',
    bankName: (user as any).bankName || '',
  })
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [passwordForm, setPasswordForm] = useState({
    newPassword: '',
    confirmPassword: '',
    verifyCode: '',
  })
  const [passwordError, setPasswordError] = useState('')
  const [sendingCode, setSendingCode] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)

  // 加载推荐人信息
  useEffect(() => {
    const fetchReferrerInfo = async () => {
      if (!user) return

      setLoadingReferrer(true)
      try {
        console.log('[Profile] 开始获取推荐人信息，用户ID:', user.id)
        const response = await userApi.getReferrer()
        console.log('[Profile] 推荐人信息响应:', response)
        if (response.success && response.data.referrer) {
          console.log('[Profile] 设置推荐人信息:', response.data.referrer)
          setReferrerInfo(response.data.referrer)
        } else {
          console.log('[Profile] 无推荐人信息')
          setReferrerInfo(null)
        }
      } catch (error) {
        console.error('[Profile] 获取推荐人信息失败:', error)
        setReferrerInfo(null)
      } finally {
        setLoadingReferrer(false)
      }
    }

    fetchReferrerInfo()
  }, [user])

  // 绑定推荐码
  const handleBindReferralCode = async (referralCode: string) => {
    if (!referralCode.trim()) {
      alert('请输入推荐码')
      return
    }

    try {
      const response = await userApi.applyReferralCode({
        user_id: user!.id,
        referral_code: referralCode.trim()
      })

      if (response.success) {
        alert(`推荐码绑定成功！获得 ${response.data.reward_lingzhi} 灵值奖励`)
        // 重新加载推荐人信息
        const referrerResponse = await userApi.getReferrer()
        if (referrerResponse.success && referrerResponse.data.referrer) {
          setReferrerInfo(referrerResponse.data.referrer)
        }
        // 更新用户灵值
        if (response.data.reward_lingzhi) {
          updateUser({ ...user!, total_lingzhi: (user!.total_lingzhi || 0) + response.data.reward_lingzhi })
        }
      } else {
        alert(response.message || '推荐码绑定失败')
      }
    } catch (error: any) {
      console.error('绑定推荐码失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '绑定失败，请重试'
      alert(errorMessage)
    }
  }

  // 处理头像上传
  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // 验证文件类型
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      alert('请上传 PNG、JPG、JPEG、GIF 或 WebP 格式的图片')
      return
    }

    // 验证文件大小 (5MB)
    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      alert('图片大小不能超过 5MB')
      return
    }

    setUploadingAvatar(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const token = localStorage.getItem('token')
      const response = await fetch(`/api/upload/avatar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.message || result.error || '上传失败')
      }

      // 更新头像URL
      setFormData(prev => ({ ...prev, avatarUrl: result.data.avatar_url }))

      // 立即保存头像更新
      try {
        const updateResponse = await userApi.updateProfile({
          avatarUrl: result.data.avatar_url,
        })

        if (updateResponse.success && updateResponse.data) {
          updateUser(updateResponse.data)
          alert('头像上传成功')
        } else {
          console.error('updateProfile 响应:', updateResponse)
          alert(`头像URL已更新，但保存到个人资料失败: ${JSON.stringify(updateResponse)}`)
        }
      } catch (updateError: any) {
        console.error('保存头像URL失败:', updateError)
        const errorMsg = updateError.response?.data?.error || updateError.response?.data?.message || updateError.message
        alert(`保存头像URL失败: ${errorMsg}`)
      }
    } catch (error: any) {
      console.error('上传头像失败:', error)
      alert(error.message || '上传失败，请重试')
    } finally {
      setUploadingAvatar(false)
      // 清空 input 以允许重新选择同一文件
      e.target.value = ''
    }
  }

  const handleSave = async () => {
    try {
      const response = await userApi.updateProfile({
        username: formData.username,
        email: formData.email,
        phone: formData.phone,
        realName: formData.realName,
        avatarUrl: formData.avatarUrl,
        title: formData.title,
        position: formData.position,
        gender: formData.gender,
        bio: formData.bio,
        location: formData.location,
        website: formData.website,
        idCard: formData.idCard,
        bankAccount: formData.bankAccount,
        bankName: formData.bankName,
      })

      if (response.success && response.data) {
        // 使用后端返回的完整用户数据更新 AuthContext
        updateUser(response.data)
        setIsEditing(false)
        alert('个人信息已更新')
      } else {
        alert('更新失败')
      }
    } catch (error: any) {
      console.error('更新用户信息失败:', error)
      const errorMessage = error?.response?.data?.message || error?.message || '更新失败，请重试'
      alert(errorMessage)
    }
  }

  // 发送验证码
  const handleSendVerifyCode = async () => {
    if (!formData.phone) {
      setPasswordError('请先设置手机号')
      return
    }

    setSendingCode(true)
    setPasswordError('')

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/send-verify-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          phone: formData.phone
        })
      })

      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.message || result.error || '发送验证码失败')
      }

      // 开始倒计时
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer)
            return 0
          }
          return prev - 1
        })
      }, 1000)

      alert('验证码已发送到您的手机')
    } catch (error: any) {
      console.error('发送验证码失败:', error)
      setPasswordError(error.message || '发送验证码失败，请重试')
    } finally {
      setSendingCode(false)
    }
  }

  const handlePasswordChange = async () => {
    setPasswordError('')

    // 验证输入
    if (!formData.phone) {
      setPasswordError('请先设置手机号')
      return
    }
    if (!passwordForm.verifyCode) {
      setPasswordError('请输入验证码')
      return
    }
    if (!passwordForm.newPassword) {
      setPasswordError('请输入新密码')
      return
    }
    if (passwordForm.newPassword.length < 6) {
      setPasswordError('新密码长度不能少于6位')
      return
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordError('两次输入的新密码不一致')
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('请先登录')
        return
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${user?.id}/password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          phone: formData.phone,
          verify_code: passwordForm.verifyCode,
          new_password: passwordForm.newPassword
        })
      })

      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.message || result.error || '密码修改失败')
      }

      alert('密码修改成功，请重新登录')
      // 重置表单
      setPasswordForm({
        newPassword: '',
        confirmPassword: '',
        verifyCode: '',
      })
      setCountdown(0)
      setShowPasswordModal(false)
      // 退出登录
      logout()
    } catch (error: any) {
      console.error('密码修改失败:', error)
      setPasswordError(error.message || '密码修改失败，请重试')
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">个人中心</h1>
        <p className="text-gray-600 mt-2">管理您的个人信息和账户设置</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧个人信息卡片 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 基本信息 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">基本信息</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors"
                >
                  编辑
                </button>
              )}
            </div>

            <div className="flex items-start space-x-6 mb-6">
              <div className="relative group cursor-pointer" onClick={() => document.getElementById('avatar-upload-large')?.click()}>
                <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full overflow-hidden flex items-center justify-center">
                  {formData.avatarUrl || user?.avatarUrl ? (
                    <img
                      src={formData.avatarUrl || user?.avatarUrl}
                      alt="头像"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-white text-3xl font-bold">
                      {user?.username ? user.username.charAt(0).toUpperCase() : "?"}
                    </div>
                  )}
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="w-6 h-6 text-white" />
                </div>
                <input
                  id="avatar-upload-large"
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                  onChange={handleAvatarUpload}
                  disabled={uploadingAvatar}
                  className="hidden"
                />
              </div>
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                      <input
                        type="text"
                        value={formData.username}
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <h3 className="text-2xl font-bold">{user?.username}</h3>
                    <p className="text-gray-600 mt-1">{user?.currentStage || '探索者'}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Mail className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">邮箱</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.email || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Phone className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">手机号</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.phone || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Mail className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">真实姓名</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="text"
                      value={formData.realName}
                      onChange={(e) => setFormData({ ...formData, realName: e.target.value })}
                      placeholder="请输入真实姓名"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.realName || '未设置'}</div>
                </div>
              </div>

              {/* 头像上传 */}
              <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <div className="flex items-center space-x-3 w-full">
                  <div className="w-16 h-16 bg-gray-200 rounded-full overflow-hidden flex-shrink-0">
                    {formData.avatarUrl || user?.avatarUrl ? (
                      <img
                        src={formData.avatarUrl || user?.avatarUrl}
                        alt="头像"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <Camera className="w-8 h-8" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-gray-500 mb-2">用户头像</div>
                    <div className="flex items-center space-x-2">
                      <label className="relative cursor-pointer bg-white border border-gray-300 rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-2">
                        <Upload className="w-4 h-4" />
                        <span>{uploadingAvatar ? '上传中...' : '上传头像'}</span>
                        <input
                          type="file"
                          accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                          onChange={handleAvatarUpload}
                          disabled={uploadingAvatar}
                          className="hidden"
                        />
                      </label>
                      <span className="text-xs text-gray-400">支持 PNG、JPG、JPEG、GIF、WebP (最大5MB)</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">注册时间</div>
                  <div className="font-semibold">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">更新时间</div>
                  <div className="font-semibold">
                    {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : '-'}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">头衔</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="请输入头衔"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.title || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">职位</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="text"
                      value={formData.position}
                      onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                      placeholder="请输入职位"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.position || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Globe className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">性别</div>
                  <div className="font-semibold">{isEditing ? (
                    <select
                      value={formData.gender}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    >
                      <option value="">请选择</option>
                      <option value="男">男</option>
                      <option value="女">女</option>
                    </select>
                  ) : user?.gender || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <MapPin className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">所在地</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      placeholder="请输入所在地"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.location || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Globe className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">个人网站</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="url"
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                      placeholder="请输入个人网站URL"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : (
                    user?.website ? (
                      <a href={user.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {user.website}
                      </a>
                    ) : '未设置'
                  )}</div>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Mail className="w-5 h-5 text-gray-500 mt-1" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">个人简介</div>
                  <div className="font-semibold">{isEditing ? (
                    <textarea
                      value={formData.bio}
                      onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                      placeholder="请输入个人简介（最多500字）"
                      maxLength={500}
                      rows={3}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : (
                    <div className="text-sm text-gray-700">{user?.bio || '未设置'}</div>
                  )}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">我的推荐码</div>
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{user?.referral_code || '未设置'}</div>
                    <Link
                      to="/referral"
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                    >
                      查看二维码 →
                    </Link>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <UserPlus className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">我的推荐人</div>
                  <div className="font-semibold">
                    {loadingReferrer ? (
                      <span className="text-gray-400">加载中...</span>
                    ) : referrerInfo ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-primary-600 font-medium">
                          {referrerInfo.realName || referrerInfo.username}
                        </span>
                        <span className="text-xs text-gray-400">(ID: {referrerInfo.id})</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-400">无推荐人</span>
                        <button
                          onClick={() => {
                            const code = prompt('请输入推荐码：')
                            if (code) handleBindReferralCode(code)
                          }}
                          className="text-xs text-primary-600 hover:text-primary-700 underline"
                        >
                          绑定推荐码
                        </button>
                      </div>
                    )}
                  </div>
                  {/* 调试信息 */}
                  {process.env.NODE_ENV === 'development' && (
                    <div className="text-xs text-gray-300 mt-1">
                      Debug: loading={loadingReferrer ? 'true' : 'false'}, referrer={referrerInfo ? JSON.stringify(referrerInfo) : 'null'}
                    </div>
                  )}
                </div>
              </div>

              {/* 身份证号 */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Shield className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">身份证号</div>
                  <div className="font-semibold">
                    {isEditing ? (
                      <input
                        type="text"
                        value={formData.id_card || ''}
                        onChange={(e) => setFormData({ ...formData, id_card: e.target.value })}
                        placeholder="请输入身份证号（选填，用于提现验证）"
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    ) : (
                      <span className="text-sm">
                        {formData.id_card
                          ? formData.id_card.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
                          : '未设置'}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* 银行信息 */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Wallet className="w-5 h-5 text-gray-500" />
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs text-gray-500">开户银行</div>
                    <div className="font-semibold">
                      {isEditing ? (
                        <input
                          type="text"
                          value={formData.bank_name || ''}
                          onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                          placeholder="请输入开户银行"
                          className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        />
                      ) : (formData.bank_name || '未设置')}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">银行账号</div>
                    <div className="font-semibold">
                      {isEditing ? (
                        <input
                          type="text"
                          value={formData.bank_account || ''}
                          onChange={(e) => setFormData({ ...formData, bank_account: e.target.value })}
                          placeholder="请输入银行账号"
                          className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        />
                      ) : (
                        formData.bank_account
                          ? formData.bank_account.replace(/(\d{4})\d+(\d{4})/, '$1 **** **** $2')
                          : '未设置'
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">注册时间</div>
                  <div className="font-semibold">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">更新时间</div>
                  <div className="font-semibold">
                    {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : '-'}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">参与级别</div>
                  <div className="font-semibold">{user?.participationLevel || '未选择'}</div>
                </div>
              </div>
            </div>

            {isEditing && (
              <div className="mt-6 flex space-x-3">
                <button
                  onClick={handleSave}
                  className="flex-1 bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-2 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all"
                >
                  保存
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  取消
                </button>
              </div>
            )}
          </div>

          {/* 账户设置 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center space-x-2">
              <Settings className="w-6 h-6" />
              <span>账户设置</span>
            </h2>

            <div className="space-y-4">
              <button className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">修改邮箱</div>
                    <div className="text-sm text-gray-500">更改您的邮箱地址</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <Link to="/security" className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Shield className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">安全设置</div>
                    <div className="text-sm text-gray-500">管理设备和登录安全</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </Link>

              <button
                onClick={() => setShowPasswordModal(true)}
                className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <Lock className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">修改密码</div>
                    <div className="text-sm text-gray-500">更新您的登录密码</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button
                onClick={logout}
                className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-red-50 transition-colors border-red-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <LogOut className="w-5 h-5 text-red-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold text-red-600">退出登录</div>
                    <div className="text-sm text-red-500">安全退出您的账户</div>
                  </div>
                </div>
                <span className="text-red-400">→</span>
              </button>
            </div>
          </div>
        </div>

        {/* 右侧统计卡片 */}
        <div className="space-y-6">
          {/* 灵值统计 */}
          <div className="bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl p-6 text-white">
            <div className="flex items-center space-x-3 mb-4">
              <Wallet className="w-8 h-8" />
              <div>
                <div className="text-sm opacity-80">总灵值</div>
                <div className="text-3xl font-bold">{user?.total_lingzhi}</div>
              </div>
            </div>
            <div className="text-sm opacity-80">
              等值：{(user?.total_lingzhi! * 0.1).toFixed(1)} 元
            </div>
          </div>

          {/* 里程碑进度 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold mb-4 flex items-center space-x-2">
              <Target className="w-5 h-5 text-primary-600" />
              <span>里程碑进度</span>
            </h3>

            <div className="space-y-4">
              {[
                { name: '初次收获', target: 10 },
                { name: '积累达人', target: 100 },
                { name: '灵值先锋', target: 500 },
                { name: '价值创造者', target: 1000 },
              ].map((milestone, idx) => {
                const completed = user!.total_lingzhi >= milestone.target
                return (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {completed ? (
                        <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs">✓</span>
                        </div>
                      ) : (
                        <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                      )}
                      <span className={`text-sm ${completed ? 'text-gray-900' : 'text-gray-500'}`}>
                        {milestone.name}
                      </span>
                    </div>
                    <span className="text-sm font-semibold">{milestone.target}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 快捷操作 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold mb-4">快捷操作</h3>
            <div className="space-y-2">
              <Link
                to="/recharge"
                className="w-full text-left p-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all flex items-center justify-between"
              >
                <span>购买灵值</span>
                <Wallet className="w-5 h-5" />
              </Link>
              <button className="w-full text-left p-3 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors">
                查看收入预测
              </button>
              <button className="w-full text-left p-3 bg-secondary-50 text-secondary-700 rounded-lg hover:bg-secondary-100 transition-colors">
                查看里程碑
              </button>
              <Link
                to="/partner"
                className="w-full text-left p-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors flex items-center justify-between"
              >
                <span>申请成为合伙人</span>
                <Target className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 密码修改弹窗 */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4">修改密码</h2>

            {passwordError && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {passwordError}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                <input
                  type="text"
                  value={formData.phone}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                />
                <p className="text-xs text-gray-500 mt-1">验证码将发送到此手机号</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">验证码</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={passwordForm.verifyCode}
                    onChange={(e) => setPasswordForm({ ...passwordForm, verifyCode: e.target.value })}
                    placeholder="请输入验证码"
                    maxLength={6}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleSendVerifyCode}
                    disabled={sendingCode || countdown > 0}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      countdown > 0
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-primary-500 text-white hover:bg-primary-600'
                    }`}
                  >
                    {countdown > 0 ? `${countdown}秒` : sendingCode ? '发送中...' : '发送验证码'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">新密码</label>
                <input
                  type="password"
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                  placeholder="请输入新密码（至少6位）"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
                <input
                  type="password"
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                  placeholder="请再次输入新密码"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowPasswordModal(false)
                    setPasswordError('')
                    setPasswordForm({
                      newPassword: '',
                      confirmPassword: '',
                      verifyCode: '',
                    })
                    setCountdown(0)
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handlePasswordChange}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all"
                >
                  确认修改
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Profile
