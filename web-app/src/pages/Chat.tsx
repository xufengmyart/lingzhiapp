import { useState, useRef, useEffect } from 'react'
import { ChatProvider, useChat } from '../contexts/ChatContext'
import { Send, Sparkles, User, Bot, ThumbsUp, ThumbsDown, MessageSquarePlus, X, ChevronDown, Menu, X as CloseIcon, Brain, Lightbulb } from 'lucide-react'
import api from '../services/api'
import { agentApi } from '../services/api'
import { vrTheme } from '../utils/vr-theme'
import { chatTheme } from '../styles/chat-theme'
import KnowledgeSidebar from '../components/KnowledgeSidebar'
import { useChatBilling } from '../hooks/useChatBilling'
import ChatEndDialog from '../components/ChatEndDialog'

interface Agent {
  id: number
  name: string
  description: string
  avatar_url: string
}

interface KnowledgeItem {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
}

const ChatContent = () => {
  const { messages, loading, sendMessage, clearChat } = useChat()
  const [input, setInput] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [feedbackModal, setFeedbackModal] = useState<{ open: boolean; messageId: string; messageContent: string }>({
    open: false,
    messageId: '',
    messageContent: ''
  })
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false)
  const [showKnowledgeSidebar, setShowKnowledgeSidebar] = useState(false) // 默认隐藏侧栏
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false) // 移动端侧栏打开状态
  const [isMobile, setIsMobile] = useState(false) // 是否为移动端
  const [enableThinking, setEnableThinking] = useState(false) // 深度思考模式开关
  const [chatEndDialogOpen, setChatEndDialogOpen] = useState(false) // 对话结束对话框

  // 检测移动端
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // 对话计费Hook
  const {
    billingInfo,
    startBilling,
    stopBilling,
    resetBilling,
    addFeedbackReward,
    formatDuration,
    isBilling
  } = useChatBilling()

  // 加载智能体列表
  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const response = await agentApi.getAgents()
      if (response.success) {
        const activeAgents = response.data.filter((a: any) => a.status === 'active')
        setAgents(activeAgents)
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

    // 如果是第一条消息，开始计费
    if (!isBilling) {
      startBilling()
    }

    const agentIdToSend = selectedAgent?.id || (agents.length > 0 ? agents[0].id : 2)
    console.log('[Chat] 发送消息，智能体ID:', agentIdToSend, '选中智能体:', selectedAgent, '深度思考:', enableThinking)

    await sendMessage(input, agentIdToSend, enableThinking)
    setInput('')
  }

  const handleKnowledgeSelect = (item: KnowledgeItem) => {
    // 将知识库内容作为问题发送给智能体
    const question = `我想了解：${item.title}`
    setInput(question)
    // 自动提交
    setTimeout(() => {
      handleSubmit(new Event('submit') as any)
    }, 100)
  }

  const handleFeedback = async (type: 'helpful' | 'not_helpful' | 'suggestion', question?: string) => {
    setFeedbackSubmitting(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-User-ID': localStorage.getItem('userId') || ''
        },
        body: JSON.stringify({
          type,
          question: feedbackModal.messageContent,
          comment: question || '',
          agent_id: 1
        })
      })

      const result = await response.json()

      if (result.success) {
        const reward = result.data.contribution_value
        alert(`反馈提交成功！获得 ${reward} 灵值`)
        
        // 添加反馈奖励
        addFeedbackReward(reward)
        
        setFeedbackModal({ open: false, messageId: '', messageContent: '' })
      } else {
        alert(`反馈提交失败：${result.error}`)
      }
    } catch (error) {
      console.error('提交反馈失败:', error)
      alert('提交反馈失败，请稍后重试')
    } finally {
      setFeedbackSubmitting(false)
    }
  }

  // 处理"新对话"按钮点击
  const handleNewChat = () => {
    if (isBilling) {
      // 如果正在计费，停止计费并显示对话框
      stopBilling()
      setChatEndDialogOpen(true)
    } else {
      // 如果没有计费，直接清空聊天
      clearChat()
    }
  }

  // 关闭对话框并清空聊天
  const handleChatEndDialogClose = () => {
    setChatEndDialogOpen(false)
    clearChat()
    resetBilling()
  }

  // 处理侧栏切换
  const toggleSidebar = () => {
    if (isMobile) {
      setIsMobileSidebarOpen(!isMobileSidebarOpen)
    } else {
      setShowKnowledgeSidebar(!showKnowledgeSidebar)
    }
  }

  // 关闭移动端侧栏
  const closeMobileSidebar = () => {
    setIsMobileSidebarOpen(false)
  }

  return (
    <div className="flex h-[calc(100vh-80px)] gap-0 relative">
      {/* 移动端遮罩层 */}
      {isMobile && isMobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeMobileSidebar}
        />
      )}

      {/* 知识库侧边栏 */}
      {(showKnowledgeSidebar || isMobileSidebarOpen) && (
        <div
          className={`
            ${isMobile
              ? 'fixed inset-0 z-50 md:hidden'
              : 'relative'
            }
            transition-all duration-300 ease-in-out
          `}
        >
          <KnowledgeSidebar
            onKnowledgeSelect={(item) => {
              handleKnowledgeSelect(item)
              closeMobileSidebar()
            }}
          />
          {/* 移动端关闭按钮 */}
          {isMobile && (
            <button
              onClick={closeMobileSidebar}
              className="absolute top-4 right-4 z-10 p-2 bg-white/10 backdrop-blur-sm rounded-lg hover:bg-white/20 transition-all"
            >
              <CloseIcon className="w-5 h-5 text-white" />
            </button>
          )}
        </div>
      )}

      {/* 主聊天区域 */}
      <div className={`flex-1 flex flex-col ${vrTheme.bgGradient} border border-white/20 ${showKnowledgeSidebar ? 'rounded-l-none' : 'rounded-3xl'}`}>
        {/* 聊天头部 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} p-3.5 sm:p-4 flex items-center justify-between gap-2 sm:gap-3`}>
          <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
            <button
              onClick={toggleSidebar}
              className="p-2 hover:bg-white/10 rounded-lg transition-all flex-shrink-0 group"
              title={isMobile ? '打开知识库' : (showKnowledgeSidebar ? '隐藏知识库' : '显示知识库')}
            >
              {(isMobile && !isMobileSidebarOpen) || (!isMobile && !showKnowledgeSidebar) ? (
                <Menu className="w-4 h-4 text-white group-hover:text-[#00C3FF] transition-colors" />
              ) : (
                <CloseIcon className="w-4 h-4 text-white group-hover:text-[#00C3FF] transition-colors" />
              )}
            </button>
            <div className={`relative w-10 h-10 sm:w-11 sm:h-11 ${vrTheme.button.gradient} rounded-full flex items-center justify-center ${vrTheme.button.glow} flex-shrink-0 transition-all duration-300 hover:scale-105`}>
              <Sparkles className="w-5 h-5 sm:w-5.5 sm:h-5.5 text-white" />
              <div className="absolute inset-0 bg-white/20 rounded-full animate-pulse"></div>
            </div>
            <div className="flex-1 min-w-[120px] overflow-hidden pr-2">
              <h2 className="font-semibold text-white text-sm sm:text-base whitespace-normal break-words leading-tight mb-1 drop-shadow-md">灵值元宇宙智能体</h2>
              <p className="text-xs sm:text-sm text-[#00C3FF]/80 whitespace-normal break-words leading-tight drop-shadow-sm">您的专属元宇宙向导</p>
            </div>
          </div>
          <button
            onClick={handleNewChat}
            className="px-4 py-2 sm:px-5 sm:py-2.5 bg-gradient-to-r from-[#00C3FF]/20 to-[#47D1FF]/20 border border-[#00C3FF]/30 rounded-xl hover:from-[#00C3FF]/30 hover:to-[#47D1FF]/30 hover:shadow-[0_0_20px_rgba(0,195,255,0.3)] transition-all text-xs sm:text-sm text-white flex-shrink-0"
          >
            新对话
          </button>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6" id="messages-container">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 px-4">
              <div className={`relative w-20 h-20 sm:w-24 sm:h-24 mb-6 ${vrTheme.button.gradient} rounded-full flex items-center justify-center ${vrTheme.button.glow}`}>
                <Sparkles className="w-10 h-10 sm:w-12 sm:h-12 text-white" />
                <div className="absolute inset-0 bg-white/20 rounded-full animate-pulse"></div>
              </div>
              <h3 className="text-xl sm:text-2xl font-semibold text-white mb-3">开始您的对话</h3>
              <p className="text-sm sm:text-base text-[#B4C7E7]/70 mb-2 text-center max-w-md">
                与智能体交流，探索灵值元宇宙的价值
              </p>
              <p className="text-xs text-[#B4C7E7]/50 mb-6 text-center">
                您可以询问关于灵值生态、合伙人制度、西安文化等问题
              </p>
              {(!showKnowledgeSidebar && !isMobileSidebarOpen) && (
                <button
                  onClick={toggleSidebar}
                  className={`px-5 py-3 rounded-xl transition-all text-sm sm:text-base ${vrTheme.button.gradient} ${vrTheme.button.glow} hover:scale-105 active:scale-95`}
                >
                  <span className="flex items-center gap-2">
                    <Lightbulb className="w-4 h-4" />
                    打开知识库
                  </span>
                </button>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 animate-message-slide-in ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                    message.role === 'user'
                      ? `${chatTheme.avatar.user.bg} ${chatTheme.avatar.user.shadow} ${chatTheme.avatar.user.ring}`
                      : `${chatTheme.avatar.assistant.bg} ${chatTheme.avatar.assistant.shadow} ${chatTheme.avatar.assistant.ring} ${chatTheme.avatar.assistant.pulse}`
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-6 h-6 text-white" />
                  ) : (
                    <Bot className="w-6 h-6 text-white" />
                  )}
                </div>
                <div className="flex-1 max-w-[75%]">
                  {/* 显示思考过程 */}
                  {message.role === 'assistant' && message.thinking && (
                    <div className={`mb-3 rounded-2xl p-4 backdrop-blur-sm transition-all duration-300 ${chatTheme.bubble.thinking.bg} ${chatTheme.bubble.thinking.border} ${chatTheme.bubble.thinking.shadow} ${chatTheme.bubble.thinking.glow}`}>
                      <div className="flex items-center gap-2 mb-3 text-purple-300">
                        <Brain className="w-5 h-5 animate-pulse" />
                        <span className="font-semibold text-sm">深度思考过程</span>
                      </div>
                      <p className={`text-sm ${chatTheme.bubble.thinking.text} whitespace-pre-wrap leading-relaxed`}>
                        {message.thinking}
                      </p>
                    </div>
                  )}
                  <div
                    className={`rounded-2xl p-4 backdrop-blur-sm transition-all duration-300 ${
                      message.isError
                        ? `${chatTheme.bubble.error.bg} ${chatTheme.bubble.error.border} ${chatTheme.bubble.error.shadow}`
                        : message.role === 'user'
                        ? `${chatTheme.bubble.user.bg} ${chatTheme.bubble.user.border} ${chatTheme.bubble.user.shadow} ${chatTheme.bubble.user.glow}`
                        : `${chatTheme.bubble.assistant.bg} ${chatTheme.bubble.assistant.border} ${chatTheme.bubble.assistant.shadow} ${chatTheme.bubble.assistant.glow}`
                    }`}
                  >
                    <p className={`text-base whitespace-pre-wrap leading-relaxed ${
                      message.isError
                        ? chatTheme.bubble.error.text
                        : message.role === 'user'
                        ? chatTheme.bubble.user.text
                        : chatTheme.bubble.assistant.text
                    }`}>
                      {message.content}
                    </p>
                    <span className="text-xs opacity-50 mt-3 block">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  {message.role === 'assistant' && !message.isError && (
                    <div className="flex items-center space-x-2 mt-3 ml-2">
                      <button
                        onClick={() => setFeedbackModal({ open: true, messageId: message.id, messageContent: message.content })}
                        className={`text-xs flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all duration-300 ${chatTheme.feedback.bg} ${chatTheme.feedback.border} ${chatTheme.feedback.text} ${chatTheme.feedback.hover} ${chatTheme.feedback.hoverText}`}
                      >
                        <MessageSquarePlus className="w-3.5 h-3.5" />
                        <span>反馈</span>
                      </button>
                      <button
                        className={`text-xs flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all duration-300 ${chatTheme.feedback.bg} ${chatTheme.feedback.border} ${chatTheme.feedback.text} ${chatTheme.feedback.hover} ${chatTheme.feedback.hoverText}`}
                        title="这条回复有帮助"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>
                      <button
                        className={`text-xs flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all duration-300 ${chatTheme.feedback.bg} ${chatTheme.feedback.border} ${chatTheme.feedback.text} ${chatTheme.feedback.hover} ${chatTheme.feedback.hoverText}`}
                        title="这条回复需要改进"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex items-start space-x-3 animate-message-slide-in">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${chatTheme.avatar.assistant.bg} ${chatTheme.avatar.assistant.shadow} ${chatTheme.avatar.assistant.ring} ${chatTheme.avatar.assistant.pulse}`}>
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className={`p-5 rounded-2xl backdrop-blur-sm ${chatTheme.bubble.assistant.bg} ${chatTheme.bubble.assistant.border} ${chatTheme.bubble.assistant.shadow}`}>
                <div className="flex space-x-2">
                  <div className={`w-3 h-3 rounded-full animate-typing ${chatTheme.loading.dots[0]}`} style={{ animationDelay: '0s' }}></div>
                  <div className={`w-3 h-3 rounded-full animate-typing ${chatTheme.loading.dots[1]}`} style={{ animationDelay: '0.2s' }}></div>
                  <div className={`w-3 h-3 rounded-full animate-typing ${chatTheme.loading.dots[2]}`} style={{ animationDelay: '0.4s' }}></div>
                </div>
                <p className="text-xs mt-2 text-[#B4C7E7]/50">灵枢正在思考...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <div className="p-4 sm:p-5 border-t border-white/10 bg-[#0A0D18]/80 backdrop-blur-xl">
          {/* 深度思考模式开关 */}
          <div className="flex items-center justify-between mb-4 px-1">
            <label className="flex items-center gap-3 cursor-pointer group">
              <div className={`relative w-14 h-7 transition-all duration-300 rounded-full ${
                enableThinking
                  ? `${chatTheme.thinkingToggle.active} ${chatTheme.thinkingToggle.glow}`
                  : chatTheme.thinkingToggle.inactive
              }`}>
                <div className={`absolute top-1 left-1 w-5 h-5 rounded-full transition-all duration-300 ${chatTheme.thinkingToggle.thumb} ${
                  enableThinking ? 'translate-x-7' : ''
                }`}></div>
              </div>
              <input
                type="checkbox"
                checked={enableThinking}
                onChange={(e) => setEnableThinking(e.target.checked)}
                className="sr-only"
              />
              <span className="flex items-center gap-2 text-sm text-[#B4C7E7] group-hover:text-white transition-colors">
                <Brain className="w-4 h-4" />
                深度思考模式
              </span>
            </label>
            <span className={`text-xs ${enableThinking ? 'text-[#00C3FF]' : 'text-[#B4C7E7]/50'}`}>
              {enableThinking ? '已启用 - 展示思考过程' : '已禁用 - 快速响应'}
            </span>
          </div>

          {/* 灵值计费信息显示 */}
          {isBilling && (
            <div className={`mb-4 p-3 rounded-xl ${chatTheme.bubble.assistant.bg} ${chatTheme.bubble.assistant.border} transition-all duration-300`}>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#00C3FF]" />
                  <span className="text-[#B4C7E7]">对话时长:</span>
                  <span className="text-white font-semibold">{formatDuration(billingInfo.duration)}</span>
                </div>
                {billingInfo.consumedLingzhi > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-[#B4C7E7]">消耗灵值:</span>
                    <span className="text-red-400 font-semibold">-{billingInfo.consumedLingzhi}</span>
                  </div>
                )}
                {billingInfo.earnedLingzhi > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-[#B4C7E7]">获得灵值:</span>
                    <span className="text-green-400 font-semibold">+{billingInfo.earnedLingzhi}</span>
                  </div>
                )}
              </div>
              <p className="text-xs text-[#B4C7E7]/60 mt-2">
                计费规则：每5分钟消耗1灵值，提交反馈可获得灵值奖励
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入您的问题，灵枢将为您详细解答..."
              className={`flex-1 px-4 py-3.5 rounded-xl border outline-none transition-all duration-300 ${chatTheme.input.bg} ${chatTheme.input.border} ${chatTheme.input.focus} ${chatTheme.input.placeholder} ${chatTheme.input.text}`}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className={`px-5 py-3.5 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 ${vrTheme.button.gradient} ${vrTheme.button.glow} hover:scale-105 active:scale-95`}
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </form>
        </div>
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

      {/* 对话结束对话框 */}
      <ChatEndDialog
        open={chatEndDialogOpen}
        onClose={handleChatEndDialogClose}
        duration={billingInfo.duration}
        consumedLingzhi={billingInfo.consumedLingzhi}
        earnedLingzhi={billingInfo.earnedLingzhi}
        hasSubmittedFeedback={billingInfo.hasSubmittedFeedback}
      />
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
