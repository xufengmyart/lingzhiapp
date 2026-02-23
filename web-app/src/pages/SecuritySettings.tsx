import { useState, useEffect } from 'react'
import { Shield, Smartphone, MapPin, Clock, Trash2, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

interface Device {
  id: number
  device_id: string
  device_name: string
  device_type: string
  ip_address: string
  location?: string
  is_current: boolean
  last_active_at: string
  created_at: string
}

interface SecuritySettings {
  require_phone_verification: boolean
  single_login_enabled: boolean
}

const SecuritySettings = () => {
  const [devices, setDevices] = useState<Device[]>([])
  const [settings, setSettings] = useState<SecuritySettings>({
    require_phone_verification: true,
    single_login_enabled: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadDevices()
    loadSettings()
  }, [])

  const loadDevices = async () => {
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/user/devices`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      const data = await response.json()
      if (data.success) {
        setDevices(data.data)
      }
    } catch (error) {
      console.error('加载设备列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = async () => {
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/user/security/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      const data = await response.json()
      if (data.success) {
        setSettings(data.data)
      }
    } catch (error) {
      console.error('加载安全设置失败:', error)
    }
  }

  const handleRemoveDevice = async (deviceId: string) => {
    if (!confirm('确定要移除此设备吗？')) return

    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/user/devices/${deviceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        alert('设备已移除')
        loadDevices()
      } else {
        alert(data.message || '移除失败')
      }
    } catch (error) {
      console.error('移除设备失败:', error)
      alert('移除失败，请重试')
    }
  }

  const handleRevokeAll = async () => {
    if (!confirm('确定要移除所有其他设备吗？仅保留当前设备。')) return

    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/user/devices/revoke-all`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        alert(data.message)
        loadDevices()
      } else {
        alert(data.message || '操作失败')
      }
    } catch (error) {
      console.error('操作失败:', error)
      alert('操作失败，请重试')
    }
  }

  const handleUpdateSettings = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || ''
      const response = await fetch(`${apiBase}/user/security/settings`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      })

      const data = await response.json()
      if (data.success) {
        alert('安全设置已更新')
      } else {
        alert(data.message || '更新失败')
      }
    } catch (error) {
      console.error('更新设置失败:', error)
      alert('更新失败，请重试')
    } finally {
      setSaving(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Shield className="w-8 h-8 mr-3 text-primary-600" />
          安全设置
        </h1>
        <p className="text-gray-600 mt-2">管理您的账户安全设置和登录设备</p>
      </div>

      {/* 安全设置 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">登录安全</h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <div className="font-semibold">手机验证码登录</div>
              <div className="text-sm text-gray-500 mt-1">
                登录时需要手机验证码验证，提高账户安全性
              </div>
            </div>
            <button
              onClick={() => setSettings({ ...settings, require_phone_verification: !settings.require_phone_verification })}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                settings.require_phone_verification ? 'bg-primary-500' : 'bg-gray-300'
              }`}
            >
              <div
                className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-transform ${
                  settings.require_phone_verification ? 'left-8' : 'left-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <div className="font-semibold">单点登录</div>
              <div className="text-sm text-gray-500 mt-1">
                同一账号只能在一个设备上登录，新登录会使旧会话失效
              </div>
            </div>
            <button
              onClick={() => setSettings({ ...settings, single_login_enabled: !settings.single_login_enabled })}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                settings.single_login_enabled ? 'bg-primary-500' : 'bg-gray-300'
              }`}
            >
              <div
                className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-transform ${
                  settings.single_login_enabled ? 'left-8' : 'left-1'
                }`}
              />
            </button>
          </div>
        </div>

        <button
          onClick={handleUpdateSettings}
          disabled={saving}
          className="mt-6 w-full bg-primary-500 text-white py-2 rounded-lg font-semibold hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? '保存中...' : '保存设置'}
        </button>
      </div>

      {/* 设备管理 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold flex items-center">
            <Smartphone className="w-5 h-5 mr-2" />
            已登录设备
          </h2>
          {devices.length > 1 && (
            <button
              onClick={handleRevokeAll}
              className="text-sm text-red-600 hover:text-red-700 font-semibold"
            >
              移除所有其他设备
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : devices.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无登录设备
          </div>
        ) : (
          <div className="space-y-3">
            {devices.map((device) => (
              <div
                key={device.id}
                className={`p-4 border rounded-lg ${
                  device.is_current ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      {device.is_current && (
                        <span className="px-2 py-1 bg-primary-500 text-white text-xs rounded-full">
                          当前设备
                        </span>
                      )}
                      <span className="font-semibold">{device.device_name}</span>
                    </div>

                    <div className="mt-2 space-y-1 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Smartphone className="w-4 h-4" />
                        <span>{device.device_type}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4" />
                        <span>{device.ip_address}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4" />
                        <span>最后活跃：{formatDate(device.last_active_at)}</span>
                      </div>
                    </div>
                  </div>

                  {!device.is_current && (
                    <button
                      onClick={() => handleRemoveDevice(device.device_id)}
                      className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="移除设备"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {devices.length > 1 && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <strong>安全提示：</strong>
                检测到有 {devices.length} 个设备已登录。建议定期检查并移除不熟悉的设备。
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 安全说明 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">安全建议</h2>
        <div className="space-y-3">
          <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-green-800">启用手机验证码</div>
              <div className="text-sm text-green-700">即使密码泄露，没有您的手机也无法登录</div>
            </div>
          </div>
          <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-green-800">开启单点登录</div>
              <div className="text-sm text-green-700">防止账号在多个设备同时登录</div>
            </div>
          </div>
          <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
            <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-red-800">定期检查登录设备</div>
              <div className="text-sm text-red-700">移除不熟悉的设备，保护账户安全</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SecuritySettings
