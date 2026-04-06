import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach auth token automatically when present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const movieAPI = {
  // Search for movies
  searchMovies: async (query, limit = 10) => {
    const response = await api.get('/movies/search', { params: { query, limit } })
    return response.data
  },

  // Get content-based recommendations
  getContentRecommendations: async (title, n_recommendations = 10) => {
    const response = await api.post('/recommendations/content-based', { title, n_recommendations })
    return response.data
  },

  // Get mood-based recommendations
  getMoodRecommendations: async (mood, n_recommendations = 5) => {
    const response = await api.post('/recommendations/mood-based', { mood, n_recommendations })
    return response.data
  },

  // Get personalized recommendations (requires auth)
  getPersonalizedRecommendations: async (n = 10) => {
    const response = await api.get('/user/recommendations/personalized', { params: { n } })
    return response.data
  },

  // Trigger NCF model re-training (requires auth)
  trainNcfModel: async () => {
    const response = await api.post('/user/recommendations/train-model')
    return response.data
  },

  // Rate a movie (requires auth)
  rateMovie: async (movieId, movieTitle, rating) => {
    const response = await api.post('/user/ratings', {
      movie_id: movieId,
      movie_title: movieTitle,
      rating,
      review: '',
    })
    return response.data
  },

  // Get the user's ratings (requires auth)
  getUserRatings: async () => {
    const response = await api.get('/user/ratings')
    return response.data
  },

  // Get popular movies
  getPopularMovies: async (limit = 20) => {
    const response = await api.get('/movies/popular', { params: { limit } })
    return response.data
  },

  // Get movie details
  getMovieDetails: async (movieId) => {
    const response = await api.get(`/movies/${movieId}`)
    return response.data
  },

  // Get movie poster
  getMoviePoster: async (movieId) => {
    try {
      const response = await api.get(`/movies/${movieId}/poster`)
      return response.data.poster_url
    } catch {
      return null
    }
  },

  // Get genre statistics (JSON)
  getGenreStatistics: async () => {
    const response = await api.get('/statistics/genres')
    return response.data
  },

  // Get available moods
  getAvailableMoods: async () => {
    const response = await api.get('/statistics/moods')
    return response.data
  },

  // Calculate watchlist stats
  getWatchlistStats: async (movieIds) => {
    const response = await api.post('/watchlist/stats', movieIds)
    return response.data
  },

  // Matplotlib chart URLs (fetched as <img src=...>)
  chartUrls: {
    genreRatings: `${API_BASE_URL}/statistics/chart/genres`,
    ratingsDistribution: `${API_BASE_URL}/statistics/chart/ratings`,
    watchlistGenres: `${API_BASE_URL}/user/chart/watchlist`,
  },
}

export default api


