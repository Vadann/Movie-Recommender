import streamlit as st
import requests
import pickle
import pandas as pd
import difflib
import matplotlib.pyplot as plt
from config import TMDB_API_KEY

with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

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

def add_to_watchlist(movie):
    if movie not in st.session_state['watchlist']:
        st.session_state['watchlist'].append(movie)
        st.success(f"Added {movie} to your Watchlist!")

def remove_from_watchlist(movie):
    if movie in st.session_state['watchlist']:
        st.session_state['watchlist'].remove(movie)
        st.success(f"Removed {movie} from your Watchlist.")

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
section = st.sidebar.radio("Go to:", ["Popular Movies", "Get Recommendations", "Watchlist", "About"])

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

                # Fetch the movie details to get the rating
                movie_details, rating = fetch_movie_details(movie_id)

                with col:
                    # Make poster clickable
                    st.markdown(f"[![{movie_title}]({poster_url})]({movie_url})", unsafe_allow_html=True)
                    st.write(f"**{movie_title}**")
                    st.write(f"Rating: {rating}/10")  # Display the rating
                    if st.button(f"Add {movie_title} to Watchlist", key=movie_id):
                        add_to_watchlist(movie_title)

elif section == "Get Recommendations":
    st.title("🎬 Movie Recommender")
    search_query = st.text_input("🔍 Search for a movie:", placeholder="Enter movie title...")

    if search_query:
        suggestions = get_search_suggestions(search_query, movies['title'].values)
        st.write("### Search Suggestions:")
        for suggestion in suggestions:
            st.write(suggestion)

    if search_query:
        filtered_movies = movies[movies['title'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_movies = movies

    selected_movie = st.selectbox("🎥 Select a movie:", filtered_movies['title'].values)

    if st.button('🔮 Get Recommendations'):
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
                    genres_bullet_list = "\n".join([f"- {genre}" for genre in movie_genres])
                    movie_url = f"https://www.themoviedb.org/movie/{movie_id}"

                    # Fetch the movie details to get the rating
                    movie_details, rating = fetch_movie_details(movie_id)

                    with col:
                        # Make poster clickable
                        st.markdown(f"[![{movie_title}]({poster_url})]({movie_url})", unsafe_allow_html=True)
                        st.write(f"**{movie_title}**")
                        st.write(f"Rating: {rating}/10")  # Display the rating
                        with st.expander(f"Genres for {movie_title}"):
                            st.markdown(f"**Genres:**\n{genres_bullet_list}")

elif section == "Watchlist":
    st.header("📚 Your Watchlist")
    if st.session_state['watchlist']:
        for movie in st.session_state['watchlist']:
            st.write(f"**{movie}**")
            if st.button(f"Remove {movie} from Watchlist"):
                remove_from_watchlist(movie)
    else:
        st.write("Your watchlist is empty.")

elif section == "About":
    st.header("About")
    st.markdown("Made with ❤️ using Streamlit and TMDB API. Powered by Hayk.")
    plot_genre_distribution()

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and TMDB API.")
