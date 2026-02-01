import { useState } from 'react'
import { ArrowLeft, Lock, Smartphone } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'

const ForgotPassword = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const fromAdmin = location.pathname.startsWith('/admin')

  const [step, setStep] = useState(1) // 1: 输入手机号, 2: 输入验证码, 3: 重置密码
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const apiPrefix = fromAdmin ? '/api/admin' : '/api'

  const sendCode = async () => {
    if (!phone) {
      setError('请输入手机号')
      return
    }
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      setError('请输入正确的手机号')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await fetch(`${apiPrefix}/send-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      })

      const data = await response.json()

      if (data.success) {
        setMessage('验证码已发送，请查收')
        setStep(2)
        startCountdown()
      } else {
        setError(data.message || '发送失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  const startCountdown = () => {
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
  }

  const verifyCode = async () => {
    if (!code) {
      setError('请输入验证码')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${apiPrefix}/verify-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code }),
      })

      const data = await response.json()

      if (data.success) {
        setStep(3)
        setMessage('')
      } else {
        setError(data.message || '验证码错误')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async () => {
    if (!newPassword) {
      setError('请输入新密码')
      return
    }
    if (newPassword.length < 6) {
      setError('密码长度至少6位')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${apiPrefix}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code, newPassword }),
      })

      const data = await response.json()

      if (data.success) {
        setMessage('密码重置成功')
        setTimeout(() => {
          navigate(fromAdmin ? '/admin/login' : '/login')
        }, 2000)
      } else {
        setError(data.message || '重置失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* 返回按钮 */}
        <button
          onClick={() => navigate(fromAdmin ? '/admin/login' : '/login')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回登录
        </button>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-4 shadow-lg">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">找回密码</h1>
          <p className="text-gray-600">通过手机号验证重置密码</p>
        </div>

        {/* 步骤1: 输入手机号 */}
        {step === 1 && (
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  手机号
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Smartphone className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="请输入手机号"
                    maxLength={11}
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">
                  {error}
                </div>
              )}

              {message && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-600 text-sm">
                  {message}
                </div>
              )}

              <button
                onClick={sendCode}
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? '发送中...' : '发送验证码'}
              </button>
            </div>
          </div>
        )}

        {/* 步骤2: 输入验证码 */}
        {step === 2 && (
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  验证码
                </label>
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-2xl tracking-widest"
                  placeholder="请输入6位验证码"
                  maxLength={6}
                />
              </div>

              <button
                onClick={sendCode}
                disabled={countdown > 0 || loading}
                className="w-full py-3 px-4 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {countdown > 0 ? `${countdown}秒后重新发送` : '重新发送验证码'}
              </button>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={verifyCode}
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? '验证中...' : '下一步'}
              </button>
            </div>
          </div>
        )}

        {/* 步骤3: 重置密码 */}
        {step === 3 && (
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  新密码
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入新密码（至少6位）"
                  minLength={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  确认新密码
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请再次输入新密码"
                  minLength={6}
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">
                  {error}
                </div>
              )}

              {message && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-600 text-sm">
                  {message}
                </div>
              )}

              <button
                onClick={resetPassword}
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? '重置中...' : '重置密码'}
              </button>
            </div>
          </div>
        )}

        {/* 提示 */}
        <p className="text-center text-gray-500 text-sm mt-6">
          验证码有效期为5分钟
        </p>
      </div>
    </div>
  )
}

export default ForgotPassword
