import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface LearningRecord {
  id: number;
  knowledge_id: number;
  knowledge_title: string;
  learning_type: 'reading' | 'practice' | 'meditation';
  duration: number;
  notes: string;
  reward: number;
  created_at: string;
}

interface JourneyStage {
  id: number;
  stage_name: string;
  stage_level: number;
  description: string;
  requirements: string;
  progress: number;
  is_completed: boolean;
  completed_at: string | null;
}

const UserLearning: React.FC = () => {
  const { user, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();
  const [learningRecords, setLearningRecords] = useState<LearningRecord[]>([]);
  const [journeyStages, setJourneyStages] = useState<JourneyStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'records' | 'stages'>('records');
  const [totalReward, setTotalReward] = useState(0);

  useEffect(() => {
    // 如果用户未登录，跳转到登录页面
    if (!authLoading && !user) {
      navigate('/');
      return;
    }

    // 如果用户已登录，加载数据
    if (user) {
      fetchData();
    }
  }, [user, authLoading, navigate]);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token不存在');
      navigate('/');
      return;
    }

    try {
      const [recordsRes, stagesRes] = await Promise.all([
        fetch('/api/user/learning-records', {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch('/api/user/journey-stages', {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);

      const recordsData = await recordsRes.json();
      const stagesData = await stagesRes.json();

      if (recordsData.success) {
        setLearningRecords(recordsData.data);
        setTotalReward(recordsData.data.reduce((sum: number, r: LearningRecord) => sum + r.reward, 0));
      }

      if (stagesData.success) {
        setJourneyStages(stagesData.data);
      }

      setLoading(false);
    } catch (error) {
      console.error('获取数据失败:', error);
      setLoading(false);
    }
  };

  const getLearningTypeText = (type: string) => {
    switch (type) {
      case 'reading': return '阅读';
      case 'practice': return '实践';
      case 'meditation': return '冥想';
      default: return '未知';
    }
  };

  const getLearningTypeColor = (type: string) => {
    switch (type) {
      case 'reading': return 'bg-blue-100 text-blue-800';
      case 'practice': return 'bg-green-100 text-green-800';
      case 'meditation': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">用户修行记录</h1>
        <p className="text-gray-600">记录和追踪您的修行之旅</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-sm p-6"
        >
          <div className="text-sm text-gray-600 mb-1">总学习次数</div>
          <div className="text-3xl font-bold text-gray-900">{learningRecords.length}</div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-sm p-6"
        >
          <div className="text-sm text-gray-600 mb-1">总学习时长</div>
          <div className="text-3xl font-bold text-blue-600">
            {(learningRecords.reduce((sum, r) => sum + r.duration, 0) / 60).toFixed(1)}h
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-sm p-6"
        >
          <div className="text-sm text-gray-600 mb-1">获得灵值</div>
          <div className="text-3xl font-bold text-green-600">{totalReward}</div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-sm p-6"
        >
          <div className="text-sm text-gray-600 mb-1">完成阶段</div>
          <div className="text-3xl font-bold text-purple-600">
            {journeyStages.filter(s => s.is_completed).length}/{journeyStages.length}
          </div>
        </motion.div>
      </div>

      {/* 标签切换 */}
      <div className="bg-white rounded-xl shadow-sm mb-6">
        <div className="flex">
          <button
            onClick={() => setActiveTab('records')}
            className={`flex-1 py-4 text-center font-medium transition-colors ${
              activeTab === 'records'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            学习记录
          </button>
          <button
            onClick={() => setActiveTab('stages')}
            className={`flex-1 py-4 text-center font-medium transition-colors ${
              activeTab === 'stages'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            修行阶段
          </button>
        </div>
      </div>

      {/* 学习记录 */}
      {activeTab === 'records' && (
        <div className="space-y-4">
          {learningRecords.map((record, index) => (
            <motion.div
              key={record.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{record.knowledge_title}</h3>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getLearningTypeColor(record.learning_type)}`}>
                      {getLearningTypeText(record.learning_type)}
                    </span>
                    <span className="text-sm text-gray-500">{record.duration} 分钟</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">获得灵值</div>
                  <div className="text-xl font-bold text-green-600">+{record.reward}</div>
                </div>
              </div>

              {record.notes && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">{record.notes}</div>
                </div>
              )}

              <div className="mt-3 text-sm text-gray-500">
                {new Date(record.created_at).toLocaleString('zh-CN')}
              </div>
            </motion.div>
          ))}

          {learningRecords.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <p className="text-gray-600">暂无学习记录</p>
              <button
                onClick={() => {
                  const token = localStorage.getItem('token');
                  if (token) {
                    navigate('/knowledge');
                  } else {
                    navigate('/');
                  }
                }}
                className="mt-4 bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
              >
                开始学习
              </button>
            </div>
          )}
        </div>
      )}

      {/* 修行阶段 */}
      {activeTab === 'stages' && (
        <div className="space-y-6">
          {journeyStages.map((stage, index) => (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-white rounded-xl shadow-sm p-6 ${
                stage.is_completed ? 'border-2 border-green-500' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                  stage.is_completed ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {stage.is_completed ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-lg font-semibold">{stage.stage_level}</span>
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{stage.stage_name}</h3>
                      <p className="text-sm text-gray-500">第 {stage.stage_level} 阶段</p>
                    </div>
                    {stage.is_completed && (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        已完成
                      </span>
                    )}
                  </div>

                  <p className="text-gray-600 mb-4">{stage.description}</p>

                  {stage.requirements && (
                    <div className="mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-1">达成要求</div>
                      <div className="text-sm text-gray-600">{stage.requirements}</div>
                    </div>
                  )}

                  {!stage.is_completed && stage.progress > 0 && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-600">进度</span>
                        <span className="text-sm font-medium">{stage.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${stage.progress}%` }}
                          transition={{ duration: 1 }}
                          className="bg-blue-600 h-2 rounded-full"
                        />
                      </div>
                    </div>
                  )}

                  {stage.is_completed && stage.completed_at && (
                    <div className="mt-4 text-sm text-green-600">
                      完成时间：{new Date(stage.completed_at).toLocaleString('zh-CN')}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}

          {journeyStages.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <p className="text-gray-600">暂无修行阶段</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserLearning;
