# Codebase Concerns

**Analysis Date:** 2026-02-21

## Tech Debt

**Hardcoded Default JWT Secret Key:**
- Issue: Default secret key "your-secret-key-change-this-in-production" used in production code
- Files: `backend/app/config.py` (line 16)
- Impact: Any attacker can forge valid JWT tokens without knowing the actual secret, allowing unauthorized access to user accounts and protected endpoints
- Fix approach: Enforce SECRET_KEY configuration from environment variables with validation that it differs from default on startup

**Broad Exception Catching:**
- Issue: Multiple locations catch all exceptions with bare `except Exception:` blocks without specific error logging
- Files:
  - `backend/app/auth/security.py` (lines 63, 88)
  - `backend/app/api/auth_routes.py` (line 180)
  - `backend/app/ml/recommender.py` (lines 219, 242)
- Impact: Swallows critical errors, makes debugging difficult, masks security issues, hides data corruption
- Fix approach: Replace with specific exception types (e.g., `except jwt.PyJWTError:`, `except SQLAlchemyError:`), add proper logging for each exception type

**Debug Print Statements in Production Code:**
- Issue: Excessive `print()` calls for logging user data and system state
- Files:
  - `backend/app/api/user_routes.py` (lines 79, 80, 89, 110, 114)
  - `backend/app/main.py` (lines 27-28)
  - `backend/app/database.py` (line 30)
- Impact: Sensitive user information (usernames, IDs, error details) printed to stdout, performance overhead, not suitable for production logging
- Fix approach: Replace with structured logging using Python's `logging` module with proper log levels and handlers

**Hardcoded Localhost Origins in CORS Configuration:**
- Issue: CORS allows only localhost:3000 and localhost:5173 hardcoded in code
- Files:
  - `backend/app/main.py` (line 17)
  - `backend/app/config.py` (line 27)
- Impact: Must modify code to deploy to production; frontend and backend URLs are environment-dependent
- Fix approach: Make CORS origins configurable via environment variables, with fallback defaults only for development

**Duplicate Authentication/Security Implementations:**
- Issue: Two separate security implementations (security.py and security_minimal.py) creating maintenance burden
- Files:
  - `backend/app/auth/security.py` (105 lines)
  - `backend/app/auth/security_minimal.py` (104 lines)
- Impact: Code duplication, inconsistent token handling logic, difficult to maintain both versions
- Fix approach: Consolidate into single implementation, remove minimal version if not actively used

**Multiple Duplicated Requirements Files:**
- Issue: Four different requirements files with unclear purpose and potential inconsistency
- Files:
  - `backend/requirements.txt`
  - `backend/requirements-minimal.txt`
  - `backend/requirements-simple.txt`
  - `backend/requirements-working.txt`
- Impact: Unclear which to use, risk of dependency version conflicts, maintenance overhead
- Fix approach: Keep single requirements.txt with clear extras (e.g., `pip install -r requirements.txt[dev]` or `[prod]`)

**Streaming API Response without Proper Content-Type:**
- Issue: `/watchlist/stats` endpoint accepts `List[int]` via POST but passes movieIds directly to API without proper serialization
- Files: `frontend/src/services/api.js` (line 78)
- Impact: Potential request format issues with some servers
- Fix approach: Ensure movieIds is properly serialized as JSON array

## Known Bugs

**Version Number Mismatch:**
- Symptoms: API returns version "1.0.0" in root response but FastAPI title shows "2.0.0"
- Files: `backend/app/main.py` (lines 10, 40)
- Trigger: Call `GET /` endpoint, observe inconsistent version
- Workaround: Manually track which version is correct in documentation

**OAuth Callback Routes Not Implemented:**
- Symptoms: OAuth routes exist but return placeholder messages
- Files: `backend/app/api/auth_routes.py` (lines 198-213)
- Trigger: Attempt to use Google OAuth login
- Workaround: Use email/password authentication only; OAuth infrastructure exists but incomplete

**Potential Database Connection Issue with Mixed Async/Sync:**
- Symptoms: FastAPI uses async/await but SQLAlchemy SessionLocal is synchronous
- Files: `backend/app/database.py` (line 15)
- Trigger: High-concurrency scenarios may expose threading issues
- Workaround: Application currently works but not optimal for async performance

## Security Considerations

**JWT Token Validation Too Permissive:**
- Risk: `decode_token()` function catches all exceptions and returns generic 401, but doesn't validate token type field strictly in all paths
- Files: `backend/app/auth/security.py` (lines 58-68)
- Current mitigation: Token type is checked in refresh endpoint (line 147 of auth_routes.py) but not in general decode
- Recommendations: Always validate token type in decode_token(), reject unknown token types immediately

**Hardcoded API Endpoints on Frontend:**
- Risk: Frontend API_BASE_URL hardcoded to localhost:8000, won't work in production or different environments
- Files: `frontend/src/services/api.js` (line 3)
- Current mitigation: Works for local development only
- Recommendations: Use environment variables (e.g., `import.meta.env.VITE_API_BASE_URL`) or runtime config

