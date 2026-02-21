# Codebase Structure

**Analysis Date:** 2026-02-21

## Directory Layout

```
Movie-Recommender/
├── backend/                        # Python FastAPI backend
│   ├── app/
│   │   ├── api/                   # API endpoints (routers)
│   │   │   ├── routes.py          # Movie search, recommendations, stats
│   │   │   ├── auth_routes.py     # User signup, login, token refresh
│   │   │   ├── user_routes.py     # Watchlist, ratings (auth required)
│   │   │   └── __init__.py
│   │   ├── auth/                  # Authentication logic
│   │   │   ├── security.py        # JWT, password hashing, oauth2 scheme
│   │   │   ├── schemas.py         # Pydantic auth models (UserCreate, etc.)
│   │   │   ├── oauth.py           # OAuth2 provider setup (stub)
│   │   │   └── __init__.py
│   │   ├── ml/                    # Machine learning / recommendation
│   │   │   ├── recommender.py     # MovieRecommender class, recommendation logic
│   │   │   ├── preprocessing.py   # Data preprocessing, feature extraction, similarity matrix
│   │   │   ├── movie_data.pkl     # Pickled processed data (generated)
│   │   │   └── __init__.py
│   │   ├── main.py                # FastAPI app creation, startup, router registration
│   │   ├── config.py              # Settings, env config via pydantic-settings
│   │   ├── database.py            # SQLAlchemy engine, session factory, db init
│   │   ├── models_db.py           # SQLAlchemy ORM models (User, WatchlistItem, MovieRating)
│   │   ├── models.py              # Pydantic request/response schemas
│   │   └── __init__.py
│   ├── requirements.txt           # Python dependencies (FastAPI, SQLAlchemy, etc.)
│   ├── requirements-*.txt         # Alternative requirement sets (minimal, working)
│   ├── venv/                      # Virtual environment (not committed)
│   ├── test_auth.py               # Manual auth testing script
│   ├── test_setup.py              # Manual setup verification script
│   └── debug_config.py            # Debug utility script
├── frontend/                      # React + Vite frontend
│   ├── src/
│   │   ├── pages/                 # Page components (page-level UI)
│   │   │   ├── Home.jsx           # Popular movies, mood selection
│   │   │   ├── Recommendations.jsx # Content-based & mood-based search
│   │   │   ├── Watchlist.jsx      # User watchlist display & management
│   │   │   ├── Statistics.jsx     # Genre stats, watchlist stats
│   │   │   ├── Login.jsx          # Email/password login form
│   │   │   ├── Signup.jsx         # User registration form
│   │   │   └── Documentation.jsx  # API documentation
│   │   ├── components/            # Reusable components
│   │   │   ├── MovieCard.jsx      # Movie card display (title, genres, rating, actions)
│   │   │   └── ParticlesBackground.jsx # Animated background
│   │   ├── context/               # React Context for state management
│   │   │   ├── AuthContext.jsx    # User auth state, login/logout/signup
│   │   │   └── WatchlistContext.jsx # Watchlist cache state
│   │   ├── services/              # API client modules
│   │   │   ├── api.js            # Axios instance, movieAPI methods (search, recommendations, etc.)
│   │   │   └── authAPI.js        # Auth endpoints (login, signup, token refresh, getCurrentUser)
│   │   ├── App.jsx                # Main app component (routing, navigation, layout)
│   │   ├── main.jsx               # React entry point (ReactDOM.createRoot)
│   │   └── index.css              # Global styles
│   ├── public/                    # Static assets (favicon, etc.)
│   ├── package.json               # Dependencies (React, axios, react-router, tailwindcss)
│   ├── vite.config.js             # Vite build config
│   ├── tailwind.config.js         # Tailwind CSS config
│   ├── postcss.config.js          # PostCSS for Tailwind processing
│   └── index.html                 # HTML template
├── data/                          # Raw data (CSVs, not committed)
│   ├── tmdb_5000_movies.csv       # Movie data from TMDB (title, overview, genres, etc.)
│   └── tmdb_5000_credits.csv      # Cast and crew data
├── .planning/                     # GSD planning documents
│   └── codebase/                  # Architecture & structure analysis
├── .claude/                       # Claude Code workspace config
├── start.sh                       # Bash script to start both backend + frontend
├── start.bat                      # Windows script to start both backend + frontend
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview
├── PROJECT_OVERVIEW.md            # Detailed project description
├── SETUP_GUIDE.md                 # Setup instructions
├── AUTH_SETUP.md                  # OAuth configuration guide
├── TESTING_GUIDE.md               # Testing instructions
└── LICENSE                        # MIT license

```

