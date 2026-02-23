import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useMemory } from '../contexts/MemoryContext'
import { ChatProvider, useChat } from '../contexts/ChatContext'
import { MemoryPanel } from '../components/MemoryPanel'
import { Brain, MessageSquare, ArrowRight, RefreshCw, Settings } from 'lucide-react'

const ChatWithMemory = () => {
  const { user } = useAuth()
  const { enableMemory, setEnableMemory, messages, loading, sendMessage } = useChat()
  const [input, setInput] = useState('')

  const handleSend = async () => {
    if (!input.trim() || loading) return
    await sendMessage(input)
    setInput('')
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：对话区域 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* 头部 */}
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">智能对话</h2>
                  <p className="text-sm text-gray-500">AI 助手</p>
                </div>
              </div>
              <button
                onClick={() => setEnableMemory(!enableMemory)}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                  enableMemory ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}
              >
                <Brain className="w-4 h-4" />
                {enableMemory ? '记忆已启用' : '启用记忆'}
              </button>
            </div>

            {/* 消息列表 */}
            <div className="h-[500px] overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">开始你的对话</p>
                  <p className="text-sm mt-2">
                    {enableMemory ? '记忆功能已启用，我会记住我们的对话' : '启用记忆功能以获得更好的体验'}
                  </p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={message.id || index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.isError
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs mt-2 opacity-70">
                        {message.timestamp?.toLocaleTimeString('zh-CN', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                ))
              )}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="flex items-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-gray-600" />
                      <span className="text-gray-600">思考中...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 输入区域 */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder={enableMemory ? '输入消息...（记忆已启用）' : '输入消息...'}
                  disabled={loading}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <span>发送</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：记忆管理 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                记忆管理
              </h2>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              <MemoryPanel userId={user?.id || 1} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 包装组件以提供所有必要的 Context
export default function ChatMemoryPage() {
  const { user } = useAuth()

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">请先登录</h2>
          <p className="text-yellow-700">登录后使用对话记忆功能</p>
        </div>
      </div>
    )
  }

  return (
    <ChatProvider userId={user.id}>
      <ChatWithMemory />
    </ChatProvider>
  )
}
