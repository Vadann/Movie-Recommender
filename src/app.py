import streamlit as st
import requests
import pickle
import pandas as pd
import difflib
import matplotlib.pyplot as plt
from config import TMDB_API_KEY

with open('src\movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Move all function definitions to the top
def get_mood_recommendations(mood):
    mood_genres = {
        "Happy": ["Comedy", "Animation", "Family"],
        "Sad": ["Drama", "Romance"],
        "Excited": ["Action", "Adventure", "Sci-Fi"],
        "Scared": ["Horror", "Thriller"],
        "Thoughtful": ["Documentary", "History", "Mystery"]
    }
    
    recommended_movies = []
    selected_genres = mood_genres[mood]
    
    for _, movie in movies.iterrows():
        if any(genre in selected_genres for genre in movie['genres']):
            recommended_movies.append(movie)
    
    return pd.DataFrame(recommended_movies).sample(min(5, len(recommended_movies)))

def show_movie_statistics():
    st.header("📊 Movie Statistics")
    
    # Average rating by genre
    genre_ratings = {}
    for _, movie in movies.iterrows():
        rating = movie['vote_average']
        for genre in movie['genres']:
            if genre not in genre_ratings:
                genre_ratings[genre] = []
            genre_ratings[genre].append(rating)
    
    avg_genre_ratings = {genre: sum(ratings)/len(ratings) 
                        for genre, ratings in genre_ratings.items()}
    
    # Create a bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    genres = list(avg_genre_ratings.keys())
    ratings = list(avg_genre_ratings.values())
    
    ax.bar(genres, ratings, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title("Average Rating by Genre")
    st.pyplot(fig)

def calculate_watchlist_time():
    total_minutes = 0
    for movie in st.session_state['watchlist']:
        movie_data = movies[movies['title'] == movie]
        if not movie_data.empty:
            runtime = movie_data['runtime'].values[0]  # You'll need to add runtime to your dataset
            total_minutes += runtime
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return hours, minutes

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):
    api_key = TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return full_path


# Function to get movie recommendations based on cosine similarity
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices]


# Fetch popular movies from TMDB
def fetch_popular_movies():
    api_key = TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    return data['results']


# Fetch movie poster URL
def fetch_poster_url(poster_path):
    return f"https://image.tmdb.org/t/p/w500{poster_path}"


# Search suggestions for user input
def get_search_suggestions(query, movie_titles):
    return difflib.get_close_matches(query, movie_titles)


# Plot genre distribution
def plot_genre_distribution():
    all_genres = []
    for movie in movies['genres']:
        all_genres.extend(movie)  # Flatten the list of genres
    genre_counts = pd.Series(all_genres).value_counts()

    fig, ax = plt.subplots(figsize=(10, 6))
    genre_counts.plot(kind="bar", ax=ax, color="salmon")
    ax.set_title("Genre Distribution")
    ax.set_xlabel("Genres")
    ax.set_ylabel("Number of Movies")
    st.pyplot(fig)


def plot_watchlist_genre_distribution():
    if st.session_state['watchlist']:
        watchlist_genres = []
        watchlist_ratings = []

        # Gather genres and ratings from the watchlist
        for movie in st.session_state['watchlist']:
            movie_data = movies[movies['title'] == movie]
            if not movie_data.empty:
                genres = movie_data['genres'].values[0]
                rating = movie_data['vote_average'].values[0]  # Assuming the 'vote_average' column exists
                watchlist_genres.extend(genres)
                watchlist_ratings.append(rating)

        # Genre Distribution
        genre_counts = pd.Series(watchlist_genres).value_counts()
        st.subheader("🎥 Genre Distribution in Watchlist")
        fig, ax = plt.subplots(figsize=(10, 6))
        genre_counts.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title("Genre Distribution")
        ax.set_xlabel("Genres")
        ax.set_ylabel("Number of Movies")
        st.pyplot(fig)

        # Rating Trends
        st.subheader("⭐ Ratings of Movies in Watchlist")
        st.line_chart(watchlist_ratings)

    else:
        st.warning("Your watchlist is empty. Add movies to see analytics!")


# Watchlist functionality
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []

if 'user_ratings' not in st.session_state:
    st.session_state['user_ratings'] = {}
if 'user_reviews' not in st.session_state:
    st.session_state['user_reviews'] = {}

def add_to_watchlist(movie):
    if movie not in st.session_state['watchlist']:
        st.session_state['watchlist'].append(movie)
        st.success(f"Added {movie} to your Watchlist!")


def remove_from_watchlist(movie):
    if movie in st.session_state['watchlist']:
        st.session_state['watchlist'].remove(movie)
        st.success(f"Removed {movie} from your Watchlist.")


def add_user_rating(movie, rating, review=""):
    st.session_state['user_ratings'][movie] = rating
    if review:
        st.session_state['user_reviews'][movie] = review
    st.success(f"Added your {rating}⭐ rating for {movie}")


# Fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    api_key = TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    movie_data = response.json()
    rating = movie_data.get('vote_average', 'N/A')  # Rating is under 'vote_average'
    return movie_data, rating


# Layout and Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", ["Popular Movies", "Get Recommendations", "Watchlist", "Statistics", "About"])

# Update the movie display function to handle watchlist items better
def display_movie_card(col, movie_title, poster_url, movie_url, rating, movie_id, show_watchlist=True):
    with col:
        # Movie poster
        st.markdown(f"[![{movie_title}]({poster_url})]({movie_url})", unsafe_allow_html=True)
        
        # Movie info container
        with st.container():
            st.markdown(f"**{movie_title}**")
            st.markdown(f"⭐ {rating}/10")
            
            if show_watchlist:
                if movie_title in st.session_state['watchlist']:
                    if st.button("✓ In Watchlist", key=f"remove_{movie_id}"):
                        remove_from_watchlist(movie_title)
                else:
                    if st.button("+ Watchlist", key=f"add_{movie_id}"):
                        add_to_watchlist(movie_title)
            else:  # This is for the watchlist view
                if st.button("Remove", key=f"remove_watchlist_{movie_id}", use_container_width=True):
                    remove_from_watchlist(movie_title)

