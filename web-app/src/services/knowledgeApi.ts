import api from './api'

export interface KnowledgeBase {
  id: number
  name: string
  description: string
  vector_db_id: string | null
  document_count: number
  created_at: string
  updated_at: string
}

/**
 * 知识库管理 API (v9)
 */
export const knowledgeApi = {
  /**
   * 获取知识库列表
   */
  getKnowledgeBases: async () => {
    const response = await api.get('/v9/knowledge/bases')
    return response.data
  },

  /**
   * 创建知识库
   */
  createKnowledgeBase: async (name: string, description: string = '', createdBy?: number) => {
    const response = await api.post('/v9/knowledge/bases', {
      name,
      description,
      created_by: createdBy
    })
    return response.data
  },

  /**
   * 绑定知识库到智能体
   */
  bindKnowledgeBase: async (agentId: number, kbId: number) => {
    const response = await api.post(`/v9/agent/${agentId}/bind-kb/${kbId}`)
    return response.data
  },

  /**
   * 解绑知识库
   */
  unbindKnowledgeBase: async (agentId: number, kbId: number) => {
    const response = await api.delete(`/v9/agent/${agentId}/unbind-kb/${kbId}`)
    return response.data
  }
}
