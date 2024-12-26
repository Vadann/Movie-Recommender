import pandas as pd

# Sample DataFrame
data = {
    'movie_id': [1, 2, 3],
    'title': ['Toy Story', 'Avatar', 'The Matrix'],
    'genre': ['Animation', 'Action', 'Sci-Fi'],
    'rating': [8.3, 7.8, 8.7],
    'release_year': [1995, 2009, 1999]
}

df = pd.DataFrame(data)
print(df)
print()

row = df.loc[df['title'] == 'Avatar']
print(row)

print()
rating = df.loc[df['title'] == 'Avatar', 'rating']
print(rating)

print()

print(df.iloc[2]['genre'])