**No Rate Limiting on Authentication Endpoints:**
- Risk: Brute force attacks possible on login, signup, and token endpoints
- Files:
  - `backend/app/api/auth_routes.py` (lines 26, 64, 102, 138)
  - Backend routes have no rate limiting middleware
- Current mitigation: None
- Recommendations: Add `slowapi` or similar rate limiting library, limit login attempts to 5/minute per IP

**Refresh Token Not Invalidated on Logout:**
- Risk: Tokens remain valid after logout; users can continue using expired refresh tokens
- Files: `backend/app/api/auth_routes.py` (lines 191-195)
- Current mitigation: Logout returns success message but tokens still valid in JWT
- Recommendations: Maintain token blacklist in database, check against it on every request

**No Input Validation on User Ratings:**
- Risk: Rating field accepts any float value without bounds checking
- Files:
  - `backend/app/api/user_routes.py` (line 42)
  - `backend/app/models_db.py` (line 65)
- Current mitigation: None
- Recommendations: Validate rating is between 0.0-10.0, add Pydantic Field constraints

**SQL Injection Risk in Watchlist Genres Storage:**
- Risk: Genres stored as comma-separated string instead of proper JSON or separate table
- Files:
  - `backend/app/models_db.py` (line 44)
  - `backend/app/api/user_routes.py` (line 101)
- Current mitigation: Using ORM (SQLAlchemy) partially mitigates, but data structure is fragile
- Recommendations: Use JSON column type or create WatchlistGenre junction table

**No HTTPS Enforcement:**
- Risk: All connections over HTTP in development, will expose auth tokens in transit
- Files: `backend/app/config.py` (line 24)
- Current mitigation: Localhost development only
- Recommendations: Configure HTTPS in production, add HSTS headers

## Performance Bottlenecks

**Global Recommender Instance Never Reloaded:**
- Problem: ML model loaded once at startup and cached globally; new movies/data requires restart
- Files: `backend/app/ml/recommender.py` (lines 247-258)
- Cause: `_recommender_instance` is module-level singleton with no refresh mechanism
- Improvement path: Add cache invalidation strategy, consider periodic reload or on-demand hot-swapping

**Cosine Similarity Matrix Computed at Preprocessing Time:**
- Problem: Entire similarity matrix precomputed and pickled; 5000+ movies = millions of values in memory
- Files: `backend/app/ml/preprocessing.py` (lines 79-87)
- Cause: ContentBasedFiltering loads full matrix into RAM
- Improvement path: Lazy-load matrix, compute similarities on-demand with caching, or use approximate nearest neighbors (Annoy/Faiss)

**No Database Connection Pooling Configuration:**
- Problem: SessionLocal created without pool size limits; high concurrency can exhaust connections
- Files: `backend/app/database.py` (lines 9-13)
- Cause: Default SQLAlchemy pool configuration
- Improvement path: Set `pool_size=20, max_overflow=40` in engine creation, add connection pool monitoring

**Pandas DataFrame Iteration in Recommendation Logic:**
- Problem: Multiple `.iterrows()` calls which are notoriously slow in pandas
- Files:
  - `backend/app/ml/recommender.py` (lines 122-124, 153, 162)
  - `backend/app/ml/preprocessing.py` (lines 25, 36)
- Cause: Using pandas API inefficiently instead of vectorized operations
- Improvement path: Use `.apply()` with vectorized operations, or convert to numpy arrays for iteration

**Frontend Makes Separate API Calls for Watchlist Stats:**
- Problem: Calculates stats client-side instead of delegating to server; extra round-trip
- Files: `frontend/src/pages/Watchlist.jsx` likely duplicates `/api/watchlist/stats` logic
- Cause: Stats endpoint exists but frontend may not use it
- Improvement path: Ensure frontend always calls dedicated stats endpoint

## Fragile Areas

**Movie Data Pipeline is Tightly Coupled:**
- Files:
  - `backend/app/ml/preprocessing.py` (creates pickle)
  - `backend/app/ml/recommender.py` (loads pickle)
  - `backend/app/api/routes.py` (accesses raw recommender)
- Why fragile: CSV format changes, pickle format incompatibility, no schema validation
- Safe modification:
  - Add pydantic models to validate data shape
  - Add version number to pickle file
  - Create abstraction layer between routes and recommender
- Test coverage: No tests for preprocessing pipeline or data loading

**String-Based Genre/Keyword Storage:**
- Files:
  - `backend/app/models_db.py` (lines 44, 65)
  - `backend/app/ml/preprocessing.py` (lines 42, 45)
  - Frontend JSON handling
- Why fragile: No schema enforcement, easy to introduce inconsistent formats (comma vs pipe separated)
- Safe modification: Use JSON columns with schema validation, or create proper junction tables
- Test coverage: No tests for genre parsing/storage

**Frontend Authentication Context Swallows Errors:**
- Files: `frontend/src/context/AuthContext.jsx` (lines 29-31)
- Why fragile: Auth check failure is silently caught and logged to console only
- Safe modification: Add proper error boundaries, user notifications, and specific error handling
- Test coverage: No tests for auth context error states

