import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userApi } from '../services/api'
import { Mail, Phone, Calendar, Wallet, Target, Settings, LogOut, Lock, Key } from 'lucide-react'

const Profile = () => {
  const { user, logout, updateUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
  })

  const handleSave = async () => {
    try {
      const response = await userApi.updateProfile({
        username: formData.username,
        email: formData.email,
        phone: formData.phone,
      })

      if (response.success && response.data) {
        // 使用后端返回的完整用户数据更新 AuthContext
        updateUser(response.data)
        setIsEditing(false)
        alert('个人信息已更新')
      } else {
        alert('更新失败')
      }
    } catch (error: any) {
      console.error('更新用户信息失败:', error)
      const errorMessage = error?.response?.data?.message || error?.message || '更新失败，请重试'
      alert(errorMessage)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">个人中心</h1>
        <p className="text-gray-600 mt-2">管理您的个人信息和账户设置</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧个人信息卡片 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 基本信息 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">基本信息</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors"
                >
                  编辑
                </button>
              )}
            </div>

            <div className="flex items-start space-x-6 mb-6">
              <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-3xl font-bold">
                {user?.username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                      <input
                        type="text"
                        value={formData.username}
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <h3 className="text-2xl font-bold">{user?.username}</h3>
                    <p className="text-gray-600 mt-1">{user?.currentStage || '探索者'}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Mail className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">邮箱</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.email || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Phone className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">手机号</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : user?.phone || '未设置'}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">注册时间</div>
                  <div className="font-semibold">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">参与级别</div>
                  <div className="font-semibold">{user?.participationLevel || '未选择'}</div>
                </div>
              </div>
            </div>

            {isEditing && (
              <div className="mt-6 flex space-x-3">
                <button
                  onClick={handleSave}
                  className="flex-1 bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-2 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all"
                >
                  保存
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  取消
                </button>
              </div>
            )}
          </div>

          {/* 账户设置 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center space-x-2">
              <Settings className="w-6 h-6" />
              <span>账户设置</span>
            </h2>

            <div className="space-y-4">
              <button className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">修改邮箱</div>
                    <div className="text-sm text-gray-500">更改您的邮箱地址</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <Link to="/security" className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Shield className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">安全设置</div>
                    <div className="text-sm text-gray-500">管理设备和登录安全</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </Link>

              <button className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <Lock className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">修改密码</div>
                    <div className="text-sm text-gray-500">更新您的登录密码</div>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button
                onClick={logout}
                className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-red-50 transition-colors border-red-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <LogOut className="w-5 h-5 text-red-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold text-red-600">退出登录</div>
                    <div className="text-sm text-red-500">安全退出您的账户</div>
                  </div>
                </div>
                <span className="text-red-400">→</span>
              </button>
            </div>
          </div>
        </div>

        {/* 右侧统计卡片 */}
        <div className="space-y-6">
          {/* 灵值统计 */}
          <div className="bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl p-6 text-white">
            <div className="flex items-center space-x-3 mb-4">
              <Wallet className="w-8 h-8" />
              <div>
                <div className="text-sm opacity-80">总灵值</div>
                <div className="text-3xl font-bold">{user?.totalLingzhi}</div>
              </div>
            </div>
            <div className="text-sm opacity-80">
              等值：{(user?.totalLingzhi! * 0.1).toFixed(1)} 元
            </div>
          </div>

          {/* 里程碑进度 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold mb-4 flex items-center space-x-2">
              <Target className="w-5 h-5 text-primary-600" />
              <span>里程碑进度</span>
            </h3>

            <div className="space-y-4">
              {[
                { name: '初次收获', target: 10 },
                { name: '积累达人', target: 100 },
                { name: '灵值先锋', target: 500 },
                { name: '价值创造者', target: 1000 },
              ].map((milestone, idx) => {
                const completed = user!.totalLingzhi >= milestone.target
                return (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {completed ? (
                        <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs">✓</span>
                        </div>
                      ) : (
                        <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                      )}
                      <span className={`text-sm ${completed ? 'text-gray-900' : 'text-gray-500'}`}>
                        {milestone.name}
                      </span>
                    </div>
                    <span className="text-sm font-semibold">{milestone.target}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 快捷操作 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold mb-4">快捷操作</h3>
            <div className="space-y-2">
              <Link
                to="/recharge"
                className="w-full text-left p-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all flex items-center justify-between"
              >
                <span>购买灵值</span>
                <Wallet className="w-5 h-5" />
              </Link>
              <button className="w-full text-left p-3 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors">
                查看收入预测
              </button>
              <button className="w-full text-left p-3 bg-secondary-50 text-secondary-700 rounded-lg hover:bg-secondary-100 transition-colors">
                查看里程碑
              </button>
              <Link
                to="/partner"
                className="w-full text-left p-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors flex items-center justify-between"
              >
                <span>申请成为合伙人</span>
                <Target className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