## Directory Purposes

**`backend/app/`**
- Purpose: Main FastAPI application package
- Contains: API routes, authentication, ML logic, database models, configuration
- Key files: `main.py` (app creation), `config.py` (settings), `database.py` (ORM setup)

**`backend/app/api/`**
- Purpose: HTTP endpoint handlers grouped by feature domain
- Contains: routes.py (movies), auth_routes.py (auth), user_routes.py (user-specific)
- Pattern: Each file has APIRouter with related endpoints, included with prefix in main.py

**`backend/app/auth/`**
- Purpose: Authentication and authorization utilities
- Contains: security.py (JWT, password hashing), schemas.py (auth Pydantic models), oauth.py (OAuth provider setup)
- Usage: Imported by routes for token validation and user dependency injection

**`backend/app/ml/`**
- Purpose: Machine learning recommendation engine
- Contains: recommender.py (core logic), preprocessing.py (data pipeline), movie_data.pkl (processed data)
- Pipeline: preprocessing.py loads CSVs → extracts features → computes cosine similarity → saves pickle
- Runtime: recommender.py loads pickle on startup, provides recommendation methods

**`frontend/src/pages/`**
- Purpose: Full-page components matching route paths
- Contains: One JSX per route (Home, Recommendations, Watchlist, etc.)
- Pattern: Pages import components, contexts, services; handle layout and data fetching

**`frontend/src/context/`**
- Purpose: Global state management via React Context API
- Contains: AuthContext (user, login, logout), WatchlistContext (watchlist cache)
- Usage: Wrapped around <App> in main, consumed via useAuth() or useWatchlist() hooks

**`frontend/src/services/`**
- Purpose: Axios API clients and API communication layer
- Contains: api.js (movie endpoints), authAPI.js (auth endpoints)
- Pattern: Singleton axios instances with base URLs, export named methods for each endpoint

**`data/`**
- Purpose: Raw CSV data source (not committed to git, provided separately)
- Contains: tmdb_5000_movies.csv (5000 movies with metadata), tmdb_5000_credits.csv (cast/crew)
- Usage: preprocessing.py reads from here, generates movie_data.pkl

## Key File Locations

**Entry Points:**

- **Backend:** `backend/app/main.py` - FastAPI app creation, starts on `uvicorn app.main:app --reload`
- **Frontend:** `frontend/src/main.jsx` - React root, runs on `npm run dev` (Vite)
- **Data Setup:** `backend/app/ml/preprocessing.py` - One-time script to generate `movie_data.pkl`

**Configuration:**

- `backend/app/config.py` - Settings class, .env file loading, TMDB API, database URL, JWT secrets
- `frontend/package.json` - Dependencies, dev/build scripts
- `frontend/vite.config.js` - Vite dev server port, React plugin
- `frontend/tailwind.config.js` - Tailwind CSS theme customization

**Core Logic:**

- `backend/app/ml/recommender.py` - Content-based and mood-based recommendation algorithms
- `backend/app/auth/security.py` - Password hashing, JWT creation/validation
- `backend/app/models_db.py` - User, WatchlistItem, MovieRating ORM models
- `frontend/src/context/AuthContext.jsx` - Auth state management
- `frontend/src/services/api.js` - Movie API client

**Testing & Debug:**

- `backend/test_auth.py` - Manual test for auth endpoints
- `backend/test_setup.py` - Manual test for system setup
- `backend/debug_config.py` - Utility to print current config

## Naming Conventions

