import { useState, useEffect } from 'react'
import { Users, UserPlus, Network, Zap, ChevronDown, ChevronUp, Search, Filter } from 'lucide-react'
import api from '../services/api'

interface ReferralNode {
  id: number
  username: string
  referral_code: string
  level: number
  status: string
  created_at: string
  children?: ReferralNode[]
}

interface ReferralNetworkProps {}

const ReferralNetwork = () => {
  const [networkData, setNetworkData] = useState<ReferralNode[]>([])
  const [selectedNode, setSelectedNode] = useState<ReferralNode | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'tree' | 'list'>('tree')
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set())

  useEffect(() => {
    loadReferralNetwork()
  }, [])

  const loadReferralNetwork = async () => {
    try {
      const response = await api.get('/referral/network')
      if (response.data.success) {
        setNetworkData(response.data.data || [])
        // 默认展开第一层
        if (response.data.data && response.data.data.length > 0) {
          setExpandedNodes(new Set([response.data.data[0].id]))
        }
      }
    } catch (error) {
      console.error('加载推荐网络失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleNode = (nodeId: number) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev)
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId)
      } else {
        newSet.add(nodeId)
      }
      return newSet
    })
  }

  const renderTreeNode = (node: ReferralNode, depth: number = 0): JSX.Element => {
    const isExpanded = expandedNodes.has(node.id)
    const hasChildren = node.children && node.children.length > 0

    return (
      <div key={node.id} className="ml-4">
        <div
          className={`flex items-center gap-3 p-4 bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl hover:border-[#00C3FF]/50 transition-all cursor-pointer ${selectedNode?.id === node.id ? 'border-[#00C3FF]' : ''}`}
          style={{ marginLeft: `${depth * 20}px` }}
          onClick={() => setSelectedNode(node)}
        >
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            node.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
          }`}>
            <Users className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="text-white font-medium">{node.username}</div>
            <div className="text-[#B4C7E7] text-sm">{node.referral_code}</div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-[#00C3FF] text-sm font-medium">层级 {node.level}</div>
              <div className="text-[#B4C7E7] text-xs">{hasChildren ? `${node.children?.length} 个直推` : '无直推'}</div>
            </div>
            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleNode(node.id)
                }}
                className="p-2 hover:bg-[#00C3FF]/10 rounded-lg transition-colors"
              >
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-[#B4C7E7]" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-[#B4C7E7]" />
                )}
              </button>
            )}
          </div>
        </div>
        {isExpanded && hasChildren && node.children?.map(child => renderTreeNode(child, depth + 1))}
      </div>
    )
  }

  const renderListView = () => {
    const flattenNodes = (nodes: ReferralNode[]): ReferralNode[] => {
      let result: ReferralNode[] = []
      const traverse = (node: ReferralNode) => {
        result.push(node)
        if (node.children) {
          node.children.forEach(traverse)
        }
      }
      nodes.forEach(traverse)
      return result
    }

    const allNodes = flattenNodes(networkData)

    return (
      <div className="space-y-3">
        {allNodes
          .filter(node =>
            searchQuery === '' ||
            node.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
            node.referral_code.toLowerCase().includes(searchQuery.toLowerCase())
          )
          .map(node => (
            <div
              key={node.id}
              className={`flex items-center gap-4 p-4 bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl hover:border-[#00C3FF]/50 transition-all cursor-pointer ${selectedNode?.id === node.id ? 'border-[#00C3FF]' : ''}`}
              onClick={() => setSelectedNode(node)}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                node.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              }`}>
                <Users className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="text-white font-medium">{node.username}</div>
                <div className="text-[#B4C7E7] text-sm">{node.referral_code}</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-[#00C3FF] text-sm font-medium">层级 {node.level}</div>
                  <div className="text-[#B4C7E7] text-xs">
                    {node.children ? `${node.children.length} 个直推` : '无直推'}
                  </div>
                </div>
                <div className="text-[#B4C7E7] text-xs">
                  {new Date(node.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
      </div>
    )
  }

  const getNodeCount = (nodes: ReferralNode[]): number => {
    let count = 0
    const traverse = (node: ReferralNode) => {
      count++
      if (node.children) {
        node.children.forEach(traverse)
      }
    }
    nodes.forEach(traverse)
    return count
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#091422] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00C3FF]"></div>
      </div>
    )
  }

  const totalNodes = getNodeCount(networkData)

  return (
    <div className="min-h-screen bg-[#091422] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <Network className="w-10 h-10 text-[#00C3FF]" />
              <h1 className="text-3xl font-bold text-white">客户关系网络</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-2 bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl text-white">
                <span className="text-[#B4C7E7]">总用户：</span>
                <span className="text-[#00C3FF] font-bold">{totalNodes}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 工具栏 */}
        <div className="flex items-center gap-4 mb-6 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#B4C7E7]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索用户名或推荐码..."
              className="w-full pl-10 pr-4 py-3 bg-[#121A2F] border border-[#00C3FF]/20 rounded-xl text-white placeholder-[#B4C7E7] focus:outline-none focus:border-[#00C3FF]/50"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('tree')}
              className={`px-4 py-3 rounded-xl flex items-center gap-2 transition-colors ${
                viewMode === 'tree'
                  ? 'bg-[#00C3FF] text-white'
                  : 'bg-[#121A2F] border border-[#00C3FF]/20 text-[#B4C7E7] hover:border-[#00C3FF]/50'
              }`}
            >
              <Network className="w-5 h-5" />
              树形视图
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-3 rounded-xl flex items-center gap-2 transition-colors ${
                viewMode === 'list'
                  ? 'bg-[#00C3FF] text-white'
                  : 'bg-[#121A2F] border border-[#00C3FF]/20 text-[#B4C7E7] hover:border-[#00C3FF]/50'
              }`}
            >
              <Users className="w-5 h-5" />
              列表视图
            </button>
          </div>
        </div>

        {/* 主内容区 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：关系网络 */}
          <div className="lg:col-span-2 bg-[#0A0D18]/80 border border-[#00C3FF]/20 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Network className="w-6 h-6 text-[#00C3FF]" />
              <h2 className="text-xl font-bold text-white">推荐关系</h2>
            </div>
            {networkData.length === 0 ? (
              <div className="text-center py-12 text-[#B4C7E7]">
                <UserPlus className="w-16 h-16 text-[#B4C7E7] mx-auto mb-4" />
                <p className="text-lg mb-2">还没有推荐关系</p>
                <p className="text-sm">开始推荐用户，构建您的客户网络</p>
              </div>
            ) : viewMode === 'tree' ? (
              <div className="space-y-2">
                {networkData.map(node => renderTreeNode(node))}
              </div>
            ) : (
              renderListView()
            )}
          </div>

          {/* 右侧：详情面板 */}
          <div className="bg-[#0A0D18]/80 border border-[#00C3FF]/20 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-6 h-6 text-[#00C3FF]" />
              <h2 className="text-xl font-bold text-white">详细信息</h2>
            </div>
            {selectedNode ? (
              <div className="space-y-6">
                <div className="text-center">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 ${
                    selectedNode.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    <Users className="w-10 h-10" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2">{selectedNode.username}</h3>
                  <div className="text-[#B4C7E7]">{selectedNode.referral_code}</div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 bg-[#121A2F] rounded-xl">
                    <span className="text-[#B4C7E7]">推荐层级</span>
                    <span className="text-[#00C3FF] font-bold">第 {selectedNode.level} 层</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-[#121A2F] rounded-xl">
                    <span className="text-[#B4C7E7]">账户状态</span>
                    <span className={`font-bold ${selectedNode.status === 'active' ? 'text-green-400' : 'text-gray-400'}`}>
                      {selectedNode.status === 'active' ? '活跃' : '未活跃'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-[#121A2F] rounded-xl">
                    <span className="text-[#B4C7E7]">直推人数</span>
                    <span className="text-[#00C3FF] font-bold">{selectedNode.children?.length || 0} 人</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-[#121A2F] rounded-xl">
                    <span className="text-[#B4C7E7]">加入时间</span>
                    <span className="text-[#00C3FF] font-bold">
                      {new Date(selectedNode.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-[#00C3FF]/10 border border-[#00C3FF]/20 rounded-xl">
                  <div className="text-center">
                    <div className="text-[#B4C7E7] text-sm mb-2">预估收益</div>
                    <div className="text-3xl font-bold text-[#00C3FF]">¥ 1,234.56</div>
                    <div className="text-[#B4C7E7] text-xs mt-1">本月累计</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-[#B4C7E7]">
                <Network className="w-16 h-16 text-[#B4C7E7] mx-auto mb-4" />
                <p>点击用户查看详细信息</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReferralNetwork
