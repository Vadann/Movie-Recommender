import { useState, useEffect } from 'react'
import { Heart, Trash2, Clock, LogIn } from 'lucide-react'
import { Link } from 'react-router-dom'
import MovieCard from '../components/MovieCard'
import { useWatchlist } from '../context/WatchlistContext'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import authAPI from '../services/authAPI'

export default function Watchlist() {
  const { watchlist, clearWatchlist, loading } = useWatchlist()
  const { isAuthenticated } = useAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    if (watchlist.length > 0 && isAuthenticated) {
      fetchStats()
    } else if (watchlist.length > 0) {
      // Calculate stats locally for non-authenticated users
      calculateLocalStats()
    }
  }, [watchlist, isAuthenticated])

  const fetchStats = async () => {
    try {
      const token = authAPI.getAccessToken()
      const response = await axios.get('http://localhost:8000/api/user/watchlist/stats', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      setStats(response.data)
    } catch (err) {
      console.error('Error fetching watchlist stats:', err)
      calculateLocalStats()
    }
  }

  const calculateLocalStats = () => {
    const total_runtime = watchlist.reduce((sum, m) => sum + (m.runtime || 0), 0)
    const ratings = watchlist.filter(m => m.vote_average).map(m => m.vote_average)
    const average_rating = ratings.length > 0 ? ratings.reduce((a, b) => a + b) / ratings.length : 0
    
    const genre_dist = {}
    watchlist.forEach(m => {
      if (m.genres) {
        m.genres.forEach(genre => {
          genre_dist[genre] = (genre_dist[genre] || 0) + 1
        })
      }
    })

    setStats({
      total_movies: watchlist.length,
      total_runtime,
      genre_distribution: genre_dist,
      average_rating: average_rating.toFixed(2)
    })
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-2">
          <Heart className="h-6 w-6 text-red-500" />
          <h2 className="section-title mb-0">Your Watchlist</h2>
        </div>
        {watchlist.length > 0 && (
          <button
            onClick={clearWatchlist}
            className="btn-secondary flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {!isAuthenticated && (
        <div className="mb-6 bg-blue-900/30 border border-blue-700 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <LogIn className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-blue-200 font-medium">Login to sync your watchlist</p>
              <p className="text-blue-300 text-sm">Your watchlist is currently saved locally. Login to save it to the cloud!</p>
            </div>
          </div>
          <Link to="/login" className="btn-primary inline-block mt-3">
            Login / Sign Up
          </Link>
        </div>
      )}

      {watchlist.length === 0 ? (
        <div className="text-center py-16">
          <Heart className="h-16 w-16 text-gray-700 mx-auto mb-4" />
          <h3 className="text-2xl font-semibold mb-2">Your watchlist is empty</h3>
          <p className="text-gray-400 mb-6">
            Start adding movies to keep track of what you want to watch!
          </p>
          <Link to="/recommendations" className="btn-primary inline-block">
            Discover Movies
          </Link>
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          {stats && (
            <div className="grid md:grid-cols-4 gap-4 mb-8">
              <StatCard
                label="Total Movies"
                value={stats.total_movies}
                icon="🎬"
              />
              <StatCard
                label="Total Runtime"
                value={`${Math.floor(stats.total_runtime / 60)}h ${stats.total_runtime % 60}m`}
                icon={<Clock className="h-6 w-6" />}
              />
              <StatCard
                label="Avg Rating"
                value={`${stats.average_rating}/10`}
                icon="⭐"
              />
              <StatCard
                label="Top Genre"
                value={Object.entries(stats.genre_distribution).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}
                icon="🎭"
              />
            </div>
          )}

          {/* Genre Distribution */}
          {stats && stats.genre_distribution && (
            <div className="bg-gray-800/50 rounded-xl p-6 mb-8">
              <h3 className="text-xl font-semibold mb-4">Genre Distribution</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {Object.entries(stats.genre_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .map(([genre, count]) => (
                    <div key={genre} className="bg-gray-700/50 rounded-lg p-3">
                      <p className="text-sm text-gray-400">{genre}</p>
                      <p className="text-2xl font-bold text-red-500">{count}</p>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Movies Grid */}
          {loading ? (
            <div className="text-center py-12">
              <div className="loader mx-auto mb-4"></div>
              <p className="text-gray-400">Loading your watchlist...</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {watchlist.map((movie) => {
                // Format movie data for MovieCard component
                const formattedMovie = {
                  movie_id: movie.movie_id,
                  title: movie.movie_title || movie.title,
                  genres: typeof movie.genres === 'string' 
                    ? movie.genres.split(',').map(g => g.trim()).filter(Boolean)
                    : (movie.genres || []),
                  vote_average: movie.vote_average,
                  runtime: movie.runtime,
                  overview: movie.overview
                }
                return (
                  <MovieCard key={movie.movie_id} movie={formattedMovie} showDetails />
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function StatCard({ label, value, icon }) {
  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{label}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  )
}

