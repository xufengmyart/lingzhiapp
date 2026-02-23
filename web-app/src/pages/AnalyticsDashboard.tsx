import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription 
} from '../components/ui/Card';
import { Loading } from '../components/ui/Loading';
import { 
  TrendingUp, 
  TrendingDown,
  Users, 
  DollarSign,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  ArrowUp,
  ArrowDown,
  BarChart3,
  PieChart,
  FileText
} from 'lucide-react';

interface DashboardData {
  resources: {
    total: number;
    authorized: number;
    matchable: number;
  };
  matches: {
    total: number;
    approved: number;
    pending: number;
  };
  participations: {
    total: number;
    active: number;
    completed: number;
    totalInvested: number;
  };
  profits: {
    total: number;
    distributed: number;
    pending: number;
  };
  recentActivities: Array<{
    type: string;
    title: string;
    createdAt: string;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/reports/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      if (result.success) {
        setData(result.data);
      }
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return (num / 10000).toFixed(1) + '万';
    }
    return num.toLocaleString();
  };

  const formatCurrency = (num: number) => {
    return '¥' + num.toLocaleString();
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">数据可视化仪表盘</h1>
          <p className="text-gray-600 mt-1">实时监控您的资源、项目和收益数据</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={fetchDashboardData}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
            刷新
          </Button>
          <Button
            variant="outline"
            className="flex items-center gap-2"
          >
            <Download size={18} />
            导出报表
          </Button>
        </div>
      </div>

      {/* 核心指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 资源卡片 */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">资源总数</p>
                <p className="text-3xl font-bold mt-2">{data?.resources.total || 0}</p>
                <p className="text-sm text-gray-500 mt-2">
                  已授权 {data?.resources.authorized || 0} / 可匹配 {data?.resources.matchable || 0}
                </p>
              </div>
              <div className="p-4 bg-blue-100 rounded-xl">
                <FileText size={32} className="text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 匹配卡片 */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">匹配次数</p>
                <p className="text-3xl font-bold mt-2">{data?.matches.total || 0}</p>
                <p className="text-sm text-gray-500 mt-2">
                  已接受 {data?.matches.approved || 0} / 待确认 {data?.matches.pending || 0}
                </p>
              </div>
              <div className="p-4 bg-purple-100 rounded-xl">
                <BarChart3 size={32} className="text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 项目参与卡片 */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">参与项目</p>
                <p className="text-3xl font-bold mt-2">{data?.participations.total || 0}</p>
                <p className="text-sm text-gray-500 mt-2">
                  进行中 {data?.participations.active || 0} / 已完成 {data?.participations.completed || 0}
                </p>
              </div>
              <div className="p-4 bg-green-100 rounded-xl">
                <Users size={32} className="text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 收益卡片 */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">总收益</p>
                <p className="text-3xl font-bold mt-2">
                  {formatCurrency(data?.profits.total || 0)}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  已发放 {formatCurrency(data?.profits.distributed || 0)} / 待发放 {formatCurrency(data?.profits.pending || 0)}
                </p>
              </div>
              <div className="p-4 bg-orange-100 rounded-xl">
                <DollarSign size={32} className="text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 资源分布图 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart size={20} />
              资源分布
            </CardTitle>
            <CardDescription>
              按授权状态和可见性分布
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 已授权 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">已授权资源</span>
                  <span className="text-sm text-gray-600">
                    {data?.resources.authorized || 0} / {data?.resources.total || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-green-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.resources.total > 0 
                        ? `${(data.resources.authorized / data.resources.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 可匹配 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">可匹配资源</span>
                  <span className="text-sm text-gray-600">
                    {data?.resources.matchable || 0} / {data?.resources.total || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.resources.total > 0 
                        ? `${(data.resources.matchable / data.resources.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 匹配成功率 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 size={20} />
              匹配成功率
            </CardTitle>
            <CardDescription>
              资源匹配的成功率统计
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 已接受 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">已接受</span>
                  <span className="text-sm text-green-600 font-semibold">
                    {data && data.matches.total > 0 
                      ? `${((data.matches.approved / data.matches.total) * 100).toFixed(1)}%` 
                      : '0%'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-green-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.matches.total > 0 
                        ? `${(data.matches.approved / data.matches.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 待确认 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">待确认</span>
                  <span className="text-sm text-yellow-600 font-semibold">
                    {data && data.matches.total > 0 
                      ? `${((data.matches.pending / data.matches.total) * 100).toFixed(1)}%` 
                      : '0%'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-yellow-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.matches.total > 0 
                        ? `${(data.matches.pending / data.matches.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 项目参与统计 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity size={20} />
              项目参与统计
            </CardTitle>
            <CardDescription>
              项目参与状态分布
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 进行中 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">进行中</span>
                  <span className="text-sm text-blue-600 font-semibold">
                    {data?.participations.active || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.participations.total > 0 
                        ? `${(data.participations.active / data.participations.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 已完成 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">已完成</span>
                  <span className="text-sm text-green-600 font-semibold">
                    {data?.participations.completed || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-green-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.participations.total > 0 
                        ? `${(data.participations.completed / data.participations.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 总投资 */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">总投资额</span>
                  <span className="text-lg font-bold text-gray-900">
                    {formatCurrency(data?.participations.totalInvested || 0)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 收益统计 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp size={20} />
              收益统计
            </CardTitle>
            <CardDescription>
              分润发放情况
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 已发放 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">已发放</span>
                  <span className="text-sm text-green-600 font-semibold">
                    {formatCurrency(data?.profits.distributed || 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-green-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.profits.total > 0 
                        ? `${(data.profits.distributed / data.profits.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 待发放 */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">待发放</span>
                  <span className="text-sm text-yellow-600 font-semibold">
                    {formatCurrency(data?.profits.pending || 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-yellow-600 h-3 rounded-full transition-all"
                    style={{ 
                      width: data && data.profits.total > 0 
                        ? `${(data.profits.pending / data.profits.total) * 100}%` 
                        : '0%' 
                    }}
                  />
                </div>
              </div>

              {/* 总收益 */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">总收益</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatCurrency(data?.profits.total || 0)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 最近活动 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar size={20} />
            最近活动
          </CardTitle>
          <CardDescription>
            您的最近10条活动记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data?.recentActivities && data.recentActivities.length > 0 ? (
              data.recentActivities.map((activity, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`p-2 rounded-full ${
                    activity.type === 'participation' ? 'bg-blue-100 text-blue-600' :
                    activity.type === 'match' ? 'bg-purple-100 text-purple-600' :
                    'bg-green-100 text-green-600'
                  }`}>
                    {activity.type === 'participation' ? <Users size={16} /> :
                     activity.type === 'match' ? <BarChart3 size={16} /> :
                     <DollarSign size={16} />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(activity.createdAt).toLocaleString('zh-CN')}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                暂无活动记录
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const Button = ({ children, variant = 'default', disabled = false, onClick, className = '' }: {
  children: React.ReactNode;
  variant?: 'default' | 'outline';
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
}) => {
  const baseClass = "px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2";
  const variantClass = variant === 'outline' 
    ? "border border-gray-300 text-gray-700 hover:bg-gray-50"
    : "bg-blue-600 text-white hover:bg-blue-700";
  
  return (
    <button 
      className={`${baseClass} ${variantClass} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default AnalyticsDashboard;
