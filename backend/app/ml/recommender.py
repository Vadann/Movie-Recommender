import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import httpx
from app.config import get_settings

class MovieRecommender:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.movies_df = None
        self.cosine_sim = None
        self.settings = get_settings()
        self._load_data()
        
        # Mood to genre mapping
        self.mood_genres = {
            "happy": ["Comedy", "Animation", "Family", "Music"],
            "sad": ["Drama", "Romance"],
            "excited": ["Action", "Adventure", "Science Fiction", "Thriller"],
            "scared": ["Horror", "Thriller", "Mystery"],
            "thoughtful": ["Documentary", "History", "Mystery", "Drama"],
            "romantic": ["Romance", "Comedy", "Drama"],
            "adventurous": ["Adventure", "Action", "Fantasy"]
        }
    
    def _load_data(self):
        """Load preprocessed movie data and similarity matrix"""
        try:
            with open(self.data_path, 'rb') as f:
                self.movies_df, self.cosine_sim = pickle.load(f)
            print(f"Loaded {len(self.movies_df)} movies")
        except FileNotFoundError:
            raise Exception(
                f"Data file not found at {self.data_path}. "
                "Please run preprocessing.py first."
            )
    
    def get_movie_by_title(self, title: str) -> Optional[pd.Series]:
        """Get movie data by exact title"""
        matches = self.movies_df[self.movies_df['title'] == title]
        if matches.empty:
            return None
        return matches.iloc[0]
    
    def search_movies(self, query: str, limit: int = 10) -> List[dict]:
        """Search movies by title (fuzzy search)"""
        query = query.lower()
        matches = self.movies_df[
            self.movies_df['title'].str.lower().str.contains(query, na=False)
        ]
        
        results = []
        for _, movie in matches.head(limit).iterrows():
            results.append({
                'movie_id': int(movie['movie_id']),
                'title': movie['title'],
                'genres': movie['genres'],
                'vote_average': float(movie['vote_average']) if pd.notna(movie['vote_average']) else None
            })
        
        return results
    
    def get_content_based_recommendations(
        self, 
        title: str, 
        n_recommendations: int = 10
    ) -> Tuple[List[dict], List[float]]:
        """
        Get movie recommendations using content-based filtering
        
        Args:
            title: Movie title to base recommendations on
            n_recommendations: Number of recommendations to return
            
        Returns:
            Tuple of (recommendations list, similarity scores list)
        """
        # Find movie index
        matches = self.movies_df[self.movies_df['title'] == title]
        if matches.empty:
            return [], []
        
        idx = matches.index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort by similarity (excluding the movie itself)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n_recommendations + 1]
        
        # Get movie indices and scores
        movie_indices = [i[0] for i in sim_scores]
        similarity_scores = [i[1] for i in sim_scores]
        
        # Prepare recommendations
        recommendations = []
        for idx in movie_indices:
            movie = self.movies_df.iloc[idx]
            recommendations.append(self._format_movie(movie))
        
        return recommendations, similarity_scores
    
    def get_mood_based_recommendations(
        self, 
        mood: str, 
        n_recommendations: int = 5
    ) -> List[dict]:
        """Get recommendations based on user's mood"""
        mood = mood.lower()
        
        if mood not in self.mood_genres:
            # Default to popular movies if mood not recognized
            return self.get_popular_movies(n_recommendations)
        
        selected_genres = self.mood_genres[mood]
        
        # Filter movies by genre and rating
        mood_movies = []
        for _, movie in self.movies_df.iterrows():
            if any(genre in selected_genres for genre in movie['genres']):
                mood_movies.append(movie)
        
        mood_df = pd.DataFrame(mood_movies)
        
        if mood_df.empty:
            return []
        
        # Sort by rating and get top movies
        mood_df = mood_df.sort_values('vote_average', ascending=False)
        
        # Sample randomly from top-rated movies for variety
        n_sample = min(n_recommendations * 3, len(mood_df))
        top_movies = mood_df.head(n_sample)
        sampled = top_movies.sample(min(n_recommendations, len(top_movies)))
        
        recommendations = []
        for _, movie in sampled.iterrows():
            recommendations.append(self._format_movie(movie))
        
        return recommendations
    
    def get_popular_movies(self, n: int = 20) -> List[dict]:
        """Get top-rated popular movies"""
        # Filter movies with good ratings and sort
        popular = self.movies_df[
            self.movies_df['vote_average'] >= 7.0
        ].sort_values('vote_average', ascending=False)
        
        recommendations = []
        for _, movie in popular.head(n).iterrows():
            recommendations.append(self._format_movie(movie))
        
        return recommendations
    
    def get_genre_statistics(self) -> dict:
        """Calculate average rating by genre"""
        genre_ratings = {}
        
        for _, movie in self.movies_df.iterrows():
            rating = movie['vote_average']
            if pd.isna(rating):
                continue
                
            for genre in movie['genres']:
                if genre not in genre_ratings:
                    genre_ratings[genre] = []
                genre_ratings[genre].append(rating)
        
        # Calculate averages
        avg_genre_ratings = {
            genre: sum(ratings) / len(ratings)
            for genre, ratings in genre_ratings.items()
        }
        
        return avg_genre_ratings
    
    def get_movies_by_ids(self, movie_ids: List[int]) -> List[dict]:
        """Get movie details for a list of movie IDs"""
        movies = []
        for movie_id in movie_ids:
            movie_data = self.movies_df[self.movies_df['movie_id'] == movie_id]
            if not movie_data.empty:
                movies.append(self._format_movie(movie_data.iloc[0]))
        return movies
    
    def _format_movie(self, movie: pd.Series) -> dict:
        """Format movie data for API response"""
        return {
            'movie_id': int(movie['movie_id']),
            'title': movie['title'],
            'overview': movie['overview'] if pd.notna(movie['overview']) else None,
            'genres': movie['genres'],
            'keywords': movie['keywords'],
            'cast': movie['cast'],
            'crew': movie['crew'],
            'vote_average': float(movie['vote_average']) if pd.notna(movie['vote_average']) else None,
            'runtime': int(movie['runtime']) if pd.notna(movie['runtime']) else None
        }
    
    async def fetch_tmdb_poster(self, movie_id: int) -> Optional[str]:
        """Fetch movie poster from TMDB API"""
        if not self.settings.TMDB_API_KEY:
            return None
            
        url = f"{self.settings.TMDB_BASE_URL}/movie/{movie_id}"
        params = {"api_key": self.settings.TMDB_API_KEY}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    poster_path = data.get('poster_path')
                    if poster_path:
                        return f"{self.settings.TMDB_IMAGE_BASE_URL}{poster_path}"
        except Exception as e:
            print(f"Error fetching poster: {e}")
        
        return None
    
    async def fetch_tmdb_popular(self) -> List[dict]:
        """Fetch popular movies from TMDB"""
        if not self.settings.TMDB_API_KEY:
            return self.get_popular_movies(20)
        
        url = f"{self.settings.TMDB_BASE_URL}/movie/popular"
        params = {
            "api_key": self.settings.TMDB_API_KEY,
            "language": "en-US",
            "page": 1
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('results', [])
        except Exception as e:
            print(f"Error fetching popular movies: {e}")
        
        return self.get_popular_movies(20)

# Global instance
_recommender_instance = None

def get_recommender() -> MovieRecommender:
    """Get or create recommender instance"""
    global _recommender_instance
    
    if _recommender_instance is None:
        data_path = Path(__file__).parent / "movie_data.pkl"
        _recommender_instance = MovieRecommender(str(data_path))
    
    return _recommender_instance

