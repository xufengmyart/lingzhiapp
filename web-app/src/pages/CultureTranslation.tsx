import { useState, useEffect } from 'react'
import { BookOpen, ChevronRight, Sparkles, Target, ArrowRight, Database, Layers, Search, Filter, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import cultureTranslationApi, { TranslationProject, TranslationTask, TranslationWork, TranslationProcess } from '../services/cultureTranslationApi'

const CultureTranslation = () => {
  // 状态管理
  const [projects, setProjects] = useState<TranslationProject[]>([])
  const [tasks, setTasks] = useState<TranslationTask[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 选中状态
  const [selectedProject, setSelectedProject] = useState<TranslationProject | null>(null)
  const [selectedTask, setSelectedTask] = useState<TranslationTask | null>(null)
  const [activeTab, setActiveTab] = useState<'projects' | 'tasks' | 'work' | 'result'>('projects')

  // 转译相关状态
  const [originalContent, setOriginalContent] = useState('')
  const [userInput, setUserInput] = useState('')
  const [currentWork, setCurrentWork] = useState<TranslationWork | null>(null)
  const [currentProcess, setCurrentProcess] = useState<TranslationProcess | null>(null)

  // 步骤状态
  const steps = [
    { id: 1, title: '选择项目', icon: Database, description: '选择要参与的转译项目' },
    { id: 2, title: '领取任务', icon: Target, description: '选择并领取转译任务' },
    { id: 3, title: '输入内容', icon: Sparkles, description: '输入需要转译的内容' },
    { id: 4, title: 'AI转译', icon: Layers, description: 'AI辅助完成转译' },
  ]

  const currentStep = activeTab === 'projects' ? 1 :
                      activeTab === 'tasks' ? 2 :
                      activeTab === 'work' ? 3 : 4

  // 加载项目列表
  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await cultureTranslationApi.getTranslationProjects()
      if (response.success && response.data?.data) {
        setProjects(response.data.data)
      } else {
        setError(response.message || '加载项目失败')
      }
    } catch (err: any) {
      setError(err.message || '网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  // 选择项目并加载任务
  const selectProject = async (project: TranslationProject) => {
    setSelectedProject(project)
    setActiveTab('tasks')
    setLoading(true)
    try {
      const response = await cultureTranslationApi.getTranslationTasks({
        projectId: project.id,
        status: 'available'
      })
      if (response.success && response.data) {
        setTasks(response.data)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // 选择任务并开始转译
  const selectTaskAndStart = async (task: TranslationTask) => {
    setSelectedTask(task)
    setActiveTab('work')
  }

  // 开始转译 - 创建作品记录
  const handleStartTranslation = async () => {
    if (!selectedTask) return
    if (!originalContent.trim()) {
      setError('请输入需要转译的内容')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await cultureTranslationApi.startTranslation({
        task_id: selectedTask.id,
        original_content: originalContent
      })

      if (response.success && response.data) {
        setCurrentWork(response.data)
        setActiveTab('result')
      } else {
        setError(response.message || '创建作品失败')
      }
    } catch (err: any) {
      setError(err.message || '开始转译失败')
    } finally {
      setLoading(false)
    }
  }

  // 开始转译流程 - AI辅助转译
  const handleStartProcess = async () => {
    if (!currentWork) return
    if (!userInput.trim()) {
      setError('请输入转译要求或提示')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await cultureTranslationApi.startTranslationProcess({
        work_id: currentWork.workId,
        user_input: userInput
      })

      if (response.success && response.data) {
        setCurrentProcess(response.data)
      } else {
        setError(response.message || 'AI转译失败')
      }
    } catch (err: any) {
      setError(err.message || 'AI转译失败')
    } finally {
      setLoading(false)
    }
  }

  // 重置流程
  const resetProcess = () => {
    setSelectedProject(null)
    setSelectedTask(null)
    setCurrentWork(null)
    setCurrentProcess(null)
    setOriginalContent('')
    setUserInput('')
    setTasks([])
    setActiveTab('projects')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0D18] via-[#121A2F] to-[#0A0D18]">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0A0D18] via-[#1A2332] to-[#0A0D18] border-b border-[#00C3FF]/20 pt-20 pb-8">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
              文化转译工作台
            </h1>
            <p className="text-[#B4C7E7] text-lg">
              使用AI辅助将传统文化元素数字化转译
            </p>
          </div>

          {/* 步骤进度 */}
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                const Icon = step.icon
                const isCompleted = currentStep > step.id
                const isCurrent = currentStep === step.id

                return (
                  <div key={step.id} className="flex-1 flex items-center">
                    <div className="flex flex-col items-center flex-1">
                      <div
                        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                          isCompleted
                            ? 'bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-white'
                            : isCurrent
                            ? 'bg-[#00C3FF]/20 border-2 border-[#00C3FF] text-[#00C3FF]'
                            : 'bg-[#1A2332] border-2 border-[#00C3FF]/20 text-[#B4C7E7]'
                        }`}
                      >
                        {isCompleted ? (
                          <CheckCircle2 className="w-6 h-6" />
                        ) : (
                          <Icon className="w-6 h-6" />
                        )}
                      </div>
                      <div className={`mt-2 text-sm font-medium ${
                        isCurrent ? 'text-[#00C3FF]' : isCompleted ? 'text-white' : 'text-[#B4C7E7]'
                      }`}>
                        {step.title}
                      </div>
                    </div>
                    {index < steps.length - 1 && (
                      <div
                        className={`flex-1 h-0.5 mx-2 ${
                          isCompleted ? 'bg-gradient-to-r from-[#00C3FF] to-[#00E0FF]' : 'bg-[#00C3FF]/20'
                        }`}
                      />
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-400 font-medium">错误</p>
              <p className="text-red-400/80 text-sm">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-300"
            >
              ✕
            </button>
          </div>
        )}

        {/* Step 1: 选择项目 */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">选择转译项目</h2>
              <button
                onClick={loadProjects}
                className="text-[#00C3FF] hover:text-[#00E0FF] flex items-center gap-2"
              >
                <Database className="w-4 h-4" />
                刷新列表
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-[#00C3FF] animate-spin" />
              </div>
            ) : projects.length === 0 ? (
              <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-8 text-center">
                <Target className="w-12 h-12 text-[#00C3FF]/40 mx-auto mb-4" />
                <p className="text-[#B4C7E7]">暂无可用的转译项目</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => selectProject(project)}
                    className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6 cursor-pointer hover:border-[#00C3FF]/50 hover:shadow-lg hover:shadow-[#00C3FF]/10 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-xl font-bold text-white">{project.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        project.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {project.status === 'active' ? '进行中' : '已暂停'}
                      </span>
                    </div>

                    <p className="text-[#B4C7E7] text-sm mb-4 line-clamp-2">
                      {project.description}
                    </p>

                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-[#00C3FF]" />
                        <span className="text-[#B4C7E7]">{project.category}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-[#00C3FF]" />
                        <span className="text-[#00C3FF] font-semibold">
                          {project.baseReward} 灵值
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-[#00C3FF]/10 flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded ${
                        project.difficultyLevel === 'easy' ? 'bg-green-500/20 text-green-400' :
                        project.difficultyLevel === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {project.difficultyLevel === 'easy' ? '简单' :
                         project.difficultyLevel === 'medium' ? '中等' : '困难'}
                      </span>
                      <ArrowRight className="w-5 h-5 text-[#00C3FF]" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: 选择任务 */}
        {activeTab === 'tasks' && selectedProject && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setActiveTab('projects')}
                className="text-[#B4C7E7] hover:text-white flex items-center gap-2"
              >
                <ChevronRight className="w-4 h-4 rotate-180" />
                返回项目列表
              </button>
              <h2 className="text-2xl font-bold text-white">
                {selectedProject.title} - 选择任务
              </h2>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-[#00C3FF] animate-spin" />
              </div>
            ) : tasks.length === 0 ? (
              <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-8 text-center">
                <Target className="w-12 h-12 text-[#00C3FF]/40 mx-auto mb-4" />
                <p className="text-[#B4C7E7]">该项目暂无可用的任务</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    onClick={() => selectTaskAndStart(task)}
                    className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6 cursor-pointer hover:border-[#00C3FF]/50 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white">{task.title}</h3>
                        <p className="text-[#B4C7E7] text-sm mt-1">{task.taskCode}</p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        task.status === 'available' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {task.status === 'available' ? '可领取' : '不可用'}
                      </span>
                    </div>

                    <p className="text-[#B4C7E7] text-sm mb-4">
                      {task.description}
                    </p>

                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-[#00C3FF]" />
                        <span className="text-[#B4C7E7]">{task.sourceType} → {task.targetType}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-[#00C3FF]" />
                        <span className="text-[#00C3FF] font-semibold">
                          {task.reward} 灵值
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-[#00C3FF]/10 flex items-center justify-end">
                      <button className="bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-[#0A0D18] font-semibold py-2 px-4 rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        领取任务
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 3: 输入内容 */}
        {activeTab === 'work' && selectedTask && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setActiveTab('tasks')}
                className="text-[#B4C7E7] hover:text-white flex items-center gap-2"
              >
                <ChevronRight className="w-4 h-4 rotate-180" />
                返回任务列表
              </button>
              <h2 className="text-2xl font-bold text-white">
                {selectedTask.title} - 输入内容
              </h2>
            </div>

            {/* 任务信息 */}
            <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-3">任务信息</h3>
              <p className="text-[#B4C7E7] mb-4">{selectedTask.description}</p>
              {selectedTask.translationPrompt && (
                <div className="bg-[#0A0D18] rounded-lg p-4">
                  <p className="text-[#00C3FF] text-sm mb-2">转译提示</p>
                  <p className="text-[#B4C7E7] text-sm">{selectedTask.translationPrompt}</p>
                </div>
              )}
            </div>

            {/* 输入内容 */}
            <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6">
              <label className="block text-lg font-bold text-white mb-3">
                原始内容
              </label>
              <textarea
                value={originalContent}
                onChange={(e) => setOriginalContent(e.target.value)}
                placeholder="请输入需要转译的原始内容..."
                className="w-full h-48 bg-[#0A0D18] border border-[#00C3FF]/20 rounded-lg p-4 text-[#B4C7E7] placeholder-[#B4C7E7]/50 resize-none focus:outline-none focus:border-[#00C3FF]"
              />
            </div>

            {/* 操作按钮 */}
            <div className="flex items-center gap-4">
              <button
                onClick={resetProcess}
                className="flex-1 bg-[#121A2F] border border-[#00C3FF]/20 text-white py-3 rounded-lg hover:border-[#00C3FF]/50 transition-all"
              >
                取消
              </button>
              <button
                onClick={handleStartTranslation}
                disabled={loading || !originalContent.trim()}
                className="flex-1 bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-[#0A0D18] font-semibold py-3 rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    处理中...
                  </>
                ) : (
                  <>
                    <ArrowRight className="w-5 h-5" />
                    开始转译
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: AI转译结果 */}
        {activeTab === 'result' && currentWork && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setActiveTab('work')}
                className="text-[#B4C7E7] hover:text-white flex items-center gap-2"
              >
                <ChevronRight className="w-4 h-4 rotate-180" />
                返回修改内容
              </button>
              <h2 className="text-2xl font-bold text-white">
                AI 辅助转译
              </h2>
            </div>

            {/* 作品信息 */}
            <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">作品信息</h3>
                <span className="text-[#00C3FF] font-semibold">
                  {currentWork.reward} 灵值奖励
                </span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-[#B4C7E7]">任务：</span>
                  <span className="text-white">{currentWork.taskTitle}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#B4C7E7]">类型：</span>
                  <span className="text-white">{currentWork.sourceType} → {currentWork.targetType}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#B4C7E7]">状态：</span>
                  <span className={`font-semibold ${
                    currentWork.status === 'in_progress' ? 'text-yellow-400' :
                    currentWork.status === 'completed' ? 'text-green-400' :
                    'text-[#B4C7E7]'
                  }`}>
                    {currentWork.status === 'in_progress' ? '进行中' :
                     currentWork.status === 'completed' ? '已完成' :
                     currentWork.status}
                  </span>
                </div>
              </div>
            </div>

            {/* 输入原始内容显示 */}
            <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-3">原始内容</h3>
              <p className="text-[#B4C7E7] whitespace-pre-wrap">{currentWork.sourceContent}</p>
            </div>

            {/* AI转译输入 */}
            {!currentProcess && (
              <div className="bg-gradient-to-br from-[#00C3FF]/10 to-[#00E0FF]/5 border border-[#00C3FF]/30 rounded-lg p-6">
                <label className="block text-lg font-bold text-white mb-3 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-[#00C3FF]" />
                  AI 转译提示
                </label>
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="请输入转译要求或提示，例如：请将这段内容转化为现代艺术形式，强调其文化内涵..."
                  className="w-full h-32 bg-[#0A0D18]/50 border border-[#00C3FF]/30 rounded-lg p-4 text-[#B4C7E7] placeholder-[#B4C7E7]/50 resize-none focus:outline-none focus:border-[#00C3FF] mb-4"
                />
                <button
                  onClick={handleStartProcess}
                  disabled={loading || !userInput.trim()}
                  className="w-full bg-gradient-to-r from-[#00C3FF] to-[#00E0FF] text-[#0A0D18] font-semibold py-3 rounded-lg hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      AI 转译中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      开始 AI 转译
                    </>
                  )}
                </button>
              </div>
            )}

            {/* AI转译结果 */}
            {currentProcess && (
              <div className="bg-gradient-to-br from-[#00C3FF]/10 to-[#00E0FF]/5 border border-[#00C3FF]/30 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-[#00C3FF]" />
                    AI 转译结果
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[#B4C7E7] bg-[#00C3FF]/10 px-2 py-1 rounded-full">
                      {currentProcess.aiModel}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      currentProcess.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {currentProcess.status === 'completed' ? '已完成' : '处理中'}
                    </span>
                  </div>
                </div>

                <div className="bg-[#0A0D18]/70 rounded-lg p-6 mb-4">
                  <p className="text-[#B4C7E7] whitespace-pre-wrap leading-relaxed">
                    {currentProcess.aiTranslation}
                  </p>
                </div>

                {currentProcess.nextStep && (
                  <div className="bg-[#0A0D18]/50 border border-[#00C3FF]/20 rounded-lg p-4">
                    <p className="text-[#00C3FF] text-sm font-medium mb-1">下一步操作</p>
                    <p className="text-[#B4C7E7] text-sm">{currentProcess.nextStep}</p>
                  </div>
                )}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex items-center gap-4">
              <button
                onClick={resetProcess}
                className="flex-1 bg-[#121A2F] border border-[#00C3FF]/20 text-white py-3 rounded-lg hover:border-[#00C3FF]/50 transition-all"
              >
                重新开始
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CultureTranslation
