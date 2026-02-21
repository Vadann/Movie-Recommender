# External Integrations

**Analysis Date:** 2026-02-21

## APIs & External Services

**Movie Database:**
- TMDB (The Movie Database) - Provides movie metadata, posters, and popularity data
  - SDK/Client: httpx 0.25.2 (HTTP client in `backend/app/ml/recommender.py`)
  - Auth: `TMDB_API_KEY` environment variable configured at `backend/app/config.py`
  - Base URL: `https://api.themoviedb.org/3`
  - Image URL: `https://image.tmdb.org/t/p/w500` for poster images
  - Used by: Routes at `backend/app/api/routes.py` (`fetch_tmdb_popular()`, `fetch_tmdb_poster()`)

## Data Storage

**Databases:**
- SQLite (Development)
  - Location: `backend/movie_recommender.db`
  - Client: SQLAlchemy 2.0.23 ORM
  - Connection: `sqlite:///./movie_recommender.db` via `backend/app/database.py`

- PostgreSQL (Production)
  - Client: SQLAlchemy 2.0.23 with asyncpg 0.29.0 driver
  - Connection: `postgresql+asyncpg://user:password@localhost:5432/movie_recommender`
  - Alternative driver: psycopg2-binary 2.9.9 for sync operations
  - Migrations: alembic 1.13.0 for schema management

**File Storage:**
- Local filesystem only - Movie dataset loaded from pickle file at `backend/app/ml/recommender.py`
- No external file storage service (S3, etc.) currently integrated

**Caching:**
- None detected - In-memory movie data via pandas DataFrame at `backend/app/ml/recommender.py`

## Authentication & Identity

**Auth Provider:**
- Custom JWT-based authentication
  - Implementation: OAuth2 + JWT tokens at `backend/app/auth/security.py`
  - Token library: python-jose 3.3.0 for JWT encoding/decoding
  - Password hashing: passlib 1.7.4 with pbkdf2_sha256 scheme

**OAuth2 Support:**
- authlib 1.2.1 integrated at `backend/app/auth/oauth.py`
- Supported providers configured: Google, GitHub (infrastructure in place)
- Configuration:
  - `GOOGLE_CLIENT_ID` environment variable
  - `GOOGLE_CLIENT_SECRET` environment variable
  - `OAUTH_REDIRECT_URI` set to `http://localhost:3000/auth/callback`

**Authentication Endpoints:**
- POST `/api/auth/signup` - User registration at `backend/app/api/auth_routes.py`
- POST `/api/auth/login` - Token-based login
- POST `/api/auth/refresh` - Token refresh (refresh token support configured)

**Token Management:**
- Access tokens: 30-minute expiration (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Refresh tokens: 7-day expiration (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- Storage: Refresh tokens persisted in database table `refresh_tokens` at `backend/app/models_db.py`

## Monitoring & Observability

**Error Tracking:**
- None detected - Standard FastAPI error responses with HTTPException

**Logs:**
- Standard Python logging via FastAPI/Uvicorn
- Database initialization logs at `backend/app/database.py`
- Application startup logs at `backend/app/main.py`

## CI/CD & Deployment

**Hosting:**
- Not configured yet - Designed for:
  - Backend: Uvicorn on any Python-capable hosting
  - Frontend: Static file hosting (Vite build output)
  - Database: PostgreSQL on production server

**CI Pipeline:**
- None detected - No GitHub Actions, GitLab CI, or Jenkins configuration

## Environment Configuration

**Required Environment Variables:**
- `TMDB_API_KEY` - API key for The Movie Database
- `DATABASE_URL` - PostgreSQL connection string (defaults to SQLite in development)
- `SECRET_KEY` - JWT signing key (required for production, default provided for development)
- `GOOGLE_CLIENT_ID` - Google OAuth client ID (if using Google authentication)
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret (if using Google authentication)

**Optional Environment Variables:**
- `ALGORITHM` - JWT algorithm (defaults to HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token TTL (defaults to 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token TTL (defaults to 7)
- `ALLOWED_ORIGINS` - CORS allowed origins (defaults to localhost dev servers)
- `OAUTH_REDIRECT_URI` - OAuth callback URI (defaults to http://localhost:3000/auth/callback)

**Secrets Location:**
- Backend: `.env` file at `backend/.env` (git-ignored)
- Configuration loader: `pydantic-settings` at `backend/app/config.py` with `env_file = ".env"`

## API Endpoints

**Frontend-to-Backend Communication:**
- Base URL: `http://localhost:8000/api` configured at `frontend/src/services/api.js`
- HTTP Client: axios 1.6.2 with 10-second timeout
- Content-Type: application/json

**Movie Endpoints:**
- GET `/api/movies/search` - Search movies by title
- POST `/api/recommendations/content-based` - Content-based recommendations
- POST `/api/recommendations/mood-based` - Mood-based recommendations
- GET `/api/movies/popular` - Popular movies from TMDB or dataset
- GET `/api/movies/{movie_id}` - Movie details
- GET `/api/movies/{movie_id}/poster` - Movie poster URL
- GET `/api/statistics/genres` - Genre statistics
- GET `/api/statistics/moods` - Available mood filters
- POST `/api/watchlist/stats` - Watchlist statistics

**User Endpoints:**
- GET `/api/user/profile` - User profile information
- GET `/api/user/watchlist` - User's watchlist items
- POST `/api/user/watchlist` - Add to watchlist
- DELETE `/api/user/watchlist/{movie_id}` - Remove from watchlist
- POST `/api/user/ratings` - Rate a movie
- GET `/api/user/ratings` - User's ratings history

## Webhooks & Callbacks

**Incoming:**
- OAuth2 callback at client-side: `http://localhost:3000/auth/callback`

**Outgoing:**
- None detected

## CORS Configuration

**Allowed Origins:**
- `http://localhost:3000` - Primary React dev server
- `http://localhost:5173` - Vite dev server alternative

Configuration at `backend/app/main.py` using FastAPI CORSMiddleware:
- Credentials: Allowed
- Methods: All allowed
- Headers: All allowed

---

*Integration audit: 2026-02-21*
