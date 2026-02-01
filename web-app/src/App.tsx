import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import ChatTest from './pages/ChatTest'
import Economy from './pages/Economy'
import Partner from './pages/Partner'
import Profile from './pages/Profile'
import UserGuide from './pages/UserGuide'
import MediumVideoProject from './pages/MediumVideoProject'
import XianAesthetics from './pages/XianAesthetics'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

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
    </Routes>
  )
}

export default App
