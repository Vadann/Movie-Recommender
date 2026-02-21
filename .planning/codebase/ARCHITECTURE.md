# Architecture

**Analysis Date:** 2026-02-21

## Pattern Overview

**Overall:** Layered three-tier architecture with ML-driven backend and React frontend

**Key Characteristics:**
- Separated backend API (FastAPI) and frontend (React/Vite)
- Content-based and mood-based recommendation engines using scikit-learn
- JWT + OAuth2 authentication with session-based user management
- SQLAlchemy ORM for database abstraction (SQLite dev, PostgreSQL production)
- Context-based state management in frontend for auth and watchlist data

## Layers

**Frontend Presentation Layer:**
- Purpose: User interface for browsing, searching, and personalizing movie recommendations
- Location: `frontend/src/`
- Contains: React components (pages, context providers, services)
- Depends on: REST API endpoints, local storage for auth tokens
- Used by: End users via browser

**Frontend State & Services Layer:**
- Purpose: Manage authentication state, watchlist data, and API communication
- Location: `frontend/src/context/`, `frontend/src/services/`
- Contains: AuthContext, WatchlistContext, api.js, authAPI.js
- Depends on: Backend API, browser localStorage
- Used by: Presentation layer components

**Backend API Layer:**
- Purpose: HTTP endpoints for recommendations, user data, and authentication
- Location: `backend/app/api/`
- Contains: routes.py (movies/recommendations), auth_routes.py (auth), user_routes.py (watchlist/ratings)
- Depends on: ML recommender, database, security utilities
- Used by: Frontend, external TMDB API calls

**Backend Business Logic Layer:**
- Purpose: Core recommendation algorithms, authentication logic, and data operations
- Location: `backend/app/ml/`, `backend/app/auth/`
- Contains: recommender.py (content/mood-based filtering), security.py (JWT/password hashing)
- Depends on: Data models, configuration
- Used by: API layer

**Backend Data Layer:**
- Purpose: Database schema, ORM models, and data access
- Location: `backend/app/models_db.py`, `backend/app/database.py`
- Contains: SQLAlchemy models (User, WatchlistItem, MovieRating, RefreshToken), session factory
- Depends on: SQLAlchemy, database connection config
- Used by: API and business logic layers

**Data Processing Layer:**
- Purpose: Transform raw CSV movie data into preprocessed format for recommendations
- Location: `backend/app/ml/preprocessing.py`
- Contains: MovieDataPreprocessor class with TF-IDF and cosine similarity computation
- Depends on: pandas, scikit-learn
- Used by: Recommender during initialization (one-time setup)

## Data Flow

**Movie Recommendation Flow (Content-Based):**

1. Frontend user selects a movie via search (`Home.jsx`, `Recommendations.jsx`)
2. Frontend calls `movieAPI.getContentRecommendations(title)`
3. Backend API route `/recommendations/content-based` receives request
4. Route handler calls `recommender.get_content_based_recommendations(title)`
5. Recommender finds movie in pre-computed DataFrame using cosine similarity matrix
6. Returns list of similar movies with similarity scores
7. Frontend renders results with movie cards and metadata

**Authentication Flow:**

1. User submits login credentials via `Login.jsx` → `authAPI.login(email, password)`
2. Backend `/auth/login` endpoint validates email/password against hashed DB value
3. Backend generates JWT access token (30 min expiry) and refresh token (7 day expiry)
4. Frontend stores tokens in localStorage, calls `/auth/me` to fetch user profile
5. Frontend AuthContext stores user state, makes token available to all requests
6. Protected API calls include `Authorization: Bearer <token>` header
7. Backend validates token via `get_current_active_user` dependency injection
8. Expired access token triggers refresh using refresh token (handled in authAPI)

**Watchlist Management Flow:**

1. Authenticated user clicks "Add to Watchlist" on movie card
2. Frontend calls `authAPI` → sends POST to `/user/watchlist` with movie metadata
3. Backend checks if movie already in user's watchlist
4. If not, creates WatchlistItem row linked to user_id and movie_id
5. Frontend receives confirmation, updates local WatchlistContext
6. Watchlist page queries `/user/watchlist` to display all items
7. Delete removes WatchlistItem from database

**Mood-Based Recommendation Flow:**

1. User selects mood from dropdown in `Home.jsx` or `Recommendations.jsx`
2. Frontend calls `movieAPI.getMoodRecommendations(mood)`
3. Backend route filters movies by genres mapped to mood (e.g., "happy" → Comedy, Animation)
4. Recommender samples top-rated movies from filtered genre set
5. Returns diverse selection with variation for freshness
6. Frontend displays mood-matched recommendations

**State Management:**

- **Frontend Auth State:** Managed by `AuthContext` (React Context API)
  - Stores current user object, loading state, login/logout/signup functions
  - Synced with localStorage on login, cleared on logout

- **Frontend Watchlist State:** Managed by `WatchlistContext`
  - Caches watchlist items and ratings for UI consistency
  - Source of truth is backend database; frontend is read cache