**Hardcoded Mood-to-Genre Mappings:**
- Files: `backend/app/ml/recommender.py` (lines 18-26)
- Why fragile: If movie genres change or new moods needed, must modify code and redeploy
- Safe modification: Move to database table, load on startup, cache with invalidation
- Test coverage: No tests validating mood mappings return reasonable movies

## Scaling Limits

**Pickle File Size Grows Linearly with Movies:**
- Current capacity: ~5000 movies (est. 50-100MB pickle file based on similarity matrix)
- Limit: Approaching 1GB+ with movie databases of 100k+; memory requirements become prohibitive
- Scaling path:
  1. Switch to approximate nearest neighbors (Annoy/Faiss) with disk-based indices
  2. Implement incremental model updates (add new movies without full recompute)
  3. Consider distributed similarity computation (Spark/Ray)

**SQLite Database Not Suitable for Production:**
- Current capacity: SQLite fine for <1000 concurrent users, single writer
- Limit: Write-lock contention if multiple API instances, no replication
- Scaling path: Migrate to PostgreSQL (already in requirements), configure connection pooling, add read replicas

**Frontend Renders All Watchlist Items at Once:**
- Current capacity: Likely 10,000+ items causes UI lag
- Limit: Virtual scrolling not implemented
- Scaling path: Add pagination or infinite scroll with lazy loading

**No Caching Layer for API Responses:**
- Current capacity: Backend recomputes recommendations on every request
- Limit: 100+ concurrent users cause CPU/memory spikes
- Scaling path: Add Redis caching for popular movies (1 hour TTL), mood recommendations (30 min TTL)

## Dependencies at Risk

**PyJWT Old Pattern Usage:**
- Risk: Uses `jwt.encode()` which may change behavior in newer versions
- Impact: Token format could change in jwt 3.0+
- Migration plan: Test with `python-jose` as alternative (more actively maintained), pin jwt version <3.0

**Passlib with pbkdf2_sha256:**
- Risk: Using `passlib[bcrypt]` but not actual bcrypt; slower than bcrypt
- Impact: Password hashing takes 100ms+ per request
- Migration plan: Switch to bcrypt scheme in passlib config (already installed but not used)

**Asyncpg but Sync ORM Session:**
- Risk: Dependency mismatch - asyncpg requires async SQLAlchemy but code uses sync Session
- Impact: Async features not utilized, potential deadlocks under load
- Migration plan: Migrate to SQLAlchemy 2.0 async session (AsyncSession), make all DB operations async

## Missing Critical Features

**No Email Verification:**
- Problem: Users marked is_verified=False but never verified; no email sending code
- Blocks: Production security, password reset flows, email-based notifications
- Priority: High for production deployment

**Incomplete OAuth Implementation:**
- Problem: OAuth routes return placeholder messages, Google credentials not integrated
- Blocks: Social login feature, multi-provider auth
- Priority: Medium (basic auth works, but feature incomplete)

**No Database Migrations:**
- Problem: Alembic imported in requirements but not configured; schema changes require manual SQL
- Blocks: Database version control, safe schema evolution, deployment consistency
- Priority: High for production

**No API Documentation for Frontend:**
- Problem: API contracts not formally documented; OpenAPI available but frontend doesn't validate
- Blocks: Frontend type safety, API contract testing, consumer-driven development
- Priority: Medium

## Test Coverage Gaps

**No Unit Tests for ML Recommender:**
- What's not tested:
  - `search_movies()` fuzzy matching quality
  - `get_content_based_recommendations()` accuracy
  - `get_mood_based_recommendations()` mood filtering
  - Edge cases (empty results, invalid moods)
- Files: `backend/app/ml/recommender.py` (259 lines, 0 tests)
- Risk: Recommendation algorithm breaks silently, users get poor results
- Priority: High

**No Integration Tests for Authentication Flow:**
- What's not tested:
  - Full signup → login → protected endpoint flow
  - Token refresh cycle
  - Logout and token invalidation
  - Concurrent auth requests
- Files: `backend/app/api/auth_routes.py` (214 lines, basic test_auth.py only)
- Risk: Auth bugs only discovered in production
- Priority: High

**No Tests for Watchlist Operations:**
- What's not tested:
  - Adding/removing items
  - Duplicate prevention
  - Stats calculation accuracy
  - Concurrent watchlist modifications
- Files: `backend/app/api/user_routes.py` (258 lines, 0 automated tests)
- Risk: Data corruption, incorrect stats in production
- Priority: High

**No Frontend Component Tests:**
- What's not tested:
  - MovieCard rendering with various data
  - Watchlist state management
  - Auth context state transitions
  - Error handling in API calls
- Files: `frontend/src/components/` and `frontend/src/pages/` (no .test.jsx files)
- Risk: UI breaks silently, hard to refactor
- Priority: Medium

**No End-to-End Tests:**
- What's not tested:
  - Complete user flows (search → recommend → add watchlist)
  - Cross-browser compatibility
  - Responsive design
  - API error handling
- Files: No cypress/playwright/e2e tests
- Risk: Breaking changes only found by manual QA
- Priority: Medium

---

*Concerns audit: 2026-02-21*
