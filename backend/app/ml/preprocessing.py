import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from pathlib import Path

class MovieDataPreprocessor:
    def __init__(self, credits_path: str, movies_path: str):
        self.credits_path = credits_path
        self.movies_path = movies_path
        self.movies_df = None
        self.cosine_sim = None
        
    def convert(self, obj):
        """Convert JSON string to list of names"""
        L = []
        for i in ast.literal_eval(obj):
            L.append(i["name"])
        return L
    
    def load_and_merge_data(self):
        """Load and merge credits and movies data"""
        credits = pd.read_csv(self.credits_path)
        movies = pd.read_csv(self.movies_path)
        
        # Merge datasets
        self.movies_df = movies.merge(credits, left_on='title', right_on='title')
        
        # Select relevant columns
        self.movies_df = self.movies_df[[
            'movie_id', 'title', 'overview', 'genres', 'keywords', 
            'cast', 'crew', 'vote_average', 'runtime'
        ]]
        
        return self.movies_df
    
    def extract_features(self):
        """Extract and process features for recommendation"""
        # Process genres
        self.movies_df['genres'] = self.movies_df['genres'].apply(self.convert)
        
        # Process keywords
        self.movies_df['keywords'] = self.movies_df['keywords'].apply(self.convert)
        
        # Process cast (top 3 actors)
        self.movies_df['cast'] = self.movies_df['cast'].apply(
            lambda x: [i['name'] for i in ast.literal_eval(x)[:3]] if pd.notna(x) else []
        )
        
        # Process crew (directors only)
        self.movies_df['crew'] = self.movies_df['crew'].apply(
            lambda x: [i['name'] for i in ast.literal_eval(x) if i['job'] == "Director"] if pd.notna(x) else []
        )
        
        # Create tags for content-based filtering
        self.movies_df['tags'] = (
            self.movies_df['genres'] + 
            self.movies_df['keywords'] + 
            self.movies_df['cast'] + 
            self.movies_df['crew']
        )
        
        # Convert overview to string and add to tags
        self.movies_df['overview'] = self.movies_df['overview'].fillna('')
        
        # Combine tags into single string
        self.movies_df['tags'] = self.movies_df.apply(
            lambda row: ' '.join(row['tags']) + ' ' + row['overview'], 
            axis=1
        )
        
        # Clean and normalize
        self.movies_df['tags'] = self.movies_df['tags'].apply(lambda x: x.lower())
        
        return self.movies_df
    
    def compute_similarity_matrix(self):
        """Compute TF-IDF and cosine similarity matrix"""
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = tfidf.fit_transform(self.movies_df['tags'])
        
        # Compute cosine similarity
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        return self.cosine_sim
    
    def save_processed_data(self, output_path: str):
        """Save processed data and similarity matrix"""
        with open(output_path, 'wb') as f:
            pickle.dump((self.movies_df, self.cosine_sim), f)
        print(f"Processed data saved to {output_path}")
    
    def run_full_pipeline(self, output_path: str):
        """Run complete preprocessing pipeline"""
        print("Loading data...")
        self.load_and_merge_data()
        
        print("Extracting features...")
        self.extract_features()
        
        print("Computing similarity matrix...")
        self.compute_similarity_matrix()
        
        print("Saving processed data...")
        self.save_processed_data(output_path)
        
        return self.movies_df, self.cosine_sim

if __name__ == "__main__":
    # Get the project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    
    credits_path = project_root / "data" / "tmdb_5000_credits.csv"
    movies_path = project_root / "data" / "tmdb_5000_movies.csv"
    output_path = current_dir / "movie_data.pkl"
    
    preprocessor = MovieDataPreprocessor(
        credits_path=str(credits_path),
        movies_path=str(movies_path)
    )
    
    movies_df, cosine_sim = preprocessor.run_full_pipeline(str(output_path))
    print(f"\nProcessed {len(movies_df)} movies")
    print(f"Similarity matrix shape: {cosine_sim.shape}")

