import React, { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Trophy, Target, Gift, TrendingUp, Lock, CheckCircle, ArrowRight } from 'lucide-react'

interface JourneyStage {
  id: string
  name: string
  minLingzhi: number
  maxLingzhi: number
  unlocks: string[]
  tasks: Array<{
    id: string
    name: string
    reward: number
  }>
}

interface JourneyData {
  user_id: number
  username: string
  current_stage: string
  total_lingzhi: number
  journey_progress: number
  stage_info: JourneyStage
  completed_stages: Record<string, any>
  next_stage: {
    stage: string
    name: string
    minLingzhi: number
    progress: number
  } | null
  upgrade_ready: boolean
}

const JourneyPage: React.FC = () => {
  const [journeyData, setJourneyData] = useState<JourneyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState(false)

  // 旅程阶段配置
  const stages: Record<string, JourneyStage> = {
    newcomer: {
      id: 'newcomer',
      name: '新手入门',
      minLingzhi: 0,
      maxLingzhi: 100,
      tasks: [
        { id: 'register', name: '完成注册', reward: 10 },
        { id: 'profile', name: '完善基础信息', reward: 20 },
        { id: 'first_checkin', name: '首次签到', reward: 10 },
        { id: 'first_chat', name: '体验智能对话', reward: 10 },
      ],
      unlocks: ['基础用户信息', '每日签到', '智能对话(基础版)', '推荐系统(基础)']
    },
    explorer: {
      id: 'explorer',
      name: '探索者',
      minLingzhi: 100,
      maxLingzhi: 1000,
      tasks: [
        { id: 'checkin_7days', name: '连续签到7天', reward: 50 },
        { id: 'first_resource', name: '发布首个资源', reward: 30 },
        { id: 'browse_5_projects', name: '浏览5个项目', reward: 20 },
      ],
      unlocks: ['知识库管理', '项目浏览', '资源发布(3个/周)', '推荐奖励查看']
    },
    participant: {
      id: 'participant',
      name: '参与者',
      minLingzhi: 1000,
      maxLingzhi: 5000,
      tasks: [
        { id: 'join_project', name: '成功加入1个项目', reward: 100 },
        { id: 'resource_matched', name: '资源被匹配3次', reward: 50 },
        { id: '实名认证', name: '通过实名认证', reward: 50 },
      ],
      unlocks: ['项目参与', '资源匹配系统', '推荐系统(高级)', '分红池参与', '合伙人申请']
    },
    contributor: {
      id: 'contributor',
      name: '贡献者',
      minLingzhi: 5000,
      maxLingzhi: 10000,
      tasks: [
        { id: 'create_project', name: '创建1个项目', reward: 200 },
        { id: 'resource_realized', name: '资源变现累计2000灵值', reward: 300 },
      ],
      unlocks: ['项目创建', '资源发布(不限数量)', '资源变现', '赏金猎人系统', '投资人申请']
    },
    ecosystem_holder: {
      id: 'ecosystem_holder',
      name: '生态持有者',
      minLingzhi: 10000,
      maxLingzhi: Infinity,
      tasks: [
        { id: 'mint_first_asset', name: '铸造首个数字资产', reward: 500 },
        { id: 'asset_trades', name: '参与至少10次资产交易', reward: 500 },
      ],
      unlocks: ['数字资产铸造', '资产交易', '资产收益(自动分配)', '生态治理投票', '专属数字资产']
    }
  }

  useEffect(() => {
    fetchJourneyData()
  }, [])

  const fetchJourneyData = async () => {
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/user/journey`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const result = await response.json()
      if (result.success) {
        setJourneyData(result.data)
      }
    } catch (error) {
      console.error('获取旅程数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpgrade = async () => {
    if (!journeyData?.upgrade_ready) return
    
    setUpgrading(true)
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const token = localStorage.getItem('token')
      const response = await fetch(`${apiBase}/user/journey/upgrade`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      if (result.success) {
        alert(result.message)
        fetchJourneyData()
      } else {
        alert(result.message)
      }
    } catch (error) {
      console.error('升级失败:', error)
      alert('升级失败，请重试')
    } finally {
      setUpgrading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
      </div>
    )
  }

  const stageOrder = ['newcomer', 'explorer', 'participant', 'contributor', 'ecosystem_holder']
  const currentStageIndex = stageOrder.indexOf(journeyData?.current_stage || 'newcomer')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            用户旅程
          </h1>
          <p className="text-gray-300">从新手到生态持有者的成长之路</p>
        </div>

        {/* 当前阶段卡片 */}
        {journeyData && (
          <Card className="mb-8 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500/50">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Trophy className="w-8 h-8 text-yellow-400" />
                  <h2 className="text-2xl font-bold">{journeyData.stage_info.name}</h2>
                </div>
                <p className="text-gray-300 mb-2">当前灵值: <span className="text-cyan-400 font-bold">{journeyData.total_lingzhi}</span></p>
                <div className="flex flex-wrap gap-2">
                  {journeyData.stage_info.unlocks.map((unlock, idx) => (
                    <span key={idx} className="px-3 py-1 bg-cyan-500/20 rounded-full text-sm">
                      {unlock}
                    </span>
                  ))}
                </div>
              </div>
              
              {journeyData.upgrade_ready && (
                <Button
                  onClick={handleUpgrade}
                  disabled={upgrading}
                  className="mt-4 md:mt-0 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                >
                  {upgrading ? '升级中...' : '升级到下一阶段'}
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              )}
            </div>
          </Card>
        )}

        {/* 阶段进度 */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {stageOrder.map((stageId, index) => {
            const stage = stages[stageId]
            const isCompleted = index < currentStageIndex
            const isCurrent = index === currentStageIndex
            const isLocked = index > currentStageIndex
            
            return (
              <div
                key={stageId}
                className={`
                  relative p-4 rounded-xl border-2 transition-all
                  ${isCompleted ? 'bg-green-500/20 border-green-500/50' : ''}
                  ${isCurrent ? 'bg-cyan-500/20 border-cyan-500/50 scale-105' : ''}
                  ${isLocked ? 'bg-gray-800/50 border-gray-700/50 opacity-50' : ''}
                `}
              >
                {isCompleted && (
                  <CheckCircle className="absolute top-2 right-2 w-5 h-5 text-green-400" />
                )}
                {isLocked && (
                  <Lock className="absolute top-2 right-2 w-5 h-5 text-gray-500" />
                )}
                
                <div className="text-center">
                  <div className="text-3xl mb-2">
                    {stageId === 'newcomer' && '🌱'}
                    {stageId === 'explorer' && '🔍'}
                    {stageId === 'participant' && '🤝'}
                    {stageId === 'contributor' && '💎'}
                    {stageId === 'ecosystem_holder' && '👑'}
                  </div>
                  <h3 className="font-bold text-sm mb-1">{stage.name}</h3>
                  <p className="text-xs text-gray-400">{stage.minLingzhi}-{stage.maxLingzhi === Infinity ? '∞' : stage.maxLingzhi} 灵值</p>
                </div>
              </div>
            )
          })}
        </div>

        {/* 下一阶段进度 */}
        {journeyData?.next_stage && (
          <Card className="mb-8">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-cyan-400" />
              下一阶段目标: {journeyData.next_stage.name}
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>当前: {journeyData.total_lingzhi} 灵值</span>
                <span>目标: {journeyData.next_stage.minLingzhi} 灵值</span>
              </div>
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all"
                  style={{ width: `${Math.min(journeyData.next_stage.progress, 100)}%` }}
                />
              </div>
              <p className="text-sm text-gray-400">{journeyData.next_stage.progress.toFixed(1)}% 完成</p>
            </div>
          </Card>
        )}

        {/* 当前阶段任务 */}
        {journeyData && journeyData.stage_info.tasks && (
          <Card className="mb-8">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              当前阶段任务
            </h3>
            <div className="space-y-3">
              {journeyData.stage_info.tasks.map((task, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-cyan-500/20 rounded-full flex items-center justify-center text-cyan-400 font-bold">
                      {index + 1}
                    </div>
                    <span className="text-gray-300">{task.name}</span>
                  </div>
                  <div className="flex items-center gap-2 text-yellow-400">
                    <Gift className="w-4 h-4" />
                    <span className="font-bold">+{task.reward}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* 已完成阶段 */}
        <Card>
          <h3 className="text-lg font-bold mb-4">已完成的阶段</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(journeyData?.completed_stages || {}).map(([stageId, completedInfo]: [string, any]) => {
              if (completedInfo?.completed) {
                const stage = stages[stageId]
                return (
                  <div
                    key={stageId}
                    className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg"
                  >
                    <div className="text-2xl mb-2">
                      {stageId === 'newcomer' && '🌱'}
                      {stageId === 'explorer' && '🔍'}
                      {stageId === 'participant' && '🤝'}
                      {stageId === 'contributor' && '💎'}
                      {stageId === 'ecosystem_holder' && '👑'}
                    </div>
                    <h4 className="font-bold text-green-400">{stage.name}</h4>
                    <p className="text-xs text-gray-400 mt-1">
                      完成于: {completedInfo.completed_at ? new Date(completedInfo.completed_at).toLocaleDateString('zh-CN') : '未知'}
                    </p>
                  </div>
                )
              }
              return null
            })}
          </div>
          {Object.values(journeyData?.completed_stages || {}).filter((info: any) => info?.completed).length === 0 && (
            <p className="text-center text-gray-400 py-4">还没有完成任何阶段</p>
          )}
        </Card>
      </div>
    </div>
  )
}

export default JourneyPage
