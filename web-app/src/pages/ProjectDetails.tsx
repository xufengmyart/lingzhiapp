import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, Database, FileText, Coins, BarChart3, 
  Shield, Share2, TrendingUp, CheckCircle, Clock,
  Plus, Edit, Download, ExternalLink, ChevronRight,
  Layers, Box, Package, Lock, Wallet, DollarSign
} from 'lucide-react'
import api from '../services/api'

// ============ 类型定义 ============

interface BasicInfo {
  id: number
  name: string
  description: string
  category: string
  status: string
  budget: number
  progress: number
  startDate: string
  endDate: string
}

interface DataElement {
  id: number
  projectId: number
  elementName: string
  elementType: string
  description: string
  dataSource: string
  status: string
  createdAt: string
}

interface Resource {
  id: number
  projectId: number
  elementId: number
  resourceName: string
  resourceType: string
  resourceUrl: string
  status: string
  createdAt: string
}

interface DataAsset {
  id: number
  projectId: number
  assetName: string
  assetType: string
  dataValue: number
  estimatedValue: number
  tokenAddress: string
  tokenSymbol: string
  totalSupply: number
  currentPrice: number
  marketCap: number
  status: string
  createdAt: string
}

interface RightsRecord {
  id: number
  projectId: number
  assetId: number
  rightsType: string
  rightsHolder: string
  rightsValue: number
  certificateNo: string
  status: string
  createdAt: string
}

interface TokenRecord {
  id: number
  projectId: number
  assetId: number
  tokenAddress: string
  tokenSymbol: string
  totalSupply: number
  decimals: number
  status: string
  createdAt: string
}

interface Transaction {
  id: number
  projectId: number
  assetId: number
  transactionType: string
  fromAddress: string
  toAddress: string
  amount: number
  price: number
  totalValue: number
  txHash: string
  createdAt: string
}

interface ProjectRevenue {
  projectId: number
  totalRevenue: number
  totalTransactions: number
  avgTransactionValue: number
  updatedAt: string
}

interface ProjectDetails {
  basicInfo: BasicInfo
  dataElements: DataElement[]
  resources: Resource[]
  dataAssets: DataAsset[]
  rightsRecords: RightsRecord[]
  tokenRecords: TokenRecord[]
  transactions: Transaction[]
  revenue: ProjectRevenue | null
}

// ============ 主组件 ============

const ProjectDetails: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  
  const [projectDetails, setProjectDetails] = useState<ProjectDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'workflow' | 'elements' | 'assets' | 'transactions'>('workflow')
  const [selectedAsset, setSelectedAsset] = useState<DataAsset | null>(null)

  useEffect(() => {
    if (projectId) {
      fetchProjectDetails(parseInt(projectId))
    }
  }, [projectId])

  const fetchProjectDetails = async (pid: number) => {
    try {
      setLoading(true)
      const response = await api.get(`/api/v9/projects/${pid}/details`)
      if (response.data.success) {
        setProjectDetails(response.data.data)
      }
    } catch (error) {
      console.error('获取项目详情失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (!projectDetails) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">项目不存在或加载失败</p>
          <button 
            onClick={() => navigate(-1)}
            className="mt-4 text-indigo-600 hover:text-indigo-800"
          >
            返回
          </button>
        </div>
      </div>
    )
  }

  const { basicInfo, dataElements, resources, dataAssets, rightsRecords, tokenRecords, transactions, revenue } = projectDetails

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{basicInfo.name}</h1>
                <p className="text-sm text-gray-600">{basicInfo.description}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                <Download className="w-4 h-4" />
                导出
              </button>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2">
                <Edit className="w-4 h-4" />
                编辑
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">数据要素</p>
                <p className="text-2xl font-bold text-gray-900">{dataElements.length}</p>
              </div>
              <Database className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">资源文件</p>
                <p className="text-2xl font-bold text-gray-900">{resources.length}</p>
              </div>
              <FileText className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">数据资产</p>
                <p className="text-2xl font-bold text-gray-900">{dataAssets.length}</p>
              </div>
              <Box className="w-8 h-8 text-purple-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总收入</p>
                <p className="text-2xl font-bold text-gray-900">
                  {revenue ? `${revenue.totalRevenue.toFixed(2)}` : '0.00'}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Tab 导航 */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'workflow', label: '数据资产工作流', icon: Layers },
                { id: 'elements', label: '数据要素', icon: Database },
                { id: 'assets', label: '数据资产', icon: Box },
                { id: 'transactions', label: '交易记录', icon: BarChart3 }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'workflow' && (
              <WorkflowView 
                projectDetails={projectDetails}
                setSelectedAsset={setSelectedAsset}
              />
            )}
            {activeTab === 'elements' && (
              <ElementsView elements={dataElements} />
            )}
            {activeTab === 'assets' && (
              <AssetsView 
                assets={dataAssets} 
                rightsRecords={rightsRecords}
                tokenRecords={tokenRecords}
                setSelectedAsset={setSelectedAsset}
              />
            )}
            {activeTab === 'transactions' && (
              <TransactionsView transactions={transactions} />
            )}
          </div>
        </div>

        {/* 侧边详情面板 */}
        {selectedAsset && (
          <AssetDetailPanel 
            asset={selectedAsset}
            onClose={() => setSelectedAsset(null)}
          />
        )}
      </div>
    </div>
  )
}

