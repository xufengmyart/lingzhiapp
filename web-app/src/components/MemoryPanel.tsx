import { useState } from 'react'
import { useMemory } from '../contexts/MemoryContext'
import { Brain, MessageSquare, Clock, Star, Search, X, Plus, Trash2, Edit2 } from 'lucide-react'

export const MemoryPanel = ({ userId }: { userId: number }) => {
  const {
    conversations,
    currentConversation,
    memories,
    context,
    loading,
    error,
    loadConversations,
    loadConversation,
    createConversation,
    deleteConversation,
    loadMemories,
    createMemory,
    deleteMemory,
    searchMemories,
    loadContext
  } = useMemory()

  const [activeTab, setActiveTab] = useState<'conversations' | 'memories' | 'context'>('conversations')
  const [searchQuery, setSearchQuery] = useState('')
  const [newMemoryContent, setNewMemoryContent] = useState('')
  const [newMemoryType, setNewMemoryType] = useState('general')
  const [showAddMemory, setShowAddMemory] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleLoadData = () => {
    loadConversations(userId)
    loadMemories(userId)
    loadContext(userId)
  }

  const handleCreateMemory = async () => {
    if (!newMemoryContent.trim()) return

    await createMemory(userId, newMemoryContent, newMemoryType, 3)
    setNewMemoryContent('')
    setShowAddMemory(false)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    const results = await searchMemories(userId, searchQuery)
    console.log('搜索结果:', results)
  }

  const getMemoryTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'general': '一般',
      'preference': '偏好',
      'task': '任务',
      'important': '重要',
      'fact': '事实'
    }
    return labels[type] || type
  }

  const getMemoryTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'general': 'bg-gray-100 text-gray-700',
      'preference': 'bg-blue-100 text-blue-700',
      'task': 'bg-green-100 text-green-700',
      'important': 'bg-red-100 text-red-700',
      'fact': 'bg-purple-100 text-purple-700'
    }
    return colors[type] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      {/* 头部 */}
      <div className="bg-white rounded-xl shadow-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-600" />
            对话记忆系统
          </h2>
          <button
            onClick={handleLoadData}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? '加载中...' : '刷新'}
          </button>
        </div>

        {/* 标签页 */}
        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab('conversations')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'conversations'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            对话历史
          </button>
          <button
            onClick={() => setActiveTab('memories')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'memories'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            记忆库
          </button>
          <button
            onClick={() => setActiveTab('context')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'context'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            上下文摘要
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* 对话历史 */}
      {activeTab === 'conversations' && (
        <div className="bg-white rounded-xl shadow-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">对话列表</h3>
            <button
              onClick={() => createConversation(userId, 1, '新对话')}
              className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1 text-sm"
            >
              <Plus className="w-4 h-4" />
              新对话
            </button>
          </div>

          {conversations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>暂无对话历史</p>
            </div>
          ) : (
            <div className="space-y-3">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
                    currentConversation?.id === conv.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => loadConversation(conv.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-800 mb-1">{conv.title}</h4>
                      {conv.first_message && (
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">{conv.first_message}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(conv.updated_at)}
                        </span>
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {conv.message_count} 条消息
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteConversation(conv.id)
                      }}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 记忆库 */}
      {activeTab === 'memories' && (
        <div className="bg-white rounded-xl shadow-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">记忆库</h3>
            <button
              onClick={() => setShowAddMemory(!showAddMemory)}
              className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1 text-sm"
            >
              <Plus className="w-4 h-4" />
              添加记忆
            </button>
          </div>

          {/* 搜索 */}
          <div className="flex gap-2 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索记忆..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              搜索
            </button>
          </div>

          {/* 添加记忆 */}
          {showAddMemory && (
            <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
              <textarea
                placeholder="输入记忆内容..."
                value={newMemoryContent}
                onChange={(e) => setNewMemoryContent(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-3"
                rows={3}
              />
              <div className="flex gap-2">
                <select
                  value={newMemoryType}
                  onChange={(e) => setNewMemoryType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">一般</option>
                  <option value="preference">偏好</option>
                  <option value="task">任务</option>
                  <option value="important">重要</option>
                  <option value="fact">事实</option>
                </select>
                <button
                  onClick={handleCreateMemory}
                  disabled={!newMemoryContent.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  保存
                </button>
                <button
                  onClick={() => setShowAddMemory(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          )}

          {memories.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>暂无记忆</p>
            </div>
          ) : (
            <div className="space-y-3">
              {memories.map((memory) => (
                <div
                  key={memory.id}
                  className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getMemoryTypeColor(memory.type)}`}>
                        {getMemoryTypeLabel(memory.type)}
                      </span>
                      <div className="flex items-center gap-1 text-yellow-600">
                        {[...Array(memory.importance)].map((_, i) => (
                          <Star key={i} className="w-3 h-3 fill-current" />
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">{formatDate(memory.created_at)}</span>
                      <button
                        onClick={() => deleteMemory(memory.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-700">{memory.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 上下文摘要 */}
      {activeTab === 'context' && (
        <div className="bg-white rounded-xl shadow-lg p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">对话上下文摘要</h3>

          {!context ? (
            <div className="text-center py-8 text-gray-500">
              <p>暂无上下文信息</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* 最近对话 */}
              {context.recentConversations.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    最近对话
                  </h4>
                  <div className="space-y-2">
                    {context.recentConversations.map((conv) => (
                      <div
                        key={conv.id}
                        className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                      >
                        <h5 className="font-medium text-gray-800 mb-1">{conv.title}</h5>
                        {conv.first_message && (
                          <p className="text-sm text-gray-600 line-clamp-2">{conv.first_message}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 重要记忆 */}
              {context.importantMemories.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <Star className="w-4 h-4" />
                    重要记忆
                  </h4>
                  <div className="space-y-2">
                    {context.importantMemories.map((memory) => (
                      <div
                        key={memory.id}
                        className="p-3 bg-yellow-50 rounded-lg border border-yellow-200"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getMemoryTypeColor(memory.type)}`}>
                            {getMemoryTypeLabel(memory.type)}
                          </span>
                          <div className="flex items-center gap-1 text-yellow-600">
                            {[...Array(memory.importance)].map((_, i) => (
                              <Star key={i} className="w-3 h-3 fill-current" />
                            ))}
                          </div>
                        </div>
                        <p className="text-sm text-gray-700">{memory.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
