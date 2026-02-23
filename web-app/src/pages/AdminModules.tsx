import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const AdminModules = () => {
  const navigate = useNavigate()

  useEffect(() => {
    // 重定向到后台首页（仪表盘）
    navigate('/admin', { replace: true })
  }, [navigate])

  return null
}

export default AdminModules
