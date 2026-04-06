from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Movie(BaseModel):
    movie_id: int
    title: str
    overview: Optional[str] = None
    genres: List[str]
    keywords: List[str]
    cast: List[str]
    crew: List[str]
    vote_average: Optional[float] = None
    poster_path: Optional[str] = None

class MovieRecommendationRequest(BaseModel):
    title: str
    n_recommendations: int = Field(default=10, ge=1, le=50)

class MoodRecommendationRequest(BaseModel):
    mood: str = Field(..., description="User's current mood")
    n_recommendations: int = Field(default=5, ge=1, le=20)

class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)

class RecommendationResponse(BaseModel):
    recommendations: List[Movie]
    similarity_scores: Optional[List[float]] = None

class PopularMoviesResponse(BaseModel):
    movies: List[Dict]

class GenreStatsResponse(BaseModel):
    genre_stats: Dict[str, float]
    total_movies: int

class WatchlistRequest(BaseModel):
    movie_ids: List[int]

class WatchlistStatsResponse(BaseModel):
    total_movies: int
    total_runtime: int
    genre_distribution: Dict[str, int]
    average_rating: float

