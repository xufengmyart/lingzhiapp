import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import AdminLogin from './pages/AdminLogin'
import ForgotPassword from './pages/ForgotPassword'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import ChatTest from './pages/ChatTest'
import Economy from './pages/Economy'
import Partner from './pages/Partner'
import Profile from './pages/Profile'
import UserGuide from './pages/UserGuide'
import MediumVideoProject from './pages/MediumVideoProject'
import XianAesthetics from './pages/XianAesthetics'
import AdminDashboard from './pages/AdminDashboard'
import AgentManagement from './pages/AgentManagement'
import KnowledgeManagement from './pages/KnowledgeManagement'
import UserManagement from './pages/UserManagement'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/admin/forgot-password" element={<ForgotPassword />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat-test" element={<ChatTest />} />
          <Route path="/economy" element={<Economy />} />
          <Route path="/partner" element={<Partner />} />
          <Route path="/guide" element={<UserGuide />} />
          <Route path="/medium-video" element={<MediumVideoProject />} />
          <Route path="/xian-aesthetics" element={<XianAesthetics />} />
          <Route path="/profile" element={<Profile />} />
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
