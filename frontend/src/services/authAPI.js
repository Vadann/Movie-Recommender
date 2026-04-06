import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/auth'

const authAPI = {
  // Sign up new user
  signup: async (email, username, password, fullName = null) => {
    const response = await axios.post(`${API_BASE_URL}/signup`, {
      email,
      username,
      password,
      full_name: fullName
    })
    return response.data
  },

  // Login
  login: async (email, password) => {
    const response = await axios.post(`${API_BASE_URL}/login`, {
      email,
      password
    })
    
    // Store tokens in localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
    }
    
    return response.data
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },

  // Get current user
  getCurrentUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) return null

    try {
      const response = await axios.get(`${API_BASE_URL}/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      // Cache user info
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        // Token expired, try to refresh
        return await authAPI.refreshToken()
      }
      throw error
    }
  },

  // Refresh access token
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      authAPI.logout()
      return null
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/refresh`, {
        refresh_token: refreshToken
      })
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      return await authAPI.getCurrentUser()
    } catch (error) {
      authAPI.logout()
      return null
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token')
  },

  // Get access token
  getAccessToken: () => {
    return localStorage.getItem('access_token')
  }
}

export default authAPI


