import { useState, useEffect } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Mail, ArrowRight, User, Sparkles, Heart, Star, RefreshCw, MessageCircle, CheckCircle, AlertCircle, Shield, Link as LinkIcon } from 'lucide-react'

// 科幻太空主题配置
const dreamStyles = {
  ecosystem: {
    bg: 'bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]',
    cardBg: 'bg-[#091422]/60 backdrop-blur-lg',
    buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
    accent: 'text-[#3e8bb6]',
    decorColors: ['bg-[#3e8bb6]', 'bg-[#b5cbdb]', 'bg-[#22d3ee]'],
  },
  aurora: {
    bg: 'bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]',
    cardBg: 'bg-[#091422]/60 backdrop-blur-lg',
    buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
    accent: 'text-[#3e8bb6]',
    decorColors: ['bg-[#3e8bb6]', 'bg-[#b5cbdb]', 'bg-[#22d3ee]'],
  },
  sakura: {
    bg: 'bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]',
    cardBg: 'bg-[#091422]/60 backdrop-blur-lg',
    buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
    accent: 'text-[#3e8bb6]',
    decorColors: ['bg-[#3e8bb6]', 'bg-[#b5cbdb]', 'bg-[#22d3ee]'],
  },
  ocean: {
    bg: 'bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]',
    cardBg: 'bg-[#091422]/60 backdrop-blur-lg',
    buttonBg: 'from-[#3e8bb6] via-[#b5cbdb] to-[#22d3ee]',
    buttonHover: 'from-[#b5cbdb] via-[#22d3ee] to-[#3e8bb6]',
    accent: 'text-[#3e8bb6]',
    decorColors: ['bg-[#3e8bb6]', 'bg-[#b5cbdb]', 'bg-[#22d3ee]'],
  },
}

