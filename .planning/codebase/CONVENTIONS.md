# Coding Conventions

**Analysis Date:** 2026-02-21

## Naming Patterns

**Files:**
- Python modules: snake_case (e.g., `auth_routes.py`, `models_db.py`, `get_password_hash`)
- React components: PascalCase (e.g., `MovieCard.jsx`, `AuthContext.jsx`, `ParticlesBackground.jsx`)
- API routes files: descriptive snake_case (e.g., `auth_routes.py`, `user_routes.py`, `routes.py`)

**Functions:**
- Python functions: snake_case (e.g., `get_current_user()`, `verify_password()`, `search_movies()`)
- Async functions: same snake_case pattern, marked with `async def` (e.g., `async def signup()`, `async def get_user_watchlist()`)
- React hooks: camelCase with "use" prefix (e.g., `useAuth()`, `useContext()`)
- React component functions: PascalCase and uppercase for event handlers (e.g., `NavLink`, `AppContent`)

**Variables:**
- Python: snake_case throughout (e.g., `current_user`, `movie_ids`, `cosine_sim`, `access_token`)
- JavaScript/React: camelCase (e.g., `baseURL`, `movieAPI`, `authAPI`, `tokenUrl`)
- Constants: SCREAMING_SNAKE_CASE (e.g., `API_BASE_URL`, `TMDB_API_KEY`, `ALGORITHM`)
- Private/internal: prefix with underscore (e.g., `_load_data()`, `_format_movie()`)

**Classes/Types:**
- Python SQLAlchemy models: PascalCase (e.g., `User`, `WatchlistItem`, `MovieRating`, `RefreshToken`)
- Pydantic schemas: PascalCase (e.g., `UserResponse`, `Token`, `WatchlistItemCreate`, `RecommendationResponse`)
- React Context: PascalCase (e.g., `AuthContext`, `WatchlistContext`)

## Code Style

**Formatting:**
- Backend: No explicit formatter configured, follows PEP 8 conventions
- Frontend: Uses Tailwind CSS for styling, no explicit formatter detected
- Indentation: 4 spaces for Python, 2 spaces for JavaScript (inferred from codebase)

**Linting:**
- No `.eslintrc` or `.prettierrc` files detected
- Backend linting: Not enforced (no pytest.ini or setup.cfg found)
- Frontend linting: Not enforced (no eslint config found)

**Docstring Style:**
- Python: Triple-quoted docstrings with description and optional Args/Returns sections
  ```python
  def get_content_based_recommendations(self, title: str, n_recommendations: int = 10) -> Tuple[List[dict], List[float]]:
      """
      Get movie recommendations using content-based filtering

      Args:
          title: Movie title to base recommendations on
          n_recommendations: Number of recommendations to return

      Returns:
          Tuple of (recommendations list, similarity scores list)
      """
  ```

## Import Organization

**Order:**
1. Standard library imports (e.g., `from datetime import`, `from typing import`)
2. Third-party framework imports (e.g., `from fastapi import`, `import pandas as pd`)
3. Local app imports (e.g., `from app.config import`, `from app.models import`)

**Pattern in Python (from `auth_routes.py`):**
```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import MovieRecommendationRequest
from app.ml.recommender import get_recommender
```

**Pattern in React (from `App.jsx`):**
```javascript
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Film, TrendingUp, Heart, BarChart3, LogIn, LogOut, User, BookOpen } from 'lucide-react'
import Home from './pages/Home'
import { AuthProvider, useAuth } from './context/AuthContext'
```

**Path Aliases:**
- Python: Relative imports from app root (e.g., `from app.config import get_settings`)
- React: Relative imports from src root (e.g., `from './context/AuthContext'`, `from './pages/Home'`)

## Error Handling

**Patterns:**
- FastAPI endpoints: Raise `HTTPException` with appropriate status codes
  ```python
  if not user:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Incorrect email or password",
          headers={"WWW-Authenticate": "Bearer"},
      )
  ```

- Try-except for external API calls and file operations:
  ```python
  try:
      with open(self.data_path, 'rb') as f:
          self.movies_df, self.cosine_sim = pickle.load(f)
  except FileNotFoundError:
      raise Exception(f"Data file not found at {self.data_path}.")
  ```

- Database operations: Use direct SQLAlchemy queries with no explicit try-catch (errors bubble to FastAPI handler)

- React: Use try-catch in async auth functions, console.error for logging:
  ```javascript
  try {
      checkAuth()
  } catch (error) {
      console.error('Auth check failed:', error)
      authAPI.logout()
  }
  ```

## Logging

**Framework:** console.log and print statements (no structured logging library)

**Patterns:**
- Backend uses print() with emoji prefixes for visual distinction:
  - ✅ Success: `print("✅ Database tables created successfully!")`
  - 🚀 Startup: `print("🚀 Movie Recommender API started!")`
  - 📥 Input: `print(f"📥 Received watchlist item: {item.dict()}")`
  - ⚠️ Warning: `print(f"⚠️  Movie {item.movie_id} already in watchlist")`
  - ❌ Error: `print(f"❌ Error adding to watchlist: {e}")`

- Frontend uses console.error for exceptions and console.log for debug info (seen in AuthContext)

**When to Log:**
- Startup/initialization messages (database init, API startup)
- Data validation and transformation
- External API calls (TMDB requests)
- Authentication state changes
- Database operations (add, update)

## Comments

**When to Comment:**
- Explain "why", not "what" (code should be self-documenting)
- Comment non-obvious logic or workarounds
- Explanatory comments above complex blocks
- Few inline comments observed - code is generally self-explanatory

**Example from codebase (from `database.py`):**
```python
# Create engine (works with both SQLite and PostgreSQL)
```

**JSDoc/TSDoc:**
- Not used in this codebase (no TypeScript or JSDoc patterns observed)
- Python docstrings used for public functions and methods

## Function Design

**Size:** Functions are concise and focused:
- API route handlers: ~5-15 lines (handle request, call service, return)
- Service methods: ~10-30 lines (perform business logic)
- Helper functions: ~5-20 lines

**Parameters:**
- Type hints used throughout Python (e.g., `title: str`, `n_recommendations: int = 10`)
- Pydantic models for complex input validation
- Dependency injection for database sessions and auth (e.g., `db: Session = Depends(get_db)`)
- React functions: Props passed as objects, destructured when needed

**Return Values:**
- Explicit return type hints in Python (e.g., `-> Tuple[List[dict], List[float]]`)
- Pydantic models for API responses (e.g., `response_model=RecommendationResponse`)
- JSON serializable dicts for simple responses
- React: Return JSX or context value objects

## Module Design

**Exports:**
- Python: Module functions/classes are imported directly by name
  ```python
  from app.config import get_settings
  from app.models_db import User, WatchlistItem, MovieRating
  ```

- React: Explicit exports as named functions or default exports
  ```javascript
  export function useAuth() { ... }
  export default api
  ```

**Barrel Files:**
- `__init__.py` files exist but are mostly empty (minimal barrel pattern usage)
- Main app structure uses direct path imports (e.g., `from app.api import routes`)

**File Organization Principles:**
- Separation of concerns: models, routes, services, database access
- One responsibility per module
- Related functionality grouped (auth directory has schemas, security, oauth)
- Tests are co-located with their targets (e.g., `test_auth.py` at project root)

---

*Convention analysis: 2026-02-21*
