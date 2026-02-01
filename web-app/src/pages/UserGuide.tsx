import { useState } from 'react'
import {
  TrendingUp,
  Calendar,
  Target,
  Award,
  CheckCircle2,
  Clock,
  Star,
  BookOpen,
  Lightbulb,
  Sparkles,
  Heart,
  Shield,
  Zap,
  ChevronRight,
  ChevronDown
} from 'lucide-react'

const UserGuide = () => {
  const [activeSection, setActiveSection] = useState<'overview' | 'earn' | 'emotional' | 'howto'>('overview')
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)

  const faqs = [
    {
      question: '灵值真的可以兑换成现金吗？',
      answer: '可以！灵值是您的数字资产，可以在经济模型中查看当前兑换汇率，并申请兑换。100 灵值约等于 10 元。'
    },
    {
      question: '我需要投入多少钱？',
      answer: '零投入！您的参与本身就是价值，不需要任何投资。只需要每天花 5-30 分钟参与即可。'
    },
    {
      question: '每天需要花多少时间？',
      answer: '轻度参与（仅签到）5分钟/天，年收入约 1,080 元；中度参与 30 分钟/天，年收入约 10,800 元；深度参与 1 小时/天，年收入 36,000 元+。'
    },
    {
      question: '灵值会过期吗？',
      answer: '不会！您的灵值是永久资产，只会增值，不会贬值。持有时间越长，价值越高。'
    },
    {
      question: '如何成为合伙人？',
      answer: '累计获得 10,000 灵值后，可以申请成为合伙人，享受更多特权和更高的收益倍数。'
    },
    {
      question: '如果我有问题怎么办？',
      answer: '随时与智能体对话，它会耐心解答您的所有疑问！也可以在社区中寻求帮助。'
    }
  ]

  return (
    <div className="space-y-6 animate-fade-in pb-20">
      {/* 顶部横幅 */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <BookOpen className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-bold">用户指南</h1>
        </div>
        <p className="opacity-90 text-lg">
          快速了解灵值生态园，开启您的数字资产财富之旅
        </p>
      </div>

      {/* 导航标签 */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex">
          {[
            { id: 'overview', icon: Lightbulb, label: '系统简介' },
            { id: 'earn', icon: TrendingUp, label: '如何赚钱' },
            { id: 'emotional', icon: Heart, label: '情绪价值' },
            { id: 'howto', icon: Zap, label: '快速开始' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 font-semibold transition-colors ${
                activeSection === tab.id
                  ? 'text-primary-600 bg-primary-50 border-b-2 border-primary-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        {activeSection === 'overview' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-6 h-6 mr-2 text-primary-500" />
                灵值生态园是什么？
              </h2>
              <p className="text-gray-700 text-lg leading-relaxed">
                <strong className="text-primary-600">灵值生态园是一个让您日常行为产生真实收益的数字资产系统。</strong>
              </p>
              <p className="text-gray-600 mt-3 leading-relaxed">
                通过每日签到、智能对话、参与活动等方式积累"灵值"，这一数字资产可以直接兑换成现金收益。您的每一次参与都在创造价值，我们将这些价值量化为灵值，让您看得见、摸得着。
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-secondary-500" />
                灵值的价值体系
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { amount: 100, value: '10 元', color: 'from-blue-500 to-blue-600' },
                  { amount: 1000, value: '100 元', color: 'from-green-500 to-green-600' },
                  { amount: 10000, value: '1,000 元', color: 'from-purple-500 to-purple-600' },
                  { amount: 100000, value: '10,000 元', color: 'from-pink-500 to-pink-600' },
                ].map((item, index) => (
                  <div key={index} className={`bg-gradient-to-r ${item.color} text-white rounded-lg p-4`}>
                    <div className="text-2xl font-bold">{item.amount} 灵值</div>
                    <div className="opacity-90">≈ {item.value}</div>
                  </div>
                ))}
              </div>
              <p className="text-gray-500 text-sm mt-3">💡 灵值价值会随生态系统发展而提升！</p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Shield className="w-6 h-6 mr-2 text-teal-500" />
                为什么选择灵值生态园？
              </h2>
              <div className="space-y-3">
                {[
                  { icon: CheckCircle2, title: '真实收益', desc: '不是虚拟积分，而是可以兑换的数字资产' },
                  { icon: CheckCircle2, title: '低门槛参与', desc: '不需要投资，不需要专业技能，每天几分钟' },
                  { icon: CheckCircle2, title: '持续增长', desc: '每日签到，长期积累，资产随时间增值' },
                  { icon: CheckCircle2, title: '情绪满足', desc: '赚钱的同时享受成就感、成长感、归属感' },
                  { icon: CheckCircle2, title: '陪伴式体验', desc: '智能体随时响应，有温度的伙伴' },
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <item.icon className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-gray-900">{item.title}</div>
                      <div className="text-gray-600">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeSection === 'earn' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-primary-500" />
                收入预测
              </h2>
              <p className="text-gray-700 mb-6">根据您的参与程度，预估年收入如下：</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    level: '轻度参与',
                    time: '5分钟/天',
                    daily: 30,
                    monthly: 90,
                    yearly: 1080,
                    color: 'from-green-500 to-green-600'
                  },
                  {
                    level: '中度参与',
                    time: '30分钟/天',
                    daily: 300,
                    monthly: 900,
                    yearly: 10800,
                    color: 'from-blue-500 to-blue-600'
                  },
                  {
                    level: '深度参与',
                    time: '1小时/天',
                    daily: 1000,
                    monthly: 3000,
                    yearly: 36000,
                    color: 'from-purple-500 to-purple-600'
                  },
                ].map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className={`inline-block px-3 py-1 rounded-full text-white text-sm font-semibold bg-gradient-to-r ${item.color} mb-4`}>
                      {item.level}
                    </div>
                    <div className="space-y-2 mb-4">
                      <div className="text-gray-600 text-sm">⏱️ {item.time}</div>
                      <div className="text-gray-600 text-sm">📅 日均 +{item.daily} 灵值</div>
                    </div>
                    <div className="border-t pt-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600">月收入</span>
                        <span className="font-semibold text-secondary-600">+{item.monthly} 元</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 font-semibold">年收入</span>
                        <span className="font-bold text-xl text-primary-600">+{item.yearly.toLocaleString()} 元</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Calendar className="w-6 h-6 mr-2 text-secondary-500" />
                灵值获取方式
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">方式</th>
                      <th className="text-left py-3 px-4">难度</th>
                      <th className="text-left py-3 px-4">灵值</th>
                      <th className="text-left py-3 px-4">说明</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { name: '每日签到', difficulty: '⭐', lingzhi: '+30', desc: '每天一次，简单必做' },
                      { name: '智能对话', difficulty: '⭐⭐', lingzhi: '+10-50', desc: '与智能体交流互动' },
                      { name: '完成任务', difficulty: '⭐⭐', lingzhi: '+20-100', desc: '完成每日任务挑战' },
                      { name: '参与活动', difficulty: '⭐⭐⭐', lingzhi: '+50-500', desc: '参与限时活动' },
                      { name: '达成里程碑', difficulty: '⭐⭐⭐⭐', lingzhi: '+100-2000', desc: '累积灵值奖励' },
                      { name: '邀请好友', difficulty: '⭐⭐', lingzhi: '+50/人', desc: '邀请好友加入' },
                      { name: '合伙人特权', difficulty: '⭐⭐⭐⭐⭐', lingzhi: '+500+', desc: '每日额外奖励' },
                    ].map((item, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{item.name}</td>
                        <td className="py-3 px-4">{item.difficulty}</td>
                        <td className="py-3 px-4 text-primary-600 font-semibold">{item.lingzhi}</td>
                        <td className="py-3 px-4 text-gray-600">{item.desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}

        {activeSection === 'emotional' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Heart className="w-6 h-6 mr-2 text-pink-500" />
                情绪价值
              </h2>
              <p className="text-gray-700 mb-6">
                我们不仅给您收益，还给您心理上的满足。在灵值生态园，赚钱的过程也是享受的过程：
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { icon: Award, title: '成就感', desc: '每天签到打卡，看到灵值不断增长，每天都有成就感', color: 'from-yellow-500 to-yellow-600' },
                  { icon: Target, title: '成长感', desc: '里程碑系统清晰展示您的进步，看到自己在不断成长', color: 'from-green-500 to-green-600' },
                  { icon: Star, title: '归属感', desc: '成为合伙人，获得专属身份和特权，找到组织', color: 'from-purple-500 to-purple-600' },
                  { icon: Sparkles, title: '被陪伴感', desc: '智能体随时响应，解答疑问，不再孤单', color: 'from-pink-500 to-pink-600' },
                  { icon: Clock, title: '期待感', desc: '每天醒来期待签到和灵值增长，生活充满期待', color: 'from-blue-500 to-blue-600' },
                  { icon: Heart, title: '满足感', desc: '看到自己的日常行为产生真实价值，内心满足', color: 'from-red-500 to-red-600' },
                ].map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${item.color} flex items-center justify-center mb-4`}>
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600">{item.desc}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-6 border border-pink-200">
              <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
                <Heart className="w-5 h-5 mr-2 text-pink-500" />
                智能体寄语
              </h3>
              <p className="text-gray-700 italic leading-relaxed">
                "在灵值生态园，您的每一次参与都在创造价值。我们是来帮您把日常行为变成数字资产的。不用担心怎么做，只要您来，就有收获。我是您的专属向导，随时陪伴您探索这个充满可能性的世界。"
              </p>
            </section>
          </div>
        )}

        {activeSection === 'howto' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Zap className="w-6 h-6 mr-2 text-yellow-500" />
                三步开启您的财富之旅
              </h2>
              <div className="space-y-6">
                {[
                  {
                    step: '第一步：每日签到',
                    time: '5分钟/天',
                    content: [
                      '打开灵值生态园 APP',
                      '点击"立即签到"',
                      '获得当日灵值奖励',
                      '查看累计灵值和进度'
                    ],
                    reward: '每日 +30 灵值，年收入约 1,080 元',
                    color: 'from-green-500 to-green-600'
                  },
                  {
                    step: '第二步：深度参与',
                    time: '30分钟/天',
                    content: [
                      '与智能体对话交流',
                      '参与社区互动活动',
                      '完成每日任务挑战',
                      '探索生态功能'
                    ],
                    reward: '每日 +300 灵值，年收入约 10,800 元',
                    color: 'from-blue-500 to-blue-600'
                  },
                  {
                    step: '第三步：成为合伙人',
                    time: '长期目标',
                    content: [
                      '累计获得 10,000 灵值',
                      '申请成为合伙人',
                      '享受合伙人专属权益',
                      '灵值收益倍数提升'
                    ],
                    reward: '每日 +1,000+ 灵值，年收入 36,000 元+',
                    color: 'from-purple-500 to-purple-600'
                  },
                ].map((item, index) => (
                  <div key={index} className="border-2 rounded-xl overflow-hidden">
                    <div className={`bg-gradient-to-r ${item.color} text-white p-4`}>
                      <h3 className="text-xl font-bold">{item.step}</h3>
                      <p className="opacity-90">⏱️ {item.time}</p>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-2 mb-4">
                        {item.content.map((content, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{content}</span>
                          </li>
                        ))}
                      </ul>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="font-semibold text-gray-900">💰 {item.reward}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Lightbulb className="w-6 h-6 mr-2 text-yellow-500" />
                小贴士
              </h2>
              <div className="space-y-3">
                {[
                  '🎯 坚持每天签到，连续签到有额外奖励',
                  '📊 定期查看里程碑进度，设定小目标',
                  '💬 多与智能体对话，了解更多生态价值',
                  '🤝 邀请好友加入，获得邀请奖励',
                  '🏆 努力达到 10,000 灵值，成为合伙人',
                  '⏰ 建立每日签到习惯，形成条件反射',
                  '📖 阅读用户指南，了解系统规则',
                ].map((tip, index) => (
                  <div key={index} className="flex items-center space-x-3 bg-blue-50 rounded-lg p-3">
                    <span className="text-lg">{tip.split(' ')[0]}</span>
                    <span className="text-gray-700">{tip.split(' ').slice(1).join(' ')}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>

      {/* 常见问题 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <Lightbulb className="w-6 h-6 mr-2 text-yellow-500" />
          常见问题
        </h2>
        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div key={index} className="border rounded-lg">
              <button
                onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <span className="font-semibold text-gray-900">{faq.question}</span>
                {expandedFaq === index ? (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                )}
              </button>
              {expandedFaq === index && (
                <div className="px-4 pb-4 text-gray-700">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-8 text-white text-center shadow-xl">
        <h2 className="text-2xl font-bold mb-4">🎉 立即开始您的财富之旅</h2>
        <p className="opacity-90 mb-6">今天开始，每天签到，一年后就是一笔不小的收入！</p>
        <button
          onClick={() => window.location.href = '/'}
          className="inline-flex items-center space-x-2 bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
        >
          <Zap className="w-5 h-5" />
          <span>立即开始</span>
        </button>
      </div>
    </div>
  )
}

export default UserGuide