// ============ 数据资产工作流视图 ============

const WorkflowView: React.FC<{
  projectDetails: ProjectDetails
  setSelectedAsset: (asset: DataAsset | null) => void
}> = ({ projectDetails, setSelectedAsset }) => {
  const steps = [
    { id: 1, name: '项目', icon: Package, count: 1, color: 'blue' },
    { id: 2, name: '分析', icon: Database, count: projectDetails.dataElements.length, color: 'green' },
    { id: 3, name: '要素', icon: Layers, count: projectDetails.dataElements.length, color: 'purple' },
    { id: 4, name: '资源', icon: FileText, count: projectDetails.resources.length, color: 'orange' },
    { id: 5, name: '数据化', icon: Database, count: projectDetails.dataAssets.length, color: 'cyan' },
    { id: 6, name: '确权', icon: Shield, count: projectDetails.rightsRecords.length, color: 'indigo' },
    { id: 7, name: '通证', icon: Coins, count: projectDetails.tokenRecords.length, color: 'yellow' },
    { id: 8, name: '市场', icon: TrendingUp, count: projectDetails.dataAssets.length, color: 'pink' },
    { id: 9, name: '交易', icon: BarChart3, count: projectDetails.transactions.length, color: 'red' },
    { id: 10, name: '账户', icon: Wallet, count: 1, color: 'emerald' }
  ]

  const getColorClass = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      orange: 'bg-orange-500',
      cyan: 'bg-cyan-500',
      indigo: 'bg-indigo-500',
      yellow: 'bg-yellow-500',
      pink: 'bg-pink-500',
      red: 'bg-red-500',
      emerald: 'bg-emerald-500'
    }
    return colors[color] || 'bg-gray-500'
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">数据资产完整工作流程</h3>
        <p className="text-sm text-gray-600">
          项目 → 分析 → 各要素 → 对应资源 → 数据化 → 确权 → 通证 → 形成数据资产 → 市场 → 交易 → 入公司账户
        </p>
      </div>

      {/* 工作流步骤 */}
      <div className="relative">
        {/* 连接线 */}
        <div className="absolute top-8 left-0 right-0 h-1 bg-gray-200 -z-10"></div>

        <div className="flex justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isCompleted = step.count > 0
            const isActive = index === 0 || isCompleted

            return (
              <div key={step.id} className="flex flex-col items-center">
                <div className={`
                  w-16 h-16 rounded-full flex items-center justify-center
                  ${isActive ? getColorClass(step.color) : 'bg-gray-300'}
                  ${isCompleted ? 'ring-4 ring-offset-2 ' + getColorClass(step.color).replace('bg-', 'ring-') : ''}
                  transition-all duration-300
                `}>
                  {isCompleted ? (
                    <CheckCircle className="w-8 h-8 text-white" />
                  ) : (
                    <Icon className="w-8 h-8 text-white" />
                  )}
                </div>
                <div className="mt-3 text-center">
                  <p className="text-sm font-medium text-gray-900">{step.name}</p>
                  <p className="text-xs text-gray-600">{step.count}</p>
                </div>
                {index < steps.length - 1 && (
                  <ChevronRight className="absolute top-6 left-[calc(5%_+_index_*_10%)] text-gray-400" style={{ left: `${(index + 1) * 10}%` }} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* 数据资产列表 */}
      {projectDetails.dataAssets.length > 0 && (
        <div className="mt-8">
          <h4 className="text-md font-semibold text-gray-900 mb-4">已形成的数据资产</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projectDetails.dataAssets.map((asset) => (
              <div 
                key={asset.id}
                onClick={() => setSelectedAsset(asset)}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-indigo-500 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium text-gray-900">{asset.assetName}</h5>
                  <span className={`
                    px-2 py-1 text-xs rounded-full
                    ${asset.status === 'tokenized' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                  `}>
                    {asset.status === 'tokenized' ? '已通证化' : '处理中'}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>估算价值:</span>
                    <span className="font-medium">{asset.estimatedValue.toFixed(2)}</span>
                  </div>
                  {asset.tokenSymbol && (
                    <div className="flex justify-between">
                      <span>通证:</span>
                      <span className="font-medium">{asset.tokenSymbol}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>当前价格:</span>
                    <span className="font-medium">{asset.currentPrice.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 交易统计 */}
      {projectDetails.revenue && (
        <div className="mt-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 text-white">
          <h4 className="text-md font-semibold mb-4">项目收入统计</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm opacity-80">总收入</p>
              <p className="text-2xl font-bold">{projectDetails.revenue.totalRevenue.toFixed(2)}</p>
            </div>
            <div className="text-center">
              <p className="text-sm opacity-80">总交易数</p>
              <p className="text-2xl font-bold">{projectDetails.revenue.totalTransactions}</p>
            </div>
            <div className="text-center">
              <p className="text-sm opacity-80">平均交易额</p>
              <p className="text-2xl font-bold">{projectDetails.revenue.avgTransactionValue.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ============ 数据要素视图 ============

const ElementsView: React.FC<{ elements: DataElement[] }> = ({ elements }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">数据要素</h3>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          新增要素
        </button>
      </div>

      {elements.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无数据要素</p>
          <p className="text-sm mt-1">点击"新增要素"开始创建</p>
        </div>
      ) : (
        <div className="space-y-3">
          {elements.map((element) => (
            <div key={element.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{element.elementName}</h4>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  element.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {element.status === 'completed' ? '已完成' : '处理中'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">类型</p>
                  <p className="text-gray-900">{element.elementType}</p>
                </div>
                <div>
                  <p className="text-gray-600">数据源</p>
                  <p className="text-gray-900">{element.dataSource}</p>
                </div>
              </div>
              {element.description && (
                <p className="mt-2 text-sm text-gray-600">{element.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ============ 数据资产视图 ============

const AssetsView: React.FC<{
  assets: DataAsset[]
  rightsRecords: RightsRecord[]
  tokenRecords: TokenRecord[]
  setSelectedAsset: (asset: DataAsset | null) => void
}> = ({ assets, rightsRecords, tokenRecords, setSelectedAsset }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">数据资产</h3>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          新增资产
        </button>
      </div>

      {assets.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Box className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无数据资产</p>
          <p className="text-sm mt-1">请先创建数据要素和资源</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {assets.map((asset) => {
            const rights = rightsRecords.filter(r => r.assetId === asset.id)
            const tokens = tokenRecords.filter(t => t.assetId === asset.id)

            return (
              <div 
                key={asset.id}
                onClick={() => setSelectedAsset(asset)}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-indigo-500 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{asset.assetName}</h4>
                  <div className="flex items-center gap-2">
                    {rights.length > 0 && (
                      <span className="px-2 py-1 text-xs rounded-full bg-indigo-100 text-indigo-800">
                        已确权
                      </span>
                    )}
                    {tokens.length > 0 && (
                      <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                        已通证化
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">数据价值:</span>
                    <span className="font-medium">{asset.dataValue.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">估算价值:</span>
                    <span className="font-medium">{asset.estimatedValue.toFixed(2)}</span>
                  </div>
                  {asset.tokenSymbol && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-600">通证符号:</span>
                        <span className="font-medium">{asset.tokenSymbol}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">当前价格:</span>
                        <span className="font-medium">{asset.currentPrice.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">市值:</span>
                        <span className="font-medium">{asset.marketCap.toFixed(2)}</span>
                      </div>
                    </>
                  )}
                </div>

                {asset.tokenAddress && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">合约地址:</span>
                      <a 
                        href={`https://etherscan.io/address/${asset.tokenAddress}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                      >
                        {asset.tokenAddress.substring(0, 10)}...
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ============ 交易记录视图 ============

const TransactionsView: React.FC<{ transactions: Transaction[] }> = ({ transactions }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">交易记录</h3>

      {transactions.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无交易记录</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">类型</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">金额</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">价格</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">总值</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">时间</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span className={`
                      px-2 py-1 text-xs rounded-full
                      ${tx.transactionType === 'buy' ? 'bg-green-100 text-green-800' : 
                        tx.transactionType === 'sell' ? 'bg-red-100 text-red-800' : 
                        'bg-blue-100 text-blue-800'}
                    `}>
                      {tx.transactionType === 'buy' ? '买入' : tx.transactionType === 'sell' ? '卖出' : '转账'}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-medium">{tx.amount}</td>
                  <td className="py-3 px-4">{tx.price.toFixed(2)}</td>
                  <td className="py-3 px-4 font-medium">{tx.totalValue.toFixed(2)}</td>
                  <td className="py-3 px-4 text-gray-600">
                    {new Date(tx.createdAt).toLocaleString('zh-CN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ============ 资产详情面板 ============

const AssetDetailPanel: React.FC<{
  asset: DataAsset
  onClose: () => void
}> = ({ asset, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900">{asset.assetName}</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <span className="sr-only">关闭</span>
              <span className="text-2xl">&times;</span>
            </button>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">数据价值</p>
                <p className="text-xl font-bold text-gray-900">{asset.dataValue.toFixed(2)}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">估算价值</p>
                <p className="text-xl font-bold text-gray-900">{asset.estimatedValue.toFixed(2)}</p>
              </div>
            </div>

            {asset.tokenSymbol && (
              <div className="bg-indigo-50 rounded-lg p-4">
                <p className="text-sm text-indigo-600 mb-2 font-medium">通证信息</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">符号:</span>
                    <span className="ml-2 font-medium">{asset.tokenSymbol}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">总供应量:</span>
                    <span className="ml-2 font-medium">{asset.totalSupply.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">当前价格:</span>
                    <span className="ml-2 font-medium">{asset.currentPrice.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">市值:</span>
                    <span className="ml-2 font-medium">{asset.marketCap.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="text-sm text-gray-600">
              <p>创建时间: {new Date(asset.createdAt).toLocaleString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetails
