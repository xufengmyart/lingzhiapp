import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Shield, Lock } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const AdminLogin = () => {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (data.success) {
        // 保存管理员token
        localStorage.setItem('token', data.data.token)
        localStorage.setItem('adminUser', JSON.stringify(data.data.admin))
        navigate('/admin')
      } else {
        setError(data.message || '登录失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo和标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-4 shadow-2xl">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">后台管理系统</h1>
          <p className="text-gray-400">灵值生态园智能体</p>
        </div>

        {/* 登录表单 */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 用户名 */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                管理员账号
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-500" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="请输入管理员账号"
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            {/* 密码 */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                密码
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-500" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="请输入密码"
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            {/* 忘记密码 */}
            <div className="text-right">
              <Link
                to="/admin/forgot-password"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                忘记密码？
              </Link>
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* 登录按钮 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          {/* 默认账号提示 */}
          <div className="mt-6 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
            <p className="text-gray-400 text-sm mb-2">默认管理员账号：</p>
            <p className="text-gray-300 text-sm">
              账号：<span className="text-blue-400 font-mono">admin</span>
            </p>
            <p className="text-gray-300 text-sm">
              密码：<span className="text-blue-400 font-mono">admin123</span>
            </p>
          </div>
        </div>

        {/* 版权信息 */}
        <p className="text-center text-gray-500 text-sm mt-8">
          © 2026 灵值生态园智能体
        </p>
      </div>
    </div>
  )
}

export default AdminLogin
