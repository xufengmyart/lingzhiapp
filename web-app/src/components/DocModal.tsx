import { useState, useEffect } from 'react'
import { X, ArrowLeft, BookOpen, Clock } from 'lucide-react'

interface DocDetail {
  id: number
  title: string
  slug: string
  category: string
  description: string
  icon: string
  content: string
  is_published: boolean
  created_at: string
  updated_at: string
}

interface DocModalProps {
  slug?: string
  onClose: () => void
}

const DocModal: React.FC<DocModalProps> = ({ slug, onClose }) => {
  const [doc, setDoc] = useState<DocDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (slug) {
      loadDoc(slug)
    }
  }, [slug])

  const loadDoc = async (docSlug: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api'}/docs/${docSlug}`)
      const data = await response.json()

      if (data.success) {
        setDoc(data.data)
      } else {
        setError(data.message || '加载文档失败')
      }
    } catch (err) {
      setError('网络错误，请稍后重试')
      console.error('加载文档失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const renderMarkdown = (content: string) => {
    // 确保content是字符串
    if (!content || typeof content !== 'string') {
      return '<p class="text-gray-400">暂无内容</p>'
    }

    // 简单的Markdown渲染
    return content
      .replace(/^# (.*)/gm, '<h1 class="text-2xl font-bold text-white mb-4 mt-6">$1</h1>')
      .replace(/^## (.*)/gm, '<h2 class="text-xl font-bold text-[#00C3FF] mb-3 mt-5">$1</h2>')
      .replace(/^### (.*)/gm, '<h3 class="text-lg font-bold text-[#47D1FF] mb-2 mt-4">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="bg-[#00C3FF]/20 text-cyan-300 px-1.5 py-0.5 rounded text-sm">$1</code>')
      .replace(/^- (.*)/gm, '<li class="text-gray-300 ml-4 mb-1.5">$1</li>')
      .replace(/^(\d+)\. (.*)/gm, '<li class="text-gray-300 ml-4 mb-1.5">$2</li>')
      .replace(/\n\n/g, '</p><p class="mb-3">')
      .replace(/^([^<])/gm, '<p class="mb-3">$1')
  }

  if (!slug) {
    return null
  }

  return (
    <div className="fixed inset-0 z-[999999] flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      ></div>

      {/* 模态框内容 */}
      <div className="relative bg-gradient-to-br from-[#0A0D18] via-[#121A2F] to-[#0A0D18] border border-[#00C3FF]/30 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* 关闭按钮 */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-[#00C3FF]/20 hover:bg-[#00C3FF]/30 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-[#00C3FF]" />
        </button>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-cyan-400/30 rounded-full"></div>
              <div className="w-16 h-16 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin absolute top-0 left-0"></div>
            </div>
          </div>
        ) : error || !doc ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-400 mb-2">加载失败</h2>
              <p className="text-gray-500">{error || '文档不存在'}</p>
            </div>
          </div>
        ) : (
          <>
            {/* 文档标题区域 */}
            <div className="p-6 border-b border-[#00C3FF]/20">
              <div className="flex items-start gap-4">
                <div className="text-4xl flex-shrink-0">{doc.icon}</div>
                <div className="flex-1 min-w-0">
                  <h1 className="text-2xl font-bold text-white mb-2 truncate">{doc.title}</h1>
                  <p className="text-gray-400 text-sm mb-3 line-clamp-2">{doc.description}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>更新于 {new Date(doc.updated_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 文档内容区域 */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="prose prose-invert max-w-none">
                <div
                  className="text-gray-300 leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: renderMarkdown(doc.content)
                  }}
                />
              </div>
            </div>

            {/* 底部按钮 */}
            <div className="p-4 border-t border-[#00C3FF]/20 bg-[#0A0D18]/50">
              <button
                onClick={() => window.location.href = '/docs'}
                className="flex items-center gap-2 px-4 py-2 bg-[#00C3FF]/20 hover:bg-[#00C3FF]/30 text-[#00C3FF] rounded-lg transition-colors text-sm"
              >
                <BookOpen className="w-4 h-4" />
                查看所有文档
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default DocModal
