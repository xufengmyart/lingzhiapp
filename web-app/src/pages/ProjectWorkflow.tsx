import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription 
} from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Loading } from '../components/ui/Loading';
import { 
  Calendar, 
  CheckCircle, 
  Clock, 
  Play, 
  Pause,
  Plus,
  User,
  MoreVertical,
  ChevronRight,
  ChevronDown,
  Search,
  Flag,
  ListTodo,
  Activity
} from 'lucide-react';

interface Project {
  id: number;
  projectName: string;
  status: string;
}

interface Milestone {
  id: number;
  milestoneName: string;
  description: string;
  plannedDate: string;
  actualDate: string;
  status: 'pending' | 'in_progress' | 'completed' | 'delayed';
  progressPercentage: number;
  responsiblePersonId: number;
}

interface Task {
  id: number;
  taskName: string;
  description: string;
  assigneeId: number;
  assigneeName: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimatedHours: number;
  actualHours: number;
  startDate: string;
  dueDate: string;
  milestoneId: number;
}

const ProjectWorkflow: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedMilestones, setExpandedMilestones] = useState<Set<number>>(new Set());
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [taskFormData, setTaskFormData] = useState({
    taskName: '',
    description: '',
    assigneeId: 0,
    priority: 'medium' as const,
    estimatedHours: 0,
    dueDate: ''
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchMilestonesAndTasks();
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/company/projects', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success && data.data) {
        setProjects(data.data.projects || []);
        if (data.data.projects && data.data.projects.length > 0) {
          setSelectedProject(data.data.projects[0]);
        }
      }
    } catch (error) {
      console.error('获取项目列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMilestonesAndTasks = async () => {
    if (!selectedProject) return;
    
    try {
      const token = localStorage.getItem('token');
      
      const [milestoneRes, taskRes] = await Promise.all([
        fetch(`/api/projects/${selectedProject.id}/milestones`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`/api/projects/${selectedProject.id}/tasks`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      const milestoneData = await milestoneRes.json();
      const taskData = await taskRes.json();

      if (milestoneData.success) {
        setMilestones(milestoneData.data || []);
      }
      if (taskData.success) {
        setTasks(taskData.data || []);
      }
    } catch (error) {
      console.error('获取项目数据失败:', error);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProject) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/projects/${selectedProject.id}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(taskFormData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('任务创建成功');
        setShowTaskModal(false);
        resetTaskForm();
        fetchMilestonesAndTasks();
      } else {
        alert(data.message || '创建失败');
      }
    } catch (error) {
      console.error('创建任务失败:', error);
      alert('创建失败，请重试');
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, status: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/projects/${selectedProject?.id}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchMilestonesAndTasks();
      } else {
        alert(data.message || '更新失败');
      }
    } catch (error) {
      console.error('更新任务失败:', error);
    }
  };

  const resetTaskForm = () => {
    setTaskFormData({
      taskName: '',
      description: '',
      assigneeId: 0,
      priority: 'medium',
      estimatedHours: 0,
      dueDate: ''
    });
  };

  const toggleMilestone = (milestoneId: number) => {
    const newExpanded = new Set(expandedMilestones);
    if (newExpanded.has(milestoneId)) {
      newExpanded.delete(milestoneId);
    } else {
      newExpanded.add(milestoneId);
    }
    setExpandedMilestones(newExpanded);
  };

  const getMilestoneTasks = (milestoneId: number) => {
    return tasks.filter(t => t.milestoneId === milestoneId);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100', label: '待开始' },
      in_progress: { icon: Play, color: 'text-blue-600', bg: 'bg-blue-100', label: '进行中' },
      completed: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: '已完成' },
      blocked: { icon: Pause, color: 'text-red-600', bg: 'bg-red-100', label: '已阻塞' },
      delayed: { icon: Flag, color: 'text-orange-600', bg: 'bg-orange-100', label: '延期' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    if (!config) return null;
    
    const Icon = config.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        <Icon size={12} />
        {config.label}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: { color: 'text-gray-600', bg: 'bg-gray-100', label: '低' },
      medium: { color: 'text-blue-600', bg: 'bg-blue-100', label: '中' },
      high: { color: 'text-orange-600', bg: 'bg-orange-100', label: '高' },
      urgent: { color: 'text-red-600', bg: 'bg-red-100', label: '紧急' }
    };
    
    const config = priorityConfig[priority as keyof typeof priorityConfig];
    if (!config) return null;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const calculateProgress = (milestoneId: number) => {
    const milestoneTasks = getMilestoneTasks(milestoneId);
    if (milestoneTasks.length === 0) return 0;
    
    const completedTasks = milestoneTasks.filter(t => t.status === 'completed').length;
    return Math.round((completedTasks / milestoneTasks.length) * 100);
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">项目工作流</h1>
          <p className="text-gray-600 mt-1">管理项目里程碑和任务，跟踪项目进度</p>
        </div>
        <Button
          onClick={() => setShowTaskModal(true)}
          disabled={!selectedProject}
          className="flex items-center gap-2"
        >
          <Plus size={18} />
          创建任务
        </Button>
      </div>

      {/* 项目选择 */}
      {projects.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-700">选择项目:</label>
              <select
                value={selectedProject?.id || ''}
                onChange={(e) => setSelectedProject(projects.find(p => p.id === Number(e.target.value)) || null)}
                className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {projects.map(project => (
                  <option key={project.id} value={project.id}>
                    {project.projectName}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>
      )}

      {!selectedProject && projects.length > 0 && (
        <div className="text-center py-12 text-gray-500">
          请选择一个项目查看工作流
        </div>
      )}

      {selectedProject && (
        <>
          {/* 项目统计 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">里程碑</p>
                    <p className="text-2xl font-bold mt-1">{milestones.length}</p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Flag size={24} className="text-blue-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">总任务数</p>
                    <p className="text-2xl font-bold mt-1">{tasks.length}</p>
                  </div>
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <ListTodo size={24} className="text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">已完成</p>
                    <p className="text-2xl font-bold mt-1">{tasks.filter(t => t.status === 'completed').length}</p>
                  </div>
                  <div className="p-3 bg-green-100 rounded-lg">
                    <CheckCircle size={24} className="text-green-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">完成率</p>
                    <p className="text-2xl font-bold mt-1">
                      {tasks.length > 0 ? Math.round((tasks.filter(t => t.status === 'completed').length / tasks.length) * 100) : 0}%
                    </p>
                  </div>
                  <div className="p-3 bg-orange-100 rounded-lg">
                    <Activity size={24} className="text-orange-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 里程碑列表 */}
          <div className="space-y-4">
            {milestones.map((milestone, index) => {
              const milestoneTasks = getMilestoneTasks(milestone.id);
              const isExpanded = expandedMilestones.has(milestone.id);
              const progress = calculateProgress(milestone.id);

              return (
                <Card key={milestone.id} className="overflow-hidden">
                  <CardHeader 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleMilestone(milestone.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-lg">{milestone.milestoneName}</CardTitle>
                            {getStatusBadge(milestone.status)}
                          </div>
                          <CardDescription className="mt-1">
                            {milestone.description}
                          </CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-sm text-gray-600">
                            {milestoneTasks.length} 个任务 · {progress}%
                          </p>
                          <p className="text-xs text-gray-500">
                            计划: {milestone.plannedDate?.split('T')[0]}
                          </p>
                        </div>
                        {isExpanded ? (
                          <ChevronDown className="text-gray-400" size={20} />
                        ) : (
                          <ChevronRight className="text-gray-400" size={20} />
                        )}
                      </div>
                    </div>
                    {progress > 0 && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </CardHeader>

                  {isExpanded && (
                    <CardContent className="border-t">
                      <div className="space-y-3">
                        {milestoneTasks.length > 0 ? (
                          milestoneTasks.map(task => (
                            <Card key={task.id} className="border-l-4 border-l-blue-500">
                              <CardContent className="p-4">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                      <h4 className="font-semibold">{task.taskName}</h4>
                                      {getPriorityBadge(task.priority)}
                                      {getStatusBadge(task.status)}
                                    </div>
                                    <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                      <span className="flex items-center gap-1">
                                        <User size={12} />
                                        {task.assigneeName || '未分配'}
                                      </span>
                                      <span className="flex items-center gap-1">
                                        <Calendar size={12} />
                                        截止: {task.dueDate?.split('T')[0] || '无'}
                                      </span>
                                      <span>
                                        工时: {task.actualHours || 0}/{task.estimatedHours}h
                                      </span>
                                    </div>
                                  </div>
                                  {task.status !== 'completed' && (
                                    <select
                                      value={task.status}
                                      onChange={(e) => handleUpdateTaskStatus(task.id, e.target.value)}
                                      className="ml-4 px-3 py-1 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                      <option value="pending">待开始</option>
                                      <option value="in_progress">进行中</option>
                                      <option value="completed">已完成</option>
                                      <option value="blocked">已阻塞</option>
                                    </select>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          ))
                        ) : (
                          <div className="text-center py-6 text-gray-500 text-sm">
                            暂无任务，点击上方"创建任务"按钮添加
                          </div>
                        )}
                      </div>
                    </CardContent>
                  )}
                </Card>
              );
            })}

            {milestones.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                暂无里程碑，请先在后台创建项目里程碑
              </div>
            )}
          </div>

          {/* 未分配里程碑的任务 */}
          {tasks.filter(t => !t.milestoneId).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ListTodo size={20} />
                  未分配里程碑的任务
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {tasks.filter(t => !t.milestoneId).map(task => (
                    <Card key={task.id} className="border-l-4 border-l-gray-400">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold">{task.taskName}</h4>
                              {getPriorityBadge(task.priority)}
                              {getStatusBadge(task.status)}
                            </div>
                            <p className="text-sm text-gray-600">{task.description}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* 创建任务弹窗 */}
      {showTaskModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg">
            <CardHeader>
              <CardTitle>创建任务</CardTitle>
              <CardDescription>
                为项目 {selectedProject?.projectName} 创建新任务
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleCreateTask} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    任务名称 *
                  </label>
                  <input
                    type="text"
                    required
                    value={taskFormData.taskName}
                    onChange={(e) => setTaskFormData({...taskFormData, taskName: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    任务描述
                  </label>
                  <textarea
                    value={taskFormData.description}
                    onChange={(e) => setTaskFormData({...taskFormData, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      负责人ID
                    </label>
                    <input
                      type="number"
                      value={taskFormData.assigneeId}
                      onChange={(e) => setTaskFormData({...taskFormData, assigneeId: Number(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      优先级
                    </label>
                    <select
                      value={taskFormData.priority}
                      onChange={(e) => setTaskFormData({...taskFormData, priority: e.target.value as any})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">低</option>
                      <option value="medium">中</option>
                      <option value="high">高</option>
                      <option value="urgent">紧急</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      预估工时(小时)
                    </label>
                    <input
                      type="number"
                      value={taskFormData.estimatedHours}
                      onChange={(e) => setTaskFormData({...taskFormData, estimatedHours: Number(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      截止日期
                    </label>
                    <input
                      type="date"
                      value={taskFormData.dueDate}
                      onChange={(e) => setTaskFormData({...taskFormData, dueDate: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowTaskModal(false);
                      resetTaskForm();
                    }}
                  >
                    取消
                  </Button>
                  <Button type="submit">创建</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ProjectWorkflow;
