import streamlit as st
import pymysql
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import base64

# Function to add background image
def set_background_image(image_path):
    # Read the image file
    with open(image_path, "rb") as img_file:
        img = img_file.read()
    img_base64 = base64.b64encode(img).decode()

    # Set the background image using CSS
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

# Database Connection Function
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abdeshmukh08",
        database="moviengine",
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to execute queries
def execute_query(query, values=None, fetch=False):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            if fetch:
                return cursor.fetchall()
            connection.commit()
    finally:
        connection.close()

# Function to check if username exists
def get_user(username):
    query = "SELECT * FROM user_info WHERE username = %s"
    result = execute_query(query, (username,), fetch=True)
    return result[0] if result else None

# Function to register a user
def register_user(username, favorite_genres):
    try:
        query = "INSERT INTO user_info (username, favorite_genre) VALUES (%s, %s)"
        execute_query(query, (username, ",".join(favorite_genres)))
        return True
    except pymysql.err.IntegrityError:  # Username already exists
        return False

# Function to get all movies
def get_movies():
    query = "SELECT * FROM movies"
    return execute_query(query, fetch=True)

# Function to mark movie as watched
def mark_as_watched(user_id, movie_id):
    query = "INSERT INTO watched (user_id, movie_id) VALUES (%s, %s)"
    execute_query(query, (user_id, movie_id))

# Function to get watched movies
def get_watched_movies(user_id):
    query = "SELECT movies.* FROM movies JOIN watched ON movies.movie_id = watched.movie_id WHERE watched.user_id = %s"
    return execute_query(query, (user_id,), fetch=True)

# Recommendation Function with Updated Logic
def recommend_movies(user_id):
    # Get all movies from the database
    movies = get_movies()

    # Get user's favorite genres
    query = "SELECT favorite_genre FROM user_info WHERE user_id = %s"
    user = execute_query(query, (user_id,), fetch=True)

    if user:
        favorite_genre = user[0]["favorite_genre"].split(",")
    else:
        return []  # If no user found, return empty list

    # Get watched movies
    watched_movies = get_watched_movies(user_id)
    watched_movie_ids = {movie["movie_id"] for movie in watched_movies}

    # Exclude already watched movies
    movies = [movie for movie in movies if movie["movie_id"] not in watched_movie_ids]

    # If no new movies left, return empty list
    if not movies:
        return []

    # 1️⃣ **Favourite Genre-Based Movies**
    genre_based_movies = [
        movie for movie in movies 
        if any(genre in movie["genre"].split(",") for genre in favorite_genre)
    ]

    # 2️⃣ **Based on Movies You Watched**
    watched_movie_count = len(watched_movies)

    crew_based_recommendations = []
    plot_based_recommendations = []

    if watched_movie_count >= 2:
        # **Crew-Based Recommendations**
        crew_count = {}
        for movie in watched_movies:
            crew_members = movie["crew"].split(",") if movie["crew"] else []
            for crew in crew_members:
                crew_count[crew] = crew_count.get(crew, 0) + 1

        # Get the top 2 most frequently appearing crew members
        top_crew_members = sorted(crew_count, key=crew_count.get, reverse=True)[:2]

        # Recommend 2 movies featuring those crew members
        if top_crew_members:
            crew_based_recommendations = [
                movie for movie in movies if any(crew in movie["crew"] for crew in top_crew_members)
            ][:2]

        # **Plot-Based Recommendations**
        last_two_watched = watched_movies[-2:]  # Get last 2 watched movies

        # Extract overview texts and genres from the last 2 watched movies
        last_overviews = [movie["overview"] for movie in last_two_watched if movie["overview"]]
        relevant_genres = set()
        for movie in last_two_watched:
            relevant_genres.update(movie["genre"].split(","))

        # Filter movies that match any of these genres
        genre_filtered_movies = [
            movie for movie in movies if any(genre in movie["genre"].split(",") for genre in relevant_genres)
        ]

        if last_overviews and genre_filtered_movies:
            tfidf = TfidfVectorizer(stop_words="english")
            movie_overviews = [movie["overview"] for movie in genre_filtered_movies]

            # Fit TF-IDF only on the relevant movies
            tfidf_matrix = tfidf.fit_transform(movie_overviews)
            watched_tfidf = tfidf.transform(last_overviews)

            knn = NearestNeighbors(n_neighbors=5, metric="cosine")
            knn.fit(tfidf_matrix)

            recommended_movie_ids = set()
            for vector in watched_tfidf:
                distances, indices = knn.kneighbors(vector, n_neighbors=5)
                for idx in indices[0]:
                    recommended_movie_ids.add(genre_filtered_movies[idx]["movie_id"])

            plot_based_recommendations = [
                movie for movie in genre_filtered_movies if movie["movie_id"] in recommended_movie_ids
            ][:2]

    # 3️⃣ **General Recommendations**
    highest_budget_movie = max(movies, key=lambda x: x["budget"], default=None)
    highest_revenue_movie = max(movies, key=lambda x: x["revenue"], default=None)
    top_rated_movies = sorted(movies, key=lambda x: x["rating"], reverse=True)[:2]

    general_recommendations = []
    if highest_budget_movie: general_recommendations.append(highest_budget_movie)
    if highest_revenue_movie: general_recommendations.append(highest_revenue_movie)
    general_recommendations.extend(top_rated_movies)

    # Final recommendation list
    return {
        "Favourite Genre Based Movies": genre_based_movies[:5],
        "Based on Movies You Watched": crew_based_recommendations + plot_based_recommendations,
        "General Recommendations": general_recommendations[:4]
    }

