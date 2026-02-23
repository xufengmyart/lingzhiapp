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
import { Empty } from '../components/ui/Empty';
import { 
  Sparkles, 
  TrendingUp, 
  Users, 
  DollarSign,
  Calendar,
  CheckCircle,
  Clock,
  ArrowRight,
  Search,
  Filter,
  Building2,
  MapPin
} from 'lucide-react';

interface RecommendedProject {
  id: number;
  projectName: string;
  description: string;
  status: string;
  budget: number;
  startDate: string;
  endDate: string;
  participantCount: number;
  participationFee: number;
  matchScore?: number;
}

interface ResourceMatch {
  id: number;
  resourceId: number;
  resourceName: string;
  projectId: number;
  projectName: string;
  projectStatus: string;
  matchScore: number;
  matchReason: string;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
}

const ProjectRecommendations: React.FC = () => {
  const [projects, setProjects] = useState<RecommendedProject[]>([]);
  const [matches, setMatches] = useState<ResourceMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'recommended' | 'matches'>('recommended');
  const [searchKeyword, setSearchKeyword] = useState('');

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (activeTab === 'recommended') {
        const response = await fetch('/api/projects/recommended', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        if (data.success) {
          setProjects(data.data);
        }
      } else {
        const response = await fetch('/api/resource-matches', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        if (data.success) {
          setMatches(data.data);
        }
      }
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyProject = async (projectId: number, fee: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/project-participations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          projectId,
          participationType: 'resource_provider',
          contributionDescription: '根据资源匹配申请参与项目'
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (data.data.needPayment) {
          alert(`申请成功！需要支付参与费: ¥${data.data.paymentAmount}`);
        } else {
          alert('申请成功！等待审批');
        }
        fetchData();
      } else {
        alert(data.message || '申请失败');
      }
    } catch (error) {
      console.error('申请失败:', error);
      alert('申请失败，请重试');
    }
  };

  const handleMatchResponse = async (matchId: number, action: 'accept' | 'reject') => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/resource-matches/${matchId}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ action })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(action === 'accept' ? '已接受匹配' : '已拒绝匹配');
        fetchData();
      } else {
        alert(data.message || '操作失败');
      }
    } catch (error) {
      console.error('操作失败:', error);
      alert('操作失败，请重试');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      recruiting: { color: 'text-green-600', bg: 'bg-green-100', label: '招募中' },
      active: { color: 'text-blue-600', bg: 'bg-blue-100', label: '进行中' },
      completed: { color: 'text-gray-600', bg: 'bg-gray-100', label: '已完成' },
      closed: { color: 'text-red-600', bg: 'bg-red-100', label: '已关闭' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    if (!config) return null;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const getMatchStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100', label: '待确认' },
      approved: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: '已接受' },
      rejected: { icon: Cross, color: 'text-red-600', bg: 'bg-red-100', label: '已拒绝' }
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

  const filteredProjects = projects.filter(p => {
    if (!searchKeyword) return true;
    const keyword = searchKeyword.toLowerCase();
    return (
      p.projectName.toLowerCase().includes(keyword) ||
      p.description.toLowerCase().includes(keyword)
    );
  });

  const filteredMatches = matches.filter(m => {
    if (!searchKeyword) return true;
    const keyword = searchKeyword.toLowerCase();
    return (
      m.projectName.toLowerCase().includes(keyword) ||
      m.resourceName.toLowerCase().includes(keyword)
    );
  });

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">项目推荐</h1>
          <p className="text-gray-600 mt-1">根据您的资源智能匹配推荐项目</p>
        </div>
      </div>

      {/* Tab切换 */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          <button
            onClick={() => setActiveTab('recommended')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'recommended'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            推荐项目 ({projects.length})
          </button>
          <button
            onClick={() => setActiveTab('matches')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'matches'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            匹配记录 ({matches.length})
          </button>
        </nav>
      </div>

      {/* 搜索栏 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder={`搜索${activeTab === 'recommended' ? '项目' : '匹配记录'}...`}
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {activeTab === 'recommended' ? (
        <>
          {/* 推荐项目列表 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map(project => (
              <Card key={project.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg line-clamp-1">{project.projectName}</CardTitle>
                    {getStatusBadge(project.status)}
                  </div>
                  <CardDescription className="line-clamp-2 mt-2">
                    {project.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <DollarSign size={14} />
                        <span className="line-clamp-1">¥{project.budget?.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Users size={14} />
                        <span>{project.participantCount}人</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar size={14} />
                        <span className="line-clamp-1">{project.startDate?.split('T')[0]}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Sparkles size={14} />
                        <span className="line-clamp-1">参与费: ¥{project.participationFee?.toLocaleString()}</span>
                      </div>
                    </div>

                    {project.participationFee > 0 && (
                      <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                        <p className="text-sm text-yellow-800">
                          ⚠️ 此项目需要支付参与费 ¥{project.participationFee.toLocaleString()}
                        </p>
                      </div>
                    )}

                    <Button
                      onClick={() => handleApplyProject(project.id, project.participationFee)}
                      className="w-full flex items-center justify-center gap-2"
                    >
                      申请参与
                      <ArrowRight size={16} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <Empty 
              icon={Sparkles}
              title="暂无推荐项目"
              description="添加更多资源并设置为可匹配后，系统将为您推荐合适的项目"
            />
          )}
        </>
      ) : (
        <>
          {/* 匹配记录列表 */}
          <div className="space-y-4">
            {filteredMatches.map(match => (
              <Card key={match.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="text-blue-500" size={18} />
                        <h3 className="font-semibold text-lg">{match.resourceName}</h3>
                        <span className="text-gray-400">→</span>
                        <h4 className="font-semibold text-lg">{match.projectName}</h4>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3">{match.matchReason}</p>
                      
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="text-green-500" size={16} />
                          <span className="text-sm font-medium">
                            匹配分数: <span className="text-green-600">{match.matchScore.toFixed(0)}分</span>
                          </span>
                        </div>
                        {getMatchStatusBadge(match.status)}
                        {getStatusBadge(match.projectStatus)}
                      </div>
                    </div>

                    {match.status === 'pending' && (
                      <div className="flex gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleMatchResponse(match.id, 'reject')}
                        >
                          拒绝
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleMatchResponse(match.id, 'accept')}
                        >
                          接受
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredMatches.length === 0 && (
            <Empty 
              icon={Search}
              title="暂无匹配记录"
              description='点击"自动匹配"开始为您匹配项目'
            />
          )}
        </>
      )}
    </div>
  );
};

const Cross = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

export default ProjectRecommendations;
