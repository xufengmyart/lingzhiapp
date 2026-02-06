import { Outlet } from 'react-router-dom'
import Navigation from './Navigation'

const Layout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#2a4559] via-[#3e8bb6]/40 to-[#2a4559]">
      <Navigation />
      <main className="container mx-auto px-4 py-8 max-w-7xl pt-20">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
