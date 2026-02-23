import { useState, useEffect } from 'react'
import { Package, Gift, Video, Smartphone, Coins, Users, Tag, Ticket, CheckCircle, ArrowRight, Clock, UserPlus } from 'lucide-react'
import api from '../services/api'

interface MediumVideoProjectProps {}

const MediumVideoProject = () => {
  const [hasPurchased, setHasPurchased] = useState(false)
  const [userInfo, setUserInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUserInfo()
  }, [])

  const loadUserInfo = async () => {
    try {
      const response = await api.get('/user/info')
      setUserInfo(response.data.data)
      // 检查是否已购买中视频项目（可以通过特定字段判断）
      // 这里假设用户有 video_project_participation 字段
      setHasPurchased(response.data.data?.video_project_participation || false)
    } catch (error) {
      console.error('加载用户信息失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async () => {
    try {
      // 调用购买API（这里需要后端实现）
      const response = await api.post('/medium-video/purchase', {
        amount: 398
      })
      if (response.data.success) {
        setHasPurchased(true)
        alert('购买成功！感谢您参与中视频项目')
      } else {
        alert(response.data.message || '购买失败')
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '购买失败，请稍后重试')
    }
  }

  const benefits = [
    {
      id: 1,
      icon: <Gift className="w-8 h-8" />,
      title: '奶粉奖励',
      description: '获得奶粉（360克）一大桶',
      value: '实体店售价398元，线上售价698元',
      category: '实物奖励',
      color: 'from-pink-500 to-rose-500'
    },
    {
      id: 2,
      icon: <Video className="w-8 h-8" />,
      title: '视频号运营',
      description: '免费运营视频号一个',
      value: '养号成功后，创作者中心收益分成（平台60%，参与者40%）',
      category: '创作服务',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 3,
      icon: <Smartphone className="w-8 h-8" />,
      title: '设备支持',
      description: '获得手机一部',
      value: '支持视频创作',
      category: '实物奖励',
      color: 'from-purple-500 to-violet-500'
    },
    {
      id: 4,
      icon: <Coins className="w-8 h-8" />,
      title: '元宝值',
      description: '获得注册平台的元宝值（等同积分）为1',
      value: '可兑换各种权益',
      category: '数字资产',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      id: 5,
      icon: <UserPlus className="w-8 h-8" />,
      title: '资源变现',
      description: '获得登记自己拥有的有价值的资源的机会（1次）',
      value: '该机会可以变现',
      category: '资源权益',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 6,
      icon: <Tag className="w-8 h-8" />,
      title: '平台身份',
      description: '获得平台的身份一个',
      value: '享有平台专属权益',
      category: '身份权益',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      id: 7,
      icon: <Ticket className="w-8 h-8" />,
      title: '优惠券权益',
      description: '获得免费领取平台内所有商家的优惠券三次',
      value: '享受商家优惠',
      category: '消费权益',
      color: 'from-teal-500 to-cyan-500'
    }
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-[#091422] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00C3FF]"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#091422] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className={`w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center`}>
              <Video className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">中视频项目</h1>
          </div>
          <p className="text-[#B4C7E7] text-lg">参与视频创作，共享创作者经济红利</p>
        </div>

        {/* 参与条件卡片 */}
        <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-[#00C3FF]/30 rounded-2xl p-8 mb-12">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <Package className="w-12 h-12 text-[#00C3FF]" />
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">参与条件</h2>
                <p className="text-[#B4C7E7]">一次性支付 <span className="text-[#00C3FF] font-bold text-xl">398元</span> 获得参与权</p>
              </div>
            </div>
            {!hasPurchased ? (
              <button
                onClick={handlePurchase}
                className="px-8 py-4 bg-gradient-to-r from-[#00C3FF] to-[#0080FF] text-white font-bold rounded-xl hover:shadow-lg hover:shadow-[#00C3FF]/30 transition-all flex items-center gap-2"
              >
                <ArrowRight className="w-5 h-5" />
                立即参与
              </button>
            ) : (
              <div className="flex items-center gap-3 px-8 py-4 bg-green-500/20 border border-green-500/30 rounded-xl">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <span className="text-green-400 font-bold">已参与项目</span>
              </div>
            )}
          </div>
        </div>

        {/* 七大权益 */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
            <Gift className="w-8 h-8 text-[#00C3FF]" />
            七大权益
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit) => (
              <div
                key={benefit.id}
                className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-2xl p-6 hover:border-[#00C3FF]/50 transition-all group"
              >
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${benefit.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <div className="text-white">
                    {benefit.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{benefit.title}</h3>
                <p className="text-[#B4C7E7] mb-3">{benefit.description}</p>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-[#00C3FF]/20 text-[#00C3FF] text-xs rounded-full font-medium">
                    {benefit.category}
                  </span>
                </div>
                <p className="text-[#00C3FF] text-sm mt-3 font-medium">{benefit.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 项目统计 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <Users className="w-10 h-10 text-[#00C3FF] mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">1,234</div>
            <div className="text-[#B4C7E7] text-sm">已参与用户</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <Video className="w-10 h-10 text-[#00C3FF] mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">5,678</div>
            <div className="text-[#B4C7E7] text-sm">运营视频号</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <Coins className="w-10 h-10 text-[#00C3FF] mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">¥89,012</div>
            <div className="text-[#B4C7E7] text-sm">累计分成收益</div>
          </div>
        </div>

        {/* 参与流程 */}
        <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
            <Clock className="w-8 h-8 text-[#00C3FF]" />
            参与流程
          </h2>
          <div className="space-y-6">
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-[#00C3FF] text-white flex items-center justify-center font-bold flex-shrink-0">1</div>
              <div>
                <h3 className="text-lg font-bold text-white mb-1">支付参与费</h3>
                <p className="text-[#B4C7E7]">支付398元购买中视频项目参与权</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-[#00C3FF] text-white flex items-center justify-center font-bold flex-shrink-0">2</div>
              <div>
                <h3 className="text-lg font-bold text-white mb-1">登记信息</h3>
                <p className="text-[#B4C7E7]">填写微信号、姓名、电话、推荐人、收货地址等信息</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-[#00C3FF] text-white flex items-center justify-center font-bold flex-shrink-0">3</div>
              <div>
                <h3 className="text-lg font-bold text-white mb-1">领取权益</h3>
                <p className="text-[#B4C7E7]">领取奶粉、手机等实物奖励，享受视频号运营服务</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-[#00C3FF] text-white flex items-center justify-center font-bold flex-shrink-0">4</div>
              <div>
                <h3 className="text-lg font-bold text-white mb-1">获得收益</h3>
                <p className="text-[#B4C7E7]">视频号养号成功后，享受创作者收益分成（40%）</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MediumVideoProject
