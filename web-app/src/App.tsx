import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import LoginFull from './pages/LoginFull'
import Register from './pages/Register'
import RegisterFull from './pages/RegisterFull'
import DreamPageSelector from './pages/DreamPageSelector'
import AdminLogin from './pages/AdminLogin'
import ForgotPassword from './pages/ForgotPassword'
import DesignShowcase from './pages/DesignShowcase'
import ApiConfig from './pages/ApiConfig'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import ChatTest from './pages/ChatTest'
import Economy from './pages/Economy'
import Partner from './pages/Partner'
import Profile from './pages/Profile'
import SecuritySettings from './pages/SecuritySettings'
import UserGuide from './pages/UserGuide'
import MediumVideoProject from './pages/MediumVideoProject'
import XianAesthetics from './pages/XianAesthetics'
import CompleteProfile from './pages/CompleteProfile'
import WeChatCallback from './pages/WeChatCallback'
import Recharge from './pages/Recharge'
import AdminDashboard from './pages/AdminDashboard'
import AgentManagement from './pages/AgentManagement'
import KnowledgeManagement from './pages/KnowledgeManagement'
import UserManagement from './pages/UserManagement'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginFull />} />
      <Route path="/login" element={<Login />} />
      <Route path="/login-full" element={<LoginFull />} />
      <Route path="/register" element={<Register />} />
      <Route path="/register-full" element={<RegisterFull />} />
      <Route path="/dream-selector" element={<DreamPageSelector />} />
      <Route path="/api-config" element={<ApiConfig />} />
      <Route path="/design-showcase" element={<DesignShowcase />} />
      <Route path="/wechat/callback" element={<WeChatCallback />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/admin/forgot-password" element={<ForgotPassword />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat-test" element={<ChatTest />} />
          <Route path="/economy" element={<Economy />} />
          <Route path="/partner" element={<Partner />} />
          <Route path="/guide" element={<UserGuide />} />
          <Route path="/medium-video" element={<MediumVideoProject />} />
          <Route path="/xian-aesthetics" element={<XianAesthetics />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/security" element={<SecuritySettings />} />
          <Route path="/recharge" element={<Recharge />} />
          <Route path="/complete-profile" element={<CompleteProfile />} />
        </Route>
      </Route>

      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/users" element={<UserManagement />} />
      <Route path="/admin/agents" element={<AgentManagement />} />
      <Route path="/admin/knowledge" element={<KnowledgeManagement />} />
    </Routes>
  )
}

export default App
