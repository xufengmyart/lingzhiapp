import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ProtectedRoute = () => {
  const { user, loading, authError } = useAuth()
  const location = useLocation()

  // 加载中显示加载状态
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  // 只有在完全没有用户数据时才重定向到登录页
  if (!user) {
    console.warn('[ProtectedRoute] 用户未登录，重定向到登录页')
    return <Navigate to="/" replace state={{ from: location }} />
  }

  // 如果有用户数据但存在认证错误，显示错误提示但允许继续使用
  if (authError) {
    console.warn('[ProtectedRoute] 认证错误:', authError)
    // 可以在这里添加一个错误提示组件
    return (
      <>
        <div className="bg-yellow-50 border-b border-yellow-200 text-yellow-800 px-4 py-2 text-sm text-center">
          ⚠️ {authError}
        </div>
        <Outlet />
      </>
    )
  }

  return <Outlet />
}

export default ProtectedRoute
