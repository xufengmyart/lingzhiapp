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
  Terminal,
  Monitor,
  Zap,
  Users,
  Shield,
  ChevronRight,
  Award
} from 'lucide-react'

interface Module {
  id: string
  name: string
  description: string
  icon: any
  path: string
  status: 'active' | 'coming-soon'
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
  const [systemStats, setSystemStats] = useState<SystemStats>({
    cpu: 0,
    memory: 0,
    disk: 0,
    uptime: '-'
  })
  const [logs, setLogs] = useState<string[]>([])

  // 检查管理员登录状态
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/admin/login')
    }
  }, [navigate])

  // 加载系统状态
  useEffect(() => {
    if (activeTab === 'monitor' || activeTab === 'logs') {
      loadSystemStats()
      loadLogs()
      const interval = setInterval(() => {
        loadSystemStats()
        loadLogs()
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [activeTab])

  const loadSystemStats = () => {
    setSystemStats({
      cpu: Math.round(Math.random() * 30 + 10),
      memory: Math.round(Math.random() * 20 + 40),
      disk: 75,
      uptime: '15天 8小时 32分钟'
    })
  }

  const loadLogs = () => {
    const mockLogs = [
      `[${new Date().toISOString()}] [INFO] 系统运行正常`,
      `[${new Date(Date.now() - 60000).toISOString()}] [INFO] 监控代码变化...`,
      `[${new Date(Date.now() - 120000).toISOString()}] [SUCCESS] 系统检查完成`,
      `[${new Date(Date.now() - 180000).toISOString()}] [INFO] 数据同步正常`,
      `[${new Date(Date.now() - 240000).toISOString()}] [INFO] 用户访问统计更新`,
    ]
    setLogs(mockLogs)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('adminUser')
    navigate('/admin/login')
  }

  // 功能模块定义
  const modules: Module[] = [
    // 用户管理
    { id: 'users', name: '用户管理', description: '管理所有用户账户、角色和权限', icon: Users, path: '/admin/users', status: 'active' },
    { id: 'roles', name: '角色管理', description: '管理系统角色和权限', icon: Shield, path: '/admin/roles', status: 'active' },
    { id: 'user-types', name: '用户类型', description: '管理用户类型和分类', icon: Users, path: '/admin/user-types', status: 'active' },
    
    // AI智能
    { id: 'agents', name: '智能体管理', description: '管理AI智能体和对话配置', icon: Zap, path: '/admin/agents', status: 'active' },
    { id: 'knowledge', name: '知识库管理', description: '管理知识库和文档', icon: Monitor, path: '/admin/knowledge', status: 'active' },
    
    // 资源管理
    { id: 'resources', name: '资源管理', description: '管理用户资源和私有资源', icon: Activity, path: '/admin/resources', status: 'active' },
    { id: 'projects', name: '项目管理', description: '管理项目和推荐', icon: Rocket, path: '/admin/projects', status: 'active' },
    
    // 商家管理
    { id: 'merchants', name: '商家管理', description: '管理商家账户和工作台', icon: Shield, path: '/admin/merchants', status: 'active' },
    
    // 文化内容
    { id: 'culture', name: '文化圣地', description: '管理文化圣地和项目', icon: Monitor, path: '/admin/cultural-sites', status: 'active' },
    
    // 经济系统
    { id: 'economy', name: '经济系统', description: '管理灵值、分红和资产', icon: Activity, path: '/admin/economy', status: 'active' },
    { id: 'contribution', name: '贡献值管理', description: '管理用户贡献值', icon: Award, path: '/admin/contribution', status: 'active' },
    
    // 运营
    { id: 'operations', name: '运营管理', description: '管理推荐、反馈和通知', icon: LayoutDashboard, path: '/admin/operations', status: 'active' }
  ]

  const categories = {
    user: [modules[0], modules[1], modules[2]],
    ai: [modules[3], modules[4]],
    resource: [modules[5], modules[6]],
    business: [modules[7]],
    culture: [modules[8]],
    economy: [modules[9], modules[10]],
    operation: [modules[11]]
  }

  const handleModuleClick = (module: Module) => {
    if (module.status === 'active') {
      navigate(module.path)
    }
  }

  // 模块卡片组件
  const ModuleCard = ({ module }: { module: Module }) => (
    <button
      onClick={() => handleModuleClick(module)}
      className="bg-white rounded-lg shadow-sm p-6 text-left hover:shadow-md transition-shadow group"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <module.icon className="w-5 h-5 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
              {module.name}
            </h3>
          </div>
          <p className="text-sm text-gray-600">{module.description}</p>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-indigo-600 transition-colors" />
      </div>
    </button>
  )

  // 侧边栏菜单
  const sidebarItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: '仪表盘' },
    { id: 'modules', icon: Shield, label: '功能模块' },
    { id: 'monitor', icon: Monitor, label: '系统监控' },
    { id: 'logs', icon: Terminal, label: '日志查看' },
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
                <h1 className="text-xl font-bold text-gray-900">灵值生态园 - 后台管理系统</h1>
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
                title="退出登录"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 侧边栏 */}
      <div className={`fixed left-0 top-16 h-full bg-white border-r border-gray-200 transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'}`}>
        <div className="p-4">
          <nav className="space-y-2">
            {sidebarItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* 主内容区 */}
      <main className={`pt-16 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 仪表盘视图 */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">系统概览</h2>
              
              {/* 统计卡片 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">总用户数</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">1,234</p>
                    </div>
                    <Users className="w-8 h-8 text-indigo-600" />
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">活跃智能体</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">12</p>
                    </div>
                    <Zap className="w-8 h-8 text-yellow-600" />
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">今日访问</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">5,678</p>
                    </div>
                    <Activity className="w-8 h-8 text-green-600" />
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">系统状态</p>
                      <p className="text-3xl font-bold text-green-600 mt-1">正常</p>
                    </div>
                    <Shield className="w-8 h-8 text-green-600" />
                  </div>
                </div>
              </div>

              {/* 快速操作 */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => navigate('/admin/users')}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
                  >
                    <Users className="w-6 h-6 text-indigo-600 mb-2" />
                    <h4 className="font-medium text-gray-900">用户管理</h4>
                    <p className="text-sm text-gray-600">查看和管理用户</p>
                  </button>
                  <button
                    onClick={() => navigate('/admin/agents')}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
                  >
                    <Zap className="w-6 h-6 text-yellow-600 mb-2" />
                    <h4 className="font-medium text-gray-900">智能体管理</h4>
                    <p className="text-sm text-gray-600">配置和管理AI智能体</p>
                  </button>
                  <button
                    onClick={() => setActiveTab('modules')}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
                  >
                    <Shield className="w-6 h-6 text-green-600 mb-2" />
                    <h4 className="font-medium text-gray-900">功能模块</h4>
                    <p className="text-sm text-gray-600">查看所有功能模块</p>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 功能模块视图 */}
          {activeTab === 'modules' && (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">功能模块</h2>
                <p className="text-gray-600">共 {modules.length} 个模块，全部可用</p>
              </div>

              {/* 用户管理模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  用户管理
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {categories.user.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* AI智能模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  AI智能
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {categories.ai.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* 资源管理模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  资源管理
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {categories.resource.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* 商家管理模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  商家管理
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                  {categories.business.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* 文化内容模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Monitor className="w-5 h-5 mr-2" />
                  文化内容
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                  {categories.culture.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* 经济系统模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  经济系统
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {categories.economy.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>

              {/* 运营管理模块 */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <LayoutDashboard className="w-5 h-5 mr-2" />
                  运营管理
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                  {categories.operation.map((module) => (
                    <ModuleCard key={module.id} module={module} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 系统监控视图 */}
          {activeTab === 'monitor' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">系统监控</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">CPU 使用率</h3>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-4">
                      <div className="bg-indigo-600 h-4 rounded-full transition-all" style={{ width: `${systemStats.cpu}%` }}></div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{systemStats.cpu}%</span>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">内存使用率</h3>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-4">
                      <div className="bg-green-600 h-4 rounded-full transition-all" style={{ width: `${systemStats.memory}%` }}></div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{systemStats.memory}%</span>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">磁盘使用率</h3>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-4">
                      <div className="bg-yellow-600 h-4 rounded-full" style={{ width: `${systemStats.disk}%` }}></div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{systemStats.disk}%</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">系统信息</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">系统运行时间</p>
                    <p className="text-lg font-semibold text-gray-900">{systemStats.uptime}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">最后更新</p>
                    <p className="text-lg font-semibold text-gray-900">{new Date().toLocaleString('zh-CN')}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 日志查看视图 */}
          {activeTab === 'logs' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">系统日志</h2>
                <button
                  onClick={() => loadLogs()}
                  className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  刷新
                </button>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="space-y-2 font-mono text-sm">
                  {logs.map((log, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded">
                      <span className="text-gray-600">{log}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 系统设置视图 */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">系统设置</h2>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">系统名称</label>
                    <input
                      type="text"
                      defaultValue="灵值生态园智能体系统"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">系统版本</label>
                    <input
                      type="text"
                      defaultValue="v1.0.0"
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default AdminDashboard
