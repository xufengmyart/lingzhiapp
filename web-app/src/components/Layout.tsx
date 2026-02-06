import { Outlet } from 'react-router-dom'
import Navigation from './Navigation'

const Layout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#091422] via-[#3e8bb6]/40 to-[#091422]">
      <Navigation />
      <main className="container mx-auto px-4 py-8 max-w-7xl pt-20">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
