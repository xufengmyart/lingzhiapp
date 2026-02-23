import { useState } from 'react'
import { Lock, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react'
import { userApi } from '../services/api'

const ChangePassword = () => {
  const [formData, setFormData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState({
    old: false,
    new: false,
    confirm: false
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  const togglePasswordVisibility = (field: 'old' | 'new' | 'confirm') => {
    setShowPassword(prev => ({ ...prev, [field]: !prev[field] }))
  }

  const validateForm = (): boolean => {
    if (!formData.oldPassword) {
      setError('请输入当前密码')
      return false
    }
    if (!formData.newPassword) {
      setError('请输入新密码')
      return false
    }
    if (formData.newPassword.length < 6) {
      setError('新密码长度不能少于6位')
      return false
    }
    if (!formData.confirmPassword) {
      setError('请确认新密码')
      return false
    }
    if (formData.newPassword !== formData.confirmPassword) {
      setError('两次输入的新密码不一致')
      return false
    }
    if (formData.oldPassword === formData.newPassword) {
      setError('新密码不能与当前密码相同')
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    if (!validateForm()) {
      return
    }

    setLoading(true)
    try {
      const response = await userApi.changePassword({
        oldPassword: formData.oldPassword,
        newPassword: formData.newPassword
      })

      if (response.success) {
        setSuccess(true)
        setFormData({
          oldPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
        setTimeout(() => {
          setSuccess(false)
        }, 3000)
      } else {
        setError(response.message || '修改密码失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || '修改密码失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const getPasswordStrength = (password: string) => {
    if (!password) return 0
    let strength = 0
    if (password.length >= 8) strength++
    if (password.length >= 12) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++
    return strength
  }

  const strength = getPasswordStrength(formData.newPassword)
  const strengthText = ['很弱', '弱', '中等', '强', '很强'][strength]
  const strengthColor = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-green-600'][strength]

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">修改密码</h1>
        <p className="text-gray-600 mb-8">为了您的账户安全，请定期修改密码</p>

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            <div className="text-green-800">密码修改成功！下次登录请使用新密码。</div>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <div className="text-red-800">{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 当前密码 */}
          <div>
            <label htmlFor="oldPassword" className="block text-sm font-medium text-gray-700 mb-2">
              当前密码 <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                id="oldPassword"
                name="oldPassword"
                type={showPassword.old ? 'text' : 'password'}
                value={formData.oldPassword}
                onChange={handleInputChange}
                className="w-full px-4 py-3 pl-11 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入当前密码"
              />
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('old')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword.old ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* 新密码 */}
          <div>
            <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
              新密码 <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                id="newPassword"
                name="newPassword"
                type={showPassword.new ? 'text' : 'password'}
                value={formData.newPassword}
                onChange={handleInputChange}
                className="w-full px-4 py-3 pl-11 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入新密码（至少6位）"
              />
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('new')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {/* 密码强度指示器 */}
            {formData.newPassword && (
              <div className="mt-3">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${strengthColor}`}
                      style={{ width: `${(strength + 1) * 20}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600">{strengthText}</span>
                </div>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>密码长度：至少6位（推荐12位以上）</div>
                  <div>包含：大写字母、小写字母、数字、特殊符号</div>
                </div>
              </div>
            )}
          </div>

          {/* 确认密码 */}
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              确认新密码 <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                id="confirmPassword"
                name="confirmPassword"
                type={showPassword.confirm ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="w-full px-4 py-3 pl-11 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请再次输入新密码"
              />
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('confirm')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
              <p className="mt-2 text-sm text-red-600">两次输入的密码不一致</p>
            )}
          </div>

          {/* 提交按钮 */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setFormData({ oldPassword: '', newPassword: '', confirmPassword: '' })}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              重置
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '提交中...' : '确认修改'}
            </button>
          </div>
        </form>

        {/* 安全提示 */}
        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="font-medium text-yellow-800 mb-2">安全提示</h3>
          <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
            <li>不要使用过于简单的密码</li>
            <li>不要使用与其他网站相同的密码</li>
            <li>定期修改密码以保护账户安全</li>
            <li>如果忘记当前密码，请联系管理员重置</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ChangePassword
