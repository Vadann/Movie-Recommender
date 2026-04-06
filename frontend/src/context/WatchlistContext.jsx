import { createContext, useContext, useState, useEffect } from 'react'
import { useAuth } from './AuthContext'
import axios from 'axios'
import authAPI from '../services/authAPI'

const WatchlistContext = createContext()

export function useWatchlist() {
  const context = useContext(WatchlistContext)
  if (!context) {
    throw new Error('useWatchlist must be used within WatchlistProvider')
  }
  return context
}

export function WatchlistProvider({ children }) {
  const [watchlist, setWatchlist] = useState([])
  const [loading, setLoading] = useState(false)
  const { user, isAuthenticated } = useAuth()

  // Load watchlist when user logs in or on mount
  useEffect(() => {
    console.log('🔄 Watchlist effect triggered, isAuthenticated:', isAuthenticated)
    if (isAuthenticated && user) {
      console.log('🔐 User is authenticated, loading watchlist...')
      loadWatchlist()
    } else {
      console.log('📦 Not authenticated, using localStorage')
      // If not logged in, use localStorage as fallback
      const saved = localStorage.getItem('watchlist')
      setWatchlist(saved ? JSON.parse(saved) : [])
    }
  }, [isAuthenticated, user])

  const loadWatchlist = async () => {
    if (!isAuthenticated) {
      console.log('⚠️ Not authenticated, cannot load watchlist')
      return
    }

    try {
      setLoading(true)
      const token = authAPI.getAccessToken()
      
      console.log('📡 Fetching watchlist from backend...')
      const response = await axios.get('http://localhost:8000/api/user/watchlist', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      console.log('✅ Watchlist loaded:', response.data)
      console.log('📊 Number of items:', response.data.length)
      
      setWatchlist(response.data)
    } catch (error) {
      console.error('❌ Error loading watchlist:', error)
      console.error('Error response:', error.response?.data)
      
      if (error.response?.status === 401) {
        console.log('🔓 Token expired, clearing auth')
        // Token might be expired
        authAPI.logout()
      } else {
        // Fallback to localStorage
        const saved = localStorage.getItem('watchlist')
        setWatchlist(saved ? JSON.parse(saved) : [])
      }
    } finally {
      setLoading(false)
    }
  }

  const addToWatchlist = async (movie) => {
    // If not authenticated, use localStorage
    if (!isAuthenticated) {
      const newWatchlist = [...watchlist]
      if (!newWatchlist.find(m => m.movie_id === movie.movie_id)) {
        newWatchlist.push(movie)
        setWatchlist(newWatchlist)
        localStorage.setItem('watchlist', JSON.stringify(newWatchlist))
      }
      return
    }

    // If authenticated, save to backend
    try {
      const token = authAPI.getAccessToken()
      
      // Format the data properly
      const watchlistData = {
        movie_id: movie.movie_id,
        movie_title: movie.title || movie.movie_title,
        genres: Array.isArray(movie.genres) ? movie.genres : [],
        vote_average: movie.vote_average || null,
        runtime: movie.runtime || null
      }
      
      console.log('🎬 Adding to watchlist:', watchlistData)
      
      const response = await axios.post('http://localhost:8000/api/user/watchlist', watchlistData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      console.log('✅ Added successfully:', response.data)
      
      // Reload watchlist from backend
      await loadWatchlist()
    } catch (error) {
      console.error('❌ Error adding to watchlist:', error)
      console.error('Error response:', error.response?.data)
      
      if (error.response?.status === 401) {
        alert('Please login to save to your watchlist')
      } else if (error.response?.status === 400) {
        const detail = error.response.data?.detail
        if (detail === "Movie already in watchlist") {
          console.log('Movie already in watchlist, ignoring...')
          // Just reload to sync state
          await loadWatchlist()
        } else {
          alert(`Error: ${detail || 'Could not add to watchlist'}`)
        }
      } else {
        alert('Failed to add to watchlist. Please try again.')
      }
    }
  }

  const removeFromWatchlist = async (movieId) => {
    // If not authenticated, use localStorage
    if (!isAuthenticated) {
      const newWatchlist = watchlist.filter(m => m.movie_id !== movieId)
      setWatchlist(newWatchlist)
      localStorage.setItem('watchlist', JSON.stringify(newWatchlist))
      return
    }

    // If authenticated, remove from backend
    try {
      const token = authAPI.getAccessToken()
      await axios.delete(`http://localhost:8000/api/user/watchlist/${movieId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      // Reload watchlist from backend
      await loadWatchlist()
    } catch (error) {
      console.error('Error removing from watchlist:', error)
    }
  }

  const isInWatchlist = (movieId) => {
    return watchlist.some(m => m.movie_id === movieId)
  }

  const clearWatchlist = async () => {
    if (!isAuthenticated) {
      setWatchlist([])
      localStorage.removeItem('watchlist')
      return
    }

    // Clear all items from backend
    try {
      const token = authAPI.getAccessToken()
      for (const movie of watchlist) {
        await axios.delete(`http://localhost:8000/api/user/watchlist/${movie.movie_id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
      }
      setWatchlist([])
    } catch (error) {
      console.error('Error clearing watchlist:', error)
    }
  }

  return (
    <WatchlistContext.Provider
      value={{
        watchlist,
        addToWatchlist,
        removeFromWatchlist,
        isInWatchlist,
        clearWatchlist,
        loading,
      }}
    >
      {children}
    </WatchlistContext.Provider>
  )
}
