import { createContext, useContext, useState, useEffect } from 'react'
import authAPI from '../services/authAPI'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      if (authAPI.isAuthenticated()) {
        const userData = await authAPI.getCurrentUser()
        setUser(userData)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      authAPI.logout()
    } finally {
      setLoading(false)
    }
  }

  const signup = async (email, username, password, fullName) => {
    const userData = await authAPI.signup(email, username, password, fullName)
    // After signup, auto-login
    await login(email, password)
    return userData
  }

  const login = async (email, password) => {
    const response = await authAPI.login(email, password)
    const userData = await authAPI.getCurrentUser()
    setUser(userData)
    return response
  }

  const logout = () => {
    authAPI.logout()
    setUser(null)
  }

  const value = {
    user,
    loading,
    signup,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}


