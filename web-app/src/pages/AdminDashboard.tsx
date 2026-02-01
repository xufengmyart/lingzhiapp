import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Code,
  Rocket,
  Activity,
  Settings,
  LogOut,
  Menu,
  X,
  RefreshCw,
  Download,
  Upload,
  Terminal,
  Monitor,
  Zap
} from 'lucide-react'

interface DeployStatus {
  status: 'idle' | 'running' | 'success' | 'error'
  lastDeploy: string
  message: string
}

interface SystemStats {
  cpu: number
  memory: number
  disk: number
  uptime: string
}

const AdminDashboard = () => {
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [deployStatus, setDeployStatus] = useState<DeployStatus>({
    status: 'idle',
    lastDeploy: '-',
    message: ''
  })
  const [systemStats, setSystemStats] = useState<SystemStats>({
    cpu: 0,
    memory: 0,
    disk: 0,
    uptime: '-'
  })
  const [logs, setLogs] = useState<string[]>([])
  const [autoDeployEnabled, setAutoDeployEnabled] = useState(false)

  // 检查管理员登录状态
  useEffect(() => {
    const adminToken = localStorage.getItem('adminToken')
    if (!adminToken) {
      navigate('/admin/login')
    }
  }, [navigate])

  // 加载系统状态
  useEffect(() => {
    loadSystemStats()
    loadLogs()
    const interval = setInterval(loadSystemStats, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadSystemStats = async () => {
    // 模拟系统状态
    setSystemStats({
      cpu: Math.random() * 30 + 10,
      memory: Math.random() * 20 + 40,
      disk: 75,
      uptime: '15天 8小时 32分钟'
    })
  }

  const loadLogs = async () => {
    // 模拟日志
    const mockLogs = [
      '[2024-02-01 14:30:00] [INFO] 系统启动',
      '[2024-02-01 14:30:05] [INFO] 监控代码变化...',
      '[2024-02-01 14:30:10] [SUCCESS] 检测到文件变化',
      '[2024-02-01 14:30:12] [INFO] 自动提交代码',
      '[2024-02-01 14:30:15] [SUCCESS] 已推送到 GitHub',
      '[2024-02-01 14:30:20] [INFO] 同步到服务器',
      '[2024-02-01 14:30:25] [SUCCESS] 部署完成',
    ]
    setLogs(mockLogs)
  }

  const handleLogout = () => {
    localStorage.removeItem('adminToken')
    localStorage.removeItem('adminUser')
    navigate('/admin/login')
  }

  const handleQuickDeploy = async () => {
    setDeployStatus({
      status: 'running',
      lastDeploy: new Date().toLocaleString(),
      message: '正在部署...'
    })

    // 模拟部署过程
    await new Promise(resolve => setTimeout(resolve, 3000))

    setDeployStatus({
      status: 'success',
      lastDeploy: new Date().toLocaleString(),
      message: '部署成功！'
    })

    // 3秒后重置
    setTimeout(() => {
      setDeployStatus({
        status: 'idle',
        lastDeploy: new Date().toLocaleString(),
        message: ''
      })
    }, 3000)
  }

  const handleFullDeploy = async () => {
    setDeployStatus({
      status: 'running',
      lastDeploy: new Date().toLocaleString(),
      message: '正在完整部署...'
    })

    // 模拟部署过程
    await new Promise(resolve => setTimeout(resolve, 5000))

    setDeployStatus({
      status: 'success',
      lastDeploy: new Date().toLocaleString(),
      message: '完整部署成功！'
    })

    setTimeout(() => {
      setDeployStatus({
        status: 'idle',
        lastDeploy: new Date().toLocaleString(),
        message: ''
      })
    }, 3000)
  }

  const toggleAutoDeploy = async () => {
    setAutoDeployEnabled(!autoDeployEnabled)
    // 这里应该调用实际的 API
  }

  const sidebarItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: '仪表盘' },
    { id: 'agents', icon: Zap, label: '智能体管理', path: '/admin/agents' },
    { id: 'knowledge', icon: Monitor, label: '知识库管理', path: '/admin/knowledge' },
    { id: 'code', icon: Code, label: '代码编辑' },
    { id: 'deploy', icon: Rocket, label: '部署管理' },
    { id: 'logs', icon: Terminal, label: '日志查看' },
    { id: 'monitor', icon: Monitor, label: '系统监控' },
    { id: 'settings', icon: Settings, label: '系统设置' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200 fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              <div className="ml-4">
                <h1 className="text-xl font-bold text-gray-900">智能体后台管理系统</h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">欢迎，</span>
                <span className="font-semibold text-gray-900">管理员</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="pt-16 flex">
        {/* 侧边栏 */}
        {sidebarOpen && (
          <aside className="w-64 bg-white shadow-sm border-r border-gray-200 fixed h-full overflow-y-auto">
            <nav className="p-4 space-y-2">
              {sidebarItems.map((item) => {
                const Icon = item.icon
                const handleClick = () => {
                  if (item.path) {
                    navigate(item.path)
                  } else {
                    setActiveTab(item.id)
                  }
                }
                return (
                  <button
                    key={item.id}
                    onClick={handleClick}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === item.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </nav>
          </aside>
        )}

        {/* 主内容区域 */}
        <main className={`flex-1 p-6 ${sidebarOpen ? 'ml-64' : ''}`}>
          {activeTab === 'dashboard' && (
            <DashboardContent
              deployStatus={deployStatus}
              systemStats={systemStats}
              onQuickDeploy={handleQuickDeploy}
              onFullDeploy={handleFullDeploy}
              autoDeployEnabled={autoDeployEnabled}
              onToggleAutoDeploy={toggleAutoDeploy}
            />
          )}

          {activeTab === 'code' && (
            <CodeEditor />
          )}

          {activeTab === 'deploy' && (
            <DeployManagement
              deployStatus={deployStatus}
              onQuickDeploy={handleQuickDeploy}
              onFullDeploy={handleFullDeploy}
            />
          )}

          {activeTab === 'logs' && (
            <LogsViewer logs={logs} onLoadLogs={loadLogs} />
          )}

          {activeTab === 'monitor' && (
            <SystemMonitor systemStats={systemStats} />
          )}

          {activeTab === 'settings' && (
            <SystemSettings
              autoDeployEnabled={autoDeployEnabled}
              onToggleAutoDeploy={toggleAutoDeploy}
            />
          )}
        </main>
      </div>
    </div>
  )
}

// 仪表盘内容组件
const DashboardContent = ({
  deployStatus,
  systemStats,
  onQuickDeploy,
  onFullDeploy,
  autoDeployEnabled,
  onToggleAutoDeploy
}: any) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">仪表盘</h2>
      <p className="text-gray-600">快速查看系统状态和执行常用操作</p>
    </div>

    {/* 系统状态卡片 */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <Activity className="w-8 h-8 text-blue-500" />
          <span className="text-sm text-gray-500">CPU</span>
        </div>
        <div className="text-2xl font-bold text-gray-900">{systemStats.cpu.toFixed(1)}%</div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <Monitor className="w-8 h-8 text-green-500" />
          <span className="text-sm text-gray-500">内存</span>
        </div>
        <div className="text-2xl font-bold text-gray-900">{systemStats.memory.toFixed(1)}%</div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <Download className="w-8 h-8 text-purple-500" />
          <span className="text-sm text-gray-500">磁盘</span>
        </div>
        <div className="text-2xl font-bold text-gray-900">{systemStats.disk}%</div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <Zap className="w-8 h-8 text-yellow-500" />
          <span className="text-sm text-gray-500">运行时间</span>
        </div>
        <div className="text-lg font-bold text-gray-900">{systemStats.uptime}</div>
      </div>
    </div>

    {/* 部署控制 */}
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">部署控制</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <button
          onClick={onQuickDeploy}
          disabled={deployStatus.status === 'running'}
          className="flex items-center justify-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Rocket className="w-5 h-5" />
          <span>快速部署</span>
        </button>

        <button
          onClick={onFullDeploy}
          disabled={deployStatus.status === 'running'}
          className="flex items-center justify-center space-x-2 bg-secondary-600 text-white px-6 py-3 rounded-lg hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Upload className="w-5 h-5" />
          <span>完整部署</span>
        </button>
      </div>

      {/* 部署状态 */}
      {deployStatus.status !== 'idle' && (
        <div className={`p-4 rounded-lg ${
          deployStatus.status === 'success' ? 'bg-green-50 text-green-800' :
          deployStatus.status === 'error' ? 'bg-red-50 text-red-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          <div className="flex items-center space-x-2">
            {deployStatus.status === 'running' && <RefreshCw className="w-5 h-5 animate-spin" />}
            <span>{deployStatus.message}</span>
          </div>
        </div>
      )}

      {/* 自动部署开关 */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-gray-900">自动部署</h4>
            <p className="text-sm text-gray-600">检测到代码变化后自动部署</p>
          </div>
          <button
            onClick={onToggleAutoDeploy}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              autoDeployEnabled ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                autoDeployEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  </div>
)

// 代码编辑器组件
const CodeEditor = () => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">代码编辑</h2>
      <p className="text-gray-600">编辑和管理项目代码</p>
    </div>

    <div className="bg-gray-900 rounded-xl p-4 min-h-[600px]">
      <div className="text-gray-400">
        <pre>
{`// 欢迎使用代码编辑器
// 您可以在这里编辑项目代码
// 保存后会自动触发部署

// 示例：修改智能体配置
const agentConfig = {
  name: "灵值生态园智能体",
  version: "v7.3",
  features: [
    "用户旅程管理",
    "经济模型计算",
    "智能对话",
    "合伙人管理"
  ]
}

// 保存文件后，系统会自动检测变化并部署
`}
        </pre>
      </div>
    </div>
  </div>
)

// 部署管理组件
const DeployManagement = ({ deployStatus, onQuickDeploy, onFullDeploy }: any) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">部署管理</h2>
      <p className="text-gray-600">管理和监控系统部署</p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">快速部署</h3>
        <p className="text-gray-600 mb-4">快速部署更改（不备份）</p>
        <button
          onClick={onQuickDeploy}
          disabled={deployStatus.status === 'running'}
          className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Rocket className="w-5 h-5 inline mr-2" />
          立即部署
        </button>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">完整部署</h3>
        <p className="text-gray-600 mb-4">完整部署（包含备份）</p>
        <button
          onClick={onFullDeploy}
          disabled={deployStatus.status === 'running'}
          className="w-full bg-secondary-600 text-white px-6 py-3 rounded-lg hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Upload className="w-5 h-5 inline mr-2" />
          完整部署
        </button>
      </div>
    </div>
  </div>
)

// 日志查看器组件
const LogsViewer = ({ logs, onLoadLogs }: any) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">日志查看</h2>
        <p className="text-gray-600">查看系统运行日志</p>
      </div>
      <button
        onClick={onLoadLogs}
        className="flex items-center space-x-2 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
      >
        <RefreshCw className="w-4 h-4" />
        <span>刷新</span>
      </button>
    </div>

    <div className="bg-gray-900 rounded-xl p-4 min-h-[500px] overflow-y-auto">
      <pre className="text-gray-400 text-sm font-mono">
        {logs.map((log: string, index: number) => (
          <div key={index} className="mb-1">{log}</div>
        ))}
      </pre>
    </div>
  </div>
)

// 系统监控组件
const SystemMonitor = ({ systemStats }: any) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">系统监控</h2>
      <p className="text-gray-600">实时监控系统资源使用情况</p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">CPU 使用率</h3>
        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                {systemStats.cpu.toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
            <div style={{ width: `${systemStats.cpu}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600"></div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">内存使用率</h3>
        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-600 bg-green-200">
                {systemStats.memory.toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-green-200">
            <div style={{ width: `${systemStats.memory}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-600"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
)

// 系统设置组件
const SystemSettings = ({ autoDeployEnabled, onToggleAutoDeploy }: any) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">系统设置</h2>
      <p className="text-gray-600">配置系统参数</p>
    </div>

    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">自动部署</h3>
            <p className="text-sm text-gray-600">启用后，系统会自动检测代码变化并部署</p>
          </div>
          <button
            onClick={onToggleAutoDeploy}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              autoDeployEnabled ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                autoDeployEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        <div className="pt-6 border-t border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-2">部署冷却时间</h3>
          <p className="text-sm text-gray-600 mb-2">防止频繁部署，单位：秒</p>
          <input
            type="number"
            defaultValue={300}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="pt-6 border-t border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-2">监控间隔</h3>
          <p className="text-sm text-gray-600 mb-2">代码变化检测间隔，单位：秒</p>
          <input
            type="number"
            defaultValue={30}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
    </div>
  </div>
)

export default AdminDashboard
