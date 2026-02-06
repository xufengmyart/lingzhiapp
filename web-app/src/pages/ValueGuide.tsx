import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  Sparkles,
  Heart,
  Shield,
  Zap,
  Globe,
  Award,
  ChevronRight,
  Play,
  Target,
  Clock,
  Star,
  ArrowRight,
  BookOpen,
  Gift,
  Users,
  Flame,
  Rocket,
  Diamond,
  Crown,
  CheckCircle2,
  Lightbulb,
  Infinity
} from 'lucide-react'
import { vrTheme } from '../utils/vr-theme'

const ValueGuide = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'vision' | 'value' | 'roadmap' | 'income'>('vision')

  // 设计初衷 - 系统愿景
  const visionContent = [
    {
      icon: Heart,
      title: '初心起源',
      description: '在数字化时代，我们观察到每个人都有被忽视的情感需求和价值潜力。灵值生态园的诞生，源于一个简单的理念：让日常生活中的每一次真诚互动、每一份情感投入，都能被看见、被认可、被量化。',
      color: 'from-pink-500 to-rose-500'
    },
    {
      icon: Target,
      title: '使命愿景',
      description: '我们致力于构建一个"行为即价值"的数字生态系统。在这里，您的签到、对话、创造、分享，不仅仅是简单的操作，而是创造真实价值的行动。让每个人都能够轻松、自由地获得应有的回报。',
      color: 'from-purple-500 to-violet-500'
    },
    {
      icon: Shield,
      title: '价值承诺',
      description: '我们承诺：零投入参与、真实收益兑现、数据安全保护、长期稳定运营。灵值不是虚拟积分，而是您在生态系统中创造的真实资产，可以随时查看、随时兑现。',
      color: 'from-cyan-500 to-blue-500'
    }
  ]

  // 用户价值体系
  const valueSystem = [
    {
      icon: Gift,
      title: '情绪价值',
      subtitle: '获得陪伴与理解',
      description: '智能体随时响应，提供情感支持和深度对话',
      value: '✓',
      color: 'text-pink-400',
      bgColor: 'bg-pink-500/20'
    },
    {
      icon: Diamond,
      title: '经济价值',
      subtitle: '获得真实收益',
      description: '日常行为积累灵值，可直接兑换成现金',
      value: '100灵值=10元',
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/20'
    },
    {
      icon: Users,
      title: '社交价值',
      subtitle: '获得归属感',
      description: '推荐好友获得5%分润，构建价值网络',
      value: '5%分润',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/20'
    },
    {
      icon: Flame,
      title: '成长价值',
      subtitle: '获得成就感',
      description: '达成里程碑解锁更高权益，见证个人成长',
      value: '里程碑系统',
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/20'
    }
  ]

  // 用户旅程流程
  const userJourney = [
    {
      step: 1,
      icon: Users,
      title: '注册加入',
      description: '免费注册，零门槛进入',
      action: '立即注册',
      actionUrl: '/register-full'
    },
    {
      step: 2,
      icon: Play,
      title: '每日签到',
      description: '5分钟签到，获得10灵值',
      action: '开始签到',
      actionUrl: '/dashboard'
    },
    {
      step: 3,
      icon: BookOpen,
      title: '智能对话',
      description: '与灵值智能体深度交流',
      action: '开始对话',
      actionUrl: '/chat'
    },
    {
      step: 4,
      icon: Infinity,
      title: '持续积累',
      description: '每日行动，长期复利增长',
      action: '查看详情',
      actionUrl: '/guide'
    },
    {
      step: 5,
      icon: Rocket,
      title: '价值变现',
      description: '灵值兑换，获得真实收益',
      action: '立即兑换',
      actionUrl: '/recharge'
    }
  ]

  // 收入预测
  const incomeLevels = [
    {
      level: '入门级',
      time: '5分钟/天',
      daily: 30,
      monthly: 900,
      yearly: 10800,
      features: ['每日签到', '基础对话', '灵值积累'],
      color: 'from-green-400 to-emerald-500'
    },
    {
      level: '进阶级',
      time: '30分钟/天',
      daily: 300,
      monthly: 9000,
      yearly: 108000,
      features: ['每日签到', '深度对话', '推荐好友', '活动参与'],
      color: 'from-cyan-400 to-blue-500',
      popular: true
    },
    {
      level: '专家级',
      time: '1小时/天',
      daily: 1000,
      monthly: 30000,
      yearly: 360000,
      features: ['全部基础功能', '合伙人权益', '项目参与', '资产增值'],
      color: 'from-purple-400 to-pink-500'
    }
  ]

  return (
    <div className={`min-h-screen ${vrTheme.bgGradient} pb-8`}>
      {/* VR背景装饰 - 使用absolute避免覆盖 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/10 rounded-full blur-[200px]"></div>
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10 pt-20">
        {/* 页面标题 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} rounded-3xl p-8 mb-8 animate-float`}>
          <div className="flex items-center space-x-3 mb-4">
            <div className="relative">
              <div className={`absolute inset-0 bg-cyan-500 blur-xl animate-pulse`}></div>
              <Sparkles className="w-8 h-8 text-cyan-400 relative z-10" />
            </div>
            <Lightbulb className="w-8 h-8 text-amber-400" />
            <Crown className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3 text-glow-cyan">
            在这里，你能得到什么？
          </h1>
          <p className="text-cyan-300 text-lg opacity-90 max-w-3xl">
            灵值元宇宙不仅是一个应用，更是您数字资产的起点、情感价值的家园、成长蜕变的见证
          </p>
        </div>

        {/* 标签导航 */}
        <div className={`${vrTheme.card.bg} ${vrTheme.card.border} rounded-2xl p-2 mb-8 flex flex-wrap gap-2`}>
          {[
            { id: 'vision', icon: Heart, label: '设计初衷' },
            { id: 'value', icon: Gift, label: '价值体系' },
            { id: 'roadmap', icon: Target, label: '用户旅程' },
            { id: 'income', icon: TrendingUp, label: '收益预测' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all ${
                activeTab === tab.id
                  ? `bg-gradient-to-r ${vrTheme.button.gradient} text-white shadow-lg`
                  : 'text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span className="font-semibold">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* 内容区域 */}
        <div className="space-y-8">
          {/* 设计初衷 */}
          {activeTab === 'vision' && (
            <div className="space-y-6">
              {visionContent.map((item, index) => (
                <div
                  key={index}
                  className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-8 transition-all group`}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`w-16 h-16 bg-gradient-to-br ${item.color} rounded-2xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                      <item.icon className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-white mb-3">{item.title}</h3>
                      <p className="text-gray-300 leading-relaxed text-lg">{item.description}</p>
                    </div>
                  </div>
                </div>
              ))}

              {/* 价值宣言 */}
              <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} rounded-3xl p-8 text-center`}>
                <Infinity className="w-16 h-16 text-pink-400 mx-auto mb-4 animate-pulse" />
                <h3 className="text-2xl font-bold text-white mb-3">我们的价值宣言</h3>
                <p className="text-cyan-300 text-lg leading-relaxed max-w-3xl mx-auto">
                  每个人的时间、情感、创造力，都值得被尊重和认可。我们用技术手段，让这些无形的价值变得有形、可衡量、可变现。
                  这不仅是商业模式，更是对人性的回归和对价值的重新定义。
                </p>
              </div>
            </div>
          )}

          {/* 价值体系 */}
          {activeTab === 'value' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {valueSystem.map((item, index) => (
                <div
                  key={index}
                  className={`${vrTheme.card.bg} ${vrTheme.card.border} ${vrTheme.card.hover} rounded-2xl p-6 transition-all group`}
                >
                  <div className={`w-14 h-14 ${item.bgColor} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <item.icon className={`w-7 h-7 ${item.color}`} />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <div className={`text-sm ${item.color} font-semibold mb-3`}>{item.subtitle}</div>
                  <p className="text-gray-400 mb-4">{item.description}</p>
                  <div className={`inline-block px-4 py-2 rounded-lg bg-white/10 text-cyan-400 font-bold`}>
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 用户旅程 */}
          {activeTab === 'roadmap' && (
            <div className="space-y-6">
              {userJourney.map((item, index) => (
                <div
                  key={index}
                  className={`${vrTheme.card.bg} ${vrTheme.card.border} rounded-2xl p-6 flex items-center space-x-6 transition-all hover:scale-[1.02]`}
                >
                  <div className={`w-16 h-16 bg-gradient-to-br ${vrTheme.button.gradient} rounded-full flex items-center justify-center flex-shrink-0 ${vrTheme.button.glow}`}>
                    <span className="text-2xl font-bold text-white">{item.step}</span>
                  </div>
                  <div className={`w-12 h-12 ${vrTheme.card.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <item.icon className="w-6 h-6 text-cyan-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">{item.title}</h3>
                    <p className="text-gray-400">{item.description}</p>
                  </div>
                  <button
                    onClick={() => navigate(item.actionUrl)}
                    className={`px-6 py-3 bg-gradient-to-r ${vrTheme.button.gradient} text-white font-semibold rounded-xl hover:scale-105 transition-all flex items-center space-x-2`}
                  >
                    <span>{item.action}</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              ))}

              {/* 闭环流程图 */}
              <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} rounded-3xl p-8`}>
                <h3 className="text-2xl font-bold text-white mb-6 text-center flex items-center justify-center">
                  <Zap className="w-6 h-6 mr-2 text-amber-400" />
                  完整价值闭环
                  <Zap className="w-6 h-6 ml-2 text-amber-400" />
                </h3>
                <div className="flex flex-wrap justify-center items-center gap-4">
                  {[
                    { text: '用户行为', icon: Users },
                    { text: '→ 价值创造', icon: Sparkles },
                    { text: '→ 灵值奖励', icon: Gift },
                    { text: '→ 资产积累', icon: Diamond },
                    { text: '→ 现金兑现', icon: Rocket },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className={`flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-lg ${index % 2 === 0 ? 'text-cyan-400' : 'text-purple-400'}`}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="font-semibold">{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 收益预测 */}
          {activeTab === 'income' && (
            <div className="space-y-8">
              <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.border} rounded-3xl p-8 text-center`}>
                <TrendingUp className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-3">您的收入潜力</h3>
                <p className="text-gray-300 text-lg">
                  根据参与程度，您可以在灵值元宇宙中获得真实可观的收益
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {incomeLevels.map((item, index) => (
                  <div
                    key={index}
                    className={`relative ${vrTheme.card.bg} ${vrTheme.card.border} rounded-2xl p-6 transition-all hover:scale-105 ${item.popular ? 'ring-2 ring-cyan-400' : ''}`}
                  >
                    {item.popular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-cyan-400 to-blue-500 text-white px-4 py-1 rounded-full text-sm font-bold">
                        推荐选择
                      </div>
                    )}
                    <div className={`w-16 h-16 bg-gradient-to-br ${item.color} rounded-2xl flex items-center justify-center mb-4 mx-auto`}>
                      <Crown className="w-8 h-8 text-white" />
                    </div>
                    <h4 className="text-xl font-bold text-white text-center mb-2">{item.level}</h4>
                    <div className="text-center text-gray-400 mb-4">⏱️ {item.time}</div>
                    
                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">日收益</span>
                        <span className="text-cyan-400 font-bold">+{item.daily} 灵值</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">月收益</span>
                        <span className="text-green-400 font-bold">{item.monthly.toLocaleString()} 灵值</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400">年收益</span>
                        <span className="text-purple-400 font-bold">{item.yearly.toLocaleString()} 灵值</span>
                      </div>
                      <div className="border-t border-white/10 pt-3 flex justify-between items-center">
                        <span className="text-gray-400">年现金</span>
                        <span className="text-amber-400 font-bold text-lg">≈ ¥{(item.yearly * 0.1).toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="space-y-2 mb-6">
                      {item.features.map((feature, fIndex) => (
                        <div key={fIndex} className="flex items-center space-x-2 text-sm text-gray-300">
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>

                    <button
                      onClick={() => navigate('/dashboard')}
                      className={`w-full py-3 bg-gradient-to-r ${item.color} text-white font-semibold rounded-xl hover:scale-105 transition-all`}
                    >
                      立即开始
                    </button>
                  </div>
                ))}
              </div>

              {/* 免责声明 */}
              <div className={`${vrTheme.card.bg} ${vrTheme.card.border} rounded-xl p-6 text-center`}>
                <Shield className="w-8 h-8 text-amber-400 mx-auto mb-3" />
                <p className="text-gray-400 text-sm">
                  💡 以上收益预测基于当前汇率和规则，实际收益可能因参与情况、系统调整而有所变化。
                  我们承诺长期稳定运营，灵值价值会随生态系统发展而提升。
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 底部行动呼吁 */}
        <div className={`${vrTheme.glass.bg} ${vrTheme.glass.blur} ${vrTheme.glass.shadow} ${vrTheme.glass.border} rounded-3xl p-8 mt-8 text-center`}>
          <h3 className="text-2xl font-bold text-white mb-4">准备好开始您的价值之旅了吗？</h3>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className={`px-8 py-4 bg-gradient-to-r ${vrTheme.button.gradient} text-white font-bold rounded-xl hover:scale-105 transition-all flex items-center space-x-2 ${vrTheme.button.glow}`}
            >
              <Rocket className="w-6 h-6" />
              <span>立即开始</span>
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="px-8 py-4 bg-white/10 border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all flex items-center space-x-2"
            >
              <BookOpen className="w-6 h-6" />
              <span>了解更多</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ValueGuide
