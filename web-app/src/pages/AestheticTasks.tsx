import React, { useState, useEffect } from 'react';

interface AestheticTask {
  id: number;
  title: string;
  description: string;
  type: string;
  difficulty: string;
  required_skills: string[];
  points: number;
  contribution_reward: number;
  spirit_reward: number;
  status: string;
  assigned_to: number | null;
  deadline: string | null;
  tags: string[];
  location: string | null;
  created_at: string;
  completed_at: string | null;
}

interface TaskStats {
  completed_count: number;
  in_progress_count: number;
  submitted_count: number;
  total_points: number;
}

const AestheticTasks: React.FC = () => {
  const [tasks, setTasks] = useState<AestheticTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<AestheticTask | null>(null);
  const [activeTab, setActiveTab] = useState<'available' | 'my-tasks' | 'stats'>('available');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [userRole, setUserRole] = useState<string>('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'general',
    difficulty: 'medium',
    points: 100,
    contribution_reward: 100,
    spirit_reward: 50,
    deadline: '',
    max_participants: 1,
    tags: [],
    location: '',
    required_skills: []
  });
  const [submitData, setSubmitData] = useState<{
    content: string;
    files: string[];
  }>({
    content: '',
    files: []
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  useEffect(() => {
    const role = localStorage.getItem('userRole') || '';
    setUserRole(role);
    fetchTasks();
    fetchStats();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const userId = localStorage.getItem('userId');
      let url = `${API_BASE_URL}/api/aesthetic-tasks`;
      
      if (activeTab === 'my-tasks') {
        url += `?assigned_to=${userId}`;
      } else {
        url += '?status=open';
      }
      
      const response = await fetch(url, {
        headers: {
          'X-User-ID': userId || ''
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

  const fetchStats = async () => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/aesthetic-tasks/stats`, {
        headers: {
          'X-User-ID': userId || ''
        }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  };

  const handleClaimTask = async (taskId: number) => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/aesthetic-tasks/${taskId}/claim`, {
        method: 'POST',
        headers: {
          'X-User-ID': userId || ''
        }
      });
      if (response.ok) {
        alert('任务认领成功！');
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '认领失败');
      }
    } catch (error) {
      console.error('认领任务失败:', error);
    }
  };

  const handleSubmitTask = async () => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/aesthetic-tasks/${selectedTask?.id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId || ''
        },
        body: JSON.stringify(submitData)
      });
      if (response.ok) {
        alert('任务提交成功，等待审核！');
        setShowSubmitModal(false);
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '提交失败');
      }
    } catch (error) {
      console.error('提交任务失败:', error);
    }
  };

  const handleCreateTask = async () => {
    if (userRole !== 'admin') {
      alert('需要管理员权限');
      return;
    }
    
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/aesthetic-tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId || ''
        },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        alert('任务创建成功！');
        setShowModal(false);
        fetchTasks();
      } else {
        const error = await response.json();
        alert(error.error || '创建失败');
      }
    } catch (error) {
      console.error('创建任务失败:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'hard': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return '#2196f3';
      case 'in_progress': return '#ff9800';
      case 'submitted': return '#9c27b0';
      case 'completed': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  return (
    <div className="aesthetic-tasks">
      <div className="header">
        <h1>美学侦探任务</h1>
        <div className="header-actions">
          {userRole === 'admin' && (
            <button
              className="btn-primary"
              onClick={() => setShowModal(true)}
            >
              发布任务
            </button>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'available' ? 'active' : ''}
          onClick={() => {
            setActiveTab('available');
            fetchTasks();
          }}
        >
          可接任务
        </button>
        <button
          className={activeTab === 'my-tasks' ? 'active' : ''}
          onClick={() => {
            setActiveTab('my-tasks');
            fetchTasks();
          }}
        >
          我的任务
        </button>
        <button
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          统计数据
        </button>
      </div>

      <div className="content">
        {activeTab === 'stats' && stats && (
          <div className="stats-cards">
            <div className="stat-card">
              <div className="stat-value">{stats.completed_count}</div>
              <div className="stat-label">已完成</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.in_progress_count}</div>
              <div className="stat-label">进行中</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.submitted_count}</div>
              <div className="stat-label">待审核</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_points}</div>
              <div className="stat-label">总积分</div>
            </div>
          </div>
        )}

        {activeTab !== 'stats' && (
          <>
            {loading ? (
              <div className="loading">加载中...</div>
            ) : (
              <div className="tasks-grid">
                {tasks.map((task) => (
                  <div key={task.id} className="task-card">
                    <div className="task-header">
                      <h3>{task.title}</h3>
                      <div className="task-badges">
                        <span
                          className="badge"
                          style={{ backgroundColor: getDifficultyColor(task.difficulty) }}
                        >
                          {task.difficulty}
                        </span>
                        <span
                          className="badge"
                          style={{ backgroundColor: getStatusColor(task.status) }}
                        >
                          {task.status}
                        </span>
                      </div>
                    </div>
                    <p className="task-description">{task.description}</p>
                    <div className="task-meta">
                      <div className="meta-item">
                        <span className="icon">🎯</span>
                        <span>{task.points} 积分</span>
                      </div>
                      <div className="meta-item">
                        <span className="icon">💎</span>
                        <span>{task.contribution_reward} 贡献值</span>
                      </div>
                      <div className="meta-item">
                        <span className="icon">✨</span>
                        <span>{task.spirit_reward} 灵值</span>
                      </div>
                    </div>
                    {task.required_skills.length > 0 && (
                      <div className="task-skills">
                        {task.required_skills.map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    )}
                    {task.tags.length > 0 && (
                      <div className="task-tags">
                        {task.tags.map((tag, index) => (
                          <span key={index} className="tag">{tag}</span>
                        ))}
                      </div>
                    )}
                    <div className="task-actions">
                      {task.status === 'open' && (
                        <button
                          className="btn-primary"
                          onClick={() => handleClaimTask(task.id)}
                        >
                          认领任务
                        </button>
                      )}
                      {task.status === 'in_progress' && (
                        <button
                          className="btn-success"
                          onClick={() => {
                            setSelectedTask(task);
                            setShowSubmitModal(true);
                          }}
                        >
                          提交任务
                        </button>
                      )}
                      {task.status === 'submitted' && (
                        <button className="btn-secondary" disabled>
                          审核中
                        </button>
                      )}
                      {task.status === 'completed' && (
                        <button className="btn-secondary" disabled>
                          已完成
                        </button>
                      )}
                      <button
                        className="btn-outline"
                        onClick={() => setSelectedTask(task)}
                      >
                        详情
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* 创建任务模态框 */}
      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>发布美学侦探任务</h2>
              <button
                className="close-btn"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>任务标题 *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="输入任务标题"
                />
              </div>
              <div className="form-group">
                <label>任务描述 *</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="输入任务描述"
                  rows={4}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>任务类型</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  >
                    <option value="general">通用</option>
                    <option value="art">艺术</option>
                    <option value="content">内容</option>
                    <option value="design">设计</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>难度等级</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  >
                    <option value="easy">简单</option>
                    <option value="medium">中等</option>
                    <option value="hard">困难</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>积分奖励</label>
                  <input
                    type="number"
                    value={formData.points}
                    onChange={(e) => setFormData({ ...formData, points: Number(e.target.value) })}
                  />
                </div>
                <div className="form-group">
                  <label>贡献值奖励</label>
                  <input
                    type="number"
                    value={formData.contribution_reward}
                    onChange={(e) => setFormData({ ...formData, contribution_reward: Number(e.target.value) })}
                  />
                </div>
                <div className="form-group">
                  <label>灵值奖励</label>
                  <input
                    type="number"
                    value={formData.spirit_reward}
                    onChange={(e) => setFormData({ ...formData, spirit_reward: Number(e.target.value) })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>截止日期</label>
                <input
                  type="datetime-local"
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>地点</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="任务地点"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setShowModal(false)}
              >
                取消
              </button>
              <button
                className="btn-primary"
                onClick={handleCreateTask}
              >
                发布
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 提交任务模态框 */}
      {showSubmitModal && selectedTask && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>提交任务</h2>
              <button
                className="close-btn"
                onClick={() => setShowSubmitModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="task-info">
                <h3>{selectedTask.title}</h3>
                <p>{selectedTask.description}</p>
              </div>
              <div className="form-group">
                <label>提交内容 *</label>
                <textarea
                  value={submitData.content}
                  onChange={(e) => setSubmitData({ ...submitData, content: e.target.value })}
                  placeholder="描述您的完成情况"
                  rows={6}
                />
              </div>
              <div className="form-group">
                <label>附件</label>
                <input
                  type="text"
                  value={submitData.files.join(', ')}
                  onChange={(e) => setSubmitData({
                    ...submitData,
                    files: e.target.value.split(',').map(f => f.trim()).filter(f => f)
                  })}
                  placeholder="输入附件URL，多个用逗号分隔"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setShowSubmitModal(false)}
              >
                取消
              </button>
              <button
                className="btn-primary"
                onClick={handleSubmitTask}
              >
                提交
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AestheticTasks;
