import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ProtectedRoute = () => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}

export default ProtectedRoute
