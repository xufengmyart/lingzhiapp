import { useState, useRef, useEffect } from 'react'
import { ChatProvider, useChat } from '../contexts/ChatContext'
import { Send, Sparkles, User, Bot, ThumbsUp, ThumbsDown, MessageSquarePlus, X, ChevronDown } from 'lucide-react'
import axios from 'axios'
import { vrTheme } from '../utils/vr-theme'

interface Agent {
  id: number
  name: string
  description: string
  avatar_url: string
}

const ChatContent = () => {
  const { messages, loading, sendMessage, clearChat } = useChat()
  const [input, setInput] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [showAgentDropdown, setShowAgentDropdown] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [feedbackModal, setFeedbackModal] = useState<{ open: boolean; messageId: string; messageContent: string }>({
    open: false,
    messageId: '',
    messageContent: ''
  })
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false)

  // 加载智能体列表
  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const response = await axios.get('/api/admin/agents')
      if (response.data.success) {
        const activeAgents = response.data.data.filter((a: any) => a.status === 'active')
        setAgents(activeAgents)
        // 默认选中第一个智能体
        if (activeAgents.length > 0 && !selectedAgent) {
          setSelectedAgent(activeAgents[0])
        }
      }
    } catch (error) {
      console.error('加载智能体列表失败:', error)
    }
  }

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    
    await sendMessage(input, selectedAgent?.id)
    setInput('')
  }

  const handleFeedback = async (type: 'helpful' | 'not_helpful' | 'suggestion', question?: string) => {
    setFeedbackSubmitting(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post('/api/feedback', {
        type,
        question: feedbackModal.messageContent,
        comment: question || '',
        agent_id: 1
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.data.success) {
        alert(`反馈提交成功！获得 ${response.data.data.contribution_value} 灵值`)
        setFeedbackModal({ open: false, messageId: '', messageContent: '' })
        // 刷新用户信息
        window.location.reload()
      }
    } catch (error) {
      console.error('提交反馈失败:', error)
      alert('提交反馈失败，请稍后重试')
    } finally {
      setFeedbackSubmitting(false)
    }
  }

  return (
    <div className={`flex flex-col ${vrTheme.bgGradient} rounded-3xl shadow-2xl overflow-hidden border border-white/20`}>
      {/* 聊天头部 - VR风格 */}
      <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} p-4 flex items-center justify-between`}>
        <div className="flex items-center space-x-3">
          <div className={`relative w-10 h-10 ${vrTheme.button.gradient} rounded-full flex items-center justify-center ${vrTheme.button.glow}`}>
            <Sparkles className="w-5 h-5 text-white" />
            <div className="absolute inset-0 bg-white/20 rounded-full animate-pulse"></div>
          </div>
          <div>
            <h2 className="font-semibold text-white">灵值元宇宙智能体</h2>
            <p className="text-xs text-cyan-400 opacity-80">您的专属元宇宙向导</p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-all text-sm text-white"
        >
          新对话
        </button>
      </div>

      {/* 消息列表 - VR风格 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" id="messages-container">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Sparkles className="w-16 h-16 mb-4 text-cyan-400 animate-pulse" />
            <p className="text-lg font-medium text-white">开始您的对话</p>
            <p className="text-sm">与智能体交流，探索灵值元宇宙的价值</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-cyan-400 to-cyan-500'
                    : 'bg-gradient-to-br from-purple-400 to-purple-500'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>
              <div className="flex-1 max-w-[70%]">
                <div
                  className={`p-4 rounded-2xl backdrop-blur-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-cyan-500/80 to-cyan-600/80 text-white border border-cyan-400/30'
                      : 'bg-white/10 text-white border border-white/20'
                  }`}
                >
                  <p className="text-base whitespace-pre-wrap leading-relaxed break-all break-words">{message.content}</p>
                  <span className="text-xs opacity-60 mt-2 block">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {/* 智能体回复添加反馈按钮 */}
                {message.role === 'assistant' && (
                  <div className="flex items-center space-x-2 mt-2 ml-2">
                    <button
                      onClick={() => setFeedbackModal({ open: true, messageId: message.id, messageContent: message.content })}
                      className="text-xs text-gray-400 hover:text-cyan-400 flex items-center space-x-1 transition-colors"
                    >
                      <MessageSquarePlus className="w-3 h-3" />
                      <span>反馈</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white/10 p-4 rounded-2xl border border-white/20 backdrop-blur-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        {/* 用于自动滚动的锚点 */}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 - VR风格 */}
      <div className="p-4 border-t border-white/10 bg-white/5 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入您的问题..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-base"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>

      {/* 反馈模态框 */}
      {feedbackModal.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4">
            <div className="p-6 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold">您的反馈对我们很重要</h3>
              <button
                onClick={() => setFeedbackModal({ open: false, messageId: '', messageContent: '' })}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-600 mb-4">智能体回复：</p>
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-sm text-gray-700">
                {feedbackModal.messageContent}
              </div>

              <p className="text-sm font-medium text-gray-900 mb-3">这条回复对您有帮助吗？</p>
              <div className="grid grid-cols-2 gap-3 mb-6">
                <button
                  onClick={() => handleFeedback('helpful')}
                  disabled={feedbackSubmitting}
                  className="flex items-center justify-center space-x-2 p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 hover:border-green-400 transition-all disabled:opacity-50"
                >
                  <ThumbsUp className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-gray-700">有帮助 (+3灵值)</span>
                </button>
                <button
                  onClick={() => handleFeedback('not_helpful')}
                  disabled={feedbackSubmitting}
                  className="flex items-center justify-center space-x-2 p-4 border-2 border-orange-200 rounded-lg hover:bg-orange-50 hover:border-orange-400 transition-all disabled:opacity-50"
                >
                  <ThumbsDown className="w-5 h-5 text-orange-600" />
                  <span className="font-medium text-gray-700">无帮助 (+5灵值)</span>
                </button>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  您的问题或建议 <span className="text-xs text-gray-500">(选填，+10灵值)</span>
                </label>
                <textarea
                  id="feedback-question"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                  rows={3}
                  placeholder="请描述您遇到的问题或改进建议..."
                />
              </div>

              <button
                onClick={() => {
                  const questionInput = document.getElementById('feedback-question') as HTMLTextAreaElement
                  handleFeedback('suggestion', questionInput?.value)
                }}
                disabled={feedbackSubmitting}
                className="w-full py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50"
              >
                {feedbackSubmitting ? '提交中...' : '提交反馈'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const Chat = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">智能对话</h1>
        <p className="text-gray-600 mt-2">与灵值生态园智能体交流，探索文化价值</p>
      </div>
      <ChatProvider>
        <ChatContent />
      </ChatProvider>
    </div>
  )
}

export default Chat
