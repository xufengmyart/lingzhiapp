import { useState } from 'react'
import {
  Video,
  Play,
  TrendingUp,
  Users,
  Clock,
  DollarSign,
  Award,
  CheckCircle2,
  Sparkles,
  Upload,
  BarChart3,
  Target
} from 'lucide-react'

const MediumVideoProject = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'howto' | 'earnings' | 'faq'>('overview')

  const steps = [
    {
      step: '1',
      title: '注册账号',
      desc: '在中视频平台注册创作者账号',
      icon: Users
    },
    {
      step: '2',
      title: '内容创作',
      desc: '制作 1-30 分钟的中视频内容',
      icon: Video
    },
    {
      step: '3',
      title: '发布作品',
      desc: '上传视频并积累播放量',
      icon: Upload
    },
    {
      step: '4',
      title: '获取收益',
      desc: '达到门槛后获得创作收益',
      icon: DollarSign
    }
  ]

  const earnings = [
    { level: '新手创作者', views: '0-10万', earnings: '0-500元/月' },
    { level: '成长创作者', views: '10-50万', earnings: '500-2000元/月' },
    { level: '优质创作者', views: '50-100万', earnings: '2000-5000元/月' },
    { level: '头部创作者', views: '100万+', earnings: '5000元+/月' }
  ]

  const faqs = [
    {
      question: '什么是中视频项目？',
      answer: '中视频项目是指创作时长在 1-30 分钟之间的视频内容，通过在中视频平台发布并获得播放量来获取收益的项目。'
    },
    {
      question: '如何加入中视频项目？',
      answer: '在中视频平台注册创作者账号，发布符合要求的视频内容，累计播放量达到门槛后即可获得收益资格。'
    },
    {
      question: '中视频的收益门槛是什么？',
      answer: '通常需要累计播放量达到一定数量（如 1.7 万次播放）并通过原创性审核，即可获得创作收益资格。'
    },
    {
      question: '什么样的内容适合中视频？',
      answer: '深度知识分享、教程类内容、故事叙述、纪录片风格、访谈类节目等都适合中视频形式。'
    }
  ]

  return (
    <div className="space-y-6 animate-fade-in pb-20">
      {/* 顶部横幅 */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <Video className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-bold">中视频项目</h1>
        </div>
        <p className="opacity-90 text-lg">
          创作 1-30 分钟中视频，通过播放量获得收益
        </p>
      </div>

      {/* 标签页导航 */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex">
          {[
            { id: 'overview', icon: Target, label: '项目概述' },
            { id: 'howto', icon: Play, label: '参与指南' },
            { id: 'earnings', icon: DollarSign, label: '收益说明' },
            { id: 'faq', icon: Sparkles, label: '常见问题' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'text-orange-600 bg-orange-50 border-b-2 border-orange-500'
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
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Target className="w-6 h-6 mr-2 text-orange-500" />
                什么是中视频项目？
              </h2>
              <p className="text-gray-700 leading-relaxed">
                <strong className="text-orange-600">中视频项目</strong>是介于短视频（15秒-1分钟）和长视频（30分钟以上）之间的视频内容形式，时长通常为 <strong>1-30 分钟</strong>。
              </p>
              <p className="text-gray-700 mt-3 leading-relaxed">
                通过在中视频平台创作并发布高质量内容，积累播放量后可以获得创作收益。中视频更适合深度内容、知识分享、故事叙述等形式，能够提供更丰富的信息量和更好的观看体验。
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Award className="w-6 h-6 mr-2 text-orange-500" />
                项目优势
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { icon: Clock, title: '创作灵活', desc: '1-30 分钟时长，内容形式多样' },
                  { icon: Users, title: '用户黏性高', desc: '深度内容，观众停留时间长' },
                  { icon: DollarSign, title: '收益稳定', desc: '播放量收益，持续获得回报' },
                  { icon: TrendingUp, title: '成长空间大', desc: '中视频领域竞争相对较小' },
                ].map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                      <item.icon className="w-6 h-6 text-orange-600" />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600">{item.desc}</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="w-6 h-6 mr-2 text-orange-500" />
                适合的内容类型
              </h2>
              <div className="space-y-3">
                {[
                  '📚 深度知识分享和教程',
                  '🎬 故事叙述和纪录片风格',
                  '💼 行业分析和专业见解',
                  '🎭 访谈类节目和对话',
                  '🍽️ 美食制作和生活方式',
                  '🎮 游戏攻略和评测',
                  '✈️ 旅游攻略和体验分享',
                ].map((item, index) => (
                  <div key={index} className="flex items-center space-x-3 bg-orange-50 rounded-lg p-4">
                    <CheckCircle2 className="w-5 h-5 text-orange-600 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'howto' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Play className="w-6 h-6 mr-2 text-orange-500" />
                参与步骤
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {steps.map((item, index) => (
                  <div key={index} className="relative">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">
                        {item.step}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                        <p className="text-gray-600">{item.desc}</p>
                      </div>
                    </div>
                    {index < steps.length - 1 && (
                      <div className="hidden md:block absolute left-6 top-12 w-px h-12 bg-orange-300"></div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-6 border border-orange-200">
              <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-orange-500" />
                创作小贴士
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>• 确保视频内容原创且高质量</li>
                <li>• 封面和标题要吸引人</li>
                <li>• 视频时长控制在 5-15 分钟效果最佳</li>
                <li>• 定期更新，保持活跃度</li>
                <li>• 与观众互动，建立粉丝群体</li>
              </ul>
            </section>
          </div>
        )}

        {activeTab === 'earnings' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <DollarSign className="w-6 h-6 mr-2 text-orange-500" />
                收益等级
              </h2>
              <div className="space-y-4">
                {earnings.map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{item.level}</h3>
                        <p className="text-gray-600">累计播放量：{item.views}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-orange-600">{item.earnings}</div>
                        <div className="text-sm text-gray-500">预估月收入</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-orange-500" />
                收益来源
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { icon: Play, title: '播放收益', desc: '根据播放量计算' },
                  { icon: Users, title: '粉丝打赏', desc: '观众自愿打赏' },
                  { icon: Award, title: '平台激励', desc: '优质内容奖励' },
                ].map((item, index) => (
                  <div key={index} className="bg-orange-50 rounded-lg p-6 text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <item.icon className="w-6 h-6 text-orange-600" />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600 text-sm">{item.desc}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'faq' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Sparkles className="w-6 h-6 mr-2 text-orange-500" />
              常见问题
            </h2>
            <div className="space-y-3">
              {faqs.map((faq, index) => (
                <div key={index} className="border rounded-lg">
                  <details className="group">
                    <summary className="w-full flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 list-none">
                      <span className="font-semibold text-gray-900">{faq.question}</span>
                      <span className="text-orange-500 group-open:rotate-180 transition-transform">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </span>
                    </summary>
                    <div className="px-4 pb-4 text-gray-700">
                      {faq.answer}
                    </div>
                  </details>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-8 text-white text-center shadow-xl">
        <h2 className="text-2xl font-bold mb-4">🎬 立即开始创作</h2>
        <p className="opacity-90 mb-6">加入中视频项目，用内容创造价值</p>
        <button
          onClick={() => window.location.href = '/chat'}
          className="inline-flex items-center space-x-2 bg-white text-orange-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
        >
          <Play className="w-5 h-5" />
          <span>开始创作</span>
        </button>
      </div>
    </div>
  )
}

export default MediumVideoProject