- **Backend ML State:** Single global `MovieRecommender` instance
  - Loads movie DataFrame and cosine similarity matrix once at startup
  - Reused across all requests to avoid reloading 5000-movie dataset
  - Accessed via `get_recommender()` factory function

## Key Abstractions

**MovieRecommender:**
- Purpose: Encapsulates all recommendation logic and movie data
- Examples: `backend/app/ml/recommender.py`
- Pattern: Singleton pattern via `get_recommender()` factory; lazy loads data on first call
- Methods: search_movies, get_content_based_recommendations, get_mood_based_recommendations, get_popular_movies

**Security Module:**
- Purpose: Centralize authentication and authorization logic
- Examples: `backend/app/auth/security.py`
- Pattern: Utility functions + FastAPI dependency injection
- Functions: get_password_hash, verify_password, create_access_token, get_current_active_user

**Database Models (SQLAlchemy):**
- Purpose: Define schema and relationships for users, watchlist, ratings
- Examples: `backend/app/models_db.py` (User, WatchlistItem, MovieRating, RefreshToken)
- Pattern: Declarative mapping with ORM relationships and cascading deletes
- Relationships: User → WatchlistItem (one-to-many), User → MovieRating (one-to-many)

**API Router Pattern:**
- Purpose: Organize endpoints by feature/domain
- Examples: `routes.py` (movies), `auth_routes.py` (auth), `user_routes.py` (user data)
- Pattern: APIRouter with path prefixes in main.py
- Dependency Injection: FastAPI Depends() for auth, database session, user context

**Pydantic Models (Request/Response):**
- Purpose: Validate and serialize API payloads
- Examples: `backend/app/models.py` (MovieRecommendationRequest, RecommendationResponse, etc.)
- Pattern: Inheritance from BaseModel with Field validation
- Usage: Automatic request parsing and OpenAPI schema generation

## Entry Points

**Backend Server:**
- Location: `backend/app/main.py`
- Triggers: `python -m uvicorn app.main:app --reload` or `python app/main.py`
- Responsibilities: Create FastAPI app, register CORS middleware, include routers, initialize database on startup
- Serves: OpenAPI docs at `/docs`, REST API at `/api/...`, health check at `/health`

**Frontend Dev Server:**
- Location: `frontend/src/main.jsx` (React entry)
- Triggers: `npm run dev` (Vite dev server on :3000 or :5173)
- Responsibilities: Mount React app to DOM, initialize AuthProvider and WatchlistProvider
- Bootstrap: App.jsx sets up routing, navigation, layouts

**Data Preprocessing Script:**
- Location: `backend/app/ml/preprocessing.py` (if __name__ == "__main__")
- Triggers: `python backend/app/ml/preprocessing.py`
- Responsibilities: Load CSV data, extract features, compute cosine similarity matrix, save pickle file
- Output: `backend/app/ml/movie_data.pkl` (used by recommender at startup)

## Error Handling

**Strategy:** HTTP status codes + exception raising + try-catch blocks

**Patterns:**

**Backend:**
- HTTPException with status code (401, 404, 400, 500) for known errors
- Example: `raise HTTPException(status_code=404, detail="Movie not found")`
- JWT decode failures caught, converted to 401 Unauthorized
- Database errors caught in try-except, rolled back, returned as 500
- File not found during data loading raises Exception with helpful message

**Frontend:**
- API calls wrapped in try-catch; errors logged to console
- Login/signup failures show toast/alert messages to user
- Protected routes check `useAuth().user` and redirect to login if null
- Failed token refresh clears auth state and forces re-login

## Cross-Cutting Concerns

**Logging:**
- Backend: print() statements with emoji indicators (🚀, ✅, ❌, 📥, etc.) in user_routes.py and recommender
- Frontend: console.log() for debugging, error logging on API failures
- TMDB poster fetch failures logged but don't break flow

**Validation:**
- Backend: Pydantic models enforce type and range constraints (e.g., n_recommendations: 1-50)
- Frontend: Form validation in Login, Signup pages before submission
- Database: NOT NULL constraints, unique indexes on email/username, foreign key cascades

**Authentication:**
- Backend: JWT tokens with expiry, optional OAuth2 foundation (not fully implemented)
- Frontend: Token stored in localStorage, automatically included in Authorization header via axios interceptor (not visible in code but used pattern)
- Protected routes: FastAPI dependency `get_current_active_user` checks token and user.is_active

**Authorization:**
- Backend: User can only access their own watchlist/ratings via user_id check in query
- Frontend: Watchlist/Ratings pages hidden if not authenticated (checked via useAuth().user)
- No role-based access control; all authenticated users have same permissions

**CORS:**
- Frontend URLs (localhost:3000, localhost:5173) whitelisted in main.py CORSMiddleware
- Credentials allowed (for auth cookies/headers)

**Configuration:**
- Backend: Settings class in config.py uses .env file and pydantic-settings
- Fallback to SQLite locally, PostgreSQL in production via DATABASE_URL
- TMDB API key optional; app degrades gracefully if missing

---

*Architecture analysis: 2026-02-21*