const RegisterFull = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { register } = useAuth()
  const [styleKey, setStyleKey] = useState<keyof typeof dreamStyles>('ecosystem')
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    referrer: '',
    agreeTerms: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showStyleSwitcher, setShowStyleSwitcher] = useState(false)

  const currentStyle = dreamStyles[styleKey]

  // 从URL参数获取推荐人
  useEffect(() => {
    const referrer = searchParams.get('ref')
    if (referrer) {
      setFormData((prev) => ({ ...prev, referrer }))
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 验证输入
    if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim()) {
      setError('请填写所有必填项')
      setLoading(false)
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      setLoading(false)
      return
    }
    if (!formData.agreeTerms) {
      setError('请阅读并同意服务条款')
      setLoading(false)
      return
    }
    if (!formData.referrer.trim()) {
      setError('请填写推荐人用户名（关系锁定）')
      setLoading(false)
      return
    }

    try {
      await register(formData.username, formData.email, formData.password, formData.referrer)
      navigate('/')
    } catch (err: any) {
      console.error('注册错误:', err)
      
      // 根据错误类型显示不同的提示
      if (err.response?.status === 400) {
        setError(err.response?.data?.message || '注册信息有误，请检查后重试')
      } else if (err.response?.status === 409) {
        setError('用户名或邮箱已存在，请直接登录')
      } else if (err.response?.status === 429) {
        setError('注册过于频繁，请稍后再试')
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        setError('网络连接失败，请检查网络后重试')
      } else {
        setError(err.response?.data?.message || '注册失败，请稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden ${currentStyle.bg}`}>
      {/* 静态背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 ${currentStyle.decorColors[0]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-40 right-32 w-24 h-24 ${currentStyle.decorColors[1]} rounded-full blur-3xl opacity-30`}></div>
        <div className={`absolute top-1/2 left-10 w-40 h-40 ${currentStyle.decorColors[2]} rounded-full blur-3xl opacity-20`}></div>
        <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-white/30 backdrop-blur rounded-2xl rotate-12"></div>
        <div className="absolute bottom-32 right-1/4 w-20 h-20 bg-white/40 backdrop-blur rounded-3xl -rotate-6"></div>
        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 w-12 h-24 bg-white/20 backdrop-blur rounded-full"></div>
      </div>

      {/* 风格切换按钮 */}
      <button onClick={() => setShowStyleSwitcher(!showStyleSwitcher)} className="absolute top-4 right-4 z-50 p-2 bg-white/50 backdrop-blur rounded-full hover:bg-white/70 shadow-lg"><RefreshCw className="w-6 h-6 text-gray-700" /></button>

      {showStyleSwitcher && (
        <div className="absolute top-16 right-4 z-50 bg-white/90 backdrop-blur-lg rounded-2xl p-4 shadow-2xl border border-white/30">
          <div className="text-sm font-semibold text-gray-700 mb-3">选择梦幻风格</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(dreamStyles).map(([key, style]) => (
              <button key={key} onClick={() => { setStyleKey(key as keyof typeof dreamStyles); setShowStyleSwitcher(false); }} className={`p-2 rounded-lg border-2 ${styleKey === key ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300'}`}>
                <div className={`w-full h-8 rounded-md ${style.bg}`}></div>
                <div className="text-xs mt-1 text-gray-600">{key}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="w-full max-w-md relative z-10">
        {/* 头部 */}
        <div className="text-center mb-8">
          <div className="relative inline-block mb-4">
            <div className={`w-20 h-20 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl flex items-center justify-center mx-auto shadow-xl`}><User className="w-10 h-10 text-white" /></div>
            <div className={`absolute inset-0 bg-gradient-to-br ${currentStyle.buttonBg} rounded-2xl blur-xl opacity-50`}></div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-center space-x-2"><Sparkles className="w-5 h-5 text-amber-500" /><Heart className="w-5 h-5 text-emerald-500" /><Star className="w-5 h-5 text-teal-500" /></div>
            <div className="text-2xl font-bold text-gray-800">创建你的账户</div>
            <div className={`text-sm ${currentStyle.accent} font-medium`}>加入灵值生态园，开启智慧之旅</div>
          </div>
        </div>

        {/* 注册表单 */}
        <div className={`${currentStyle.cardBg} rounded-3xl shadow-2xl p-8 border border-white/50 backdrop-blur-xl`}>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-start space-x-2"><AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" /><span>{error}</span></div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
              <div className="relative"><User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="text" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="请输入用户名" required /></div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
              <div className="relative"><Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="请输入邮箱" required /></div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">密码</label>
              <div className="relative"><Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="请输入密码" required /></div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
              <div className="relative"><Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="password" value={formData.confirmPassword} onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })} className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="请再次输入密码" required /></div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">推荐人（必填）<span className="text-red-500">*</span></label>
              <div className="relative"><LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-500" /><input type="text" value={formData.referrer} onChange={(e) => setFormData({ ...formData, referrer: e.target.value })} className="w-full pl-10 pr-3 py-3 border border-emerald-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-emerald-50" placeholder="请填写推荐人用户名" required /></div>
              <p className="mt-1 text-xs text-gray-500">推荐人用于建立关系锁定，是进入生态系统的必要条件</p>
            </div>

            <div className="flex items-start space-x-2">
              <input type="checkbox" id="agreeTerms" checked={formData.agreeTerms} onChange={(e) => setFormData({ ...formData, agreeTerms: e.target.checked })} className="mt-1" />
              <label htmlFor="agreeTerms" className="text-sm text-gray-600">我已阅读并同意<a href="#" className={`font-medium ${currentStyle.accent} hover:underline`}>服务条款</a>和<a href="#" className={`font-medium ${currentStyle.accent} hover:underline`}>隐私政策</a></label>
            </div>

            <div className="space-y-3">
              <button type="submit" disabled={loading} className={`w-full py-3 px-4 bg-gradient-to-r ${currentStyle.buttonBg} text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center ${loading ? 'opacity-70' : ''}`}>{loading ? <RefreshCw className="w-5 h-5 animate-spin mr-2" /> : <CheckCircle className="w-5 h-5 mr-2" />}{loading ? '注册中...' : '立即注册'}</button>
              <button type="button" className="w-full py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 flex items-center justify-center"><MessageCircle className="w-5 h-5 mr-2" />微信注册</button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">已有账户？<Link to="/login-full" className={`font-semibold ${currentStyle.accent} hover:underline`}>立即登录</Link></div>
        </div>

        <div className="mt-6 text-center"><Link to="/dream-selector" className="text-sm text-gray-600 hover:text-gray-800">切换风格</Link></div>
      </div>
    </div>
  )
}

export default RegisterFull
