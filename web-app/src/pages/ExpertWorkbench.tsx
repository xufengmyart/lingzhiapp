import React, { useState, useEffect } from 'react';

interface Task {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  reward_contribution: number;
  reward_lingzhi: number;
  status: string;
  claimed_by: number | null;
  submitted_at: string | null;
  completed_at: string | null;
  created_at: string;
}

interface AIGCWork {
  id: number;
  expert_id: number;
  title: string;
  description: string;
  work_type: string;
  image_url: string;
  reward_contribution: number;
  reward_lingzhi: number;
  status: string;
  created_at: string;
}

const ExpertWorkbench: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tasks' | 'works'>('tasks');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [aigcWorks, setAigcWorks] = useState<AIGCWork[]>([]);
  const [loading, setLoading] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showWorkModal, setShowWorkModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [userRole, setUserRole] = useState<string>('');
  const [userId, setUserId] = useState<string>('');
  const [taskFilter, setTaskFilter] = useState<'all' | 'available' | 'claimed' | 'submitted'>('all');
  const [submissionData, setSubmissionData] = useState({
    submission_url: '',
    notes: ''
  });
  const [workFormData, setWorkFormData] = useState({
    title: '',
    description: '',
    work_type: '',
    image_url: ''
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  useEffect(() => {
    const role = localStorage.getItem('userRole') || '';
    const uid = localStorage.getItem('userId') || '';
    setUserRole(role);
    setUserId(uid);
    
    if (role === 'expert' || role === 'admin') {
      fetchTasks();
      fetchAIGCWorks();
    }
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/tasks`, {
        headers: {
          'X-User-ID': userId
        }
      });
      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('获取任务列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIGCWorks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/aigc-works`, {
        headers: {
          'X-User-ID': userId
        }
      });
      const data = await response.json();
      setAigcWorks(data.works || []);
    } catch (error) {
      console.error('获取AIGC作品列表失败:', error);
    }
  };

  const handleClaimTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/tasks/${taskId}/claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        }
      });
      if (response.ok) {
        alert('任务承接成功！');
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '承接失败');
      }
    } catch (error) {
      console.error('承接任务失败:', error);
    }
  };

  const handleSubmitTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/tasks/${taskId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify(submissionData)
      });
      if (response.ok) {
        alert('任务提交成功！');
        setShowTaskModal(false);
        setSelectedTask(null);
        setSubmissionData({ submission_url: '', notes: '' });
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '提交失败');
      }
    } catch (error) {
      console.error('提交任务失败:', error);
    }
  };

  const handleCompleteTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        }
      });
      if (response.ok) {
        alert('任务审核完成！');
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '审核失败');
      }
    } catch (error) {
      console.error('审核任务失败:', error);
    }
  };

  const handleOpenTaskSubmit = (task: Task) => {
    setSelectedTask(task);
    setShowTaskModal(true);
  };

  const handleCreateWork = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/aigc-works`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify(workFormData)
      });
      if (response.ok) {
        alert('作品上传成功！已获得200贡献值+100灵值奖励');
        setShowWorkModal(false);
        setWorkFormData({
          title: '',
          description: '',
          work_type: '',
          image_url: ''
        });
        fetchAIGCWorks();
      } else {
        const error = await response.json();
        alert(error.error || '上传失败');
      }
    } catch (error) {
      console.error('上传作品失败:', error);
    }
  };

  const handleDeleteWork = async (workId: number) => {
    if (!confirm('确定要删除这个作品吗？')) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/expert/aigc-works/${workId}`, {
        method: 'DELETE',
        headers: {
          'X-User-ID': userId
        }
      });
      if (response.ok) {
        alert('作品删除成功！');
        fetchAIGCWorks();
      } else {
        const error = await response.json();
        alert(error.error || '删除失败');
      }
    } catch (error) {
      console.error('删除作品失败:', error);
    }
  };

  const filterTasks = (tasks: Task[]) => {
    switch (taskFilter) {
      case 'available':
        return tasks.filter(t => t.status === 'available');
      case 'claimed':
        return tasks.filter(t => t.status === 'claimed' && t.claimed_by === Number(userId));
      case 'submitted':
        return tasks.filter(t => t.status === 'submitted');
      default:
        return tasks;
    }
  };

  const filteredTasks = filterTasks(tasks);

  if (userRole !== 'expert' && userRole !== 'admin') {
    return (
      <div className="expert-workbench">
        <div className="access-denied">
          <h2>权限不足</h2>
          <p>此页面仅限专家访问</p>
        </div>
      </div>
    );
  }

  return (
    <div className="expert-workbench">
      <div className="header">
        <h1>专家工作台</h1>
        <div className="header-actions">
          {activeTab === 'works' && (
            <button
              className="btn-primary"
              onClick={() => setShowWorkModal(true)}
            >
              + 上传AIGC作品
            </button>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'tasks' ? 'active' : ''}
          onClick={() => setActiveTab('tasks')}
        >
          任务管理
        </button>
        <button
          className={activeTab === 'works' ? 'active' : ''}
          onClick={() => setActiveTab('works')}
        >
          AIGC作品
        </button>
      </div>

      <div className="content">
        {activeTab === 'tasks' && (
          <div className="tasks-management">
            <div className="tasks-header">
              <h3>任务列表</h3>
              <div className="task-filters">
                <select
                  value={taskFilter}
                  onChange={(e) => setTaskFilter(e.target.value as any)}
                >
                  <option value="all">全部任务</option>
                  <option value="available">可认领</option>
                  <option value="claimed">已认领</option>
                  <option value="submitted">待审核</option>
                </select>
              </div>
            </div>
            
            {loading ? (
              <div className="loading">加载中...</div>
            ) : filteredTasks.length > 0 ? (
              <div className="tasks-grid">
                {filteredTasks.map((task) => (
                  <div key={task.id} className="task-card">
                    <div className="task-header">
                      <h4>{task.title}</h4>
                      <span className={`status-badge ${task.status}`}>
                        {task.status === 'available' && '可认领'}
                        {task.status === 'claimed' && '进行中'}
                        {task.status === 'submitted' && '待审核'}
                        {task.status === 'completed' && '已完成'}
                      </span>
                    </div>
                    <div className="task-body">
                      <p className="description">{task.description}</p>
                      <div className="task-meta">
                        <span className="category">{task.category}</span>
                        <span className={`difficulty ${task.difficulty}`}>
                          {task.difficulty === 'easy' && '简单'}
                          {task.difficulty === 'medium' && '中等'}
                          {task.difficulty === 'hard' && '困难'}
                        </span>
                      </div>
                      <div className="task-reward">
                        <span className="reward-item">
                          <i className="icon-contribution"></i>
                          {task.reward_contribution} 贡献值
                        </span>
                        <span className="reward-item">
                          <i className="icon-lingzhi"></i>
                          {task.reward_lingzhi} 灵值
                        </span>
                      </div>
                      <div className="task-footer">
                        <span className="date">
                          发布于 {new Date(task.created_at).toLocaleDateString('zh-CN')}
                        </span>
                        <div className="task-actions">
                          {task.status === 'available' && (
                            <button
                              className="btn-primary btn-sm"
                              onClick={() => handleClaimTask(task.id)}
                            >
                              承接任务
                            </button>
                          )}
                          {task.status === 'claimed' && task.claimed_by === Number(userId) && (
                            <button
                              className="btn-success btn-sm"
                              onClick={() => handleOpenTaskSubmit(task)}
                            >
                              提交成果
                            </button>
                          )}
                          {task.status === 'submitted' && userRole === 'admin' && (
                            <button
                              className="btn-success btn-sm"
                              onClick={() => handleCompleteTask(task.id)}
                            >
                              审核通过
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>暂无任务记录</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'works' && (
          <div className="aigc-works">
            <h3>AIGC作品库</h3>
            {aigcWorks.length > 0 ? (
              <div className="works-grid">
                {aigcWorks.map((work) => (
                  <div key={work.id} className="work-card">
                    {work.image_url && (
                      <div className="work-image">
                        <img src={work.image_url} alt={work.title} />
                      </div>
                    )}
                    <div className="work-content">
                      <h4>{work.title}</h4>
                      <p className="description">{work.description}</p>
                      <div className="work-meta">
                        <span className="work-type">{work.work_type}</span>
                        <span className={`status-badge ${work.status}`}>
                          {work.status}
                        </span>
                      </div>
                      <div className="work-reward">
                        <span className="reward-item">
                          +{work.reward_contribution} 贡献值
                        </span>
                        <span className="reward-item">
                          +{work.reward_lingzhi} 灵值
                        </span>
                      </div>
                      <div className="work-footer">
                        <span className="date">
                          {new Date(work.created_at).toLocaleDateString('zh-CN')}
                        </span>
                        <button
                          className="btn-danger btn-sm"
                          onClick={() => handleDeleteWork(work.id)}
                        >
                          删除
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>暂无AIGC作品</p>
                <button className="btn-primary" onClick={() => setShowWorkModal(true)}>
                  上传第一个作品
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 任务提交模态框 */}
      {showTaskModal && selectedTask && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>提交任务成果</h2>
              <button className="close-btn" onClick={() => setShowTaskModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="task-info">
                <h4>{selectedTask.title}</h4>
                <p>{selectedTask.description}</p>
              </div>
              <div className="form-group">
                <label>提交链接 *</label>
                <input
                  type="url"
                  value={submissionData.submission_url}
                  onChange={(e) => setSubmissionData({ ...submissionData, submission_url: e.target.value })}
                  placeholder="输入成果链接（GitHub、云盘等）"
                />
              </div>
              <div className="form-group">
                <label>备注说明</label>
                <textarea
                  value={submissionData.notes}
                  onChange={(e) => setSubmissionData({ ...submissionData, notes: e.target.value })}
                  placeholder="输入完成任务的相关说明"
                  rows={4}
                />
              </div>
              <div className="info-text">
                💡 提交后将获得 {selectedTask.reward_contribution} 贡献值 + {selectedTask.reward_lingzhi} 灵值 奖励
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowTaskModal(false)}>取消</button>
              <button className="btn-success" onClick={() => handleSubmitTask(selectedTask.id)}>提交</button>
            </div>
          </div>
        </div>
      )}

      {/* AIGC作品上传模态框 */}
      {showWorkModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>上传AIGC作品</h2>
              <button className="close-btn" onClick={() => setShowWorkModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>作品标题 *</label>
                <input
                  type="text"
                  value={workFormData.title}
                  onChange={(e) => setWorkFormData({ ...workFormData, title: e.target.value })}
                  placeholder="输入作品标题"
                />
              </div>
              <div className="form-group">
                <label>作品类型 *</label>
                <select
                  value={workFormData.work_type}
                  onChange={(e) => setWorkFormData({ ...workFormData, work_type: e.target.value })}
                >
                  <option value="">选择类型</option>
                  <option value="image">图像生成</option>
                  <option value="video">视频生成</option>
                  <option value="text">文本创作</option>
                  <option value="audio">音频生成</option>
                </select>
              </div>
              <div className="form-group">
                <label>作品描述 *</label>
                <textarea
                  value={workFormData.description}
                  onChange={(e) => setWorkFormData({ ...workFormData, description: e.target.value })}
                  placeholder="描述作品创意和实现方式"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>作品图片URL *</label>
                <input
                  type="url"
                  value={workFormData.image_url}
                  onChange={(e) => setWorkFormData({ ...workFormData, image_url: e.target.value })}
                  placeholder="输入作品的图片链接"
                />
              </div>
              <div className="info-text">
                💡 上传成功后将获得 200 贡献值 + 100 灵值 奖励
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowWorkModal(false)}>取消</button>
              <button className="btn-primary" onClick={handleCreateWork}>上传</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpertWorkbench;
