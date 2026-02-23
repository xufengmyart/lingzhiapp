import { useState, useEffect } from 'react'
import { Trophy, Medal, Award, Crown, Target, Flame, Star, Lock, Unlock } from 'lucide-react'

interface Achievement {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  requirement: string
  unlocked: boolean
  unlocked_at?: string
  progress: number
  max_progress: number
  reward: number
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

interface AchievementSystemProps {}

const AchievementSystem = ({}: AchievementSystemProps) => {
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null)
  const [filterRarity, setFilterRarity] = useState<'all' | 'unlocked' | 'locked'>('all')

  const rarityConfig = {
    common: {
      color: 'from-gray-400 to-gray-500',
      bgColor: 'bg-gray-500/20',
      borderColor: 'border-gray-500/30',
      text: '普通'
    },
    rare: {
      color: 'from-blue-400 to-blue-500',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30',
      text: '稀有'
    },
    epic: {
      color: 'from-purple-400 to-purple-500',
      bgColor: 'bg-purple-500/20',
      borderColor: 'border-purple-500/30',
      text: '史诗'
    },
    legendary: {
      color: 'from-yellow-400 to-orange-500',
      bgColor: 'bg-yellow-500/20',
      borderColor: 'border-yellow-500/30',
      text: '传说'
    }
  }

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    // 模拟数据，实际应从API获取
    const mockAchievements: Achievement[] = [
      {
        id: '1',
        title: '初次签到',
        description: '完成第一次签到',
        icon: <Star className="w-8 h-8" />,
        requirement: '累计签到1天',
        unlocked: true,
        unlocked_at: '2026-02-16',
        progress: 1,
        max_progress: 1,
        reward: 10,
        rarity: 'common'
      },
      {
        id: '2',
        title: '连续7天',
        description: '连续签到7天',
        icon: <Flame className="w-8 h-8" />,
        requirement: '连续签到7天',
        unlocked: true,
        unlocked_at: '2026-02-15',
        progress: 7,
        max_progress: 7,
        reward: 50,
        rarity: 'rare'
      },
      {
        id: '3',
        title: '月度达人',
        description: '连续签到30天',
        icon: <Trophy className="w-8 h-8" />,
        requirement: '连续签到30天',
        unlocked: false,
        progress: 7,
        max_progress: 30,
        reward: 200,
        rarity: 'epic'
      },
      {
        id: '4',
        title: '年度王者',
        description: '连续签到365天',
        icon: <Crown className="w-8 h-8" />,
        requirement: '连续签到365天',
        unlocked: false,
        progress: 7,
        max_progress: 365,
        reward: 1000,
        rarity: 'legendary'
      },
      {
        id: '5',
        title: '初次对话',
        description: '与智能体完成第一次对话',
        icon: <Award className="w-8 h-8" />,
        requirement: '累计对话1次',
        unlocked: true,
        progress: 1,
        max_progress: 1,
        reward: 10,
        rarity: 'common'
      },
      {
        id: '6',
        title: '对话达人',
        description: '累计对话100次',
        icon: <Medal className="w-8 h-8" />,
        requirement: '累计对话100次',
        unlocked: false,
        progress: 5,
        max_progress: 100,
        reward: 100,
        rarity: 'rare'
      },
      {
        id: '7',
        title: '推荐新手',
        description: '成功推荐1位用户',
        icon: <Target className="w-8 h-8" />,
        requirement: '累计推荐1人',
        unlocked: false,
        progress: 0,
        max_progress: 1,
        reward: 50,
        rarity: 'common'
      },
      {
        id: '8',
        title: '推荐专家',
        description: '成功推荐10位用户',
        icon: <Star className="w-8 h-8" />,
        requirement: '累计推荐10人',
        unlocked: false,
        progress: 0,
        max_progress: 10,
        reward: 200,
        rarity: 'epic'
      }
    ]
    setAchievements(mockAchievements)
  }

  const filteredAchievements = achievements.filter(achievement => {
    if (filterRarity === 'unlocked') return achievement.unlocked
    if (filterRarity === 'locked') return !achievement.unlocked
    return true
  })

  const unlockedCount = achievements.filter(a => a.unlocked).length
  const totalReward = achievements.filter(a => a.unlocked).reduce((sum, a) => sum + a.reward, 0)

  return (
    <div className="min-h-screen bg-[#091422] py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <Trophy className="w-12 h-12 text-[#FFD700]" />
            <h1 className="text-4xl font-bold text-white">成就系统</h1>
          </div>
          <p className="text-[#B4C7E7] text-lg">完成成就，解锁奖励，展示你的荣耀</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <div className="flex items-center justify-center gap-3 mb-3">
              <Trophy className="w-8 h-8 text-[#FFD700]" />
              <div className="text-3xl font-bold text-white">{unlockedCount}</div>
            </div>
            <div className="text-[#B4C7E7]">已解锁成就</div>
            <div className="text-sm text-[#B4C7E7]">/{achievements.length} 总计</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <div className="flex items-center justify-center gap-3 mb-3">
              <Star className="w-8 h-8 text-[#00C3FF]" />
              <div className="text-3xl font-bold text-white">{totalReward}</div>
            </div>
            <div className="text-[#B4C7E7]">累计奖励灵值</div>
            <div className="text-sm text-[#B4C7E7]">已完成成就</div>
          </div>
          <div className="bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl p-6 text-center">
            <div className="flex items-center justify-center gap-3 mb-3">
              <Target className="w-8 h-8 text-[#FF6B6B]" />
              <div className="text-3xl font-bold text-white">
                {Math.round((unlockedCount / achievements.length) * 100)}%
              </div>
            </div>
            <div className="text-[#B4C7E7]">完成进度</div>
            <div className="text-sm text-[#B4C7E7]">继续努力</div>
          </div>
        </div>

        {/* 筛选器 */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setFilterRarity('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterRarity === 'all'
                ? 'bg-[#00C3FF] text-white'
                : 'bg-[#121A2F] text-[#B4C7E7] hover:text-white'
            }`}
          >
            全部
          </button>
          <button
            onClick={() => setFilterRarity('unlocked')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              filterRarity === 'unlocked'
                ? 'bg-[#00C3FF] text-white'
                : 'bg-[#121A2F] text-[#B4C7E7] hover:text-white'
            }`}
          >
            <Unlock className="w-4 h-4" />
            已解锁
          </button>
          <button
            onClick={() => setFilterRarity('locked')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              filterRarity === 'locked'
                ? 'bg-[#00C3FF] text-white'
                : 'bg-[#121A2F] text-[#B4C7E7] hover:text-white'
            }`}
          >
            <Lock className="w-4 h-4" />
            未解锁
          </button>
        </div>

        {/* 成就列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAchievements.map(achievement => {
            const config = rarityConfig[achievement.rarity]
            const progress = Math.min(100, (achievement.progress / achievement.max_progress) * 100)

            return (
              <div
                key={achievement.id}
                onClick={() => setSelectedAchievement(achievement)}
                className={`bg-[#121A2F] border ${config.borderColor} rounded-2xl p-6 cursor-pointer hover:border-[#00C3FF]/50 transition-all ${
                  !achievement.unlocked ? 'opacity-70' : ''
                }`}
              >
                {/* 图标 */}
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${config.color} flex items-center justify-center text-white mb-4 ${
                  achievement.unlocked ? '' : 'grayscale'
                }`}>
                  {achievement.icon}
                </div>

                {/* 标题和稀有度 */}
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">{achievement.title}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${config.bgColor} text-[#B4C7E7]`}>
                    {config.text}
                  </span>
                </div>

                {/* 描述 */}
                <p className="text-[#B4C7E7] text-sm mb-3">{achievement.description}</p>

                {/* 进度条 */}
                {achievement.progress < achievement.max_progress && (
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-[#B4C7E7] mb-1">
                      <span>{achievement.progress}/{achievement.max_progress}</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <div className="h-2 bg-[#091422] rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${config.color} transition-all duration-300`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* 奖励 */}
                <div className="flex items-center gap-2 text-sm">
                  <Star className="w-4 h-4 text-[#FFD700]" />
                  <span className="text-[#B4C7E7]">奖励: </span>
                  <span className="text-[#00C3FF] font-bold">+{achievement.reward} 灵值</span>
                </div>

                {/* 状态标记 */}
                {achievement.unlocked ? (
                  <div className="absolute top-4 right-4">
                    <Unlock className="w-5 h-5 text-green-400" />
                  </div>
                ) : (
                  <div className="absolute top-4 right-4">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* 成就详情弹窗 */}
        {selectedAchievement && (
          <div
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-[999999] p-4"
            onClick={() => setSelectedAchievement(null)}
          >
            <div
              className="bg-gradient-to-br from-[#091422] to-[#0A1628] border border-[#00C3FF]/30 rounded-3xl w-full max-w-md p-8"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                {/* 图标 */}
                <div className={`w-24 h-24 rounded-3xl bg-gradient-to-r ${rarityConfig[selectedAchievement.rarity].color} flex items-center justify-center text-white mx-auto mb-6 ${
                  selectedAchievement.unlocked ? '' : 'grayscale'
                }`}>
                  {selectedAchievement.icon}
                </div>

                {/* 标题 */}
                <h2 className="text-2xl font-bold text-white mb-2">{selectedAchievement.title}</h2>
                <span className={`inline-block px-3 py-1 text-sm rounded-full ${rarityConfig[selectedAchievement.rarity].bgColor} text-[#B4C7E7] mb-4`}>
                  {rarityConfig[selectedAchievement.rarity].text}
                </span>

                {/* 描述 */}
                <p className="text-[#B4C7E7] mb-6">{selectedAchievement.description}</p>

                {/* 进度 */}
                {selectedAchievement.progress < selectedAchievement.max_progress ? (
                  <div className="mb-6">
                    <div className="flex justify-between text-sm text-[#B4C7E7] mb-2">
                      <span>{selectedAchievement.requirement}</span>
                      <span className="text-[#00C3FF]">
                        {selectedAchievement.progress}/{selectedAchievement.max_progress}
                      </span>
                    </div>
                    <div className="h-3 bg-[#121A2F] rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${rarityConfig[selectedAchievement.rarity].color}`}
                        style={{
                          width: `${Math.min(100, (selectedAchievement.progress / selectedAchievement.max_progress) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="mb-6 p-4 bg-green-500/20 border border-green-500/30 rounded-xl">
                    <div className="text-green-400 font-bold">已达成！</div>
                    {selectedAchievement.unlocked_at && (
                      <div className="text-[#B4C7E7] text-sm mt-1">
                        {selectedAchievement.unlocked_at} 解锁
                      </div>
                    )}
                  </div>
                )}

                {/* 奖励 */}
                <div className="flex items-center justify-center gap-2 mb-6">
                  <Star className="w-5 h-5 text-[#FFD700]" />
                  <span className="text-[#B4C7E7]">奖励: </span>
                  <span className="text-[#00C3FF] text-xl font-bold">+{selectedAchievement.reward} 灵值</span>
                </div>

                {/* 关闭按钮 */}
                <button
                  onClick={() => setSelectedAchievement(null)}
                  className="w-full py-3 bg-[#00C3FF] text-white font-bold rounded-xl hover:bg-[#0080FF] transition-colors"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AchievementSystem