# Update the Popular Movies section
if section == "Popular Movies":
    st.header("🌟 Popular Movies from TMDB")
    popular_movies = fetch_popular_movies()

    for i in range(0, len(popular_movies), 5):
        cols = st.columns(5)
        for col, j in zip(cols, range(i, i + 5)):
            if j < len(popular_movies):
                movie = popular_movies[j]
                movie_title = movie['title']
                poster_path = movie['poster_path']
                poster_url = fetch_poster_url(poster_path)
                movie_id = movie['id']
                movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
                movie_details, rating = fetch_movie_details(movie_id)
                
                display_movie_card(col, movie_title, poster_url, movie_url, rating, movie_id)

# Update the Recommendations section
elif section == "Get Recommendations":
    st.title("🎬 Movie Recommender")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search for a movie:", placeholder="Enter movie title...")
    with col2:
        if search_query:
            filtered_movies = movies[movies['title'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_movies = movies
        selected_movie = st.selectbox("Select a movie:", filtered_movies['title'].values)

    if st.button('🔮 Get Recommendations', type="primary"):
        recommendations = get_recommendations(selected_movie)
        st.write("### Movies You Should Watch:")

        for i in range(0, 10, 5):
            cols = st.columns(5)
            for col, j in zip(cols, range(i, i + 5)):
                if j < len(recommendations):
                    movie_title = recommendations.iloc[j]['title']
                    movie_id = recommendations.iloc[j]['movie_id']
                    movie_genres = recommendations.iloc[j]['genres']
                    poster_url = fetch_poster(movie_id)
                    movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
                    movie_details, rating = fetch_movie_details(movie_id)
                    
                    display_movie_card(col, movie_title, poster_url, movie_url, rating, movie_id)
                    
                    with st.expander(f"Genres"):
                        st.markdown("\n".join([f"- {genre}" for genre in movie_genres]))

    st.divider()
    
    # Mood-based recommendations
    st.subheader("🎭 Get Recommendations by Mood")
    col1, col2 = st.columns([3, 1])
    with col1:
        mood = st.selectbox("How are you feeling today?", 
                        ["Happy", "Sad", "Excited", "Scared", "Thoughtful"])
    with col2:
        mood_button = st.button("Get Recommendations", type="primary")
    
    if mood_button:
        mood_recommendations = get_mood_recommendations(mood)
        cols = st.columns(5)
        for i, (_, movie) in enumerate(mood_recommendations.head().iterrows()):
            movie_title = movie['title']
            movie_id = movie['movie_id']
            poster_url = fetch_poster(movie_id)
            movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
            movie_details, rating = fetch_movie_details(movie_id)
            
            display_movie_card(cols[i], movie_title, poster_url, movie_url, rating, movie_id)

# Update the Watchlist section
elif section == "Watchlist":
    st.header("📚 Your Watchlist")
    if st.session_state['watchlist']:
        # Calculate number of rows needed
        n_movies = len(st.session_state['watchlist'])
        n_cols = 5
        n_rows = (n_movies + n_cols - 1) // n_cols  # Ceiling division
        
        for row in range(n_rows):
            cols = st.columns(n_cols)
            for col_idx in range(n_cols):
                movie_idx = row * n_cols + col_idx
                if movie_idx < n_movies:
                    movie_title = st.session_state['watchlist'][movie_idx]
                    movie_data = movies[movies['title'] == movie_title]
                    if not movie_data.empty:
                        movie_id = movie_data['movie_id'].values[0]
                        poster_url = fetch_poster(movie_id)
                        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
                        movie_details, rating = fetch_movie_details(movie_id)
                        
                        display_movie_card(cols[col_idx], movie_title, poster_url, 
                                        movie_url, rating, movie_id, show_watchlist=False)
        
        st.divider()
        hours, minutes = calculate_watchlist_time()
        st.info(f"⏱️ Total watch time: {hours} hours and {minutes} minutes")
    else:
        st.info("Your watchlist is empty. Add some movies from the recommendations!")

elif section == "Statistics":
    show_movie_statistics()

elif section == "About":
    st.header("About")
    st.markdown("Made with ❤️ using Streamlit and TMDB API. Powered by Hayk.")
    plot_genre_distribution()

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and TMDB API.")

def find_similar_users():
    if not st.session_state['user_ratings']:
        return []
    
    # Create a simple recommendation based on similar ratings
    similar_users = []
    user_genres = set()
    
    # Get user's preferred genres based on highly rated movies
    for movie, rating in st.session_state['user_ratings'].items():
        if rating >= 8:  # High rating threshold
            movie_data = movies[movies['title'] == movie]
            if not movie_data.empty:
                user_genres.update(movie_data['genres'].values[0])
    
    # Generate fake similar users (in a real app, this would be actual user data)
    if user_genres:
        similar_users = [
            {"name": "Movie Fan #1", "matching_genres": len(user_genres) - 1},
            {"name": "Cinema Lover #2", "matching_genres": len(user_genres) - 2},
        ]
    
    return similar_users

# Add to your app
if st.session_state['user_ratings']:
    st.subheader("👥 Users with Similar Taste")
    similar_users = find_similar_users()
    for user in similar_users:
        st.write(f"{user['name']} - {user['matching_genres']} matching genres")
