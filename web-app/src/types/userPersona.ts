// 用户类型定义
export enum UserType {
  CULTURE_LOVER = 'culture_lover',           // 文化爱好者
  CREATOR = 'creator',                        // 创作者
  BUSINESS = 'business',                      // 商业人士
  SCHOLAR = 'scholar',                        // 研究学者
  INVESTOR = 'investor',                      // 投资者
}

// 用户类型信息接口
export interface UserTypeConfig {
  id: UserType
  name: string
  description: string
  icon: string
  color: string
  interests: string[]
  recommendedPages: string[]
  benefits: string[]
}

// 用户类型配置
export const USER_TYPES: UserTypeConfig[] = [
  {
    id: UserType.CULTURE_LOVER,
    name: '文化爱好者',
    description: '热爱传统文化、艺术和美学，探索文化之美',
    icon: '🏛️',
    color: 'from-purple-500 to-pink-500',
    interests: ['传统文化', '美学艺术', '文化转译', '历史探索'],
    recommendedPages: ['知识库', '文化转译', '文化项目'],
    benefits: ['深度文化知识库', '文化转译工具', '文化项目参与机会', '美学内容鉴赏']
  },
  {
    id: UserType.CREATOR,
    name: '创作者',
    description: '设计师、艺术家、内容创作者，寻找创作灵感',
    icon: '🎨',
    color: 'from-blue-500 to-cyan-500',
    interests: ['设计创作', '艺术表达', '内容产出', '灵感发现'],
    recommendedPages: ['设计展示', '资源市场', '智能对话', '美学侦探'],
    benefits: ['设计资源库', 'AI创意助手', '作品展示平台', '创作灵值奖励']
  },
  {
    id: UserType.BUSINESS,
    name: '商业人士',
    description: '企业家、创业者、市场营销，探索商业价值',
    icon: '💼',
    color: 'from-green-500 to-emerald-500',
    interests: ['商业模式', '品牌建设', '市场推广', '合作机会'],
    recommendedPages: ['公司项目', '合伙招募', '资源市场', '智能对话'],
    benefits: ['商业资源对接', '项目合作机会', '品牌曝光平台', '灵值激励体系']
  },
  {
    id: UserType.SCHOLAR,
    name: '研究学者',
    description: '研究员、学者、学生，追求学术探索',
    icon: '📚',
    color: 'from-orange-500 to-yellow-500',
    interests: ['学术研究', '知识探索', '理论分析', '数据研究'],
    recommendedPages: ['知识库', '智能对话', '数据分析', '用户学习'],
    benefits: ['海量知识库', 'AI研究助手', '数据分析工具', '学术资源']
  },
  {
    id: UserType.INVESTOR,
    name: '投资者',
    description: '投资人、合伙人，寻找投资机会',
    icon: '💎',
    color: 'from-amber-500 to-red-500',
    interests: ['投资机会', '项目评估', '价值发现', '合作共赢'],
    recommendedPages: ['公司项目', '合伙招募', '公司信息', '动态资讯'],
    benefits: ['优质项目池', '投资机会推荐', '平台透明度', '灵值投资体系']
  }
]

// 获取用户类型配置
export const getUserTypeConfig = (typeId: UserType): UserTypeConfig | undefined => {
  return USER_TYPES.find(type => type.id === typeId)
}
