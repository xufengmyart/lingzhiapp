import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, TrendingUp, BookOpen, Calendar, Users, CreditCard, Gift, Award, CheckCircle, ArrowRight, Search, Filter } from 'lucide-react'

interface Project {
  id: string
  name: string
  description: string
  category: 'core' | 'feature' | 'service'
  status: 'active' | 'coming' | 'beta'
  icon: React.ReactNode
  features: string[]
  benefits: string[]
  route: string
  badge?: string
}

export default function ProjectLibrary() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'core' | 'feature' | 'service'>('all')

  const projects: Project[] = [
    {
      id: 'daily-checkin',
      name: '每日签到',
      description: '每日签到获取灵值奖励，培养坚持习惯，连续签到奖励更丰厚',
      category: 'core',
      status: 'active',
      icon: <Gift className="w-8 h-8" />,
      features: [
        '每日签到获取基础灵值',
        '连续签到获得额外奖励',
        '签到记录和历史查询',
        '签到日历可视化'
      ],
      benefits: [
        '轻松获取灵值',
        '培养良好习惯',
        '连续签到享受双倍奖励',
        '参与活动必备'
      ],
      route: '/',
      badge: '热门'
    },
    {
      id: 'knowledge-base',
      name: '知识库管理',
      description: '集中管理知识内容，支持知识检索、分类管理、智能问答',
      category: 'feature',
      status: 'active',
      icon: <BookOpen className="w-8 h-8" />,
      features: [
        '知识内容上传和管理',
        '智能分类和标签',
        '全文检索功能',
        '知识问答助手'
      ],
      benefits: [
        '高效管理知识资产',
        '快速查找所需信息',
        'AI辅助知识整理',
        '团队知识共享'
      ],
      route: '/knowledge-base',
      badge: '推荐'
    },
    {
      id: 'recharge',
      name: '灵值充值',
      description: '多种充值档位，充值即享优惠，合伙人专属特权等你开启',
      category: 'service',
      status: 'active',
      icon: <CreditCard className="w-8 h-8" />,
      features: [
        '7种充值档位选择',
        '微信/支付宝支付',
        '即时到账服务',
        '合伙人专属礼包'
      ],
      benefits: [
        '灵活充值选择',
        '充值享优惠',
        '获得更多灵值',
        '解锁合伙人权益'
      ],
      route: '/recharge',
      badge: '热门'
    },
    {
      id: 'company-news',
      name: '公司动态',
      description: '了解陕西媄月商业艺术有限责任公司最新资讯、产品更新、活动通知',
      category: 'feature',
      status: 'active',
      icon: <Calendar className="w-8 h-8" />,
      features: [
        '最新新闻动态',
        '产品更新公告',
        '活动通知和报名',
        '公司发展历程'
      ],
      benefits: [
        '第一时间了解资讯',
        '参与公司活动',
        '了解产品发展',
        '把握市场动态'
      ],
      route: '/company-news'
    },
    {
      id: 'economy-model',
      name: '经济模型',
      description: '了解灵值生态园经济体系，查看收入预测、里程碑进度',
      category: 'feature',
      status: 'active',
      icon: <TrendingUp className="w-8 h-8" />,
      features: [
        '收入预测分析',
        '里程碑追踪',
        '经济规则说明',
        '收益计算器'
      ],
      benefits: [
        '清晰了解收益模型',
        '规划成长路径',
        '追踪里程碑进度',
        '做出明智决策'
      ],
      route: '/economy'
    },
    {
      id: 'partner-program',
      name: '合伙人计划',
      description: '申请成为灵值生态园合伙人，享受邀请奖励、专属权益、收益分成',
      category: 'service',
      status: 'active',
      icon: <Award className="w-8 h-8" />,
      features: [
        '三档合伙人等级',
        '邀请奖励机制',
        '专属权益特权',
        '收益分成方案'
      ],
      benefits: [
        '获得邀请奖励',
        '享受专属权益',
        '参与收益分成',
        '提升个人影响力'
      ],
      route: '/partner',
      badge: '限时'
    },
    {
      id: 'ai-dialogue',
      name: 'AI智能对话',
      description: '与灵值智能体进行自然对话，获取情绪支持、成长建议、生活指导',
      category: 'core',
      status: 'beta',
      icon: <Sparkles className="w-8 h-8" />,
      features: [
        '自然语言对话',
        '情绪识别和共情',
        '个性化回复',
        '多轮对话支持'
      ],
      benefits: [
        '获得情绪支持',
        '获得成长建议',
        '24小时在线陪伴',
        '保护隐私安全'
      ],
      route: '/chat',
      badge: '测试中'
    },
    {
      id: 'user-community',
      name: '用户社区',
      description: '加入灵值生态园用户社区，分享经验、交流心得、共同成长',
      category: 'feature',
      status: 'coming',
      icon: <Users className="w-8 h-8" />,
      features: [
        '用户交流论坛',
        '经验分享专栏',
        '活动报名入口',
        '用户排行榜'
      ],
      benefits: [
        '结识志同道合的朋友',
        '分享和学习经验',
        '参与社区活动',
        '获得社区奖励'
      ],
      route: '#',
      badge: '即将上线'
    }
  ]

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || project.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = [
    { id: 'all', name: '全部项目' },
    { id: 'core', name: '核心功能' },
    { id: 'feature', name: '特色功能' },
    { id: 'service', name: '服务内容' }
  ]

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">已上线</span>
      case 'beta':
        return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full">测试中</span>
      case 'coming':
        return <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">即将上线</span>
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'core':
        return 'from-purple-500 to-indigo-500'
      case 'feature':
        return 'from-blue-500 to-cyan-500'
      case 'service':
        return 'from-emerald-500 to-teal-500'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 头部 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                项目库
              </h1>
              <p className="text-gray-600 text-lg">
                探索灵值生态园的所有功能和服务
              </p>
            </div>
            <div className="flex items-center gap-2 bg-purple-100 px-4 py-2 rounded-full">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span className="text-purple-700 font-semibold">共 {projects.length} 个项目</span>
            </div>
          </div>

          {/* 搜索和筛选 */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="搜索项目..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              />
            </div>
            <div className="flex gap-2">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id as any)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    selectedCategory === cat.id
                      ? 'bg-purple-600 text-white shadow-lg'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 项目列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all overflow-hidden group cursor-pointer"
              onClick={() => project.route !== '#' && navigate(project.route)}
            >
              {/* 头部 */}
              <div className={`bg-gradient-to-r ${getCategoryColor(project.category)} p-6 relative`}>
                {project.badge && (
                  <div className="absolute top-4 right-4 bg-white/20 backdrop-blur-sm text-white text-xs font-bold px-3 py-1 rounded-full">
                    {project.badge}
                  </div>
                )}
                <div className="text-white">
                  {project.icon}
                </div>
                <h3 className="text-xl font-bold text-white mt-4">{project.name}</h3>
                <p className="text-white/80 text-sm mt-2">{project.description}</p>
              </div>

              {/* 内容 */}
              <div className="p-6">
                {/* 状态标签 */}
                <div className="mb-4">
                  {getStatusBadge(project.status)}
                </div>

                {/* 功能列表 */}
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-800 mb-2 text-sm">主要功能</h4>
                  <ul className="space-y-1">
                    {project.features.slice(0, 3).map((feature, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <span className="truncate">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 权益 */}
                {project.benefits.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-800 mb-2 text-sm">核心权益</h4>
                    <ul className="space-y-1">
                      {project.benefits.slice(0, 2).map((benefit, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                          <Award className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                          <span className="truncate">{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 按钮 */}
                <button
                  className={`w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${
                    project.status === 'active'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg transform hover:scale-[1.02]'
                      : project.status === 'coming'
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white hover:shadow-lg transform hover:scale-[1.02]'
                  }`}
                  disabled={project.status === 'coming'}
                >
                  {project.status === 'active' && (
                    <>
                      立即体验 <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                  {project.status === 'beta' && (
                    <>
                      参与测试 <Sparkles className="w-4 h-4" />
                    </>
                  )}
                  {project.status === 'coming' && (
                    <>
                      即将上线 <Clock className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* 无结果提示 */}
        {filteredProjects.length === 0 && (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-gray-500 text-lg">没有找到匹配的项目</p>
            <p className="text-gray-400 text-sm mt-2">尝试调整搜索词或筛选条件</p>
          </div>
        )}
      </div>
    </div>
  )
}
