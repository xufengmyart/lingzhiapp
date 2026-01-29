import { useState } from 'react'
import { useChat } from '../contexts/ChatContext'
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react'

/**
 * 对话功能测试页面
 * 用于验证对话功能是否正常工作
 */
const ChatTest = () => {
  const { messages, loading, sendMessage, clearChat } = useChat()
  const [testResults, setTestResults] = useState<Array<{
    test: string
    status: 'pending' | 'success' | 'error'
    message: string
  }>>([])

  const runTest = async (testName: string, testFn: () => Promise<void>) => {
    setTestResults((prev) => [...prev, { test: testName, status: 'pending', message: '运行中...' }])

    try {
      await testFn()
      setTestResults((prev) =>
        prev.map((r) =>
          r.test === testName
            ? { ...r, status: 'success', message: '通过' }
            : r
        )
      )
    } catch (error: any) {
      setTestResults((prev) =>
        prev.map((r) =>
          r.test === testName
            ? { ...r, status: 'error', message: error.message || '失败' }
            : r
        )
      )
    }
  }

  const runAllTests = async () => {
    setTestResults([])

    // 测试1：发送简单消息
    await runTest('发送简单消息', async () => {
      await sendMessage('你好')
      await new Promise((resolve) => setTimeout(resolve, 1500))
      if (messages.length < 2) throw new Error('未收到回复')
    })

    // 测试2：发送空消息（应该被阻止）
    await runTest('空消息处理', async () => {
      try {
        await sendMessage('')
      } catch (error) {
        throw new Error('空消息应该被阻止')
      }
    })

    // 测试3：连续发送消息
    await runTest('连续发送消息', async () => {
      await sendMessage('测试消息1')
      await new Promise((resolve) => setTimeout(resolve, 1500))
      await sendMessage('测试消息2')
      await new Promise((resolve) => setTimeout(resolve, 1500))
    })

    // 测试4：清除对话
    await runTest('清除对话', async () => {
      clearChat()
      await new Promise((resolve) => setTimeout(resolve, 500))
    })
  }

  const resetTests = () => {
    setTestResults([])
    clearChat()
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">对话功能测试</h1>
        <p className="text-gray-600 mt-2">验证对话功能是否正常工作</p>
      </div>

      {/* 测试控制面板 */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">测试控制</h2>
          <div className="space-x-2">
            <button
              onClick={runAllTests}
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>运行全部测试</span>
            </button>
            <button
              onClick={resetTests}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
            >
              重置
            </button>
          </div>
        </div>

        {/* 测试结果 */}
        <div className="space-y-3">
          {testResults.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              点击"运行全部测试"开始测试
            </div>
          ) : (
            testResults.map((result, index) => (
              <div
                key={index}
                className={`flex items-center space-x-3 p-4 rounded-lg ${
                  result.status === 'success'
                    ? 'bg-green-50'
                    : result.status === 'error'
                    ? 'bg-red-50'
                    : 'bg-yellow-50'
                }`}
              >
                {result.status === 'success' ? (
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                ) : result.status === 'error' ? (
                  <XCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
                ) : (
                  <RefreshCw className="w-6 h-6 text-yellow-500 flex-shrink-0 animate-spin" />
                )}
                <div className="flex-1">
                  <div className="font-medium">{result.test}</div>
                  <div className="text-sm text-gray-600">{result.message}</div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  result.status === 'success'
                    ? 'bg-green-100 text-green-700'
                    : result.status === 'error'
                    ? 'bg-red-100 text-red-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {result.status === 'success' ? '通过' : result.status === 'error' ? '失败' : '运行中'}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 实时对话测试 */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h2 className="text-xl font-semibold mb-4">实时对话测试</h2>
        <p className="text-gray-600 mb-4">在下方输入消息，测试对话功能是否正常：</p>

        <div className="space-y-4">
          <input
            type="text"
            placeholder="输入测试消息..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.currentTarget.value.trim() && !loading) {
                sendMessage(e.currentTarget.value.trim())
                e.currentTarget.value = ''
              }
            }}
          />

          <div className="text-sm text-gray-600">
            <p>当前对话轮数: {messages.length}</p>
            <p>会话ID: {messages.length > 0 ? '已创建' : '未创建'}</p>
          </div>
        </div>
      </div>

      {/* 诊断信息 */}
      <div className="bg-blue-50 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4 text-blue-900">诊断信息</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Mock API:</span>
            <span className="font-medium text-green-600">✅ 已启用</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">当前状态:</span>
            <span className={`font-medium ${loading ? 'text-yellow-600' : 'text-green-600'}`}>
              {loading ? '🔄 加载中' : '✅ 空闲'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">消息数量:</span>
            <span className="font-medium">{messages.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">错误日志:</span>
            <span className="font-medium">查看浏览器控制台 (F12)</span>
          </div>
        </div>
      </div>

      {/* 帮助信息 */}
      <div className="bg-gray-50 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">需要帮助？</h2>
        <ul className="space-y-2 text-gray-600">
          <li>• 如果测试失败，请查看 <a href="/TIMEOUT_FIX.md" className="text-primary-600 hover:underline">超时问题排查指南</a></li>
          <li>• 查看浏览器控制台 (F12) 获取详细错误信息</li>
          <li>• 尝试清除浏览器缓存后重试</li>
          <li>• 使用无痕模式测试</li>
        </ul>
      </div>
    </div>
  )
}

export default ChatTest
