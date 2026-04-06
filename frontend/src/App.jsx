import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Film, TrendingUp, Heart, BarChart3, LogIn, LogOut, User } from 'lucide-react'
import Home from './pages/Home'
import Recommendations from './pages/Recommendations'
import Watchlist from './pages/Watchlist'
import Statistics from './pages/Statistics'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Documentation from './pages/Documentation'
import { WatchlistProvider } from './context/WatchlistContext'
import { AuthProvider, useAuth } from './context/AuthContext'
import ParticlesBackground from './components/ParticlesBackground'

function AppContent() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen relative overflow-hidden">
      <ParticlesBackground />
      <div className="relative z-10">
      {/* Navigation */}
      <nav className="bg-gray-900/70 backdrop-blur-xl border-b border-gray-800/50 sticky top-0 z-50 shadow-lg shadow-black/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center space-x-2 group">
              <Film className="h-8 w-8 text-red-500 group-hover:text-red-400 transition-colors" />
              <span className="text-xl font-bold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent">
                Movie Recommender
              </span>
            </Link>
            
            <div className="flex items-center space-x-1">
              <NavLink to="/" icon={<TrendingUp className="h-5 w-5" />}>
                Popular
              </NavLink>
              <NavLink to="/recommendations" icon={<Film className="h-5 w-5" />}>
                Recommendations
              </NavLink>
              <NavLink to="/watchlist" icon={<Heart className="h-5 w-5" />}>
                Watchlist
              </NavLink>
              <NavLink to="/statistics" icon={<BarChart3 className="h-5 w-5" />}>
                Statistics
              </NavLink>
              
              {/* Auth Section */}
              <div className="ml-4 border-l border-gray-700 pl-4 flex items-center space-x-2">
                {user ? (
                  <>
                    <div className="flex items-center space-x-2 px-3 py-2 text-gray-300">
                      <User className="h-4 w-4" />
                      <span className="text-sm hidden sm:inline">{user.username}</span>
                    </div>
                    <button
                      onClick={logout}
                      className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition-all duration-200"
                    >
                      <LogOut className="h-5 w-5" />
                      <span className="text-sm hidden sm:inline">Logout</span>
                    </button>
                  </>
                ) : (
                  <NavLink to="/login" icon={<LogIn className="h-5 w-5" />}>
                    Login
                  </NavLink>
                )}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/docs" element={<Documentation />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900/70 backdrop-blur-xl border-t border-gray-800/50 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-400">
            Made with ❤️ using FastAPI, React, OAuth, and Machine Learning
          </p>
        </div>
      </footer>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <WatchlistProvider>
        <Router>
          <AppContent />
        </Router>
      </WatchlistProvider>
    </AuthProvider>
  )
}

function NavLink({ to, icon, children }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition-all duration-200"
    >
      {icon}
      <span className="hidden sm:inline">{children}</span>
    </Link>
  )
}

export default App

