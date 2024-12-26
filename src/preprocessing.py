import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 0)

credits = pd.read_csv('../data/tmdb_5000_credits.csv')
movies = pd.read_csv('../data/tmdb_5000_movies.csv')

movies = movies.merge(credits, left_on='title', right_on='title')

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Cleans the messy genre dict from dataset, into more readable list form.
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i["name"])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)[:3]])
movies['crew'] = movies['crew'].apply(lambda x: [i['name'] for i in ast.literal_eval(x) if i['job'] == "Director"])

movies['tags'] = movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew','tags']]
movies['tags'] = movies['tags'].apply(lambda x: " ".join(x))
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['tags'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies['title'].iloc[movie_indices]

with open('movie_data.pkl', 'wb') as file:
    pickle.dump((movies, cosine_sim), file)