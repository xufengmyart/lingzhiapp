import { Outlet } from 'react-router-dom'
import Navigation from './Navigation'

const Layout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0D18] via-[#121A2F]/40 to-[#0A0D18]">
      <Navigation />
      <main className="container mx-auto px-4 py-8 max-w-7xl pt-20">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
