import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { partnerApi } from '../services/api'
import { Award, CheckCircle2, TrendingUp, Users, Lock } from 'lucide-react'

const Partner = () => {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<'qualification' | 'apply' | 'privileges'>('qualification')
  const [applicationData, setApplicationData] = useState({
    userName: '',
    phone: '',
    reason: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await partnerApi.submitApplication({
        userId: user!.id,
        userName: applicationData.userName,
        phone: applicationData.phone,
        currentLingzhi: user!.totalLingzhi,
        reason: applicationData.reason,
      })
      alert('申请提交成功！')
      setActiveTab('qualification')
    } catch (error) {
      console.error('申请失败:', error)
      alert('申请失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">合伙人计划</h1>
        <p className="text-gray-600 mt-2">成为合伙人，享受更多权益和更高收益</p>
      </div>

      {/* 标签页 */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex border-b">
          {[
            { id: 'qualification', icon: Award, label: '资格检查' },
            { id: 'apply', icon: CheckCircle2, label: '申请成为合伙人' },
            { id: 'privileges', icon: Users, label: '合伙人权益' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'text-primary-600 bg-primary-50 border-b-2 border-primary-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'qualification' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold">合伙人资格要求</h3>
                    <p className="opacity-90 mt-2">累计获得 10,000 灵值</p>
                  </div>
                  <Award className="w-16 h-16 opacity-80" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border rounded-xl p-6">
                  <h3 className="font-semibold mb-4">当前状态</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">当前灵值</span>
                      <span className="font-semibold text-primary-600">{user?.totalLingzhi} 灵值</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">距离资格</span>
                      <span className="font-semibold text-secondary-600">
                        {Math.max(0, 10000 - user!.totalLingzhi)} 灵值
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">资格状态</span>
                      <span className={`font-semibold ${
                        user!.totalLingzhi >= 10000 ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {user!.totalLingzhi >= 10000 ? '✅ 已达成' : '⏳ 进行中'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="border rounded-xl p-6">
                  <h3 className="font-semibold mb-4">青铜合伙人权益</h3>
                  <ul className="space-y-3 text-sm">
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>推荐分红：15%/8%/5%</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>优先参与基础项目</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>基础合伙人咨询服务</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>免费参加线上活动</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'apply' && (
            <div className="max-w-2xl mx-auto">
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-700">
                  💡 提示：您需要累计获得 10,000 灵值才能申请成为合伙人。当前您有 {user?.totalLingzhi} 灵值。
                </p>
              </div>

              {user!.totalLingzhi >= 10000 ? (
                <form onSubmit={handleSubmitApplication} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">真实姓名</label>
                    <input
                      type="text"
                      value={applicationData.userName}
                      onChange={(e) => setApplicationData({ ...applicationData, userName: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                    <input
                      type="tel"
                      value={applicationData.phone}
                      onChange={(e) => setApplicationData({ ...applicationData, phone: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">申请理由</label>
                    <textarea
                      value={applicationData.reason}
                      onChange={(e) => setApplicationData({ ...applicationData, reason: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="请简述您的申请理由..."
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50"
                  >
                    {loading ? '提交中...' : '提交申请'}
                  </button>
                </form>
              ) : (
                <div className="text-center py-12">
                  <Award className="w-24 h-24 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900">还未达到资格要求</h3>
                  <p className="text-gray-600 mt-2">
                    继续积累灵值，距离合伙人资格还有 {10000 - user!.totalLingzhi} 灵值
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'privileges' && (
            <div className="space-y-6">
              {[
                {
                  level: '青铜合伙人',
                  lingzhi: 10000,
                  commission: ['15%', '8%', '5%'],
                  features: ['基础推荐分红', '优先参与基础项目', '基础咨询服务', '免费线上活动'],
                },
                {
                  level: '白银合伙人',
                  lingzhi: 50000,
                  commission: ['18%', '10%', '6%'],
                  features: ['进阶推荐分红', '优先参与中级项目', '进阶咨询服务', '免费线下活动（每年2次）'],
                },
                {
                  level: '黄金合伙人',
                  lingzhi: 200000,
                  commission: ['20%', '12%', '8%'],
                  features: ['高级推荐分红', '优先参与高级项目', 'VIP咨询服务', '免费线下活动（每年5次）', '基础股权期权'],
                },
              ].map((partner) => (
                <div key={partner.level} className="border rounded-xl p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold">{partner.level}</h3>
                    <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold">
                      {partner.lingzhi.toLocaleString()} 灵值
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center space-x-2">
                        <TrendingUp className="w-5 h-5 text-primary-600" />
                        <span>推荐分红</span>
                      </h4>
                      <div className="flex space-x-4">
                        {partner.commission.map((rate, idx) => (
                          <div key={idx} className="text-center">
                            <div className="text-2xl font-bold text-primary-600">{rate}</div>
                            <div className="text-xs text-gray-500">{['一级', '二级', '三级'][idx]}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-3 flex items-center space-x-2">
                        <Lock className="w-5 h-5 text-secondary-600" />
                        <span>专属权益</span>
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {partner.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center space-x-2">
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Partner
