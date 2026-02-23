import { useState, useEffect } from 'react'
import { Card, Table, Statistic, Row, Col, Select, DatePicker, Button, Tag, Space, message } from 'antd'
import { ReloadOutlined, ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'

const { RangePicker } = DatePicker
const { Option } = Select

interface APIMetricData {
  id: number
  endpoint: string
  method: string
  avgResponseTime: number
  p95ResponseTime: number
  p99ResponseTime: number
  successRate: number
  errorRate: number
  totalRequests: number
  errorCount: number
}

interface AlertRule {
  id: number
  name: string
  metricType: string
  threshold: number
  condition: string
  enabled: boolean
}

const APIMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<APIMetricData[]>([])
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState<string>('24h')
  const [chartData, setChartData] = useState<any[]>([])
  const [alertRules, setAlertRules] = useState<AlertRule[]>([])

  useEffect(() => {
    fetchMetrics()
    fetchAlertRules()
  }, [timeRange])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/admin/api-monitor?timeRange=${timeRange}`)
      const result = await response.json()
      if (result.success) {
        setMetrics(result.data.metrics || [])
        setChartData(result.data.chartData || [])
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('获取API监控数据失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchAlertRules = async () => {
    try {
      const response = await fetch('/api/admin/api-monitor/alerts')
      const result = await response.json()
      if (result.success) {
        setAlertRules(result.data || [])
      }
    } catch (error) {
      console.error('Failed to fetch alert rules:', error)
    }
  }

  const handleToggleAlert = async (ruleId: number, enabled: boolean) => {
    try {
      const response = await fetch(`/api/admin/api-monitor/alerts/${ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      })
      const result = await response.json()
      if (result.success) {
        message.success('告警规则更新成功')
        fetchAlertRules()
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('更新告警规则失败')
    }
  }

  const columns: ColumnsType<APIMetricData> = [
    {
      title: '端点',
      dataIndex: 'endpoint',
      key: 'endpoint',
      ellipsis: true
    },
    {
      title: '方法',
      dataIndex: 'method',
      key: 'method',
      width: 100,
      render: (method: string) => <Tag color="blue">{method}</Tag>
    },
    {
      title: '总请求数',
      dataIndex: 'totalRequests',
      key: 'totalRequests',
      width: 120
    },
    {
      title: '平均响应时间(ms)',
      dataIndex: 'avgResponseTime',
      key: 'avgResponseTime',
      width: 150,
      render: (time: number) => (
        <span style={{ color: time > 1000 ? '#ff4d4f' : time > 500 ? '#faad14' : '#52c41a' }}>
          {time.toFixed(2)}
        </span>
      )
    },
    {
      title: 'P95响应时间(ms)',
      dataIndex: 'p95ResponseTime',
      key: 'p95ResponseTime',
      width: 150,
      render: (time: number) => time.toFixed(2)
    },
    {
      title: 'P99响应时间(ms)',
      dataIndex: 'p99ResponseTime',
      key: 'p99ResponseTime',
      width: 150,
      render: (time: number) => time.toFixed(2)
    },
    {
      title: '成功率',
      dataIndex: 'successRate',
      key: 'successRate',
      width: 120,
      render: (rate: number) => (
        <Tag color={rate >= 99 ? 'green' : rate >= 95 ? 'orange' : 'red'}>
          {rate.toFixed(2)}%
        </Tag>
      )
    },
    {
      title: '错误数',
      dataIndex: 'errorCount',
      key: 'errorCount',
      width: 100,
      render: (count: number) => (
        <Tag color={count > 0 ? 'red' : 'green'}>{count}</Tag>
      )
    }
  ]

  const alertColumns: ColumnsType<AlertRule> = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '监控指标',
      dataIndex: 'metricType',
      key: 'metricType'
    },
    {
      title: '阈值',
      dataIndex: 'threshold',
      key: 'threshold'
    },
    {
      title: '条件',
      dataIndex: 'condition',
      key: 'condition',
      render: (condition: string) => <Tag color="blue">{condition}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled: boolean, record) => (
        <Tag
          color={enabled ? 'green' : 'default'}
          style={{ cursor: 'pointer' }}
          onClick={() => handleToggleAlert(record.id, !enabled)}
        >
          {enabled ? '已启用' : '已禁用'}
        </Tag>
      )
    }
  ]

  return (
    <div className="api-monitor">
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总请求数"
              value={metrics.reduce((sum, m) => sum + m.totalRequests, 0)}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均响应时间"
              value={metrics.length > 0 ? metrics.reduce((sum, m) => sum + m.avgResponseTime, 0) / metrics.length : 0}
              suffix="ms"
              precision={2}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均成功率"
              value={metrics.length > 0 ? metrics.reduce((sum, m) => sum + m.successRate, 0) / metrics.length : 0}
              suffix="%"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误总数"
              value={metrics.reduce((sum, m) => sum + m.errorCount, 0)}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="响应时间趋势"
        style={{ marginBottom: 24 }}
        extra={
          <Space>
            <Select
              defaultValue="24h"
              style={{ width: 150 }}
              onChange={setTimeRange}
            >
              <Option value="1h">最近1小时</Option>
              <Option value="24h">最近24小时</Option>
              <Option value="7d">最近7天</Option>
              <Option value="30d">最近30天</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={fetchMetrics} loading={loading}>
              刷新
            </Button>
          </Space>
        }
      >
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="avgResponseTime" stroke="#8884d8" name="平均响应时间(ms)" />
            <Line type="monotone" dataKey="p95ResponseTime" stroke="#82ca9d" name="P95响应时间(ms)" />
            <Line type="monotone" dataKey="p99ResponseTime" stroke="#ffc658" name="P99响应时间(ms)" />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Card
        title="API性能指标"
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={columns}
          dataSource={metrics}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`
          }}
        />
      </Card>

      <Card title="告警规则配置">
        <Table
          columns={alertColumns}
          dataSource={alertRules}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  )
}

export default APIMonitor
