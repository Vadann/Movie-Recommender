import { useState, useEffect } from 'react'
import { BarChart3 } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { movieAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Statistics() {
  const [genreStats, setGenreStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const { isAuthenticated } = useAuth()

  // Chart image URLs — the browser fetches these as regular <img> requests.
  // The backend generates them server-side with matplotlib and returns PNG bytes.
  const genreChartUrl = movieAPI.chartUrls.genreRatings
  const ratingsChartUrl = movieAPI.chartUrls.ratingsDistribution
  const watchlistChartUrl = movieAPI.chartUrls.watchlistGenres

  useEffect(() => {
    fetchStatistics()
  }, [])

  const fetchStatistics = async () => {
    try {
      setLoading(true)
      const data = await movieAPI.getGenreStatistics()
      setGenreStats(data)
    } catch (err) {
      console.error('Error fetching statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Loading statistics..." />
  }

  const sortedGenres = Object.entries(genreStats.genre_stats).sort((a, b) => b[1] - a[1])

  return (
    <div className="animate-fade-in">
      <div className="flex items-center space-x-2 mb-8">
        <BarChart3 className="h-6 w-6 text-red-500" />
        <h2 className="section-title mb-0">Movie Statistics</h2>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-red-900/50 to-red-800/50 rounded-xl p-6 border border-red-700">
          <h3 className="text-gray-300 mb-2">Total Movies</h3>
          <p className="text-4xl font-bold">{genreStats.total_movies}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/50 rounded-xl p-6 border border-purple-700">
          <h3 className="text-gray-300 mb-2">Total Genres</h3>
          <p className="text-4xl font-bold">{Object.keys(genreStats.genre_stats).length}</p>
        </div>
        <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/50 rounded-xl p-6 border border-blue-700">
          <h3 className="text-gray-300 mb-2">Highest Rated Genre</h3>
          <p className="text-2xl font-bold">{sortedGenres[0][0]}</p>
          <p className="text-sm text-gray-400">⭐ {sortedGenres[0][1].toFixed(1)} avg rating</p>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Matplotlib Charts (server-generated PNG images)                     */}
      {/* ------------------------------------------------------------------ */}
      <div className="space-y-8 mb-8">
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-1">Average Rating by Genre</h3>
          <p className="text-sm text-gray-400 mb-4">
            Generated server-side with <code className="text-pink-400">matplotlib</code> from the TMDB 5000 dataset.
          </p>
          <img
            src={genreChartUrl}
            alt="Average rating per genre bar chart"
            className="w-full rounded-lg"
            onError={(e) => { e.target.style.display = 'none' }}
          />
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-1">Rating Distribution</h3>
          <p className="text-sm text-gray-400 mb-4">
            Histogram of <code className="text-pink-400">vote_average</code> across all{' '}
            {genreStats.total_movies} movies — generated with{' '}
            <code className="text-pink-400">matplotlib</code>.
          </p>
          <img
            src={ratingsChartUrl}
            alt="Movie rating distribution histogram"
            className="w-full rounded-lg"
            onError={(e) => { e.target.style.display = 'none' }}
          />
        </div>

        {/* Watchlist chart — only shown when authenticated */}
        {isAuthenticated && (
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-semibold mb-1">Your Watchlist Genres</h3>
            <p className="text-sm text-gray-400 mb-4">
              Personalised pie chart of your watchlist genre distribution, generated with{' '}
              <code className="text-pink-400">matplotlib</code>.
            </p>
            <div className="flex justify-center">
              <img
                src={`${watchlistChartUrl}?t=${Date.now()}`}
                alt="Watchlist genre pie chart"
                className="max-w-md w-full rounded-lg"
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Dataset info */}
      <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">About the Dataset</h3>
        <p className="text-gray-400 leading-relaxed">
          This recommender uses the TMDB 5000 Movie Dataset ({genreStats.total_movies} movies).
          Content-based filtering is computed with TF-IDF vectorisation and cosine similarity
          (scikit-learn). Personalized recommendations layer on top via Neural Collaborative
          Filtering (TensorFlow) trained on your rating history.
        </p>
      </div>
    </div>
  )
}
