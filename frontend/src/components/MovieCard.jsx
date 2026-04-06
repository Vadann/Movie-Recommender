import { useState, useEffect } from 'react'
import { Heart, Star, Info } from 'lucide-react'
import { useWatchlist } from '../context/WatchlistContext'
import { movieAPI } from '../services/api'

export default function MovieCard({ movie, showDetails = false }) {
  const { addToWatchlist, removeFromWatchlist, isInWatchlist } = useWatchlist()
  const [posterUrl, setPosterUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const inWatchlist = isInWatchlist(movie.movie_id)

  useEffect(() => {
    const fetchPoster = async () => {
      try {
        const url = await movieAPI.getMoviePoster(movie.movie_id)
        setPosterUrl(url)
      } catch (error) {
        console.error('Error fetching poster:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPoster()
  }, [movie.movie_id])

  const handleWatchlistToggle = async (e) => {
    e.stopPropagation()
    if (inWatchlist) {
      await removeFromWatchlist(movie.movie_id)
    } else {
      // Format movie data properly for backend
      const movieData = {
        movie_id: movie.movie_id,
        title: movie.title,
        genres: movie.genres || [],
        vote_average: movie.vote_average,
        runtime: movie.runtime,
        overview: movie.overview
      }
      await addToWatchlist(movieData)
    }
  }

  return (
    <div className="card group relative">
      {/* Poster */}
      <div className="relative aspect-[2/3] bg-gray-700 overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="loader"></div>
          </div>
        ) : posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            <Info className="h-12 w-12" />
          </div>
        )}

        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="absolute bottom-0 left-0 right-0 p-4">
            {showDetails && movie.overview && (
              <p className="text-sm text-gray-300 line-clamp-3 mb-2">
                {movie.overview}
              </p>
            )}
            {movie.genres && (
              <div className="flex flex-wrap gap-1">
                {movie.genres.slice(0, 3).map((genre, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-red-600/80 px-2 py-1 rounded-full"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Watchlist button */}
        <button
          onClick={handleWatchlistToggle}
          className={`absolute top-2 right-2 p-2 rounded-full backdrop-blur-sm transition-all duration-200 ${
            inWatchlist
              ? 'bg-red-600 text-white'
              : 'bg-black/50 text-white hover:bg-red-600'
          }`}
        >
          <Heart
            className="h-5 w-5"
            fill={inWatchlist ? 'currentColor' : 'none'}
          />
        </button>
      </div>

      {/* Movie Info */}
      <div className="p-4">
        <h3 className="font-semibold text-white line-clamp-1 mb-2">
          {movie.title}
        </h3>

        {movie.vote_average && (
          <div className="flex items-center space-x-1 text-yellow-400">
            <Star className="h-4 w-4 fill-current" />
            <span className="text-sm font-medium">
              {movie.vote_average.toFixed(1)}
            </span>
          </div>
        )}

        {movie.runtime && (
          <p className="text-sm text-gray-400 mt-1">
            {Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m
          </p>
        )}
      </div>
    </div>
  )
}

