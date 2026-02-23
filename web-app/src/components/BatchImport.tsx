import { useState, useRef } from 'react'
import { Upload, FileSpreadsheet, X, Check, AlertCircle, Download, Loader2 } from 'lucide-react'

interface BatchImportProps {
  projectId: number
  importType: 'elements' | 'resources'
  onImportComplete: () => void
}

interface ImportError {
  row: number
  field: string
  message: string
}

interface ImportResult {
  total: number
  success: number
  failed: number
  errors: ImportError[]
}

/**
 * 批量导入组件
 * 支持Excel (.xlsx, .xls) 和 CSV 文件导入
 */
const BatchImport: React.FC<BatchImportProps> = ({
  projectId,
  importType,
  onImportComplete
}) => {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isParsing, setIsParsing] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [preview, setPreview] = useState<any[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
      setPreview([])
      
      // 解析文件预览
      parseFilePreview(selectedFile)
    }
  }

  const parseFilePreview = async (file: File) => {
    setIsParsing(true)
    try {
      const text = await file.text()
      
      if (file.name.endsWith('.csv')) {
        // CSV 文件解析
        const lines = text.split('\n').filter(line => line.trim())
        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim())
          const rows = lines.slice(1, 6).map(line => {
            const values = line.split(',').map(v => v.trim())
            const row: any = {}
            headers.forEach((header, index) => {
              row[header] = values[index] || ''
            })
            return row
          })
          setPreview(rows)
        }
      } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        // Excel文件需要使用库解析，这里只做简单提示
        setPreview([{ message: 'Excel文件预览需要上传到服务器' }])
      }
    } catch (error) {
      console.error('文件解析失败:', error)
      setPreview([{ error: '文件解析失败' }])
    } finally {
      setIsParsing(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('project_id', projectId.toString())
      formData.append('import_type', importType)

      const response = await fetch(`/api/v9/projects/${projectId}/batch-import`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setResult({
          total: data.data.total || 0,
          success: data.data.success || 0,
          failed: data.data.failed || 0,
          errors: data.data.errors || []
        })
        
        if (data.data.failed === 0) {
          setTimeout(() => {
            onImportComplete()
          }, 1500)
        }
      } else {
        setResult({
          total: 0,
          success: 0,
          failed: 1,
          errors: [{ row: 0, field: 'file', message: data.message || '上传失败' }]
        })
      }
    } catch (error) {
      console.error('上传失败:', error)
      setResult({
        total: 0,
        success: 0,
        failed: 1,
        errors: [{ row: 0, field: 'file', message: '网络错误' }]
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveFile = () => {
    setFile(null)
    setPreview([])
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const downloadTemplate = () => {
    const headers = importType === 'elements' 
      ? ['element_name', 'element_type', 'description', 'data_source', 'processing_method']
      : ['resource_name', 'resource_type', 'resource_url', 'element_id']
    
    const sampleRow = importType === 'elements'
      ? ['文化要素', 'text', '文化描述', '人工采集', '标准化处理']
      : ['文化资源', 'image', 'https://example.com/resource.jpg', '1']
    
    const csvContent = [
      headers.join(','),
      sampleRow.join(',')
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${importType}_template.csv`
    link.click()
  }

  return (
    <div className="space-y-6">
      {/* 下载模板 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-blue-900 mb-1">下载导入模板</h4>
            <p className="text-sm text-blue-700">
              请使用模板格式准备数据，避免导入错误
            </p>
          </div>
          <button
            onClick={downloadTemplate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            下载模板
          </button>
        </div>
      </div>

      {/* 文件上传区域 */}
      {!file ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          onDrop={(e) => {
            e.preventDefault()
            const droppedFile = e.dataTransfer.files[0]
            if (droppedFile) {
              handleFileSelect({ target: { files: [droppedFile] } } as any)
            }
          }}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-500 transition-colors cursor-pointer"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">
            点击上传或拖拽文件到此处
          </p>
          <p className="text-sm text-gray-400">
            支持 CSV、Excel (.xlsx, .xls) 格式
          </p>
        </div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <FileSpreadsheet className="w-8 h-8 text-green-500" />
              <div>
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              onClick={handleRemoveFile}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* 文件预览 */}
          {preview.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                数据预览 (前5行):
              </h4>
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {preview[0] && !preview[0].message && !preview[0].error && Object.keys(preview[0]).map((key) => (
                        <th key={key} className="px-4 py-2 text-left font-medium text-gray-700">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((row, index) => (
                      <tr key={index} className="border-t border-gray-200">
                        {row.message ? (
                          <td colSpan={100} className="px-4 py-2 text-gray-500">
                            {row.message}
                          </td>
                        ) : row.error ? (
                          <td colSpan={100} className="px-4 py-2 text-red-500">
                            {row.error}
                          </td>
                        ) : (
                          Object.values(row).map((value, cellIndex) => (
                            <td key={cellIndex} className="px-4 py-2 text-gray-900">
                              {String(value).substring(0, 50)}
                              {String(value).length > 50 && '...'}
                            </td>
                          ))
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 上传按钮 */}
          <div className="flex gap-3">
            <button
              onClick={handleUpload}
              disabled={isUploading || isParsing}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  上传中...
                </>
              ) : isParsing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  解析中...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  开始导入
                </>
              )}
            </button>
            <button
              onClick={handleRemoveFile}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      )}

      {/* 导入结果 */}
      {result && (
        <div className={`rounded-lg p-4 ${result.failed === 0 ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
          <div className="flex items-start gap-3">
            {result.failed === 0 ? (
              <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <h4 className={`font-medium mb-2 ${result.failed === 0 ? 'text-green-900' : 'text-yellow-900'}`}>
                {result.failed === 0 ? '导入成功' : '导入完成'}
              </h4>
              <div className="grid grid-cols-3 gap-4 text-sm mb-4">
                <div>
                  <p className="text-gray-600">总记录</p>
                  <p className="font-medium text-gray-900">{result.total}</p>
                </div>
                <div>
                  <p className="text-gray-600">成功</p>
                  <p className="font-medium text-green-600">{result.success}</p>
                </div>
                <div>
                  <p className="text-gray-600">失败</p>
                  <p className="font-medium text-red-600">{result.failed}</p>
                </div>
              </div>
              
              {result.errors.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">错误详情:</p>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {result.errors.map((error, index) => (
                      <div key={index} className="text-xs bg-white rounded px-3 py-2">
                        <span className="text-gray-600">行 {error.row}</span>: {error.field} - {error.message}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BatchImport
