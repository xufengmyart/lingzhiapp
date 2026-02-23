import { useState, useEffect } from 'react'
import { Card, Table, Tag, Button, Space, Input, Select, DatePicker, Statistic, Row, Col, message, Modal, Form, InputNumber } from 'antd'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { ArrowUpOutlined, ArrowDownOutlined, DollarOutlined, ShoppingOutlined } from '@ant-design/icons'

const { RangePicker } = DatePicker
const { Option } = Select

interface AssetData {
  id: number
  projectId: number
  assetName: string
  assetType: string
  estimatedValue: number
  tokenAddress: string
  tokenSymbol: string
  totalSupply: number
  currentPrice: number
  change24h: number
  volume24h: number
  status: string
}

interface OrderData {
  id: number
  assetId: number
  orderType: 'buy' | 'sell'
  amount: number
  price: number
  status: string
  createdAt: string
}

const AssetMarket: React.FC = () => {
  const [assets, setAssets] = useState<AssetData[]>([])
  const [orders, setOrders] = useState<OrderData[]>([])
  const [marketStats, setMarketStats] = useState<any>(null)
  const [priceHistory, setPriceHistory] = useState<any[]>([])
  const [selectedAsset, setSelectedAsset] = useState<AssetData | null>(null)
  const [loading, setLoading] = useState(false)
  const [orderModalVisible, setOrderModalVisible] = useState(false)
  const [listModalVisible, setListModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchMarketStats()
    fetchMarketAssets()
    fetchOrders()
  }, [])

  const fetchMarketStats = async () => {
    try {
      const response = await fetch('/api/v9/market/stats')
      const result = await response.json()
      if (result.success) {
        setMarketStats(result.data)
      }
    } catch (error) {
      console.error('Failed to fetch market stats:', error)
    }
  }

  const fetchMarketAssets = async () => {
    try {
      const response = await fetch('/api/v9/market/assets')
      const result = await response.json()
      if (result.success) {
        setAssets(result.data)
      }
    } catch (error) {
      console.error('Failed to fetch market assets:', error)
    }
  }

  const fetchOrders = async () => {
    try {
      const response = await fetch('/api/v9/market/orders')
      const result = await response.json()
      if (result.success) {
        setOrders(result.data)
      }
    } catch (error) {
      console.error('Failed to fetch orders:', error)
    }
  }

  const fetchPriceHistory = async (assetId: number) => {
    try {
      const response = await fetch(`/api/v9/market/assets/${assetId}/price-history`)
      const result = await response.json()
      if (result.success) {
        setPriceHistory(result.data)
      }
    } catch (error) {
      console.error('Failed to fetch price history:', error)
    }
  }

  const handleAssetClick = (asset: AssetData) => {
    setSelectedAsset(asset)
    fetchPriceHistory(asset.id)
  }

  const handleCreateOrder = async (values: any) => {
    try {
      setLoading(true)
      const response = await fetch('/api/v9/market/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assetId: selectedAsset?.id,
          orderType: values.orderType,
          amount: values.amount,
          price: values.price,
          userId: 1 // TODO: 从认证上下文获取
        })
      })
      const result = await response.json()
      if (result.success) {
        message.success('订单创建成功')
        setOrderModalVisible(false)
        fetchOrders()
        form.resetFields()
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('创建订单失败')
    } finally {
      setLoading(false)
    }
  }

  const handleListAsset = async (values: any) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/v9/market/assets/${selectedAsset?.id}/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price: values.price,
          minOrder: values.minOrder
        })
      })
      const result = await response.json()
      if (result.success) {
        message.success('资产挂牌成功')
        setListModalVisible(false)
        fetchMarketAssets()
        form.resetFields()
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('资产挂牌失败')
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '资产名称',
      dataIndex: 'assetName',
      key: 'assetName'
    },
    {
      title: '类型',
      dataIndex: 'assetType',
      key: 'assetType',
      render: (type: string) => <Tag color="blue">{type}</Tag>
    },
    {
      title: '当前价格',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      render: (price: number) => `$${price.toFixed(2)}`
    },
    {
      title: '24h涨跌',
      dataIndex: 'change24h',
      key: 'change24h',
      render: (change: number) => (
        <span style={{ color: change >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(change).toFixed(2)}%
        </span>
      )
    },
    {
      title: '24h成交量',
      dataIndex: 'volume24h',
      key: 'volume24h',
      render: (volume: number) => `$${volume.toFixed(2)}`
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: any = {
          'listed': 'green',
          'tokenized': 'blue',
          'pending': 'orange'
        }
        return <Tag color={colors[status] || 'default'}>{status}</Tag>
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: AssetData) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleAssetClick(record)}>
            查看详情
          </Button>
          <Button type="link" size="small" onClick={() => { setSelectedAsset(record); setOrderModalVisible(true) }}>
            交易
          </Button>
        </Space>
      )
    }
  ]

  const orderColumns = [
    {
      title: '订单ID',
      dataIndex: 'id',
      key: 'id'
    },
    {
      title: '类型',
      dataIndex: 'orderType',
      key: 'orderType',
      render: (type: string) => (
        <Tag color={type === 'buy' ? 'green' : 'red'}>
          {type === 'buy' ? '买入' : '卖出'}
        </Tag>
      )
    },
    {
      title: '数量',
      dataIndex: 'amount',
      key: 'amount'
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `$${price.toFixed(2)}`
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: any = {
          'pending': 'orange',
          'filled': 'green',
          'cancelled': 'red'
        }
        return <Tag color={colors[status] || 'default'}>{status}</Tag>
      }
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt'
    }
  ]

  return (
    <div className="asset-market">
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总交易额"
              value={marketStats?.totalVolume || 0}
              prefix={<DollarOutlined />}
              suffix="USD"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="24h交易量"
              value={marketStats?.['24hVolume'] || 0}
              prefix={<DollarOutlined />}
              suffix="USD"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃交易者"
              value={marketStats?.activeTraders || 0}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="挂牌资产数"
              value={marketStats?.listedAssets || 0}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {selectedAsset && priceHistory.length > 0 && (
        <Card title={`${selectedAsset.assetName} - 价格走势`} style={{ marginBottom: 24 }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={priceHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="price" stroke="#8884d8" name="价格 (USD)" />
              <Line type="monotone" dataKey="volume" stroke="#82ca9d" name="成交量" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      <Card title="资产交易市场" style={{ marginBottom: 24 }}>
        <Table
          columns={columns}
          dataSource={assets}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Card title="我的订单">
        <Table
          columns={orderColumns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title="创建交易订单"
        open={orderModalVisible}
        onCancel={() => setOrderModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreateOrder} layout="vertical">
          <Form.Item label="订单类型" name="orderType" rules={[{ required: true }]}>
            <Select>
              <Option value="buy">买入</Option>
              <Option value="sell">卖出</Option>
            </Select>
          </Form.Item>
          <Form.Item label="数量" name="amount" rules={[{ required: true }]}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="价格" name="price" rules={[{ required: true }]}>
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              提交订单
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AssetMarket