**Python Files:**
- Modules: `snake_case` (e.g., `auth_routes.py`, `movie_data.pkl`)
- Classes: `PascalCase` (e.g., `MovieRecommender`, `User`, `WatchlistItem`)
- Functions/methods: `snake_case` (e.g., `get_recommender()`, `verify_password()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `TMDB_API_KEY`, `DATABASE_URL`)

**React/JavaScript Files:**
- Components: `PascalCase` (e.g., `Home.jsx`, `MovieCard.jsx`, `AuthContext.jsx`)
- Functions: `camelCase` (e.g., `getContentRecommendations()`, `getCurrentUser()`)
- Constants: `UPPER_SNAKE_CASE` or `camelCase` depending on scope
- Files: Match component name when single-component file (e.g., `Home.jsx` for Home component)

**Directories:**
- Feature-based grouping: `api/`, `auth/`, `ml/` in backend; `pages/`, `context/`, `services/` in frontend
- Lowercase, plural for collections: `pages/`, `components/`, `services/`

**API Endpoints:**
- REST paths: kebab-case (e.g., `/api/movies/search`, `/api/recommendations/content-based`)
- Prefixed by domain: `/api/auth/...`, `/api/user/...`, `/api/movies/...`

## Where to Add New Code

**New Movie Recommendation Feature:**
- Logic: Add method to `backend/app/ml/recommender.py` (class MovieRecommender)
- Endpoint: Add route to `backend/app/api/routes.py` (router for /recommendations/*)
- Frontend: Add page in `frontend/src/pages/` or integrate into existing page, add service method in `frontend/src/services/api.js`

**New User Feature (Watchlist Item, Rating, Profile):**
- Database: Add model class to `backend/app/models_db.py`
- Endpoint: Add route to `backend/app/api/user_routes.py` (requires auth)
- Schema: Add Pydantic model to endpoint file or `backend/app/models.py`
- Frontend: Add context to `frontend/src/context/` if state-sharing needed, add page to `frontend/src/pages/`

**New Authentication Method (OAuth, SAML):**
- Logic: Add to `backend/app/auth/oauth.py` or new file `backend/app/auth/saml.py`
- Routes: Add callback endpoint to `backend/app/api/auth_routes.py`
- Frontend: Add login provider button to `frontend/src/pages/Login.jsx`

**Shared Utilities:**
- Backend helpers: `backend/app/utils/` (new directory) for non-core utilities
- Frontend hooks: `frontend/src/hooks/` (new directory) for custom React hooks
- Frontend utilities: `frontend/src/utils/` for non-API helper functions

**Tests:**
- Backend unit tests: `backend/tests/` directory (mirror src structure)
- Backend integration tests: `backend/tests/integration/`
- Frontend tests: `frontend/src/__tests__/` (co-locate or separate)
- Test naming: `test_<module>.py` for Python, `<component>.test.jsx` for React

## Special Directories

**`backend/venv/`**
- Purpose: Python virtual environment
- Generated: Yes (created by `python -m venv venv`)
- Committed: No (.gitignore excludes)
- Usage: Activate with `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

**`frontend/node_modules/`**
- Purpose: NPM package dependencies
- Generated: Yes (created by `npm install`)
- Committed: No (.gitignore excludes)
- Usage: Install with `npm install` after cloning

**`backend/app/ml/movie_data.pkl`**
- Purpose: Serialized preprocessed movie data (DataFrame + cosine similarity matrix)
- Generated: Yes (by running `python backend/app/ml/preprocessing.py`)
- Committed: No (too large, .gitignore excludes)
- Dependency: Required for recommender to run; setup script should generate it

**`.planning/codebase/`**
- Purpose: GSD planning documents (ARCHITECTURE.md, STRUCTURE.md, etc.)
- Generated: Yes (by `gsd` commands)
- Committed: Yes (documents are readable reference material)

**`data/`**
- Purpose: Raw TMDB CSV files (source data)
- Generated: No (user-provided)
- Committed: No (too large, .gitignore excludes)
- Dependency: Required before preprocessing; mentioned in SETUP_GUIDE.md

---

*Structure analysis: 2026-02-21*
