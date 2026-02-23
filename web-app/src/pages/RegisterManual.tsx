import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Lock, Phone, ArrowRight, CheckCircle, AlertCircle, Sparkles } from 'lucide-react'

// 科幻太空风格配置（与登录页一致）
const vrStyle = {
  bg: 'bg-gradient-to-br from-[#2a4559] via-[#3e8bb6]/40 to-[#2a4559]',
  cardBg: 'bg-[#2a4559]/60 backdrop-blur-xl',
  buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
  buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
  accent: 'text-[#3e8bb6]',
  glow: 'shadow-[0_0_30px_rgba(62,139,182,0.3)]',
}

// 手机号正则验证
const PHONE_REGEX = /^1[3-9]\d{9}$/

const RegisterManual = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    phone: '',
    password: '',
    passwordConfirm: '',
  })
  const [agreed, setAgreed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [referrerId, setReferrerId] = useState('')

  // 获取推荐人ID
  useEffect(() => {
    // 优先从 URL 参数获取
    const urlParams = new URLSearchParams(window.location.search)
    const urlReferrerId = urlParams.get('referrer_id')
    
    // 其次从 sessionStorage 获取
    const sessionReferrerId = sessionStorage.getItem('referrer_id')
    
    // 使用第一个找到的推荐人ID
    const finalReferrerId = urlReferrerId || sessionReferrerId || ''
    
    if (finalReferrerId) {
      setReferrerId(finalReferrerId)
      console.log('[RegisterManual] 获取到推荐人ID:', finalReferrerId)
    }
  }, [])

  // 验证输入
  const validateInputs = () => {
    if (!formData.username.trim()) {
      return '请输入用户名'
    }
    
    if (!formData.phone.trim()) {
      return '请输入手机号'
    }
    
    if (!PHONE_REGEX.test(formData.phone.trim())) {
      return '手机号格式不正确（请输入11位手机号）'
    }
    
    if (!formData.password.trim()) {
      return '请输入密码'
    }
    
    if (formData.password.length < 6) {
      return '密码长度至少为6位'
    }
    
    if (!formData.passwordConfirm.trim()) {
      return '请确认密码'
    }
    
    if (formData.password !== formData.passwordConfirm) {
      return '两次输入的密码不一致'
    }
    
    if (!agreed) {
      return '请阅读并同意用户协议和隐私政策'
    }
    
    return ''
  }

  // 提交注册
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    // 验证输入
    const validationError = validateInputs()
    if (validationError) {
      setError(validationError)
      setLoading(false)
      return
    }

    try {
      // 准备注册数据
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const registerUrl = `${apiBase}/register`
      
      const registerData: any = {
        username: formData.username.trim(),
        phone: formData.phone.trim(),
        password: formData.password,
        email: `${formData.phone.trim()}@temp.com`, // 临时邮箱
      }

      // 如果有推荐人ID，添加到注册数据中
      if (referrerId) {
        // 通过API查询推荐人的推荐码
        const userResponse = await fetch(`${apiBase}/admin/users/${referrerId}`)
        const userData = await userResponse.json()
        
        if (userData.success && userData.data) {
          registerData.referral_code = userData.data.referral_code
          console.log('[RegisterManual] 使用推荐人推荐码:', userData.data.referral_code)
        }
      }

      console.log('[RegisterManual] 提交注册数据:', registerData)
      console.log('[RegisterManual] 请求URL:', registerUrl)

      // 调用注册API
      const response = await fetch(registerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      })

      const result = await response.json()

      if (result.success) {
        setSuccess('注册成功！正在自动登录...')
        
        // 清除推荐人信息
        sessionStorage.removeItem('referrer_id')
        
        // 自动登录
        try {
          const loginResponse = await fetch(`${apiBase}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: formData.username.trim(),
              password: formData.password,
            }),
          })
          
          const loginResult = await loginResponse.json()
          
          if (loginResult.success) {
            // 保存登录信息
            localStorage.setItem('token', loginResult.data.token)
            localStorage.setItem('user', JSON.stringify(loginResult.data.user))
            localStorage.setItem('tokenCacheTime', Date.now().toString())
            
            // 跳转到首页
            setTimeout(() => {
              navigate('/dashboard')
            }, 1500)
          } else {
            // 登录失败，跳转到登录页
            setTimeout(() => {
              navigate('/login-full')
            }, 3000)
          }
        } catch (loginErr) {
          console.error('[RegisterManual] 自动登录失败:', loginErr)
          // 跳转到登录页
          setTimeout(() => {
            navigate('/login-full')
          }, 3000)
        }
      } else {
        setError(result.message || '注册失败，请稍后重试')
      }
    } catch (err: any) {
      console.error('[RegisterManual] 注册错误:', err)
      
      if (err.response?.data?.message) {
        setError(err.response.data.message)
      } else if (err.response?.status === 400) {
        setError('用户名或手机号已被使用')
      } else {
        setError('注册失败，请稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  // 自动清除提示
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center px-4 py-6 relative overflow-hidden ${vrStyle.bg}`}>
      {/* 科幻主题光晕装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#3e8bb6]/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#b5cbdb]/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#3e8bb6]/10 rounded-full blur-[200px]"></div>
      </div>

      {/* 注册卡片 */}
      <div className="w-full max-w-md relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center space-x-3 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-[#3e8bb6] blur-xl animate-pulse"></div>
              <Sparkles className="w-6 h-6 text-[#b5cbdb] relative z-10" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white whitespace-nowrap drop-shadow-lg">
            注册账号
          </h1>
          <p className="text-sm text-[#b5cbdb] mt-2 drop-shadow-md">
            填写信息·自动绑定推荐关系
          </p>
        </div>

        {/* 注册表单 */}
        <div className={`${vrStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/20 backdrop-blur-xl ${vrStyle.glow}`}>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* 用户名 */}
            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">用户名</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入用户名"
                  required
                />
              </div>
            </div>

            {/* 手机号 */}
            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">手机号</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Phone className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入11位手机号"
                  required
                />
              </div>
            </div>

            {/* 密码 */}
            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">密码</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm"
                  placeholder="请输入密码（至少6位）"
                  required
                />
              </div>
            </div>

            {/* 确认密码 */}
            <div>
              <label className="block text-sm font-medium text-[#3e8bb6] mb-2">确认密码</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-[#b5cbdb]" />
                </div>
                <input
                  type="password"
                  value={formData.passwordConfirm}
                  onChange={(e) => setFormData({ ...formData, passwordConfirm: e.target.value })}
                  className={`block w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all text-white placeholder-gray-400 backdrop-blur-sm ${
                    formData.passwordConfirm && formData.password !== formData.passwordConfirm
                      ? 'border-red-500/50'
                      : ''
                  }`}
                  placeholder="请再次输入密码"
                  required
                />
              </div>
              {formData.passwordConfirm && formData.password !== formData.passwordConfirm && (
                <p className="mt-1 text-xs text-red-400">两次输入的密码不一致</p>
              )}
            </div>

            {/* 同意条款 */}
            <div className="flex items-start space-x-3">
              <div className="flex items-center h-5">
                <input
                  id="agreement"
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="w-4 h-4 border border-white/30 rounded bg-white/5 text-[#3e8bb6] focus:ring-2 focus:ring-cyan-500 cursor-pointer"
                  required
                />
              </div>
              <div className="text-sm text-gray-300">
                <label htmlFor="agreement" className="cursor-pointer hover:text-white transition-colors">
                  我已阅读并同意
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); alert('用户协议内容\n\n1. 用户需遵守相关法律法规\n2. 禁止发布违法违规内容\n3. 保护个人信息安全\n4. 遵守社区规范\n\n点击确定表示您已阅读并同意本协议') }}
                    className="text-[#3e8bb6] hover:text-[#b5cbdb] ml-1 mr-1 transition-colors"
                  >
                    《用户协议》
                  </a>
                  和
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); alert('隐私政策内容\n\n1. 我们重视您的隐私\n2. 仅收集必要信息\n3. 不会泄露您的个人信息\n4. 严格遵守相关法律法规\n\n点击确定表示您已阅读并同意本政策') }}
                    className="text-[#3e8bb6] hover:text-[#b5cbdb] ml-1 transition-colors"
                  >
                    《隐私政策》
                  </a>
                </label>
              </div>
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg px-4 py-2 text-red-300 text-sm backdrop-blur-sm flex items-center">
                <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* 成功提示 */}
            {success && (
              <div className="bg-green-500/20 border border-green-500/50 rounded-lg px-4 py-2 text-green-300 text-sm backdrop-blur-sm flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>{success}</span>
              </div>
            )}

            {/* 提交按钮 */}
            <button
              type="submit"
              disabled={loading || !agreed}
              className={`w-full relative py-3 px-4 bg-gradient-to-r ${vrStyle.buttonBg} text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 overflow-hidden group ${
                loading || !agreed ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span className="ml-2">注册中...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <span className="text-sm">立即注册</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              )}
            </button>
          </form>

          {/* 底部导航 */}
          <div className="mt-6 pt-4 border-t border-white/10">
            <div className="flex justify-center text-sm">
              <span className="text-gray-400 mr-2">已有账号？</span>
              <button
                onClick={() => navigate('/login-full')}
                className="text-[#b5cbdb] hover:text-[#3e8bb6] font-medium transition-colors"
              >
                立即登录
              </button>
            </div>
          </div>

          {/* 推荐信息提示 */}
          {referrerId && (
            <div className="mt-4 text-center">
              <p className="text-xs text-gray-400">
                推荐人ID: {referrerId}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                注册后将自动绑定推荐关系
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RegisterManual
