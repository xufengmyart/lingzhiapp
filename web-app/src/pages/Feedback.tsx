import { useState } from 'react'
import { MessageCircle, Send, Star, Smile, Frown, AlertCircle, Lightbulb, CheckCircle } from 'lucide-react'
import { vrTheme } from '../utils/vr-theme'

interface FeedbackFormData {
  type: 'bug' | 'feature' | 'suggestion' | 'other'
  rating: number
  subject: string
  description: string
}

const Feedback = () => {
  const [formData, setFormData] = useState<FeedbackFormData>({
    type: 'suggestion',
    rating: 5,
    subject: '',
    description: '',
  })
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const feedbackTypes = [
    { value: 'bug', label: 'Bug反馈', icon: AlertCircle, color: 'text-pink-400', bg: 'bg-pink-500/20' },
    { value: 'feature', label: '功能建议', icon: Lightbulb, color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
    { value: 'suggestion', label: '意见建议', icon: MessageCircle, color: 'text-purple-400', bg: 'bg-purple-500/20' },
    { value: 'other', label: '其他', icon: Smile, color: 'text-green-400', bg: 'bg-green-500/20' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.subject.trim() || !formData.description.trim()) {
      alert('请填写主题和描述')
      return
    }

    setLoading(true)
    // 模拟提交
    setTimeout(() => {
      setSubmitted(true)
      setLoading(false)
    }, 1000)
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-4">
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} rounded-2xl p-8 max-w-md w-full text-center`}>
          <div className="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">感谢您的反馈</h2>
          <p className="text-gray-300 mb-6">我们会认真考虑您的建议，并尽快改进产品体验</p>
          <button
            onClick={() => {
              setSubmitted(false)
              setFormData({ type: 'suggestion', rating: 5, subject: '', description: '' })
            }}
            className={`${vrTheme.button.gradient} ${vrTheme.button.glow} text-white px-8 py-3 rounded-lg font-semibold transition-all hover:scale-105`}
          >
            继续反馈
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
      {/* VR背景效果 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px] animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="container mx-auto max-w-3xl relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-6 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-2xl shadow-lg">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            用户反馈
          </h1>
          <p className="text-gray-300 text-lg">
            您的声音是我们进步的动力，期待您的宝贵意见
          </p>
        </div>

        {/* 反馈表单 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} ${vrTheme.glass.shadow} rounded-2xl p-8`}>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 反馈类型 */}
            <div>
              <label className="block text-gray-300 font-semibold mb-4">反馈类型</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {feedbackTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, type: type.value as any })}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        formData.type === type.value
                          ? `${type.bg} ${type.color} border-current`
                          : 'border-white/10 text-gray-400 hover:border-white/20 hover:text-gray-300'
                      }`}
                    >
                      <Icon className="w-6 h-6 mx-auto mb-2" />
                      <span className="text-sm font-medium">{type.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 评分 */}
            <div>
              <label className="block text-gray-300 font-semibold mb-4">整体评分</label>
              <div className="flex items-center space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFormData({ ...formData, rating: star })}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= formData.rating
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-gray-600'
                      }`}
                    />
                  </button>
                ))}
                <span className="ml-3 text-gray-300 text-lg font-semibold">
                  {formData.rating} / 5
                </span>
              </div>
            </div>

            {/* 主题 */}
            <div>
              <label className="block text-gray-300 font-semibold mb-2">主题</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="简要描述反馈内容"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all"
              />
            </div>

            {/* 详细描述 */}
            <div>
              <label className="block text-gray-300 font-semibold mb-2">详细描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="请详细描述您的问题或建议..."
                rows={6}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all resize-none"
              />
            </div>

            {/* 提交按钮 */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full ${vrTheme.button.gradient} ${vrTheme.button.glow} text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2`}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>提交中...</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>提交反馈</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* 底部提示 */}
        <div className="mt-8 text-center text-gray-400">
          <p>我们会认真阅读每一条反馈，并在3个工作日内回复</p>
        </div>
      </div>
    </div>
  )
}

export default Feedback