# Streamlit App UI
st.title("Movie Recommendation System")

# Add background image (replace 'background.jpg' with your image file path)
set_background_image('bg.jpg')

# Sidebar Navigation
st.sidebar.title("🎬 Movie Recommender System")
page = st.sidebar.radio("Navigation", ["Login/Register", "Movie Dashboard", "Recommendations"])

# Function to get unique genres dynamically
def get_unique_genres():
    movies = get_movies()
    all_genres = set()
    for movie in movies:
        genres = movie["genre"].split(",")
        all_genres.update([genre.strip() for genre in genres])
    return sorted(all_genres)  # Sorting for better UI experience

if "user_id" not in st.session_state:
    st.session_state.user_id = None

def main():
    if page == "Login/Register":
        st.title("Login or Register")
        username = st.text_input("Enter Username")

        if st.button("Login"):
            user = get_user(username)
            if user:
                st.session_state.user_id = user["user_id"]
                st.success(f"🎉 Welcome back, {username}!")
            else:
                st.warning("Username not found! Please register.")

        st.subheader("New User? Register Here")
        genres = get_unique_genres()
        selected_genres = st.multiselect("Select Your Favorite Genre(s)", genres)

        if not selected_genres:
            st.warning("Please select at least one genre.")

        if st.button("Register"):
            if username and selected_genres:
                success = register_user(username, selected_genres)
                if success:
                    user = get_user(username)
                    st.session_state.user_id = user["user_id"]
                    st.success(f"🎉 Welcome, {username}! Your account has been created.")
                else:
                    st.error("Username already exists. Try logging in.")

    # Movie Dashboard Page
    elif page == "Movie Dashboard":
        if not st.session_state.user_id:
            st.warning("Please login first.")
        else:
            st.subheader("Available Movies")
            movies = get_movies()
            
            if movies:
                df = pd.DataFrame(movies)
                if all(col in df.columns for col in ["movie_id", "movie", "genre", "rating"]):
                    search_query = st.text_input("Search for a movie")
                    if search_query:
                        df = df[df["movie"].str.contains(search_query, case=False, na=False)]
                    
                    st.dataframe(df[['movie_id', 'movie', 'genre', 'rating']])
                    
                    selected_movie_id = st.selectbox("Select a movie to mark as watched", df['movie_id'])
                    if st.button("Mark as Watched"):
                        mark_as_watched(st.session_state.user_id, selected_movie_id)
                        st.success("Movie marked as watched!")
                else:
                    st.error("Movie data is incomplete or missing required columns.")
            else:
                st.write("No movies available.")

    # Recommendations Page
    elif page == "Recommendations":
        st.subheader("Recommended Movies")
        if not st.session_state.user_id:
            st.warning("Please login first.")
        else:
            recommended_movies = recommend_movies(st.session_state.user_id)
            if recommended_movies:
                st.write("🎬 **Favourite Genre Based Movies:**")
                genre_based_movies = recommended_movies["Favourite Genre Based Movies"]
                if genre_based_movies:
                    st.write(pd.DataFrame(genre_based_movies)[['movie_id', 'movie', 'genre', 'rating']])
                
                st.write("🎬 **Based on Movies You Watched:**")
                crew_plot_based_movies = recommended_movies["Based on Movies You Watched"]
                if crew_plot_based_movies:
                    st.write(pd.DataFrame(crew_plot_based_movies)[['movie_id', 'movie', 'genre', 'rating']])
                
                st.write("🎬 **General Recommendations:**")
                general_recommendations = recommended_movies["General Recommendations"]
                if general_recommendations:
                    st.write(pd.DataFrame(general_recommendations)[['movie_id', 'movie', 'genre', 'rating']])
            else:
                st.write("No recommendations available. Watch some movies first!")

if __name__ == "__main__":
    main()
