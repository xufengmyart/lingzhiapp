import { Clock, Coins, Sparkles, X, CheckCircle } from 'lucide-react'

interface ChatEndDialogProps {
  open: boolean
  onClose: () => void
  duration: number // 秒
  consumedLingzhi: number
  earnedLingzhi: number
  hasSubmittedFeedback: boolean
}

export default function ChatEndDialog({
  open,
  onClose,
  duration,
  consumedLingzhi,
  earnedLingzhi,
  hasSubmittedFeedback
}: ChatEndDialogProps) {
  if (!open) return null

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    if (minutes > 0) {
      return `${minutes}分${remainingSeconds}秒`
    }
    return `${remainingSeconds}秒`
  }

  const netLingzhi = earnedLingzhi - consumedLingzhi
  const isPositive = netLingzhi >= 0

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-cyan-500/30 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* 顶部装饰 */}
        <div className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 p-6 border-b border-cyan-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">本次对话结束</h2>
                <p className="text-sm text-cyan-400">灵值统计已更新</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-full transition-all"
            >
              <X className="w-5 h-5 text-gray-400 hover:text-white" />
            </button>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="p-6 space-y-4">
          {/* 对话时长 */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-blue-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-400">对话时长</p>
                <p className="text-lg font-semibold text-white">{formatDuration(duration)}</p>
              </div>
            </div>
          </div>

          {/* 消耗灵值 */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                <Coins className="w-5 h-5 text-red-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-400">消耗灵值</p>
                <p className="text-lg font-semibold text-red-400">
                  -{consumedLingzhi} <span className="text-sm">灵值</span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">计费规则</p>
                <p className="text-xs text-gray-400">5分钟/灵值</p>
              </div>
            </div>
          </div>

          {/* 获得灵值 */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Coins className="w-5 h-5 text-green-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-400">获得灵值</p>
                <p className="text-lg font-semibold text-green-400">
                  +{earnedLingzhi} <span className="text-sm">灵值</span>
                </p>
              </div>
              {hasSubmittedFeedback && (
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <CheckCircle className="w-3 h-3" />
                  <span>已反馈</span>
                </div>
              )}
            </div>
          </div>

          {/* 净灵值 */}
          <div className={`bg-gradient-to-r ${isPositive ? 'from-green-500/20 to-emerald-500/20 border-green-500/30' : 'from-red-500/20 to-orange-500/20 border-red-500/30'} border rounded-xl p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 ${isPositive ? 'bg-green-500/30' : 'bg-red-500/30'} rounded-lg flex items-center justify-center`}>
                  <Coins className={`w-5 h-5 ${isPositive ? 'text-green-400' : 'text-red-400'}`} />
                </div>
                <div>
                  <p className="text-sm text-gray-400">净变化</p>
                  <p className={`text-xl font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}{netLingzhi} <span className="text-sm">灵值</span>
                  </p>
                </div>
              </div>
              {isPositive && (
                <div className="text-right">
                  <p className="text-xs text-green-400">🎉 获得奖励</p>
                </div>
              )}
            </div>
          </div>

          {/* 提示信息 */}
          {!hasSubmittedFeedback && (
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-4">
              <p className="text-sm text-cyan-300">
                💡 <span className="font-semibold">提示：</span>提交反馈可以获得额外的灵值奖励哦！
              </p>
            </div>
          )}

          {/* 关闭按钮 */}
          <button
            onClick={onClose}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-xl font-semibold hover:from-cyan-600 hover:to-purple-600 transition-all"
          >
            知道了
          </button>
        </div>
      </div>
    </div>
  )
}
