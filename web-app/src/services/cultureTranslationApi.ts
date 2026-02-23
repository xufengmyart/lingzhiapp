/**
 * 文化转译 API 服务
 */

import api from './api'

// 类型定义
export interface TranslationProject {
  id: number
  projectCode: string
  title: string
  description: string
  projectType: string
  category: string
  difficultyLevel: string
  status: string
  requirements?: string
  exampleTemplate?: string
  baseReward: number
  maxParticipants?: number
  createdAt: string
  updatedAt: string
}

export interface TranslationTask {
  id: number
  project_id: number
  projectCode: string
  projectTitle: string
  projectType: string
  taskCode: string
  title: string
  description: string
  sourceContent: string
  sourceType: string
  targetType: string
  translationPrompt?: string
  status: string
  reward: number
  maxAttempts: number
  createdAt: string
  updatedAt: string
}

export interface TranslationWork {
  workId: number
  taskId: number
  taskTitle: string
  taskDescription: string
  translationPrompt?: string
  sourceContent: string
  sourceType: string
  targetType: string
  reward: number
  status: string
  createdAt: string
}

export interface TranslationProcess {
  processId: number
  workId: number
  status: string
  aiAssisted: boolean
  aiModel?: string
  aiTranslation?: string
  nextStep?: string
  createdAt: string
  updatedAt: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error_code?: string
}

/**
 * 获取转译项目列表
 */
export const getTranslationProjects = async () => {
  const response = await api.get<ApiResponse<{
    count: number
    data: TranslationProject[]
  }>>('/culture/translation/projects')
  return response.data
}

/**
 * 获取项目详情
 */
export const getTranslationProject = async (projectCode: string) => {
  const response = await api.get<ApiResponse<TranslationProject>>(
    `/culture/translation/projects/${projectCode}`
  )
  return response.data
}

/**
 * 获取任务列表
 */
export const getTranslationTasks = async (params?: {
  projectId?: number
  status?: string
  limit?: number
}) => {
  const response = await api.get<ApiResponse<TranslationTask[]>>(
    '/culture/translation/tasks',
    { params }
  )
  return response.data
}

/**
 * 获取任务详情
 */
export const getTranslationTask = async (taskId: number) => {
  const response = await api.get<ApiResponse<TranslationTask>>(
    `/culture/translation/tasks/${taskId}`
  )
  return response.data
}

/**
 * 开始转译 - 创建转译作品记录
 */
export const startTranslation = async (data: {
  task_id: number
  original_content: string
}) => {
  const response = await api.post<ApiResponse<TranslationWork>>(
    '/culture/translation/start',
    data
  )
  return response.data
}

/**
 * 开始转译流程 - AI辅助转译
 */
export const startTranslationProcess = async (data: {
  work_id: number
  user_input: string
}) => {
  const response = await api.post<ApiResponse<TranslationProcess>>(
    '/culture/translation/process/start',
    data
  )
  return response.data
}

/**
 * 提交作品
 */
export const submitWork = async (data: {
  work_id: number
  final_content: string
  media_urls?: string[]
}) => {
  const response = await api.post<ApiResponse<{
    workId: number
    status: string
    message: string
  }>>('/culture/translation/works/submit', data)
  return response.data
}

/**
 * 获取作品列表
 */
export const getTranslationWorks = async (params?: {
  userId?: number
  taskId?: number
  status?: string
}) => {
  const response = await api.get<ApiResponse<{
    count: number
    data: any[]
  }>>('/culture/translation/works', { params })
  return response.data
}

/**
 * 获取流程状态
 */
export const getProcessStatus = async (processId: number) => {
  const response = await api.get<ApiResponse<{
    processId: number
    status: string
    currentStep: string
    steps: any[]
  }>>(`/culture/translation/processes/${processId}/status`)
  return response.data
}

export default {
  getTranslationProjects,
  getTranslationProject,
  getTranslationTasks,
  getTranslationTask,
  startTranslation,
  startTranslationProcess,
  submitWork,
  getTranslationWorks,
  getProcessStatus,
}
