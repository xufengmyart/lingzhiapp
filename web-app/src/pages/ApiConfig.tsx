import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Settings, Save, CheckCircle, AlertCircle } from 'lucide-react'

const ApiConfig = () => {
  const [apiUrl, setApiUrl] = useState('')
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    // 读取当前API配置
    const savedApiUrl = localStorage.getItem('apiBaseURL')
    if (savedApiUrl) {
      setApiUrl(savedApiUrl)
    } else {
      // 自动检测
      const currentOrigin = window.location.origin
      const url = new URL(currentOrigin)
      if (!currentOrigin.includes(':8001')) {
        setApiUrl(`${url.protocol}//${url.hostname}:8001`)
      } else {
        setApiUrl(currentOrigin)
      }
    }
  }, [])

  const handleTestConnection = async () => {
    setTesting(true)
    setTestResult(null)

    try {
      const response = await fetch(`${apiUrl}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        if (data.status === 'ok') {
          setTestResult({ success: true, message: '连接成功！API服务正常运行' })
        } else {
          setTestResult({ success: false, message: 'API响应异常' })
        }
      } else {
        setTestResult({ success: false, message: `连接失败: HTTP ${response.status}` })
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: `连接失败: ${error instanceof Error ? error.message : '未知错误'}`,
      })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = () => {
    if (!apiUrl) {
      alert('请输入API地址')
      return
    }

    // 保存到localStorage
    localStorage.setItem('apiBaseURL', apiUrl)

    alert('API配置已保存！页面即将刷新...')

    // 刷新页面应用新配置
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleGoBack = () => {
    navigate(-1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Settings className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">API配置</h1>
          <p className="text-gray-600">
            如果您遇到登录或API请求问题，可能需要配置正确的API地址
          </p>
        </div>

        <div className="space-y-6">
          {/* API地址输入 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API服务地址
            </label>
            <input
              type="url"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://your-server-ip:8001"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-2 text-sm text-gray-500">
              通常格式为: http://您的服务器IP:8001
            </p>
          </div>

          {/* 测试连接按钮 */}
          <button
            onClick={handleTestConnection}
            disabled={testing || !apiUrl}
            className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {testing ? (
              <>
                <div className="w-5 h-5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
                <span>测试连接...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                <span>测试连接</span>
              </>
            )}
          </button>

          {/* 测试结果 */}
          {testResult && (
            <div
              className={`p-4 rounded-lg flex items-start space-x-3 ${
                testResult.success
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {testResult.success ? (
                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}

          {/* 保存按钮 */}
          <button
            onClick={handleSave}
            disabled={!apiUrl}
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <Save className="w-5 h-5" />
            <span>保存配置并刷新</span>
          </button>

          {/* 其他操作 */}
          <div className="flex space-x-4">
            <button
              onClick={handleGoBack}
              className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              返回
            </button>
            <button
              onClick={handleLogout}
              className="flex-1 bg-red-100 text-red-700 py-3 rounded-lg font-semibold hover:bg-red-200 transition-colors"
            >
              退出登录
            </button>
          </div>
        </div>

        {/* 帮助信息 */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">常见API地址格式：</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 本地开发：http://localhost:8001 或 http://127.0.0.1:8001</li>
            <li>• 服务器部署：http://服务器公网IP:8001</li>
            <li>• 域名访问：http://your-domain.com 或 http://your-domain.com:8001</li>
          </ul>
        </div>

        <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
          <h3 className="font-semibold text-yellow-900 mb-2">如果您不知道API地址：</h3>
          <p className="text-sm text-yellow-800">
            请联系您的系统管理员，或查看服务器部署文档：docs/PUBLIC_DEPLOYMENT.md
          </p>
        </div>
      </div>
    </div>
  )
}

export default ApiConfig
