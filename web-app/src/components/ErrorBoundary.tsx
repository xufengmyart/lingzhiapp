import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertCircle, RefreshCw, Home } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  }

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
    // 清除可能损坏的认证信息
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // 刷新页面
    window.location.href = '/'
  }

  private handleGoHome = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
    window.location.href = '/'
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-b from-[#0A0D18] via-[#121A2F] to-[#0A0D18] flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-[#121A2F] border border-red-500/30 rounded-2xl p-8 shadow-2xl">
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mb-6">
                <AlertCircle className="w-10 h-10 text-red-500" />
              </div>

              <h1 className="text-2xl font-bold text-white mb-3">
                页面出错了
              </h1>

              <p className="text-[#B4C7E7] text-sm mb-6">
                很抱歉，页面遇到了一些问题。您可以尝试刷新页面或返回首页。
              </p>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="w-full bg-[#0A0D18] rounded-lg p-4 mb-6 text-left overflow-auto max-h-40">
                  <p className="text-red-400 text-xs font-mono break-words">
                    {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo && (
                    <p className="text-[#B4C7E7] text-xs font-mono mt-2 break-words">
                      {this.state.errorInfo.componentStack}
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-3 w-full">
                <button
                  onClick={this.handleReset}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-500/30 transition-all font-medium"
                >
                  <RefreshCw className="w-4 h-4" />
                  刷新页面
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-[#00C3FF]/20 border border-[#00C3FF]/30 text-[#00C3FF] rounded-lg hover:bg-[#00C3FF]/30 transition-all font-medium"
                >
                  <Home className="w-4 h-4" />
                  返回首页
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
