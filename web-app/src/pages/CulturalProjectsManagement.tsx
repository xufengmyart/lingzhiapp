import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface CulturalProject {
  id: number;
  name: string;
  description: string;
  site_id: number | null;
  site_name?: string;
  project_type: 'renovation' | 'reconstruction' | 'creation';
  status: 'planning' | 'ongoing' | 'completed';
  progress: number;
  budget: number;
  actual_cost: number;
  start_date: string;
  end_date: string;
  manager_id: number;
  created_at: string;
}

const CulturalProjectsManagement: React.FC = () => {
  const [projects, setProjects] = useState<CulturalProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchProjects(storedToken);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchProjects(token);
    }
  }, [filterStatus]);

  const fetchProjects = async (authToken: string) => {
    try {
      let url = '/api/cultural-projects';
      if (filterStatus !== 'all') {
        url += `?status=${filterStatus}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setProjects(data.data);
      }
      setLoading(false);
    } catch (error) {
      console.error('获取文化项目列表失败:', error);
      setLoading(false);
    }
  };

  const getProjectTypeText = (type: string) => {
    switch (type) {
      case 'renovation': return '修缮';
      case 'reconstruction': return '重建';
      case 'creation': return '创作';
      default: return '未知';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planning': return 'bg-yellow-100 text-yellow-800';
      case 'ongoing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'planning': return '规划中';
      case 'ongoing': return '进行中';
      case 'completed': return '已完成';
      default: return '未知';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress < 30) return 'bg-red-500';
    if (progress < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* 头部 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">文化项目管理</h1>
        <p className="text-gray-600">管理和跟踪灵值生态园的文化项目进展</p>
      </div>

      {/* 筛选和统计 */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">筛选：</span>
            {['all', 'planning', 'ongoing', 'completed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterStatus === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? '全部' : getStatusText(status)}
              </button>
            ))}
          </div>
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-gray-500">总项目：</span>
              <span className="font-semibold">{projects.length}</span>
            </div>
            <div>
              <span className="text-gray-500">进行中：</span>
              <span className="font-semibold text-blue-600">
                {projects.filter(p => p.status === 'ongoing').length}
              </span>
            </div>
            <div>
              <span className="text-gray-500">已完成：</span>
              <span className="font-semibold text-green-600">
                {projects.filter(p => p.status === 'completed').length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 项目列表 */}
      <div className="space-y-6">
        {projects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{project.name}</h3>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {getStatusText(project.status)}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {getProjectTypeText(project.project_type)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500 mb-1">项目预算</div>
                  <div className="text-2xl font-bold text-blue-600">
                    ¥{project.budget.toLocaleString()}
                  </div>
                </div>
              </div>

              <p className="text-gray-600 mb-6 line-clamp-2">{project.description}</p>

              {/* 进度条 */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">项目进度</span>
                  <span className="text-sm font-medium">{project.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${project.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-2 rounded-full ${getProgressColor(project.progress)}`}
                  />
                </div>
              </div>

              {/* 项目信息 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">实际花费</div>
                  <div className="text-lg font-semibold text-red-600">
                    ¥{project.actual_cost.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">开始日期</div>
                  <div className="text-lg font-semibold">{project.start_date}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">结束日期</div>
                  <div className="text-lg font-semibold">{project.end_date}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">预算使用率</div>
                  <div className="text-lg font-semibold">
                    {((project.actual_cost / project.budget) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="mt-6 flex gap-3">
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                  查看详情
                </button>
                {project.status === 'ongoing' && (
                  <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                    更新进度
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-600">暂无文化项目</p>
        </div>
      )}
    </div>
  );
};

export default CulturalProjectsManagement;
