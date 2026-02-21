# Technology Stack

**Analysis Date:** 2026-02-21

## Languages

**Primary:**
- Python 3.x - Backend API and ML recommendation engine
- JavaScript/JSX - Frontend React application

**Secondary:**
- SQL - Database queries and schema

## Runtime

**Environment:**
- Node.js (for frontend development)
- Python 3.x (for backend)

**Package Manager:**
- npm (for frontend) - Lockfile: `frontend/package-lock.json` present
- pip (for backend) - Requirements files: `backend/requirements.txt`

## Frameworks

**Core:**
- FastAPI 0.104.1 - REST API framework for Python backend at `backend/app/main.py`
- React 18.2.0 - Frontend UI framework at `frontend/src/App.jsx`
- React Router DOM 6.20.1 - Frontend routing

**Testing:**
- Test files present: `backend/test_auth.py`, `backend/test_setup.py` (unit tests)

**Build/Dev:**
- Vite 5.0.8 - Frontend build tool and dev server configured at `frontend/vite.config.js`
- Uvicorn 0.24.0 - ASGI server for FastAPI at `backend/app/main.py`

## Key Dependencies

**Critical:**
- pandas 2.1.3 - Data manipulation for ML recommendations at `backend/app/ml/recommender.py`
- scikit-learn 1.3.2 - Machine learning library for content-based recommendations
- numpy 1.26.2 - Numerical computing for ML operations
- SQLAlchemy 2.0.23 - ORM for database interactions at `backend/app/database.py`
- Pydantic 2.5.0 - Data validation and settings management at `backend/app/config.py`

**Infrastructure:**
- asyncpg 0.29.0 - PostgreSQL async driver for Python
- psycopg2-binary 2.9.9 - PostgreSQL adapter for Python
- alembic 1.13.0 - Database migration tool
- axios 1.6.2 - HTTP client for frontend API calls at `frontend/src/services/api.js`

**Authentication & Security:**
- python-jose 3.3.0 - JWT token generation and verification at `backend/app/auth/security.py`
- passlib 1.7.4 - Password hashing framework
- authlib 1.2.1 - OAuth2 support for third-party authentication
- python-multipart 0.0.6 - Multipart form data parsing

**Styling & UI:**
- Tailwind CSS 3.3.6 - Utility-first CSS framework at `frontend/tailwind.config.js`
- PostCSS 8.4.32 - CSS processing tool at `frontend/postcss.config.js`
- Autoprefixer 10.4.16 - Vendor prefix automation
- lucide-react 0.294.0 - Icon library for React components

**Development:**
- ESLint 8.55.0 - JavaScript linting at `frontend/package.json`
- @vitejs/plugin-react 4.2.1 - Vite React plugin
- TypeScript types (@types/react, @types/react-dom) - Type definitions for React

**Utilities:**
- httpx 0.25.2 - HTTP client for backend API calls to TMDB
- python-dotenv 1.0.0 - Environment variable management at `backend/app/config.py`

## Configuration

**Environment:**
- Backend uses `.env` file at `backend/.env` for configuration
- Frontend environment variables managed through Vite (no .env required in current setup)
- Configuration class: `Settings` at `backend/app/config.py` using Pydantic BaseSettings

**Build:**
- Frontend: Vite configuration at `frontend/vite.config.js`
- Tailwind CSS config at `frontend/tailwind.config.js`
- PostCSS config at `frontend/postcss.config.js`
- Backend: No explicit build config (Python runtime directly executes code)

## Platform Requirements

**Development:**
- Python 3.x
- Node.js (for npm)
- SQLite for development database (`backend/movie_recommender.db`)

**Production:**
- Python 3.x runtime
- Node.js (for frontend builds)
- PostgreSQL database (configured in `backend/app/config.py` as production option)
- Web server (typically Nginx/Apache with Uvicorn for backend, static hosting for frontend)

## Database Configuration

**Default Development:**
- SQLite: `sqlite:///./movie_recommender.db` (local file-based)

**Production:**
- PostgreSQL: Configured in `backend/app/config.py`
- Connection string: `postgresql+asyncpg://user:password@localhost:5432/movie_recommender`
- ORM: SQLAlchemy 2.0.23 with async support

---

*Stack analysis: 2026-02-21*
