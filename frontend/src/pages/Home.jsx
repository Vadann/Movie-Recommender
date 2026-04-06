import { useState, useEffect } from 'react'
import { TrendingUp } from 'lucide-react'
import MovieCard from '../components/MovieCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { movieAPI } from '../services/api'

export default function Home() {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPopularMovies()
  }, [])

  const fetchPopularMovies = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await movieAPI.getPopularMovies(20)
      setMovies(data.movies)
    } catch (err) {
      setError('Failed to load popular movies. Please try again later.')
      console.error('Error fetching popular movies:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-red-500 via-pink-500 to-purple-500 bg-clip-text text-transparent">
          Discover Your Next Favorite Movie
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          AI-powered recommendations based on content similarity and your preferences
        </p>
      </div>

      {/* Popular Movies Section */}
      <div className="mb-8">
        <div className="flex items-center space-x-2 mb-6">
          <TrendingUp className="h-6 w-6 text-red-500" />
          <h2 className="section-title mb-0">Popular Movies</h2>
        </div>

        {loading ? (
          <LoadingSpinner message="Loading popular movies..." />
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button onClick={fetchPopularMovies} className="btn-primary">
              Try Again
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {movies.map((movie) => (
              <MovieCard
                key={movie.id || movie.movie_id}
                movie={{
                  movie_id: movie.id || movie.movie_id,
                  title: movie.title,
                  overview: movie.overview,
                  genres: movie.genres || [],
                  vote_average: movie.vote_average,
                  poster_path: movie.poster_path,
                }}
                showDetails
              />
            ))}
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="mt-16 grid md:grid-cols-3 gap-8">
        <FeatureCard
          title="Content-Based Filtering"
          description="Get recommendations based on movie features like genre, cast, director, and plot."
          icon="🎬"
        />
        <FeatureCard
          title="Mood-Based Discovery"
          description="Find movies that match your current mood, from happy comedies to thrilling adventures."
          icon="🎭"
        />
        <FeatureCard
          title="Personal Watchlist"
          description="Save movies to your watchlist and get insights about your preferences."
          icon="❤️"
        />
      </div>
    </div>
  )
}

function FeatureCard({ title, description, icon }) {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-red-500 transition-all duration-300">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}


