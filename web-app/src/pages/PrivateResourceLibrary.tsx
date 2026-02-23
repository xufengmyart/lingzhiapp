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
  Plus, 
  Search, 
  Filter, 
  Shield, 
  CheckCircle, 
  Clock, 
  XCircle,
  Eye,
  Edit,
  Trash2,
  Sparkles,
  Building2,
  User,
  Calendar,
  Tag
} from 'lucide-react';

interface PrivateResource {
  id: number;
  resourceName: string;
  resourceType: 'government' | 'enterprise' | 'personal' | 'other';
  department: string;
  contactName: string;
  contactPhone: string;
  contactEmail: string;
  position: string;
  description: string;
  authorizationStatus: 'unauthorized' | 'authorized' | 'pending';
  visibility: 'private' | 'matchable';
  canSolve: string;
  riskLevel: 'low' | 'medium' | 'high';
  verificationStatus: 'pending' | 'verified' | 'rejected';
  validFrom: string;
  validUntil: string;
  createdAt: string;
  updatedAt: string;
}

const PrivateResourceLibrary: React.FC = () => {
  const [resources, setResources] = useState<PrivateResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingResource, setEditingResource] = useState<PrivateResource | null>(null);
  const [formData, setFormData] = useState({
    resourceName: '',
    resourceType: 'other' as const,
    department: '',
    contactName: '',
    contactPhone: '',
    contactEmail: '',
    position: '',
    description: '',
    authorizationStatus: 'unauthorized' as const,
    visibility: 'private' as const,
    canSolve: '',
    riskLevel: 'low' as const,
    validFrom: '',
    validUntil: ''
  });
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [searchKeyword, setSearchKeyword] = useState('');

  useEffect(() => {
    fetchResources();
  }, [filterStatus, filterType]);

  const fetchResources = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = '/api/private-resources';
      const params = new URLSearchParams();
      
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterType !== 'all') params.append('resource_type', filterType);
      
      if (params.toString()) url += '?' + params.toString();
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setResources(data.data);
      }
    } catch (error) {
      console.error('获取资源列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const url = editingResource 
        ? `/api/private-resources/${editingResource.id}`
        : '/api/private-resources';
      
      const method = editingResource ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(editingResource ? '资源更新成功' : '资源创建成功');
        setShowModal(false);
        setEditingResource(null);
        resetForm();
        fetchResources();
      } else {
        alert(data.message || '操作失败');
      }
    } catch (error) {
      console.error('操作失败:', error);
      alert('操作失败，请重试');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个资源吗？')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/private-resources/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('删除成功');
        fetchResources();
      } else {
        alert(data.message || '删除失败');
      }
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败，请重试');
    }
  };

  const handleAutoMatch = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/resource-matches/auto-match', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(`自动匹配完成，创建 ${data.data.matchCount} 条匹配记录`);
      } else {
        alert(data.message || '匹配失败');
      }
    } catch (error) {
      console.error('匹配失败:', error);
      alert('匹配失败，请重试');
    }
  };

  const handleEdit = (resource: PrivateResource) => {
    setEditingResource(resource);
    setFormData({
      resourceName: resource.resourceName,
      resourceType: resource.resourceType,
      department: resource.department,
      contactName: resource.contactName,
      contactPhone: resource.contactPhone,
      contactEmail: resource.contactEmail,
      position: resource.position,
      description: resource.description,
      authorizationStatus: resource.authorizationStatus,
      visibility: resource.visibility,
      canSolve: resource.canSolve,
      riskLevel: resource.riskLevel,
      validFrom: resource.validFrom,
      validUntil: resource.validUntil
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      resourceName: '',
      resourceType: 'other',
      department: '',
      contactName: '',
      contactPhone: '',
      contactEmail: '',
      position: '',
      description: '',
      authorizationStatus: 'unauthorized',
      visibility: 'private',
      canSolve: '',
      riskLevel: 'low',
      validFrom: '',
      validUntil: ''
    });
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      authorized: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: '已授权' },
      unauthorized: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100', label: '未授权' },
      pending: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100', label: '待授权' }
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

  const getTypeBadge = (type: string) => {
    const typeConfig = {
      government: { icon: Building2, color: 'text-blue-600', bg: 'bg-blue-100', label: '政府资源' },
      enterprise: { icon: Sparkles, color: 'text-purple-600', bg: 'bg-purple-100', label: '企业资源' },
      personal: { icon: User, color: 'text-orange-600', bg: 'bg-orange-100', label: '人脉资源' },
      other: { icon: Tag, color: 'text-gray-600', bg: 'bg-gray-100', label: '其他资源' }
    };
    
    const config = typeConfig[type as keyof typeof typeConfig];
    if (!config) return null;
    
    const Icon = config.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        <Icon size={12} />
        {config.label}
      </span>
    );
  };

  const filteredResources = resources.filter(r => {
    if (!searchKeyword) return true;
    const keyword = searchKeyword.toLowerCase();
    return (
      r.resourceName.toLowerCase().includes(keyword) ||
      r.contactName.toLowerCase().includes(keyword) ||
      r.canSolve.toLowerCase().includes(keyword)
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
          <h1 className="text-3xl font-bold text-gray-900">私有资源库</h1>
          <p className="text-gray-600 mt-1">管理您的私有资源，授权后可参与项目匹配</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleAutoMatch}
            className="flex items-center gap-2"
          >
            <Sparkles size={18} />
            自动匹配项目
          </Button>
          <Button
            onClick={() => {
              setEditingResource(null);
              resetForm();
              setShowModal(true);
            }}
            className="flex items-center gap-2"
          >
            <Plus size={18} />
            添加资源
          </Button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总资源数</p>
                <p className="text-2xl font-bold mt-1">{resources.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Tag size={24} className="text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">已授权</p>
                <p className="text-2xl font-bold mt-1">{resources.filter(r => r.authorizationStatus === 'authorized').length}</p>
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
                <p className="text-sm text-gray-600">可匹配</p>
                <p className="text-2xl font-bold mt-1">{resources.filter(r => r.visibility === 'matchable').length}</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Sparkles size={24} className="text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">已验证</p>
                <p className="text-2xl font-bold mt-1">{resources.filter(r => r.verificationStatus === 'verified').length}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <Shield size={24} className="text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder="搜索资源名称、联系人、能解决的问题..."
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部状态</option>
              <option value="authorized">已授权</option>
              <option value="unauthorized">未授权</option>
              <option value="pending">待授权</option>
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部类型</option>
              <option value="government">政府资源</option>
              <option value="enterprise">企业资源</option>
              <option value="personal">人脉资源</option>
              <option value="other">其他资源</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 资源列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredResources.map(resource => (
          <Card key={resource.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{resource.resourceName}</CardTitle>
                <div className="flex gap-2">
                  {getTypeBadge(resource.resourceType)}
                  {getStatusBadge(resource.authorizationStatus)}
                </div>
              </div>
              <CardDescription className="flex items-center gap-2 mt-2">
                <User size={14} />
                {resource.contactName}
                <span className="text-gray-400">|</span>
                <Building2 size={14} />
                {resource.department}
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">能解决的问题</p>
                  <p className="text-sm text-gray-600 line-clamp-2">{resource.canSolve}</p>
                </div>

                {resource.description && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">描述</p>
                    <p className="text-sm text-gray-600 line-clamp-2">{resource.description}</p>
                  </div>
                )}

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar size={12} />
                    {resource.validFrom || '无期限'} ~ {resource.validUntil || '长期有效'}
                  </span>
                  <span className={resource.visibility === 'matchable' ? 'text-green-600' : 'text-gray-400'}>
                    {resource.visibility === 'matchable' ? '可匹配' : '私有'}
                  </span>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleEdit(resource)}
                  >
                    <Edit size={14} className="mr-1" />
                    编辑
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    onClick={() => handleDelete(resource.id)}
                  >
                    <Trash2 size={14} />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredResources.length === 0 && (
        <Empty 
          icon={Shield}
          title="暂无资源"
          description='点击"添加资源"开始创建您的私有资源库'
        />
      )}

      {/* 添加/编辑资源弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>{editingResource ? '编辑资源' : '添加资源'}</CardTitle>
              <CardDescription>
                填写资源信息，授权后可参与项目自动匹配
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      资源名称 *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.resourceName}
                      onChange={(e) => setFormData({...formData, resourceName: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      资源类型 *
                    </label>
                    <select
                      value={formData.resourceType}
                      onChange={(e) => setFormData({...formData, resourceType: e.target.value as any})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="government">政府资源</option>
                      <option value="enterprise">企业资源</option>
                      <option value="personal">人脉资源</option>
                      <option value="other">其他资源</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      部门
                    </label>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => setFormData({...formData, department: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      联系人姓名 *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.contactName}
                      onChange={(e) => setFormData({...formData, contactName: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      联系电话 *
                    </label>
                    <input
                      type="tel"
                      required
                      value={formData.contactPhone}
                      onChange={(e) => setFormData({...formData, contactPhone: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      联系邮箱
                    </label>
                    <input
                      type="email"
                      value={formData.contactEmail}
                      onChange={(e) => setFormData({...formData, contactEmail: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      职位
                    </label>
                    <input
                      type="text"
                      value={formData.position}
                      onChange={(e) => setFormData({...formData, position: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      风险等级
                    </label>
                    <select
                      value={formData.riskLevel}
                      onChange={(e) => setFormData({...formData, riskLevel: e.target.value as any})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">低风险</option>
                      <option value="medium">中风险</option>
                      <option value="high">高风险</option>
                    </select>
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      能解决的问题 * (用于自动匹配)
                    </label>
                    <textarea
                      required
                      value={formData.canSolve}
                      onChange={(e) => setFormData({...formData, canSolve: e.target.value})}
                      rows={2}
                      placeholder="例如：教育政策咨询、项目申报指导、资金申请支持等"
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      资源描述
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={2}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      授权状态
                    </label>
                    <select
                      value={formData.authorizationStatus}
                      onChange={(e) => setFormData({...formData, authorizationStatus: e.target.value as any})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="unauthorized">未授权</option>
                      <option value="pending">待授权</option>
                      <option value="authorized">已授权</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      可见性
                    </label>
                    <select
                      value={formData.visibility}
                      onChange={(e) => setFormData({...formData, visibility: e.target.value as any})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="private">私有（仅自己可见）</option>
                      <option value="matchable">可匹配（可参与自动匹配）</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      有效期开始
                    </label>
                    <input
                      type="date"
                      value={formData.validFrom}
                      onChange={(e) => setFormData({...formData, validFrom: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      有效期结束
                    </label>
                    <input
                      type="date"
                      value={formData.validUntil}
                      onChange={(e) => setFormData({...formData, validUntil: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowModal(false);
                      setEditingResource(null);
                      resetForm();
                    }}
                  >
                    取消
                  </Button>
                  <Button type="submit">
                    {editingResource ? '更新' : '创建'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PrivateResourceLibrary;
