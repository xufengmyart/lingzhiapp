import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Building2, Search, Filter, Star, MapPin, Phone, Globe, Mail, Award, TrendingUp, Shield, Users, Clock, CheckCircle, AlertCircle, Calendar, DollarSign, Tag } from 'lucide-react'

interface Merchant {
  id: string
  name: string
  description: string
  category: string
  logo: string
  rating: number
  review_count: number
  location: string
  phone: string
  email: string
  website: string
  business_license: string
  verified: boolean
  established_year: number
  services: string[]
  tags: string[]
  status: 'active' | 'pending' | 'suspended'
  joined_date: string
  lingzhi_points: number
  total_deals: number
}

// 10个企业数据
const MOCK_MERCHANTS: Merchant[] = [
  {
    id: '1',
    name: '翰林文化发展有限公司',
    description: '专注于传统文化传承与创新，提供文化策划、艺术展览、文创产品开发等服务。致力于让传统文化在现代生活中焕发新生。',
    category: '文化艺术',
    logo: '/assets/merchants/hanlin.png',
    rating: 4.8,
    review_count: 156,
    location: '北京市朝阳区',
    phone: '010-88886666',
    email: 'contact@hanlin-culture.com',
    website: 'https://www.hanlin-culture.com',
    business_license: '91110108MA01K2L3X5',
    verified: true,
    established_year: 2015,
    services: ['文化策划', '艺术展览', '文创开发', '非遗传承'],
    tags: ['文化', '艺术', '文创', '非遗'],
    status: 'active',
    joined_date: '2024-01-15',
    lingzhi_points: 8500,
    total_deals: 89
  },
  {
    id: '2',
    name: '智创科技有限公司',
    description: '高新技术企业，专注于人工智能、大数据、云计算等前沿技术的研发与应用。为生态伙伴提供智能化解决方案。',
    category: '科技创新',
    logo: '/assets/merchants/zhichuang.png',
    rating: 4.9,
    review_count: 234,
    location: '上海市浦东新区',
    phone: '021-66668888',
    email: 'info@zhichuang-tech.com',
    website: 'https://www.zhichuang-tech.com',
    business_license: '91310115MA1K4L8M2P',
    verified: true,
    established_year: 2018,
    services: ['AI解决方案', '大数据分析', '云计算服务', '技术咨询'],
    tags: ['科技', 'AI', '大数据', '云计算'],
    status: 'active',
    joined_date: '2024-01-20',
    lingzhi_points: 9200,
    total_deals: 145
  },
  {
    id: '3',
    name: '灵韵禅茶文化传播有限公司',
    description: '专业禅茶文化传播企业，集禅茶种植、加工、销售、文化体验于一体。传承千年禅茶文化，倡导健康生活理念。',
    category: '禅茶文化',
    logo: '/assets/merchants/lingyun.png',
    rating: 4.7,
    review_count: 189,
    location: '杭州市西湖区',
    phone: '0571-87654321',
    email: 'service@lingyun-tea.com',
    website: 'https://www.lingyun-tea.com',
    business_license: '91330106MA1A5B9C8D',
    verified: true,
    established_year: 2012,
    services: ['禅茶销售', '茶艺培训', '文化体验', '品牌合作'],
    tags: ['禅茶', '文化', '培训', '体验'],
    status: 'active',
    joined_date: '2024-02-01',
    lingzhi_points: 7800,
    total_deals: 112
  },
  {
    id: '4',
    name: '华夏艺术研究院',
    description: '国家级艺术研究机构，致力于中国传统艺术的研究、保护、传承与创新。汇聚众多艺术大师和专家学者。',
    category: '艺术研究',
    logo: '/assets/merchants/huaxia.png',
    rating: 4.9,
    review_count: 267,
    location: '北京市东城区',
    phone: '010-65432109',
    email: 'research@huaxia-art.com',
    website: 'https://www.huaxia-art.com',
    business_license: '91110101MA01X9Y8Z7',
    verified: true,
    established_year: 2008,
    services: ['艺术研究', '作品鉴定', '教育培训', '展览策划'],
    tags: ['艺术', '研究', '鉴定', '教育'],
    status: 'active',
    joined_date: '2024-01-25',
    lingzhi_points: 9500,
    total_deals: 178
  },
  {
    id: '5',
    name: '天圆数字创意有限公司',
    description: '领先的数字创意服务商，专注于数字化内容创作、互动体验设计、元宇宙场景构建。用科技赋能创意。',
    category: '数字创意',
    logo: '/assets/merchants/tianyuan.png',
    rating: 4.6,
    review_count: 143,
    location: '深圳市南山区',
    phone: '0755-88889999',
    email: 'hello@tianyuan-creative.com',
    website: 'https://www.tianyuan-creative.com',
    business_license: '91440300MA5F6E5D4C',
    verified: true,
    established_year: 2019,
    services: ['数字内容', '互动设计', '元宇宙', '品牌营销'],
    tags: ['数字', '创意', '互动', '元宇宙'],
    status: 'active',
    joined_date: '2024-02-05',
    lingzhi_points: 7200,
    total_deals: 95
  },
  {
    id: '6',
    name: '国学书院教育科技有限公司',
    description: '专业国学教育机构，致力于传统国学文化的普及与传承。提供线上线下一体化的国学教育服务。',
    category: '国学教育',
    logo: '/assets/merchants/guoxue.png',
    rating: 4.8,
    review_count: 198,
    location: '成都市高新区',
    phone: '028-98765432',
    email: 'education@guoxue-shuyuan.com',
    website: 'https://www.guoxue-shuyuan.com',
    business_license: '91510100MA2K9L7M6N',
    verified: true,
    established_year: 2014,
    services: ['国学课程', '师资培训', '教材开发', '文化讲座'],
    tags: ['国学', '教育', '培训', '文化'],
    status: 'active',
    joined_date: '2024-01-30',
    lingzhi_points: 8800,
    total_deals: 134
  },
  {
    id: '7',
    name: '东方美学设计事务所',
    description: '新东方美学设计领军者，融合传统美学与现代设计理念。提供空间设计、产品设计、品牌视觉设计等服务。',
    category: '设计服务',
    logo: '/assets/merchants/dongfang.png',
    rating: 4.7,
    review_count: 167,
    location: '上海市徐汇区',
    phone: '021-54321098',
    email: 'design@dongfang-aesthetics.com',
    website: 'https://www.dongfang-aesthetics.com',
    business_license: '91310104MA1B8C6D5E',
    verified: true,
    established_year: 2016,
    services: ['空间设计', '产品设计', '品牌设计', '设计咨询'],
    tags: ['设计', '美学', '空间', '品牌'],
    status: 'active',
    joined_date: '2024-02-10',
    lingzhi_points: 8100,
    total_deals: 108
  },
  {
    id: '8',
    name: '灵心健康管理咨询有限公司',
    description: '专注于身心健康管理的专业机构，融合中医养生、心理咨询、运动康复等多元化服务。倡导身心合一的健康理念。',
    category: '健康管理',
    logo: '/assets/merchants/lingxin.png',
    rating: 4.6,
    review_count: 134,
    location: '广州市天河区',
    phone: '020-34567890',
    email: 'health@lingxin-wellness.com',
    website: 'https://www.lingxin-wellness.com',
    business_license: '91440106MA4D7C5B4A',
    verified: true,
    established_year: 2017,
    services: ['健康管理', '心理咨询', '中医养生', '康复服务'],
    tags: ['健康', '养生', '心理', '康复'],
    status: 'active',
    joined_date: '2024-02-08',
    lingzhi_points: 7600,
    total_deals: 87
  },
  {
    id: '9',
    name: '丝路文旅发展有限公司',
    description: '专业的文化旅游服务商，深度挖掘丝绸之路文化内涵。提供文化研学、定制旅游、文创产品等服务。',
    category: '文化旅游',
    logo: '/assets/merchants/silu.png',
    rating: 4.8,
    review_count: 211,
    location: '西安市雁塔区',
    phone: '029-87654321',
    email: 'travel@silu-culture.com',
    website: 'https://www.silu-culture.com',
    business_license: '91610113MA3E6D5C4B',
    verified: true,
    established_year: 2013,
    services: ['文化研学', '定制旅游', '文创产品', '文化传播'],
    tags: ['旅游', '文化', '研学', '丝路'],
    status: 'active',
    joined_date: '2024-02-12',
    lingzhi_points: 8900,
    total_deals: 156
  },
  {
    id: '10',
    name: '道源生态农业开发有限公司',
    description: '致力于生态农业开发与有机农产品生产，遵循自然农法理念。从源头保障食品安全，传递健康生活方式。',
    category: '生态农业',
    logo: '/assets/merchants/daoyuan.png',
    rating: 4.7,
    review_count: 178,
    location: '洛阳市嵩县',
    phone: '0379-65432109',
    email: 'farm@daoyuan-eco.com',
    website: 'https://www.daoyuan-eco.com',
    business_license: '91410325MA5F4E3D2C',
    verified: true,
    established_year: 2011,
    services: ['有机种植', '农产品销售', '农业旅游', '技术输出'],
    tags: ['农业', '生态', '有机', '健康'],
    status: 'active',
    joined_date: '2024-02-15',
    lingzhi_points: 8300,
    total_deals: 121
  }
]

