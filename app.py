import pandas as pd
import requests
import streamlit as st
import pickle

# Configure page
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Set background image using CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://user-images.githubusercontent.com/86877457/132905471-3ef27af4-ecc6-44bf-a47c-5ccf2250410c.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Optional: Make content background slightly transparent for readability */
    .block-container {
        background-color: rgba(0, 0, 0, 0.8);
        padding: 2rem;
        border-radius: 1rem;
    }

    h1, h2, h3, h4, h5, h6, p, .stButton > button {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.markdown("<h1 style='text-align: center; color: white;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

API_KEY = "630aff2f83c506eb9e3ebdd523a1876c"

# Function to fetch movie details
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_url = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')
        return {
            "title": data.get('title', 'Unknown'),
            "overview": data.get('overview', 'No overview available.'),
            "release_date": data.get('release_date', 'Unknown'),
            "rating": data.get('vote_average', 'N/A'),
            "poster": poster_url
        }
    except:
        return {
            "title": "Unknown",
            "overview": "Error loading details.",
            "release_date": "Unknown",
            "rating": "N/A",
            "poster": "https://via.placeholder.com/500x750?text=No+Image"
        }

# Recommend similar movies
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    return [(movies.iloc[i[0]].title, movies.iloc[i[0]].movie_id) for i in movies_list]

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# UI: Movie selector
selected_movie = st.selectbox("🎞️ Select a movie to get recommendations:", movies['title'].values)

# Store recommendation in session state
if st.button("Recommend"):
    st.session_state.recommendations = recommend(selected_movie)
    st.session_state.detail = None  # Clear previous detail

# Show recommendations
if "recommendations" in st.session_state:
    st.markdown("### 🧠 Recommendations:")
    cols_per_row = 5
    recs = st.session_state.recommendations

    for i in range(0, len(recs), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(recs):
                title, movie_id = recs[i + j]
                with cols[j]:
                    if st.button(title, key=f"movie_{movie_id}"):
                        st.session_state.detail = fetch_movie_details(movie_id)

# Show selected movie detail
if "detail" in st.session_state and st.session_state.detail:
    detail = st.session_state.detail
    st.markdown("----")
    st.image(detail["poster"], use_column_width=False, width=300)
    st.markdown(f"### {detail['title']}")
    st.markdown(f"**📅 Release Date:** {detail['release_date']}")
    st.markdown(f"**⭐ Rating:** {detail['rating']}")
    st.markdown(f"**📝 Overview:** {detail['overview']}")
    st.markdown("----")
