import { useState, useCallback } from 'react'
import { Card, Upload, Button, Table, message, Progress, Space, Tag, Modal, Form, Select } from 'antd'
import { InboxOutlined, UploadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import type { UploadProps, UploadFile } from 'antd'
import * as XLSX from 'xlsx'

const { Dragger } = Upload
const { Option } = Select

interface ImportItem {
  id: number
  name: string
  type: string
  data: any
  status: 'pending' | 'success' | 'error'
  error?: string
}

const BatchImport: React.FC = () => {
  const [importType, setImportType] = useState<'data_element' | 'resource'>('data_element')
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [importItems, setImportItems] = useState<ImportItem[]>([])
  const [importing, setImporting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)

  const handleFileChange: UploadProps['onChange'] = ({ fileList }) => {
    setUploadFiles(fileList)
  }

  const parseExcelFile = async (file: File) => {
    return new Promise<ImportItem[]>((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const data = e.target?.result
          const workbook = XLSX.read(data, { type: 'binary' })
          const sheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[sheetName]
          const jsonData = XLSX.utils.sheet_to_json(worksheet)

          const items = jsonData.map((row: any, index) => ({
            id: index,
            name: row.name || row.title || row.名称 || `项目${index + 1}`,
            type: importType,
            data: row,
            status: 'pending' as const
          }))

          resolve(items)
        } catch (error) {
          reject(error)
        }
      }

      reader.onerror = (error) => reject(error)
      reader.readAsBinaryString(file)
    })
  }

  const handlePreview = async () => {
    if (uploadFiles.length === 0) {
      message.warning('请先上传文件')
      return
    }

    try {
      const file = uploadFiles[0].originFileObj as File
      if (!file) {
        message.error('文件读取失败')
        return
      }

      const items = await parseExcelFile(file)
      setImportItems(items)
      setPreviewModalVisible(true)
    } catch (error) {
      message.error('文件解析失败，请检查文件格式')
    }
  }

  const handleImport = async () => {
    if (importItems.length === 0) {
      message.warning('没有可导入的数据')
      return
    }

    setImporting(true)
    setProgress(0)

    const total = importItems.length
    const successItems: ImportItem[] = []
    const failedItems: ImportItem[] = []

    for (let i = 0; i < total; i++) {
      const item = importItems[i]
      
      try {
        const response = await fetch('/api/v9/batch-import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: importType,
            items: [item.data]
          })
        })

        const result = await response.json()
        
        if (result.success) {
          successItems.push({ ...item, status: 'success' })
        } else {
          failedItems.push({ ...item, status: 'error', error: result.message })
        }
      } catch (error: any) {
        failedItems.push({ ...item, status: 'error', error: error.message })
      }

      setProgress(Math.round(((i + 1) / total) * 100))
    }

    setImportItems([...successItems, ...failedItems])
    setImporting(false)

    message.success(`导入完成：成功 ${successItems.length} 条，失败 ${failedItems.length} 条`)
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="blue">{type}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        if (status === 'success') {
          return <Tag color="green" icon={<CheckCircleOutlined />}>成功</Tag>
        } else if (status === 'error') {
          return <Tag color="red" icon={<CloseCircleOutlined />}>失败</Tag>
        }
        return <Tag color="default">待处理</Tag>
      }
    },
    {
      title: '错误信息',
      dataIndex: 'error',
      key: 'error',
      ellipsis: true,
      render: (error?: string) => error || '-'
    }
  ]

  const downloadTemplate = () => {
    const template = importType === 'data_element' ? [
      { '名称': '示例数据要素', '类型': '文本', '描述': '这是一个示例数据要素' }
    ] : [
      { '名称': '示例资源', '类型': '图片', 'URL': 'https://example.com/image.jpg', '描述': '这是一个示例资源' }
    ]

    const ws = XLSX.utils.json_to_sheet(template)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    XLSX.writeFile(wb, `${importType}_template.xlsx`)
  }

  return (
    <div className="batch-import">
      <Card title="批量导入">
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Form layout="inline">
            <Form.Item label="导入类型">
              <Select
                value={importType}
                onChange={setImportType}
                style={{ width: 200 }}
              >
                <Option value="data_element">数据要素</Option>
                <Option value="resource">资源</Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button onClick={downloadTemplate}>
                下载模板
              </Button>
            </Form.Item>
          </Form>

          <Dragger
            fileList={uploadFiles}
            onChange={handleFileChange}
            beforeUpload={() => false}
            accept=".xlsx,.xls,.csv"
            multiple={false}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持 Excel (.xlsx, .xls) 或 CSV 文件
            </p>
          </Dragger>

          <Space>
            <Button type="primary" icon={<UploadOutlined />} onClick={handlePreview} disabled={uploadFiles.length === 0}>
              预览数据
            </Button>
            <Button onClick={() => { setUploadFiles([]); setImportItems([]) }}>
              清空
            </Button>
          </Space>

          {importing && (
            <Card>
              <div style={{ marginBottom: 16 }}>
                <Progress percent={progress} status="active" />
              </div>
              <div>正在导入数据...</div>
            </Card>
          )}

          {importItems.length > 0 && (
            <Card title={`导入结果 (${importItems.length} 条)`}>
              <Table
                columns={columns}
                dataSource={importItems}
                rowKey="id"
                pagination={{
                  pageSize: 20,
                  showSizeChanger: true
                }}
              />
            </Card>
          )}
        </Space>
      </Card>

      <Modal
        title="数据预览"
        open={previewModalVisible}
        onOk={() => { setPreviewModalVisible(false) }}
        onCancel={() => setPreviewModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setPreviewModalVisible(false)}>
            取消
          </Button>,
          <Button key="import" type="primary" onClick={() => { setPreviewModalVisible(false); handleImport() }}>
            开始导入
          </Button>
        ]}
      >
        <Table
          columns={columns}
          dataSource={importItems}
          rowKey="id"
          pagination={false}
          scroll={{ y: 400 }}
        />
      </Modal>
    </div>
  )
}

export default BatchImport
