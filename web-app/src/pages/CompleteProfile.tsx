import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import {
  User,
  Phone,
  Mail,
  CreditCard,
  MapPin,
  Building2,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface UserProfile {
  real_name: string
  phone: string
  email: string
  id_card: string
  bank_account: string
  bank_name: string
  address: string
}

const CompleteProfile = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [profile, setProfile] = useState<UserProfile>({
    real_name: '',
    phone: '',
    email: '',
    id_card: '',
    bank_account: '',
    bank_name: '',
    address: ''
  })

  useEffect(() => {
    // 如果用户不是微信登录或已完善信息，跳转到首页
    if (user?.login_type !== 'wechat') {
      navigate('/')
    }
  }, [user, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 验证必填字段
    if (!profile.real_name || !profile.phone) {
      setMessage({ type: 'error', text: '请填写真实姓名和手机号' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8001/api/user/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profile)
      })

      const data = await response.json()

      if (data.success) {
        setMessage({ type: 'success', text: '信息完善成功！正在跳转...' })
        // 更新用户信息
        setTimeout(() => {
          window.location.reload()
        }, 2000)
      } else {
        setMessage({ type: 'error', text: data.message || '提交失败，请重试' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误，请重试' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full mb-4">
            <User className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">完善个人信息</h1>
          <p className="mt-2 text-gray-600">
            为了保障您的账户安全和资金安全，请完善以下信息
          </p>
        </div>

        {/* 提示信息 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-semibold mb-1">为什么需要完善信息？</p>
              <p className="opacity-90">完善个人信息后，您将能够进行充值、消费、提现等操作。我们承诺严格保护您的个人信息安全。</p>
            </div>
          </div>
        </div>

        {/* 消息提示 */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center ${
            message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
            'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 mr-3 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
          <div className="space-y-6">
            {/* 真实姓名 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                真实姓名 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  required
                  value={profile.real_name}
                  onChange={(e) => setProfile({ ...profile, real_name: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入真实姓名"
                />
              </div>
            </div>

            {/* 手机号 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                手机号码 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  required
                  value={profile.phone}
                  onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入手机号码"
                  pattern="[0-9]{11}"
                />
              </div>
            </div>

            {/* 邮箱 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                邮箱地址
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入邮箱地址"
                />
              </div>
            </div>

            {/* 身份证号 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                身份证号
              </label>
              <div className="relative">
                <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={profile.id_card}
                  onChange={(e) => setProfile({ ...profile, id_card: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入身份证号（选填，用于提现验证）"
                />
              </div>
            </div>

            {/* 银行信息 */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">银行信息（提现用）</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    开户银行
                  </label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={profile.bank_name}
                      onChange={(e) => setProfile({ ...profile, bank_name: e.target.value })}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="如：工商银行"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    银行账号
                  </label>
                  <div className="relative">
                    <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={profile.bank_account}
                      onChange={(e) => setProfile({ ...profile, bank_account: e.target.value })}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="请输入银行账号"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* 地址 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                联系地址
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <textarea
                  value={profile.address}
                  onChange={(e) => setProfile({ ...profile, address: e.target.value })}
                  rows={3}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                  placeholder="请输入联系地址（选填）"
                />
              </div>
            </div>

            {/* 提交按钮 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary-600 to-secondary-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-primary-700 hover:to-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? '提交中...' : '提交信息'}
            </button>
          </div>
        </form>

        {/* 安全提示 */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>您的信息将严格保密，仅用于账户管理和资金安全验证</p>
        </div>
      </div>
    </div>
  )
}

export default CompleteProfile
