import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, ArrowLeft, Save, X, Upload, FileText, FolderOpen } from 'lucide-react'
import MobileRichEditor from '../components/MobileRichEditor'
import api from '../services/api'

interface KnowledgeBase {
  id: number
  name: string
  description: string
  vector_db_id: string
  document_count: number
  created_at: string
  updated_at: string
}

interface Document {
  id: number
  title: string
  content: string
  file_type: string
  file_size: number
  embedding_status: string
  created_at: string
}

const KnowledgeManagement = () => {
  const navigate = useNavigate()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedKB, setSelectedKB] = useState<KnowledgeBase | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  })

  // 文档表单
  const [docForm, setDocForm] = useState({
    title: '',
    content: ''
  })
  const [isAddingDoc, setIsAddingDoc] = useState(false)
  const [documents, setDocuments] = useState<Document[]>([])

  useEffect(() => {
    fetchKnowledgeBases()
  }, [])

  const fetchKnowledgeBases = async () => {
    try {
      setLoading(true)
      const response = await api.get('/knowledge')
      if (response.data.success) {
        setKnowledgeBases(response.data.data)
      }
    } catch (err) {
      setError('获取知识库列表失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchDocuments = async (kbId: number) => {
    try {
      const response = await api.get(`/knowledge/${kbId}/documents`)
      if (response.data.success) {
        setDocuments(response.data.data.documents || [])
      }
    } catch (err) {
      setError('获取文档列表失败')
    }
  }

  const handleCreate = () => {
    setIsCreating(true)
    setFormData({ name: '', description: '' })
    setSelectedKB(null)
  }

  const handleSelectKB = (kb: KnowledgeBase) => {
    setSelectedKB(kb)
    setIsCreating(false)
    fetchDocuments(kb.id)
  }

  const handleDelete = async (kbId: number) => {
    if (!confirm('确定要删除这个知识库吗？所有文档也将被删除。')) {
      return
    }

    try {
      const response = await api.delete(`/knowledge/${kbId}`)
      if (response.data.success) {
        setMessage('知识库删除成功')
        if (selectedKB?.id === kbId) {
          setSelectedKB(null)
          setDocuments([])
        }
        fetchKnowledgeBases()
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleSubmitKB = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const response = await api.post('/knowledge', formData)
      if (response.data.success) {
        setMessage('知识库创建成功')
        setIsCreating(false)
        fetchKnowledgeBases()
      } else {
        setError(response.data.message || '创建失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '创建失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateKB = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    if (!selectedKB) return

    try {
      const response = await api.put(`/knowledge/${selectedKB.id}`, formData)
      if (response.data.success) {
        setMessage('知识库更新成功')
        fetchKnowledgeBases()
        const updated = knowledgeBases.find(kb => kb.id === selectedKB.id)
        if (updated) {
          setSelectedKB({ ...updated, ...formData })
        }
      } else {
        setError(response.data.message || '更新失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '更新失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAddDocument = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    if (!selectedKB) return

    try {
      const response = await api.post(`/knowledge/${selectedKB.id}/documents`, docForm)
      if (response.data.success) {
        setMessage('文档添加成功')
        setDocForm({ title: '', content: '' })
        setIsAddingDoc(false)
        fetchDocuments(selectedKB.id)
        fetchKnowledgeBases()
      } else {
        setError(response.data.message || '添加失败')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '添加失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDocument = async (docId: number) => {
    if (!selectedKB) return
    if (!confirm('确定要删除这个文档吗？')) {
      return
    }

    try {
      const response = await api.delete(`/knowledge/${selectedKB.id}/documents/${docId}`)
      if (response.data.success) {
        setMessage('文档删除成功')
        fetchDocuments(selectedKB.id)
        fetchKnowledgeBases()
      } else {
        setError(response.data.message || '删除失败')
      }
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleCancel = () => {
    setIsCreating(false)
    setSelectedKB(null)
    setError('')
    setMessage('')
    setDocuments([])
  }

  if (loading && knowledgeBases.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/admin')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回后台
          </button>
          <h1 className="text-xl font-bold text-gray-900">知识库管理</h1>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            创建知识库
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* 提示信息 */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {error}
          </div>
        )}
        {message && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-600">
            {message}
          </div>
        )}

        {/* 创建/编辑知识库表单 */}
        {(isCreating || selectedKB) && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                {isCreating ? '创建知识库' : '编辑知识库'}
              </h2>
              <button
                onClick={handleCancel}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <form onSubmit={isCreating ? handleSubmitKB : handleUpdateKB} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  知识库名称 *
                </label>
                <input
                  type="text"
                  value={formData.name || (selectedKB?.name || '')}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入知识库名称"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述
                </label>
                <textarea
                  value={formData.description || (selectedKB?.description || '')}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入知识库描述"
                  rows={3}
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Save className="w-5 h-5 mr-2" />
                  {loading ? '保存中...' : '保存'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300"
                >
                  取消
                </button>
              </div>
            </form>

            {/* 文档管理 */}
            {!isCreating && selectedKB && (
              <div className="mt-8 pt-8 border-t">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    文档列表 ({documents.length})
                  </h3>
                  {!isAddingDoc && (
                    <button
                      onClick={() => setIsAddingDoc(true)}
                      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      添加文档
                    </button>
                  )}
                </div>

                {/* 添加文档表单 */}
                {isAddingDoc && (
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <form onSubmit={handleAddDocument} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          文档标题
                        </label>
                        <input
                          type="text"
                          value={docForm.title}
                          onChange={(e) => setDocForm({ ...docForm, title: e.target.value })}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="请输入文档标题"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          文档内容
                        </label>
                        <MobileRichEditor
                          value={docForm.content}
                          onChange={(value) => setDocForm({ ...docForm, content: value })}
                          placeholder="请输入文档内容..."
                          height="200px"
                        />
                      </div>

                      <div className="flex gap-3">
                        <button
                          type="submit"
                          disabled={loading}
                          className="flex-1 flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          {loading ? '添加中...' : '添加'}
                        </button>
                        <button
                          type="button"
                          onClick={() => setIsAddingDoc(false)}
                          className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300"
                        >
                          取消
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* 文档列表 */}
                {documents.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>暂无文档</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {documents.map((doc) => (
                      <div key={doc.id} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 mb-1">{doc.title}</h4>
                            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                              {doc.content.substring(0, 150)}...
                            </p>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <span>{doc.file_type}</span>
                              <span>{(doc.file_size / 1024).toFixed(2)} KB</span>
                              <span>{new Date(doc.created_at).toLocaleString('zh-CN')}</span>
                            </div>
                          </div>
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="ml-4 p-2 text-red-600 hover:bg-red-100 rounded-lg"
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
          </div>
        )}

        {/* 知识库列表 */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              知识库列表 ({knowledgeBases.length})
            </h2>
          </div>

          {knowledgeBases.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FolderOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">暂无知识库</p>
              <p className="text-sm">点击上方"创建知识库"开始</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {knowledgeBases.map((kb) => (
                <div
                  key={kb.id}
                  onClick={() => handleSelectKB(kb)}
                  className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {kb.name}
                      </h3>
                      {kb.description && (
                        <p className="text-gray-600 text-sm mb-2">{kb.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{kb.document_count} 个文档</span>
                        <span>创建于 {new Date(kb.created_at).toLocaleString('zh-CN')}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(kb.id)
                        }}
                        className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200"
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
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

export default KnowledgeManagement
