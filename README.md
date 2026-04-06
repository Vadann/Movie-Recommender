# AI-Powered Movie Recommender System

A modern, full-stack movie recommendation web application built with **FastAPI**, **React**, and **Machine Learning**. This project showcases industry-standard practices for building production-ready ML applications.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

## 🌟 Features

### Machine Learning
- **Content-Based Filtering**: Uses TF-IDF vectorization and cosine similarity to recommend movies based on genres, cast, director, keywords, and plot
- **Mood-Based Recommendations**: Get movie suggestions based on your current mood
- **Similarity Scoring**: Quantitative similarity scores for recommendations

### Frontend
- Modern, responsive UI with TailwindCSS
- Dark theme optimized for movie browsing
- Personal watchlist with local storage persistence
- Interactive statistics and analytics
- Real-time movie search
- Fast and smooth animations

### Backend
- High-performance FastAPI REST API
- Automatic OpenAPI documentation
- Async/await support for better performance
- Type-safe with Pydantic models
- TMDB API integration for posters and popular movies


## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **scikit-learn**: Machine learning library for TF-IDF and similarity calculations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Pydantic**: Data validation using Python type annotations
- **httpx**: Async HTTP client for TMDB API calls

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Next-generation frontend tooling
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon set

### Machine Learning
- **TF-IDF Vectorization**: Convert text features to numerical vectors
- **Cosine Similarity**: Measure similarity between movies
- **Content-Based Filtering**: Recommend based on movie features

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the `backend` directory:
   ```env
   TMDB_API_KEY=your_api_key_here
   ```
   
   Get your free API key from [TMDB](https://www.themoviedb.org/settings/api)

5. **Run preprocessing to generate ML model**
   ```bash
   python -m app.ml.preprocessing
   ```
   
   This will:
   - Load and merge the movie datasets
   - Extract features (genres, cast, crew, keywords)
   - Compute TF-IDF vectors
   - Calculate cosine similarity matrix
   - Save processed data as `movie_data.pkl`

6. **Start the FastAPI server**
   ```bash
   python -m app.main
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   
   📚 **API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## 📊 Dataset

This project uses the **TMDB 5000 Movie Dataset** containing:
- 4,803 movies
- Movie metadata (genres, keywords, cast, crew, budget, revenue)
- User ratings and popularity scores

### Home Page - Popular Movies
Beautiful grid of trending movies with ratings and genres

### Recommendations Page
Search for any movie and get 10 similar recommendations based on ML

### Mood-Based Discovery
Choose your mood and discover perfect movies

### Watchlist
Save your favorite movies and see analytics

### Statistics
Explore dataset insights and genre ratings


## Acknowledgments

- TMDB for the movie dataset and API
- FastAPI for the amazing framework
- React and Vite for modern frontend development
- scikit-learn for ML capabilities

---

If you found this project useful, please give it a star!

