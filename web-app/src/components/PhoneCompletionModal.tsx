import { useState } from 'react'
import { Phone, CheckCircle } from 'lucide-react'

interface PhoneCompletionModalProps {
  isOpen: boolean
  onClose: () => void
  wechatInfo: {
    wechat_openid: string
    wechat_unionid?: string
    wechat_nickname: string
    wechat_avatar: string
  }
  onSuccess: (token: string, user: any) => void
  referrerId?: number
}

const PhoneCompletionModal: React.FC<PhoneCompletionModalProps> = ({
  isOpen,
  onClose,
  wechatInfo,
  onSuccess,
  referrerId
}) => {
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!phone) {
      setError('请输入手机号')
      return
    }

    // 简单的手机号验证
    const phoneRegex = /^1[3-9]\d{9}$/
    if (!phoneRegex.test(phone)) {
      setError('请输入正确的手机号')
      return
    }

    setLoading(true)

    try {
      // 调用微信注册接口
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/wechat/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          wechat_openid: wechatInfo.wechat_openid,
          wechat_unionid: wechatInfo.wechat_unionid,
          wechat_nickname: wechatInfo.wechat_nickname,
          wechat_avatar: wechatInfo.wechat_avatar,
          username: wechatInfo.wechat_nickname, // 使用微信昵称作为用户名
          phone: phone,
          email: '', // 可选
          password: '', // 微信登录不需要密码
          referrer_id: referrerId || null
        })
      })

      const result = await response.json()

      if (result.success) {
        onSuccess(result.data.token, result.data.user)
      } else {
        setError(result.message || '注册失败，请重试')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        {/* 头部 */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            微信授权成功
          </h2>
          <p className="text-gray-600">
            请补充手机号以完成注册
          </p>
        </div>

        {/* 微信信息卡片 */}
        <div className="flex items-center bg-gray-50 rounded-xl p-4 mb-6">
          <img
            src={wechatInfo.wechat_avatar}
            alt={wechatInfo.wechat_nickname}
            className="w-16 h-16 rounded-full object-cover mr-4"
          />
          <div>
            <div className="font-semibold text-gray-800">
              {wechatInfo.wechat_nickname}
            </div>
            <div className="text-sm text-gray-500">
              用户名：{wechatInfo.wechat_nickname}
            </div>
          </div>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              手机号
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="请输入手机号"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                maxLength={11}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 px-4 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition font-medium"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '注册中...' : '完成注册'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PhoneCompletionModal
