import { useState, useEffect } from 'react'
import { Calendar, Eye, Clock, TrendingUp, Filter, Search, ArrowRight } from 'lucide-react'

interface NewsItem {
  id: number
  title: string
  content: string
  summary: string
  category: string
  view_count: number
  created_at: string
  updated_at: string
  author: string
  status: string
}

const CompanyNews = () => {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('全部')

  useEffect(() => {
    loadNews()
  }, []) // 每次组件挂载时都会调用loadNews

  const loadNews = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/company/news')
      const data = await response.json()
      
      if (data.success && data.data && data.data.length > 0) {
        // 转换数据格式
        const newsData = data.data.map((item: any) => ({
          id: item.id,
          title: item.title,
          content: item.content,
          summary: item.summary || item.content.substring(0, 150) + '...',
          category: item.category || '公司动态',
          view_count: item.view_count || 0,
          created_at: item.created_at,
          updated_at: item.updated_at,
          author: item.author || 'Admin',
          status: item.status || 'published'
        }))
        setNews(newsData)
      } else {
        // API返回空数据或失败，使用默认数据
        console.log('使用默认动态资讯数据')
        setNews(defaultNews)
      }
    } catch (error) {
      console.error('Failed to load news:', error)
      // 如果API失败，使用默认数据
      console.log('API调用失败，使用默认动态资讯数据')
      setNews(defaultNews)
    } finally {
      setLoading(false)
    }
  }

  const categories = ['全部', '产品更新', '技术突破', '战略合作', '融资消息', '人事变动', '行业奖项', '社区活动']

  // 默认动态资讯数据
  const defaultNews: NewsItem[] = [
    {
      id: 1,
      title: '灵值生态园 v2.0 版本正式发布',
      content: `我们很高兴地宣布，灵值生态园 v2.0 版本正式发布！经过三个月的开发和测试，此次重大更新带来了全新的用户界面、更流畅的交互体验以及多项新功能。

主要更新内容：

1. 全新用户界面设计：采用更现代化的UI设计风格，提升视觉体验
2. 文化转译工作流优化：简化操作流程，支持批量处理和AI辅助
3. 数字资产管理增强：新增NFT铸造、交易、展示等完整功能
4. 社区互动功能升级：支持群组聊天、动态发布、评论互动
5. 性能优化：页面加载速度提升50%，操作响应更快
6. 移动端适配：优化移动端体验，支持PWA离线访问

所有现有用户可以免费升级到新版本，立即体验全新的生态功能。我们期待您的反馈！`,
      summary: '灵值生态园 v2.0 版本正式发布，带来全新用户界面和多项新功能。',
      category: '产品更新',
      view_count: 15234,
      created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      author: '产品团队',
      status: 'published'
    },
    {
      id: 2,
      title: '区块链技术架构升级完成',
      content: `经过三个月的开发和测试，我们的区块链技术架构升级已全部完成。

升级亮点：

技术突破：
• 新架构采用最新的PoS共识机制，替代原有的PoW机制
• 交易处理速度提升300%，从原来的100 TPS提升至300 TPS
• 交易成本降低50%，大幅提升用户体验

安全保障：
• 采用多重签名技术，提升资产安全性
• 新增零知识证明功能，保护用户隐私
• 优化智能合约审计流程，确保代码安全

未来规划：
• 支持跨链操作，实现与以太坊、BSC等主流链的互通
• 推出Layer2解决方案，进一步提升交易速度
• 开发去中心化交易所，实现资产的自由交易

此次升级为未来的大规模应用奠定了坚实的技术基础。`,
      summary: '区块链技术架构升级完成，交易速度提升300%，成本降低50%。',
      category: '技术突破',
      view_count: 8932,
      created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      author: '技术团队',
      status: 'published'
    },
    {
      id: 3,
      title: '与西安文化旅游集团达成战略合作',
      content: `灵值生态园与西安文化旅游集团正式签署战略合作协议，双方将在以下领域开展深度合作：

合作内容：

1. 文化遗产数字化
   • 将西安丰富的文化遗产数字化，建立数字文化资产库
   • 开发AR/VR体验，让用户沉浸式体验西安文化
   • 制作数字文化藏品，推动文化传播

2. 文化IP开发
   • 共同开发西安特色文化IP
   • 打造系列数字艺术作品
   • 推出联名商品和活动

3. 数字资产交易
   • 建立文化数字资产交易平台
   • 提供文化IP授权和交易服务
   • 推广文化价值变现新模式

此次合作将助力西安文化资源的数字化转型，为全球用户提供更丰富的文化体验，推动文化产业创新发展。`,
      summary: '与西安文化旅游集团达成战略合作，共同推动文化遗产数字化转型。',
      category: '战略合作',
      view_count: 12345,
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      author: '市场部',
      status: 'published'
    },
    {
      id: 4,
      title: '完成 A 轮融资，估值达 1.5 亿美元',
      content: `灵值生态园成功完成 A 轮融资，由知名风险投资机构领投，多家知名机构跟投。

融资详情：

• 融资金额：5000 万美元
• 估值：1.5 亿美元
• 领投方：知名风险投资机构
• 跟投方：多家知名机构

资金用途：

1. 技术研发（40%）
   • 区块链技术持续优化
   • AI技术研发投入
   • 用户体验改进

2. 市场拓展（30%）
   • 全球市场推广
   • 品牌建设
   • 渠道合作

3. 生态建设（20%）
   • 开发者社区建设
   • 内容创作者激励
   • 合作伙伴招募

4. 团队建设（10%）
   • 优秀人才引进
   • 团队能力提升
   • 组织结构优化

本轮融资将加速推动文化数字化进程，我们期待与您共同成长！`,
      summary: '完成 A 轮融资，融资金额达 5000 万美元，估值 1.5 亿美元。',
      category: '融资消息',
      view_count: 23456,
      created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      author: 'Admin',
      status: 'published'
    },
    {
      id: 5,
      title: '任命李明博士为首席技术官',
      content: `我们很高兴地宣布，李明博士正式加入灵值生态园，担任首席技术官（CTO）。

个人简介：

李明博士在区块链、人工智能和云计算领域拥有超过15年的研究和实践经验。他曾在多家知名科技公司担任技术负责人，领导团队完成了多个大型项目的技术研发和落地。

主要成就：

• 发表学术论文50余篇，引用次数超过5000次
• 获得10余项技术专利
• 主导开发了多个成功的区块链项目
• 在AI领域有深入研究，推动多个AI项目的商业化

未来规划：

李明博士将负责公司的整体技术战略和研发工作，重点关注以下方向：

1. 区块链技术的持续优化和创新
2. AI技术在文化数字化领域的应用
3. 大规模分布式系统架构设计
4. 技术团队建设和人才培养

我们相信，在李明博士的带领下，我们的技术实力将更上一层楼！`,
      summary: '任命李明博士为首席技术官，负责公司技术战略和研发工作。',
      category: '人事变动',
      view_count: 6789,
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      author: '人力资源部',
      status: 'published'
    },
    {
      id: 6,
      title: '荣获"2024年度最佳文化科技企业"奖项',
      content: `在刚刚结束的2024年度文化科技峰会上，灵值生态园凭借在文化遗产数字化领域的创新实践和突出贡献，荣获"2024年度最佳文化科技企业"奖项。

评选标准：

本次评选由多家权威机构联合发起，评选标准包括：

1. 技术创新能力
2. 行业影响力
3. 社会价值贡献
4. 用户满意度
5. 发展潜力

获奖理由：

灵值生态园在文化数字化领域有以下突出贡献：

• 首创文化转译工作流，让传统文化焕发新生
• 建立完善的数字资产管理体系
• 推动文化价值的发现和传播
• 为创作者提供便捷的创作和变现平台
• 促进文化产业的数字化转型

感言：

这个奖项是对我们团队努力的认可，也是对我们未来发展的激励。我们将继续深耕文化数字化领域，为推动文化产业创新发展贡献力量！

感谢所有用户和合作伙伴的支持！`,
      summary: '荣获"2024年度最佳文化科技企业"奖项，是对创新实践的认可。',
      category: '行业奖项',
      view_count: 9876,
      created_at: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(),
      author: '市场部',
      status: 'published'
    },
    {
      id: 7,
      title: '举办首届文化数字化创作者大赛',
      content: `灵值生态园正式宣布举办首届文化数字化创作者大赛，面向全球征集优秀的文化数字化作品。

大赛信息：

• 大赛主题：传统文化，数字新生
• 征集时间：2024年3月1日 - 2024年6月30日
• 评选时间：2024年7月1日 - 2024年7月15日
• 结果公布：2024年7月20日

奖项设置：

特等奖：1名，奖金 30 万元
一等奖：3名，奖金 10 万元/名
二等奖：10名，奖金 3 万元/名
三等奖：30名，奖金 5 千元/名
优秀奖：50名，奖金 1 千元/名

参与方式：

1. 在灵值生态园平台注册账号
2. 提交作品，包括作品描述、创作理念等
3. 作品将通过专业评审和用户投票评选

评选标准：

1. 文化价值：是否体现传统文化特色
2. 创新性：是否在数字化表现上有创新
3. 技术性：技术实现水平
4. 艺术性：艺术表现力和审美价值

我们希望通过此次大赛，发掘更多优秀的文化创作者，推动文化数字化的发展，让传统文化在数字时代焕发新生！`,
      summary: '举办首届文化数字化创作者大赛，总奖金池达 100 万元。',
      category: '社区活动',
      view_count: 15678,
      created_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
      author: '社区运营部',
      status: 'published'
    },
    {
      id: 8,
      title: '推出 AI 智能客服系统',
      content: `为了提升用户体验，灵值生态园正式推出 AI 智能客服系统。

系统特点：

1. 24小时在线：提供全天候服务支持
2. 智能问答：基于大语言模型，准确理解用户需求
3. 多模态交互：支持文字、语音、图片等多种交互方式
4. 上下文理解：支持多轮对话，理解上下文语义
5. 自学习能力：根据用户反馈不断优化

功能介绍：

• 账户问题：注册、登录、密码找回等
• 功能咨询：平台功能使用方法、操作指导等
• 技术支持：解决使用过程中遇到的技术问题
• 投诉建议：收集用户反馈，不断改进服务

使用方式：

1. 点击页面右下角的客服图标
2. 选择文字或语音输入方式
3. 输入您的问题
4. 获得智能客服的回答

未来规划：

我们计划在以下几个方面继续优化：

• 支持更多语言，服务全球用户
• 增加情感识别，提供更贴心的服务
• 集成视频通话，提供更直观的支持
• 开发自助服务系统，提升服务效率

AI 智能客服系统的推出，标志着我们的服务水平迈上新台阶。我们期待通过技术创新，为用户提供更好的服务体验！`,
      summary: '推出 AI 智能客服系统，提供 24 小时不间断的服务支持。',
      category: '产品更新',
      view_count: 11234,
      created_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
      author: '产品团队',
      status: 'published'
    },
    {
      id: 9,
      title: '与文化部数字文化工程达成合作',
      content: `灵值生态园与文化部数字文化工程正式达成合作关系，双方将共同推动文化遗产的数字化保护和传承。

合作背景：

文化部数字文化工程是国家重点文化项目，旨在通过数字技术保护和传承中华优秀传统文化。

合作内容：

1. 建立文化数字资源库
   • 收集整理各类文化数字资源
   • 建立标准化资源管理体系
   • 提供资源共享和检索服务

2. 开发文化教育平台
   • 利用数字技术开发在线教育平台
   • 提供文化知识普及服务
   • 开展线上线下文化教育活动

3. 开展文化交流活动
   • 组织文化数字展览
   • 举办文化主题活动
   • 促进国际文化交流

合作意义：

• 推动文化遗产的数字化保护
• 提升公众文化素养
• 促进文化产业发展
• 增强文化软实力

未来展望：

我们将继续深化合作，探索文化数字化的新路径，为文化强国建设贡献力量！`,
      summary: '与文化部数字文化工程达成合作，推动文化遗产数字化保护。',
      category: '战略合作',
      view_count: 13456,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      author: '市场部',
      status: 'published'
    },
    {
      id: 10,
      title: '推出跨链互操作功能',
      content: `灵值生态园正式推出跨链互操作功能，这是区块链领域的重要突破。

技术亮点：

1. 多链支持
   • 支持以太坊（ETH）
   • 支持币安智能链（BSC）
   • 支持波场（TRON）
   • 支持 Polygon（MATIC）

2. 安全可靠
   • 采用多重签名验证
   • 使用零知识证明保护隐私
   • 经过严格的安全审计

3. 快速便捷
   • 一键跨链转账
   • 实时汇率计算
   • 自动路由优化

功能介绍：

• 资产互通：在不同区块链之间自由转移数字资产
• 价值发现：发现各链上的优质资产
• 流动性聚合：聚合各链流动性，提升交易体验
• 降低成本：减少跨链手续费

使用步骤：

1. 连接钱包
2. 选择源链和目标链
3. 输入转账金额
4. 确认交易
5. 等待跨链完成

未来规划：

• 支持更多区块链网络
• 优化跨链速度
• 降低跨链成本
• 开发跨链交易策略

跨链互操作功能的推出，标志着灵值生态园在区块链技术领域迈出了重要一步。我们将继续推动区块链技术的创新和应用，为用户提供更优质的服务！`,
      summary: '推出跨链互操作功能，支持多个主流区块链网络的资产互通。',
      category: '技术突破',
      view_count: 14567,
      created_at: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000).toISOString(),
      author: '技术团队',
      status: 'published'
    }
  ]

  const filteredNews = news.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === '全部' || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] pt-20 pb-8">
      <div className="container mx-auto px-4">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00C3FF] via-[#47D1FF] to-[#00C3FF] bg-clip-text text-transparent mb-2">
            公司动态
          </h1>
          <p className="text-[#B4C7E7]">了解灵值生态园的最新动态和发展方向</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00C3FF]/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-[#00C3FF]" />
              </div>
              <span className="text-[#B4C7E7]">总动态数</span>
            </div>
            <div className="text-3xl font-bold text-white">{news.length}</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#FFB800]/20 rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-[#FFB800]" />
              </div>
              <span className="text-[#B4C7E7]">总浏览量</span>
            </div>
            <div className="text-3xl font-bold text-white">
              {news.reduce((sum, item) => sum + (item.view_count || 0), 0).toLocaleString()}
            </div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[#00FF88]/20 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-[#00FF88]" />
              </div>
              <span className="text-[#B4C7E7]">本月更新</span>
            </div>
            <div className="text-3xl font-bold text-white">{news.length}</div>
          </div>
        </div>

        {/* 筛选栏 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#B4C7E7] w-5 h-5" />
              <input
                type="text"
                placeholder="搜索动态..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0A0D18] border border-[#00C3FF]/30 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-[#B4C7E7]/60 focus:outline-none focus:border-[#00C3FF]"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2.5 rounded-lg transition-all ${
                    selectedCategory === cat
                      ? 'bg-[#00C3FF]/30 text-white border border-[#00C3FF]'
                      : 'bg-[#0A0D18] text-[#B4C7E7] border border-[#00C3FF]/20 hover:border-[#00C3FF]/50'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 动态列表 */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-[#B4C7E7]">加载中...</div>
          </div>
        ) : news.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-[#B4C7E7]">暂无动态</div>
          </div>
        ) : (
          <div className="space-y-6">
          {filteredNews.map(item => (
            <div key={item.id} className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 hover:border-[#00C3FF]/50 transition-all group">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-[#00C3FF]/10 text-[#00C3FF] rounded text-xs">
                      {item.category}
                    </span>
                    <span className="px-2 py-1 bg-[#FFB800]/10 text-[#FFB800] rounded text-xs">
                      {item.author}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-white mb-2 group-hover:text-[#00C3FF] transition-all">
                    {item.title}
                  </h2>
                </div>
              </div>
              <p className="text-[#B4C7E7] mb-4 leading-relaxed">{item.content}</p>
              <div className="flex items-center justify-between text-xs text-[#B4C7E7]/60">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(item.created_at).toLocaleString('zh-CN', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    <span>{item.view_count.toLocaleString()} 次浏览</span>
                  </div>
                </div>
                <button className="flex items-center gap-1 text-[#00C3FF] hover:gap-2 transition-all">
                  查看详情 <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default CompanyNews
