import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Users, MessageSquare, Bell, BarChart3, RefreshCw, Plus, Check, X, Search, Send } from 'lucide-react'
import api from '../services/api'

interface ReferralStats {
  totalReferrals: number
  activeReferrers: number
  todayReferrals: number
  topReferrer: {
    userId: number
    userName: string
    referralCount: number
  }
}

interface Feedback {
  id: number
  userId: number
  userName: string
  type: string
  content: string
  status: string
  rating: number
  createdAt: string
}

interface Notification {
  id: number
  title: string
  content: string
  type: string
  target: string
  status: string
  createdAt: string
}

const OperationsManagement = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'referrals' | 'feedback' | 'notifications'>('referrals')
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null)
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([])
  const [notificationList, setNotificationList] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  // 通知创建表单
  const [isCreatingNotification, setIsCreatingNotification] = useState(false)
  const [notificationForm, setNotificationForm] = useState({
    title: '',
    content: '',
    type: 'system',
    target: 'all'
  })

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError('')
      
      if (activeTab === 'referrals') {
        const response = await api.get('/admin/operations/referrals')
        if (response.data.success) {
          setReferralStats(response.data.data)
        }
      } else if (activeTab === 'feedback') {
        const response = await api.get('/admin/operations/feedback')
        if (response.data.success) {
          setFeedbackList(response.data.data || [])
        }
      } else if (activeTab === 'notifications') {
        const response = await api.get('/admin/operations/notifications')
        if (response.data.success) {
          setNotificationList(response.data.data || [])
        }
      }
    } catch (err) {
      setError('获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNotification = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await api.post('/admin/operations/notifications', notificationForm)
      if (response.data.success) {
        setMessage('通知创建成功')
        setIsCreatingNotification(false)
        setNotificationForm({
          title: '',
          content: '',
          type: 'system',
          target: 'all'
        })
        fetchData()
      } else {
        setError(response.data.message || '创建失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '创建失败')
    }
  }

  const handleFeedbackAction = async (feedbackId: number, action: 'approve' | 'reject') => {
    try {
      const status = action === 'approve' ? 'resolved' : 'rejected'
      const response = await api.put(`/admin/operations/feedback/${feedbackId}`, { status })
      if (response.data.success) {
        setMessage(`反馈已${action === 'approve' ? '处理' : '拒绝'}`)
        fetchData()
      } else {
        setError(response.data.message || '操作失败')
      }
    } catch (err) {
      setError('操作失败')
    }
  }

  const sendNotification = async (notificationId: number) => {
    try {
      const response = await api.post(`/admin/operations/notifications/${notificationId}/send`)
      if (response.data.success) {
        setMessage('通知发送成功')
        fetchData()
      } else {
        setError(response.data.message || '发送失败')
      }
    } catch (err) {
      setError('发送失败')
    }
  }

  const deleteNotification = async (notificationId: number) => {
    if (!confirm('确定要删除这个通知吗？')) {
      return
    }

    try {
      const response = await api.delete(`/admin/operations/notifications/${notificationId}`)
      if (response.data.success) {
        setMessage('通知删除成功')
        fetchData()
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('zh-CN').format(num)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/admin/modules')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">运营管理</h1>
                <p className="text-sm text-gray-600">管理推荐关系、用户反馈和系统通知</p>
              </div>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              刷新数据
            </button>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-green-50 text-green-800 px-4 py-3 rounded-lg">
            {message}
          </div>
        </div>
      )}
      {error && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-red-50 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* 标签页导航 */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('referrals')}
                className={`flex items-center px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'referrals'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Users className="w-4 h-4 mr-2" />
                推荐关系
              </button>
              <button
                onClick={() => setActiveTab('feedback')}
                className={`flex items-center px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'feedback'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                用户反馈
              </button>
              <button
                onClick={() => setActiveTab('notifications')}
                className={`flex items-center px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'notifications'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Bell className="w-4 h-4 mr-2" />
                系统通知
              </button>
              <button
                onClick={() => navigate('/admin/reports')}
                className={`flex items-center px-6 py-4 border-b-2 font-medium text-sm transition-colors`}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                报表统计
              </button>
            </nav>
          </div>
        </div>

        {/* 推荐关系 */}
        {activeTab === 'referrals' && referralStats && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">总推荐数</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatNumber(referralStats.totalReferrals)}
                    </p>
                  </div>
                  <div className="p-3 bg-indigo-100 rounded-lg">
                    <Users className="w-6 h-6 text-indigo-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">活跃推荐人</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatNumber(referralStats.activeReferrers)}
                    </p>
                  </div>
                  <div className="p-3 bg-green-100 rounded-lg">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">今日推荐</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatNumber(referralStats.todayReferrals)}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <RefreshCw className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Top推荐人</p>
                    <p className="text-sm font-bold text-gray-900 mt-1">
                      {referralStats.topReferrer?.userName || '暂无'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatNumber(referralStats.topReferrer?.referralCount || 0)} 推荐
                    </p>
                  </div>
                  <div className="p-3 bg-yellow-100 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-yellow-600" />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">推荐说明</h3>
              <div className="prose prose-sm text-gray-600">
                <p>推荐关系统计显示了平台用户的推广活动情况：</p>
                <ul>
                  <li><strong>总推荐数</strong>：平台上所有用户推荐的总人数</li>
                  <li><strong>活跃推荐人</strong>：最近7天内有推荐活动的用户数</li>
                  <li><strong>今日推荐</strong>：今天新产生的推荐关系数</li>
                  <li><strong>Top推荐人</strong>：推荐人数最多的用户</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 用户反馈 */}
        {activeTab === 'feedback' && (
          <div className="bg-white rounded-lg shadow-sm">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">用户反馈列表</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {loading ? (
                <div className="p-4 text-center text-gray-500">加载中...</div>
              ) : feedbackList.length === 0 ? (
                <div className="p-8 text-center text-gray-500">暂无反馈</div>
              ) : (
                feedbackList.map((feedback) => (
                  <div key={feedback.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-medium text-gray-900">
                            {feedback.userName}
                          </span>
                          <span className="text-sm text-gray-500">
                            (ID: {feedback.userId})
                          </span>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            feedback.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            feedback.status === 'resolved' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {feedback.status}
                          </span>
                        </div>
                        <p className="text-gray-700">{feedback.content}</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>类型: {feedback.type}</span>
                          <span>评分: {feedback.rating}/5</span>
                          <span>{new Date(feedback.createdAt).toLocaleString('zh-CN')}</span>
                        </div>
                      </div>
                      {feedback.status === 'pending' && (
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => handleFeedbackAction(feedback.id, 'approve')}
                            className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                          >
                            <Check className="w-4 h-4 text-green-600" />
                          </button>
                          <button
                            onClick={() => handleFeedbackAction(feedback.id, 'reject')}
                            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                          >
                            <X className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 系统通知 */}
        {activeTab === 'notifications' && (
          <div className="space-y-6">
            {/* 创建通知 */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">创建通知</h2>
                <button
                  onClick={() => setIsCreatingNotification(!isCreatingNotification)}
                  className="flex items-center px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {isCreatingNotification ? '取消' : '新建通知'}
                </button>
              </div>

              {isCreatingNotification && (
                <form onSubmit={handleCreateNotification} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      通知标题 *
                    </label>
                    <input
                      type="text"
                      required
                      value={notificationForm.title}
                      onChange={(e) => setNotificationForm({...notificationForm, title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      通知内容 *
                    </label>
                    <textarea
                      required
                      value={notificationForm.content}
                      onChange={(e) => setNotificationForm({...notificationForm, content: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        类型 *
                      </label>
                      <select
                        required
                        value={notificationForm.type}
                        onChange={(e) => setNotificationForm({...notificationForm, type: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="system">系统通知</option>
                        <option value="activity">活动通知</option>
                        <option value="promotion">促销通知</option>
                        <option value="reminder">提醒通知</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        目标用户 *
                      </label>
                      <select
                        required
                        value={notificationForm.target}
                        onChange={(e) => setNotificationForm({...notificationForm, target: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="all">所有用户</option>
                        <option value="active">活跃用户</option>
                        <option value="merchants">商家</option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    创建通知
                  </button>
                </form>
              )}
            </div>

            {/* 通知列表 */}
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">通知列表</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">加载中...</div>
                ) : notificationList.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">暂无通知</div>
                ) : (
                  notificationList.map((notification) => (
                    <div key={notification.id} className="p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="font-semibold text-gray-900">
                              {notification.title}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              notification.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {notification.status}
                            </span>
                          </div>
                          <p className="text-gray-700">{notification.content}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>类型: {notification.type}</span>
                            <span>目标: {notification.target}</span>
                            <span>{new Date(notification.createdAt).toLocaleString('zh-CN')}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          {notification.status === 'pending' && (
                            <button
                              onClick={() => sendNotification(notification.id)}
                              className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
                              title="发送通知"
                            >
                              <Send className="w-4 h-4 text-blue-600" />
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotification(notification.id)}
                            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                            title="删除通知"
                          >
                            <X className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default OperationsManagement
