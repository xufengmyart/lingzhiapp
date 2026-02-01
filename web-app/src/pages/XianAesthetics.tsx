import { useState } from 'react'
import {
  MapPin,
  Camera,
  Search,
  Star,
  Award,
  Users,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  Sparkles,
  Heart,
  Target
} from 'lucide-react'

const XianAesthetics = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'missions' | 'rewards' | 'faq'>('overview')

  const missions = [
    {
      id: 1,
      title: '古城墙晨光',
      location: '西安城墙',
      difficulty: '⭐⭐',
      reward: '50 灵值',
      desc: '在日出时分拍摄古城墙的光影之美'
    },
    {
      id: 2,
      title: '钟楼夜色',
      location: '钟楼',
      difficulty: '⭐⭐⭐',
      reward: '80 灵值',
      desc: '记录钟楼在夜色中的璀璨灯火'
    },
    {
      id: 3,
      title: '大雁塔倒影',
      location: '大雁塔',
      difficulty: '⭐⭐',
      reward: '60 灵值',
      desc: '寻找大雁塔在水面或镜子中的倒影'
    },
    {
      id: 4,
      title: '回民街美食',
      location: '回民街',
      difficulty: '⭐',
      reward: '40 灵值',
      desc: '拍摄回民街的美食文化'
    },
    {
      id: 5,
      title: '兵马俑凝视',
      location: '兵马俑',
      difficulty: '⭐⭐⭐⭐',
      reward: '100 灵值',
      desc: '捕捉兵马俑的历史韵味'
    },
    {
      id: 6,
      title: '大唐不夜城',
      location: '大唐不夜城',
      difficulty: '⭐⭐⭐',
      reward: '90 灵值',
      desc: '记录大唐不夜城的繁华夜景'
    }
  ]

  const rewards = [
    { level: '初级侦探', points: '0-200', badge: '🔍 见习徽章' },
    { level: '中级侦探', points: '200-500', badge: '🎯 资深徽章' },
    { level: '高级侦探', points: '500-1000', badge: '🌟 专家徽章' },
    { level: '金牌侦探', points: '1000+', badge: '🏆 荣誉徽章' }
  ]

  const faqs = [
    {
      question: '什么是西安美学侦探？',
      answer: '西安美学侦探是一个探索和发现西安城市美学的项目，通过完成摄影任务、发现城市美学来获得灵值奖励。'
    },
    {
      question: '如何参与美学侦探任务？',
      answer: '在美学侦探页面查看当前任务，前往指定地点拍摄照片，上传完成并等待审核，通过后获得灵值奖励。'
    },
    {
      question: '任务难度如何选择？',
      answer: '任务难度分为 1-4 星，难度越高，奖励越多。新手建议从 1 星任务开始，逐步提升。'
    },
    {
      question: '照片有什么要求？',
      answer: '照片需要原创、清晰，能够体现任务地点的美学特色。建议使用专业设备或高质量手机拍摄。'
    }
  ]

  return (
    <div className="space-y-6 animate-fade-in pb-20">
      {/* 顶部横幅 */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <MapPin className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-bold">西安美学侦探</h1>
        </div>
        <p className="opacity-90 text-lg">
          探索城市美学，发现西安之美
        </p>
      </div>

      {/* 标签页导航 */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex">
          {[
            { id: 'overview', icon: Target, label: '项目概述' },
            { id: 'missions', icon: Search, label: '侦探任务' },
            { id: 'rewards', icon: Award, label: '奖励体系' },
            { id: 'faq', icon: Sparkles, label: '常见问题' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'text-purple-600 bg-purple-50 border-b-2 border-purple-500'
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
                <Target className="w-6 h-6 mr-2 text-purple-500" />
                什么是西安美学侦探？
              </h2>
              <p className="text-gray-700 leading-relaxed">
                <strong className="text-purple-600">西安美学侦探</strong>是一个探索和发现西安城市美学的互动项目。通过完成各种摄影和探索任务，您将深入西安的历史文化街区，发现这座城市独特的美学魅力。
              </p>
              <p className="text-gray-700 mt-3 leading-relaxed">
                每完成一个任务，您都将获得 <strong className="text-purple-600">灵值奖励</strong>，同时也能积累美学侦探等级，解锁更多专属徽章和特权。这不仅是一场探索之旅，更是一次文化与美学的深度体验。
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Heart className="w-6 h-6 mr-2 text-purple-500" />
                项目特色
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { icon: MapPin, title: '实地探索', desc: '亲身体验西安历史古迹' },
                  { icon: Camera, title: '美学创作', desc: '用镜头记录城市之美' },
                  { icon: Users, title: '社交互动', desc: '与其他侦探分享发现' },
                  { icon: Award, title: '等级系统', desc: '积累经验，提升等级' },
                ].map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                      <item.icon className="w-6 h-6 text-purple-600" />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600">{item.desc}</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Star className="w-6 h-6 mr-2 text-purple-500" />
                探索地点
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {['古城墙', '钟楼', '大雁塔', '回民街', '兵马俑', '大唐不夜城', '华清池', '小雁塔', '西安博物院'].map((place, index) => (
                  <div key={index} className="bg-purple-50 rounded-lg p-4 text-center">
                    <MapPin className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                    <span className="text-sm font-semibold text-gray-900">{place}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'missions' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Search className="w-6 h-6 mr-2 text-purple-500" />
                当前任务
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {missions.map((mission) => (
                  <div key={mission.id} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{mission.title}</h3>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MapPin className="w-4 h-4" />
                          <span>{mission.location}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-purple-600 font-bold">{mission.reward}</div>
                        <div className="text-xs text-gray-500">难度 {mission.difficulty}</div>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4">{mission.desc}</p>
                    <button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 rounded-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all">
                      接受任务
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
              <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
                <Camera className="w-5 h-5 mr-2 text-purple-500" />
                拍摄建议
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>• 选择合适的时间段（黄金时段效果最佳）</li>
                <li>• 注意构图和光影运用</li>
                <li>• 尝试不同角度和视角</li>
                <li>• 突出地点的特色元素</li>
                <li>• 保持照片清晰度和原创性</li>
              </ul>
            </section>
          </div>
        )}

        {activeTab === 'rewards' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Award className="w-6 h-6 mr-2 text-purple-500" />
                侦探等级
              </h2>
              <div className="space-y-4">
                {rewards.map((item, index) => (
                  <div key={index} className="border-2 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-3xl">{item.badge}</div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">{item.level}</h3>
                          <p className="text-gray-600">积分范围：{item.points}</p>
                        </div>
                      </div>
                      <CheckCircle2 className="w-8 h-8 text-purple-600" />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-purple-500" />
                奖励说明
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { icon: DollarSign, title: '灵值奖励', desc: '完成任务获得灵值' },
                  { icon: Star, title: '等级徽章', desc: '解锁专属徽章' },
                  { icon: Users, title: '特权权益', desc: '高级侦探享受特权' },
                ].map((item, index) => (
                  <div key={index} className="bg-purple-50 rounded-lg p-6 text-center">
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <item.icon className="w-6 h-6 text-purple-600" />
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
              <Sparkles className="w-6 h-6 mr-2 text-purple-500" />
              常见问题
            </h2>
            <div className="space-y-3">
              {faqs.map((faq, index) => (
                <div key={index} className="border rounded-lg">
                  <details className="group">
                    <summary className="w-full flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 list-none">
                      <span className="font-semibold text-gray-900">{faq.question}</span>
                      <span className="text-purple-500 group-open:rotate-180 transition-transform">
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
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-8 text-white text-center shadow-xl">
        <h2 className="text-2xl font-bold mb-4">🔍 成为美学侦探</h2>
        <p className="opacity-90 mb-6">探索西安之美，收集美学灵值</p>
        <button
          onClick={() => window.location.href = '/xian-aesthetics?tab=missions'}
          className="inline-flex items-center space-x-2 bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
        >
          <Search className="w-5 h-5" />
          <span>开始探索</span>
        </button>
      </div>
    </div>
  )
}

export default XianAesthetics
