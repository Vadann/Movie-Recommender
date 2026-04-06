import { useState, useEffect, useCallback } from 'react'
import { Search, Sparkles, Heart, Star, UserCheck, RefreshCw } from 'lucide-react'
import MovieCard from '../components/MovieCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { movieAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

// ---------------------------------------------------------------------------
// Inline star-rating component
// ---------------------------------------------------------------------------
function RatingStars({ movieId, movieTitle, existingRating = 0, onRated }) {
  const [hovered, setHovered] = useState(0)
  const [rated, setRated] = useState(existingRating)
  const [saving, setSaving] = useState(false)

  const handleRate = async (stars) => {
    setSaving(true)
    try {
      // API expects rating 1-10; we collect 1-5 stars and multiply by 2
      await movieAPI.rateMovie(movieId, movieTitle, stars * 2)
      setRated(stars)
      onRated && onRated(movieId, stars)
    } catch (err) {
      console.error('Rating failed:', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex items-center space-x-1 mt-2">
      <span className="text-xs text-gray-400 mr-1">Rate:</span>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          disabled={saving}
          onClick={() => handleRate(star)}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(0)}
          className="focus:outline-none disabled:opacity-50"
          aria-label={`Rate ${star} stars`}
        >
          <Star
            className="h-4 w-4 transition-colors"
            fill={(hovered || rated) >= star ? '#facc15' : 'none'}
            stroke={(hovered || rated) >= star ? '#facc15' : '#6b7280'}
          />
        </button>
      ))}
      {rated > 0 && (
        <span className="text-xs text-yellow-400 ml-1">{rated}/5</span>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function Recommendations() {
  const { isAuthenticated } = useAuth()

  // Content-based state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedMovie, setSelectedMovie] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  // Mood-based state
  const [mood, setMood] = useState('happy')
  const [moodRecommendations, setMoodRecommendations] = useState([])
  const [availableMoods, setAvailableMoods] = useState([])
  const [moodLoading, setMoodLoading] = useState(false)

  // Personalized state
  const [personalizedRecs, setPersonalizedRecs] = useState([])
  const [personalizedMeta, setPersonalizedMeta] = useState(null)
  const [personalizedLoading, setPersonalizedLoading] = useState(false)
  const [userRatings, setUserRatings] = useState({}) // movieId → starCount
  const [trainingModel, setTrainingModel] = useState(false)

  useEffect(() => {
    fetchMoods()
    if (isAuthenticated) {
      fetchPersonalized()
      fetchExistingRatings()
    }
  }, [isAuthenticated])

  const fetchMoods = async () => {
    try {
      const data = await movieAPI.getAvailableMoods()
      setAvailableMoods(data.moods)
    } catch (err) {
      console.error('Error fetching moods:', err)
    }
  }

  const fetchPersonalized = async () => {
    try {
      setPersonalizedLoading(true)
      const data = await movieAPI.getPersonalizedRecommendations(10)
      setPersonalizedRecs(data.recommendations)
      setPersonalizedMeta(data)
    } catch (err) {
      console.error('Error fetching personalized recs:', err)
    } finally {
      setPersonalizedLoading(false)
    }
  }

  const fetchExistingRatings = async () => {
    try {
      const ratings = await movieAPI.getUserRatings()
      const map = {}
      ratings.forEach((r) => {
        map[r.movie_id] = Math.round(r.rating / 2) // stored as 1-10, display as 1-5
      })
      setUserRatings(map)
    } catch (err) {
      console.error('Error fetching ratings:', err)
    }
  }

  const handleRated = useCallback((movieId, stars) => {
    setUserRatings((prev) => ({ ...prev, [movieId]: stars }))
    // Refresh personalized recs after rating
    setTimeout(() => fetchPersonalized(), 500)
  }, [])

  const handleTrainModel = async () => {
    setTrainingModel(true)
    try {
      const result = await movieAPI.trainNcfModel()
      alert(result.message)
      if (result.trained) fetchPersonalized()
    } catch (err) {
      alert('Training failed. Check backend logs.')
    } finally {
      setTrainingModel(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    try {
      setLoading(true)
      const data = await movieAPI.searchMovies(searchQuery, 10)
      setSearchResults(data.results)
    } catch (err) {
      console.error('Error searching movies:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGetRecommendations = async (movie) => {
    try {
      setLoading(true)
      setSelectedMovie(movie)
      const data = await movieAPI.getContentRecommendations(movie.title, 10)
      setRecommendations(data.recommendations)
    } catch (err) {
      console.error('Error getting recommendations:', err)
      alert('Error getting recommendations. Please try another movie.')
    } finally {
      setLoading(false)
    }
  }

  const handleMoodRecommendations = async () => {
    try {
      setMoodLoading(true)
      const data = await movieAPI.getMoodRecommendations(mood, 10)
      setMoodRecommendations(data.recommendations)
    } catch (err) {
      console.error('Error getting mood recommendations:', err)
    } finally {
      setMoodLoading(false)
    }
  }

  const methodBadge = (method) => {
    const labels = {
      neural_collaborative_filtering: { text: 'Neural CF', color: 'text-purple-400 border-purple-600' },
      genre_weighted: { text: 'Genre-Weighted', color: 'text-blue-400 border-blue-600' },
      popular: { text: 'Trending', color: 'text-yellow-400 border-yellow-600' },
    }
    const m = labels[method] || { text: method, color: 'text-gray-400 border-gray-600' }
    return (
      <span className={`text-xs border rounded-full px-2 py-0.5 ml-2 ${m.color}`}>
        {m.text}
      </span>
    )
  }

  return (
    <div className="animate-fade-in space-y-16">

      {isAuthenticated && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <UserCheck className="h-6 w-6 text-purple-500" />
              <h2 className="section-title mb-0">For You</h2>
              {personalizedMeta && methodBadge(personalizedMeta.method)}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={fetchPersonalized}
                disabled={personalizedLoading}
                className="btn-secondary flex items-center space-x-1 text-sm"
              >
                <RefreshCw className={`h-4 w-4 ${personalizedLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              <button
                onClick={handleTrainModel}
                disabled={trainingModel}
                className="btn-secondary text-sm"
                title="Re-train the Neural CF model with all current ratings"
              >
                {trainingModel ? 'Training…' : 'Train NCF Model'}
              </button>
            </div>
          </div>

          {personalizedMeta && (
            <p className="text-sm text-gray-400 mb-4">
              {personalizedMeta.message}
              {personalizedMeta.rating_count === 0 && (
                <span> — Rate movies below to build your preference profile.</span>
              )}
            </p>
          )}

          {personalizedLoading ? (
            <LoadingSpinner message="Building your recommendations…" />
          ) : personalizedRecs.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {personalizedRecs.map((movie) => (
                <div key={movie.movie_id} className="flex flex-col">
                  <MovieCard movie={movie} showDetails />
                  <RatingStars
                    movieId={movie.movie_id}
                    movieTitle={movie.title}
                    existingRating={userRatings[movie.movie_id] || 0}
                    onRated={handleRated}
                  />
                </div>
              ))}
            </div>
          ) : null}
        </section>
      )}

      <section>
        <div className="flex items-center space-x-2 mb-6">
          <Sparkles className="h-6 w-6 text-red-500" />
          <h2 className="section-title mb-0">Similar Movies</h2>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search for a movie…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="input-field pl-10"
              />
            </div>
            <button onClick={handleSearch} className="btn-primary">
              Search
            </button>
          </div>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4">Search Results</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {searchResults.map((movie) => (
                <button
                  key={movie.movie_id}
                  onClick={() => handleGetRecommendations(movie)}
                  className="text-left bg-gray-800 hover:bg-gray-700 p-4 rounded-lg transition-all"
                >
                  <h4 className="font-semibold line-clamp-2">{movie.title}</h4>
                  {movie.vote_average && (
                    <p className="text-sm text-yellow-400 mt-1">
                      ⭐ {movie.vote_average.toFixed(1)}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {movie.genres.slice(0, 2).join(', ')}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {loading ? (
          <LoadingSpinner message="Finding perfect recommendations…" />
        ) : recommendations.length > 0 ? (
          <div>
            <h3 className="text-2xl font-semibold mb-4">
              Because you liked{' '}
              <span className="text-red-500">{selectedMovie?.title}</span>
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {recommendations.map((movie) => (
                <div key={movie.movie_id} className="flex flex-col">
                  <MovieCard movie={movie} showDetails />
                  {isAuthenticated && (
                    <RatingStars
                      movieId={movie.movie_id}
                      movieTitle={movie.title}
                      existingRating={userRatings[movie.movie_id] || 0}
                      onRated={handleRated}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="pt-8 border-t border-gray-800">
        <div className="flex items-center space-x-2 mb-6">
          <Heart className="h-6 w-6 text-pink-500" />
          <h2 className="section-title mb-0">Mood-Based Discovery</h2>
        </div>

        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
            <select
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              className="input-field"
            >
              {availableMoods.map((m) => (
                <option key={m} value={m}>
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </option>
              ))}
            </select>
            <button onClick={handleMoodRecommendations} className="btn-primary">
              Get Recommendations
            </button>
          </div>
        </div>

        {moodLoading ? (
          <LoadingSpinner message="Finding movies for your mood…" />
        ) : moodRecommendations.length > 0 ? (
          <div>
            <h3 className="text-xl font-semibold mb-4 capitalize">
              Perfect for when you're feeling {mood}
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {moodRecommendations.map((movie) => (
                <div key={movie.movie_id} className="flex flex-col">
                  <MovieCard movie={movie} showDetails />
                  {isAuthenticated && (
                    <RatingStars
                      movieId={movie.movie_id}
                      movieTitle={movie.title}
                      existingRating={userRatings[movie.movie_id] || 0}
                      onRated={handleRated}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    </div>
  )
}
