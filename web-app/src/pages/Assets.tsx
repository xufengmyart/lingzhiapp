import React, { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Gem, TrendingUp, DollarSign, Sparkles, Plus, ArrowRight } from 'lucide-react'

interface DigitalAsset {
  id: number
  asset_type: string
  asset_name: string
  description: string
  image_url: string | null
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  value: number
  metadata: any
  created_at: string
}

const AssetsPage: React.FC = () => {
  const [assets, setAssets] = useState<DigitalAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [showMintModal, setShowMintModal] = useState(false)
  const [minting, setMinting] = useState(false)
  const [selectedAssetType, setSelectedAssetType] = useState('')
  const [assetName, setAssetName] = useState('')
  const [assetDescription, setAssetDescription] = useState('')

  // 资产类型配置
  const assetTypes = [
    { id: 'contribution_badge', name: '贡献勋章', rarity: 'common', value: 300, icon: '🏅' },
    { id: 'ecosystem_pass', name: '生态通行证', rarity: 'rare', value: 3000, icon: '🎫' },
    { id: 'project_proof', name: '项目证明', rarity: 'epic', value: 1500, icon: '📜' },
    { id: 'resource_certificate', name: '资源凭证', rarity: 'rare', value: 800, icon: '📋' },
    { id: 'honor_badge', name: '荣誉徽章', rarity: 'legendary', value: 8000, icon: '🎖️' },
  ]

  const rarityColors = {
    common: 'from-gray-600 to-gray-700',
    rare: 'from-blue-600 to-blue-700',
    epic: 'from-purple-600 to-purple-700',
    legendary: 'from-yellow-600 to-orange-600',
  }

  const rarityBorders = {
    common: 'border-gray-500',
    rare: 'border-blue-500',
    epic: 'border-purple-500',
    legendary: 'border-yellow-500',
  }

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/user/assets', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const result = await response.json()
      if (result.success) {
        setAssets(result.data)
      }
    } catch (error) {
      console.error('获取资产失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMint = async () => {
    if (!selectedAssetType || !assetName) {
      alert('请填写完整信息')
      return
    }

    setMinting(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/user/assets/mint', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          asset_type: selectedAssetType,
          asset_name: assetName,
          description: assetDescription
        })
      })
      const result = await response.json()
      if (result.success) {
        alert('资产铸造成功！')
        setShowMintModal(false)
        setAssetName('')
        setAssetDescription('')
        setSelectedAssetType('')
        fetchAssets()
      } else {
        alert(result.message || '铸造失败')
      }
    } catch (error) {
      console.error('铸造失败:', error)
      alert('铸造失败，请重试')
    } finally {
      setMinting(false)
    }
  }

  const totalValue = assets.reduce((sum, asset) => sum + asset.value, 0)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
        <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            数字资产
          </h1>
          <p className="text-gray-300">您的数字资产收藏</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">资产总数</p>
                <p className="text-3xl font-bold">{assets.length}</p>
              </div>
              <Gem className="w-10 h-10 text-purple-400" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border-cyan-500/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">总价值</p>
                <p className="text-3xl font-bold">{totalValue.toLocaleString()} <span className="text-lg">灵值</span></p>
              </div>
              <DollarSign className="w-10 h-10 text-cyan-400" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border-yellow-500/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">月收益</p>
                <p className="text-3xl font-bold">{(totalValue * 0.01).toFixed(0)} <span className="text-lg">灵值</span></p>
              </div>
              <TrendingUp className="w-10 h-10 text-yellow-400" />
            </div>
          </Card>
        </div>

        {/* 铸造按钮 */}
        <div className="flex justify-end mb-6">
          <Button
            onClick={() => setShowMintModal(true)}
            className="bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600"
          >
            <Plus className="mr-2 w-4 h-4" />
            铸造资产
          </Button>
        </div>

        {/* 资产列表 */}
        {assets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assets.map((asset) => {
              const assetTypeConfig = assetTypes.find(t => t.id === asset.asset_type)
              const gradient = rarityColors[asset.rarity] || rarityColors.common
              const border = rarityBorders[asset.rarity] || rarityBorders.common
              
              return (
                <Card
                  key={asset.id}
                  className={`bg-gradient-to-br ${gradient} ${border} border-2 hover:scale-105 transition-transform`}
                >
                  <div className="aspect-square flex items-center justify-center text-8xl mb-4">
                    {asset.image_url ? (
                      <img src={asset.image_url} alt={asset.asset_name} className="w-full h-full object-cover rounded-lg" />
                    ) : (
                      assetTypeConfig?.icon || '💎'
                    )}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{asset.asset_name}</h3>
                  <p className="text-sm text-gray-300 mb-3">{asset.description}</p>
                  <div className="flex justify-between items-center text-sm">
                    <span className="px-3 py-1 bg-white/10 rounded-full capitalize">
                      {asset.rarity}
                    </span>
                    <span className="font-bold text-yellow-400">{asset.value.toLocaleString()} 灵值</span>
                  </div>
                  <div className="mt-3 pt-3 border-t border-white/20 text-xs text-gray-300">
                    获得于: {new Date(asset.created_at).toLocaleDateString('zh-CN')}
                  </div>
                </Card>
              )
            })}
          </div>
        ) : (
          <Card className="text-center py-12">
            <Sparkles className="w-16 h-16 mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">还没有数字资产</h3>
            <p className="text-gray-400 mb-4">完成用户旅程阶段或自行铸造数字资产</p>
            <Button onClick={() => setShowMintModal(true)}>
              <Plus className="mr-2 w-4 h-4" />
              开始铸造
            </Button>
          </Card>
        )}

        {/* 铸造模态框 */}
        {showMintModal && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md bg-gray-900 border-purple-500/50">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-purple-400" />
                铸造数字资产
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">资产类型</label>
                  <select
                    value={selectedAssetType}
                    onChange={(e) => setSelectedAssetType(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
                  >
                    <option value="">请选择资产类型</option>
                    {assetTypes.map((type) => (
                      <option key={type.id} value={type.id}>
                        {type.icon} {type.name} ({type.value} 灵值)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">资产名称</label>
                  <input
                    type="text"
                    value={assetName}
                    onChange={(e) => setAssetName(e.target.value)}
                    placeholder="为您的资产命名"
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">描述</label>
                  <textarea
                    value={assetDescription}
                    onChange={(e) => setAssetDescription(e.target.value)}
                    placeholder="描述您的资产..."
                    rows={3}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none resize-none"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => setShowMintModal(false)}
                  variant="secondary"
                  className="flex-1"
                >
                  取消
                </Button>
                <Button
                  onClick={handleMint}
                  disabled={minting}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600"
                >
                  {minting ? '铸造中...' : (
                    <>
                      立即铸造
                      <Sparkles className="ml-2 w-4 h-4" />
                    </>
                  )}
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

export default AssetsPage