const MerchantPool = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [merchants, setMerchants] = useState<Merchant[]>(MOCK_MERCHANTS)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [loading, setLoading] = useState(true)

  const categories = [
    'all',
    '文化艺术',
    '科技创新',
    '禅茶文化',
    '艺术研究',
    '数字创意',
    '国学教育',
    '设计服务',
    '健康管理',
    '文化旅游',
    '生态农业'
  ]

  useEffect(() => {
    loadMerchants()
  }, [])

  const loadMerchants = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/merchants')
      if (response.ok) {
        const data = await response.json()
        setMerchants(data.length > 0 ? data : MOCK_MERCHANTS)
      } else {
        setMerchants(MOCK_MERCHANTS)
      }
    } catch (error) {
      console.error('Failed to load merchants:', error)
      setMerchants(MOCK_MERCHANTS)
    } finally {
      setLoading(false)
    }
  }

  const filteredMerchants = merchants.filter(merchant => {
    const matchesSearch = merchant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         merchant.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         merchant.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || merchant.category === selectedCategory
    const matchesStatus = selectedStatus === 'all' || merchant.status === selectedStatus
    return matchesSearch && matchesCategory && matchesStatus
  })

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      '文化艺术': 'bg-purple-100 text-purple-800',
      '科技创新': 'bg-blue-100 text-blue-800',
      '禅茶文化': 'bg-green-100 text-green-800',
      '艺术研究': 'bg-yellow-100 text-yellow-800',
      '数字创意': 'bg-indigo-100 text-indigo-800',
      '国学教育': 'bg-red-100 text-red-800',
      '设计服务': 'bg-pink-100 text-pink-800',
      '健康管理': 'bg-teal-100 text-teal-800',
      '文化旅游': 'bg-orange-100 text-orange-800',
      '生态农业': 'bg-lime-100 text-lime-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const getStatusBadge = (status: string) => {
    const badges: { [key: string]: { icon: any; color: string; text: string } } = {
      active: { icon: CheckCircle, color: 'text-green-600', text: '活跃' },
      pending: { icon: Clock, color: 'text-yellow-600', text: '审核中' },
      suspended: { icon: AlertCircle, color: 'text-red-600', text: '已停用' }
    }
    const badge = badges[status] || badges.active
    const Icon = badge.icon
    return (
      <div className={`flex items-center gap-1 ${badge.color}`}>
        <Icon size={14} />
        <span className="text-sm">{badge.text}</span>
      </div>
    )
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        <Star size={16} className="fill-yellow-400 text-yellow-400" />
        <span className="font-medium">{rating}</span>
        <span className="text-gray-500 text-sm">({merchants.find(m => m.rating === rating)?.review_count || 0}条评价)</span>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">商家资源池</h1>
          </div>
          <p className="text-gray-600">
            发现优质企业商家，建立商业合作，共创生态价值
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">入驻商家</p>
                <p className="text-2xl font-bold text-gray-900">{merchants.length}</p>
              </div>
              <Building2 className="w-10 h-10 text-blue-600 bg-blue-50 rounded-lg p-2" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">活跃商家</p>
                <p className="text-2xl font-bold text-gray-900">{merchants.filter(m => m.status === 'active').length}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-600 bg-green-50 rounded-lg p-2" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">总交易额</p>
                <p className="text-2xl font-bold text-gray-900">
                  {merchants.reduce((sum, m) => sum + m.total_deals, 0)}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-purple-600 bg-purple-50 rounded-lg p-2" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">平均评分</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(merchants.reduce((sum, m) => sum + m.rating, 0) / merchants.length).toFixed(1)}
                </p>
              </div>
              <Star className="w-10 h-10 text-yellow-600 bg-yellow-50 rounded-lg p-2" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="搜索商家名称、描述或标签..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex-shrink-0">
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? '全部类别' : cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Status Filter */}
            <div className="flex-shrink-0">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                <option value="all">全部状态</option>
                <option value="active">活跃</option>
                <option value="pending">审核中</option>
                <option value="suspended">已停用</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results Info */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-600">
            找到 <span className="font-semibold text-gray-900">{filteredMerchants.length}</span> 个商家
          </p>
        </div>

        {/* Merchant List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredMerchants.map(merchant => (
            <div key={merchant.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                    <Building2 className="w-8 h-8 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{merchant.name}</h3>
                    {merchant.verified && (
                      <div className="flex items-center gap-1 text-blue-600">
                        <Shield size={14} />
                        <span className="text-sm">已认证</span>
                      </div>
                    )}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${getCategoryColor(merchant.category)}`}>
                  {merchant.category}
                </span>
              </div>

              {/* Description */}
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {merchant.description}
              </p>

              {/* Rating & Status */}
              <div className="flex items-center justify-between mb-4">
                {renderStars(merchant.rating)}
                {getStatusBadge(merchant.status)}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {merchant.tags.slice(0, 3).map((tag, index) => (
                  <span key={index} className="flex items-center gap-1 text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    <Tag size={10} />
                    {tag}
                  </span>
                ))}
                {merchant.tags.length > 3 && (
                  <span className="text-xs text-gray-500">+{merchant.tags.length - 3}</span>
                )}
              </div>

              {/* Info */}
              <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin size={14} />
                  <span className="truncate">{merchant.location}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar size={14} />
                  <span>{merchant.established_year}年创立</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Users size={14} />
                  <span>{merchant.total_deals}笔交易</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <DollarSign size={14} />
                  <span>{merchant.lingzhi_points}灵值</span>
                </div>
              </div>

              {/* Services */}
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-2">主营服务：</p>
                <div className="flex flex-wrap gap-1">
                  {merchant.services.slice(0, 4).map((service, index) => (
                    <span key={index} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
                      {service}
                    </span>
                  ))}
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {merchant.phone && (
                    <a href={`tel:${merchant.phone}`} className="flex items-center gap-1 hover:text-blue-600">
                      <Phone size={14} />
                    </a>
                  )}
                  {merchant.email && (
                    <a href={`mailto:${merchant.email}`} className="flex items-center gap-1 hover:text-blue-600">
                      <Mail size={14} />
                    </a>
                  )}
                  {merchant.website && (
                    <a href={merchant.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-blue-600">
                      <Globe size={14} />
                    </a>
                  )}
                </div>
                <button
                  onClick={() => navigate(`/merchant-detail/${merchant.id}`)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors"
                >
                  查看详情
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredMerchants.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无匹配商家</h3>
            <p className="text-gray-600 mb-4">尝试调整搜索条件或筛选选项</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
                setSelectedStatus('all')
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              清除筛选
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default MerchantPool
