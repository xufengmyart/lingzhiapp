import { useState, useEffect } from 'react'
import { Card, Table, Tag, Button, Space, Select, Input, DatePicker, message, Modal, Descriptions } from 'antd'
import { ReloadOutlined, ExclamationCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

const { RangePicker } = DatePicker
const { Option } = Select

interface ErrorLogData {
  id: number
  errorType: string
  message: string
  stackTrace?: string
  context?: any
  userId?: number
  ipAddress?: string
  userAgent?: string
  requestUrl?: string
  requestMethod?: string
  severity: 'critical' | 'error' | 'warning'
  resolved: boolean
  createdAt: string
}

const ErrorLogs: React.FC = () => {
  const [logs, setLogs] = useState<ErrorLogData[]>([])
  const [loading, setLoading] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedLog, setSelectedLog] = useState<ErrorLogData | null>(null)
  const [filter, setFilter] = useState({
    severity: undefined as string | undefined,
    resolved: undefined as boolean | undefined,
    keyword: ''
  })

  useEffect(() => {
    fetchLogs()
  }, [filter])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filter.severity) params.append('severity', filter.severity)
      if (filter.resolved !== undefined) params.append('resolved', filter.resolved.toString())
      if (filter.keyword) params.append('keyword', filter.keyword)

      const response = await fetch(`/api/admin/error-logs?${params}`)
      const result = await response.json()
      if (result.success) {
        setLogs(result.data)
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('获取错误日志失败')
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetail = (log: ErrorLogData) => {
    setSelectedLog(log)
    setDetailModalVisible(true)
  }

  const handleMarkResolved = async (logId: number) => {
    try {
      const response = await fetch(`/api/admin/error-logs/${logId}/resolve`, {
        method: 'PUT'
      })
      const result = await response.json()
      if (result.success) {
        message.success('标记已解决成功')
        fetchLogs()
      } else {
        message.error(result.message)
      }
    } catch (error) {
      message.error('标记已解决失败')
    }
  }

  const handleDelete = async (logId: number) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这条错误日志吗？',
      onOk: async () => {
        try {
          const response = await fetch(`/api/admin/error-logs/${logId}`, {
            method: 'DELETE'
          })
          const result = await response.json()
          if (result.success) {
            message.success('删除成功')
            fetchLogs()
          } else {
            message.error(result.message)
          }
        } catch (error) {
          message.error('删除失败')
        }
      }
    })
  }

  const columns: ColumnsType<ErrorLogData> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '严重性',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => {
        const colors: any = {
          'critical': 'red',
          'error': 'orange',
          'warning': 'yellow'
        }
        return <Tag color={colors[severity] || 'default'}>{severity}</Tag>
      }
    },
    {
      title: '错误类型',
      dataIndex: 'errorType',
      key: 'errorType',
      width: 150
    },
    {
      title: '错误信息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true
    },
    {
      title: '用户ID',
      dataIndex: 'userId',
      key: 'userId',
      width: 100
    },
    {
      title: 'IP地址',
      dataIndex: 'ipAddress',
      key: 'ipAddress',
      width: 150
    },
    {
      title: '请求URL',
      dataIndex: 'requestUrl',
      key: 'requestUrl',
      ellipsis: true
    },
    {
      title: '状态',
      dataIndex: 'resolved',
      key: 'resolved',
      width: 100,
      render: (resolved: boolean) => (
        <Tag color={resolved ? 'green' : 'red'}>
          {resolved ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
          {resolved ? '已解决' : '未解决'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
            查看详情
          </Button>
          {!record.resolved && (
            <Button type="link" size="small" onClick={() => handleMarkResolved(record.id)}>
              标记已解决
            </Button>
          )}
          <Button type="link" size="small" danger onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div className="error-logs">
      <Card
        title="错误日志管理"
        extra={
          <Button icon={<ReloadOutlined />} onClick={fetchLogs} loading={loading}>
            刷新
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Select
            placeholder="严重性"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilter({ ...filter, severity: value })}
          >
            <Option value="critical">严重</Option>
            <Option value="error">错误</Option>
            <Option value="warning">警告</Option>
          </Select>
          <Select
            placeholder="状态"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilter({ ...filter, resolved: value === 'true' })}
          >
            <Option value="true">已解决</Option>
            <Option value="false">未解决</Option>
          </Select>
          <Input
            placeholder="搜索关键词"
            style={{ width: 200 }}
            onChange={(e) => setFilter({ ...filter, keyword: e.target.value })}
          />
        </Space>

        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`
          }}
        />
      </Card>

      <Modal
        title="错误详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedLog && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="严重性">
              <Tag color={selectedLog.severity === 'critical' ? 'red' : selectedLog.severity === 'error' ? 'orange' : 'yellow'}>
                {selectedLog.severity}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="错误类型">{selectedLog.errorType}</Descriptions.Item>
            <Descriptions.Item label="错误信息">{selectedLog.message}</Descriptions.Item>
            {selectedLog.stackTrace && (
              <Descriptions.Item label="堆栈跟踪">
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                  {selectedLog.stackTrace}
                </pre>
              </Descriptions.Item>
            )}
            {selectedLog.context && (
              <Descriptions.Item label="上下文">
                <pre>{JSON.stringify(selectedLog.context, null, 2)}</pre>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="用户ID">{selectedLog.userId || '-'}</Descriptions.Item>
            <Descriptions.Item label="IP地址">{selectedLog.ipAddress || '-'}</Descriptions.Item>
            <Descriptions.Item label="User Agent">
              <div style={{ maxWidth: 600, wordBreak: 'break-all' }}>
                {selectedLog.userAgent || '-'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="请求URL">{selectedLog.requestUrl || '-'}</Descriptions.Item>
            <Descriptions.Item label="请求方法">{selectedLog.requestMethod || '-'}</Descriptions.Item>
            <Descriptions.Item label="创建时间">{selectedLog.createdAt}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={selectedLog.resolved ? 'green' : 'red'}>
                {selectedLog.resolved ? '已解决' : '未解决'}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default ErrorLogs
