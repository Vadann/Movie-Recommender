from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import (
    MovieRecommendationRequest,
    MoodRecommendationRequest,
    RecommendationResponse,
    PopularMoviesResponse,
    GenreStatsResponse,
    Movie
)
from app.ml.recommender import get_recommender

router = APIRouter()

@router.get("/movies/search")
async def search_movies(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for movies by title"""
    recommender = get_recommender()
    results = recommender.search_movies(query, limit)
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }

@router.post("/recommendations/content-based", response_model=RecommendationResponse)
async def get_content_recommendations(request: MovieRecommendationRequest):
    """Get content-based movie recommendations"""
    recommender = get_recommender()
    
    # Check if movie exists
    movie = recommender.get_movie_by_title(request.title)
    if movie is None:
        raise HTTPException(
            status_code=404,
            detail=f"Movie '{request.title}' not found. Please try searching first."
        )
    
    recommendations, scores = recommender.get_content_based_recommendations(
        request.title,
        request.n_recommendations
    )
    
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found"
        )
    
    return {
        "recommendations": recommendations,
        "similarity_scores": [float(score) for score in scores]
    }

@router.post("/recommendations/mood-based")
async def get_mood_recommendations(request: MoodRecommendationRequest):
    """Get mood-based movie recommendations"""
    recommender = get_recommender()
    
    recommendations = recommender.get_mood_based_recommendations(
        request.mood,
        request.n_recommendations
    )
    
    return {
        "mood": request.mood,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@router.get("/movies/popular")
async def get_popular_movies(limit: int = Query(20, ge=1, le=50)):
    """Get popular movies from TMDB or dataset"""
    recommender = get_recommender()
    
    # Try TMDB first, fallback to dataset
    movies = await recommender.fetch_tmdb_popular()
    
    if not movies:
        movies = recommender.get_popular_movies(limit)
    
    return {
        "movies": movies[:limit],
        "count": len(movies[:limit])
    }

@router.get("/movies/{movie_id}")
async def get_movie_details(movie_id: int):
    """Get detailed information about a specific movie"""
    recommender = get_recommender()
    
    movie_data = recommender.movies_df[recommender.movies_df['movie_id'] == movie_id]
    
    if movie_data.empty:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = movie_data.iloc[0]
    details = recommender._format_movie(movie)
    
    # Try to fetch poster
    poster_url = await recommender.fetch_tmdb_poster(movie_id)
    if poster_url:
        details['poster_url'] = poster_url
    
    return details

@router.get("/movies/{movie_id}/poster")
async def get_movie_poster(movie_id: int):
    """Get movie poster URL"""
    recommender = get_recommender()
    poster_url = await recommender.fetch_tmdb_poster(movie_id)
    
    if not poster_url:
        raise HTTPException(status_code=404, detail="Poster not found")
    
    return {"poster_url": poster_url}

@router.get("/statistics/genres", response_model=GenreStatsResponse)
async def get_genre_statistics():
    """Get statistical analysis of genres"""
    recommender = get_recommender()
    genre_stats = recommender.get_genre_statistics()
    
    return {
        "genre_stats": genre_stats,
        "total_movies": len(recommender.movies_df)
    }

@router.get("/statistics/moods")
async def get_available_moods():
    """Get list of available moods for recommendations"""
    recommender = get_recommender()
    
    return {
        "moods": list(recommender.mood_genres.keys()),
        "mood_genres": recommender.mood_genres
    }

@router.post("/watchlist/stats")
async def calculate_watchlist_stats(movie_ids: List[int]):
    """Calculate statistics for a watchlist"""
    recommender = get_recommender()
    
    movies = recommender.get_movies_by_ids(movie_ids)
    
    if not movies:
        return {
            "total_movies": 0,
            "total_runtime": 0,
            "genre_distribution": {},
            "average_rating": 0.0
        }
    
    # Calculate statistics
    total_runtime = sum(m['runtime'] for m in movies if m['runtime'])
    ratings = [m['vote_average'] for m in movies if m['vote_average']]
    average_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    # Genre distribution
    genre_dist = {}
    for movie in movies:
        for genre in movie['genres']:
            genre_dist[genre] = genre_dist.get(genre, 0) + 1
    
    return {
        "total_movies": len(movies),
        "total_runtime": total_runtime,
        "genre_distribution": genre_dist,
        "average_rating": round(average_rating, 2)
    }

