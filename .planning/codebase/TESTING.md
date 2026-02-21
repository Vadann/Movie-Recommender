# Testing Patterns

**Analysis Date:** 2026-02-21

## Test Framework

**Runner:**
- Backend: pytest (inferred from requirements-dev.txt, not explicitly detected in setup)
- Frontend: Not configured - no testing framework detected
- Config: No pytest.ini or setup.cfg found

**Assertion Library:**
- Backend: Standard pytest assertions (if tests exist)
- Frontend: Not applicable

**Run Commands:**
```bash
# Backend - Manual testing via test_auth.py and test_setup.py
python test_auth.py              # Run auth integration tests
python test_setup.py             # Check setup and dependencies

# Start backend for integration testing
python -m app.main               # Starts server on http://localhost:8000

# Frontend - No test runner configured
npm run dev                       # Start dev server for manual testing
```

## Test File Organization

**Location:**
- Backend: Manual test scripts at project root
  - `test_auth.py` - Authentication and protected endpoint tests
  - `test_setup.py` - Setup verification and configuration tests
  - No unit test files found (no `test_*.py` or `*_test.py` files in app directory)

- Frontend: No test files found
  - Testing not implemented

**Naming:**
- `test_*.py` for manual verification scripts
- Tests are standalone scripts that use requests library to test live API

**Structure:**
```
backend/
├── test_auth.py          # Full auth flow test
├── test_setup.py         # Setup verification
└── app/
    ├── main.py
    ├── api/
    └── ...
```

## Test Structure

**Test Pattern (from `test_auth.py`):**
```python
"""
Quick test script to verify authentication is working
Run: python test_auth.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

print("🧪 Testing Movie Recommender Authentication\n")
print("=" * 50)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("   ✅ Backend is running!")
    else:
        print("   ❌ Backend health check failed")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect to backend: {e}")
    exit(1)
```

**Patterns:**
- Setup: Print section headers with emoji indicators
- Execution: HTTP requests to live API endpoints
- Assertions: Check status codes and response content
- Teardown: Explicit db.close() calls
- Error handling: Try-catch blocks with meaningful error messages
- Exit codes: exit(1) on failure, implicit success at end

## Manual Testing Approach

**Live API Testing:**
Test scripts use `requests` library to make HTTP calls to the actual running FastAPI server:
- No mocking of external services
- Tests are integration tests, not unit tests
- All tests are synchronous (no async test patterns)

**Test Sequence (from `test_auth.py`):**
1. Health check endpoint
2. Sign up with test credentials
3. Login with email/password
4. Access protected endpoint with Bearer token
5. Test watchlist operations (add and retrieve)
6. Test security (request without token should fail)
7. Database verification (count users and watchlist items)

## Coverage Verification

**Requirements:** No automated coverage target
- Manual verification via test scripts
- Tests only verify happy path and basic error handling
- No systematic edge case testing

**View Coverage:**
```bash
# No coverage tool configured
# Manual testing only via test_auth.py and test_setup.py
python test_auth.py
python test_setup.py
```

## Test Types

**Integration Tests:**
- `test_auth.py`: Full authentication flow
  - User signup, login, token validation
  - Protected endpoint access
  - Database persistence verification
  - Security validation (401 without token)

- `test_setup.py`: Environment and setup verification
  - Python version check
  - Required packages verification (FastAPI, Pandas, scikit-learn)
  - .env file presence check
  - Dataset file existence
  - ML model file existence
  - Configuration loading test

**Unit Tests:**
- Not found in codebase
- No isolated component tests

**E2E Tests:**
- Not formally configured
- Manual frontend testing only (no automated E2E framework)
- Frontend can be manually tested via `http://localhost:3000`

## Testing Best Practices Observed

**What IS Being Tested:**
- End-to-end auth flows (signup, login, token usage)
- API response status codes and structure
- Database integration (items are persisted and retrievable)
- Security (protected endpoints reject unauthenticated requests)
- Setup validation (dependencies installed, files present)

**What IS NOT Tested:**
- Individual function/method units
- Edge cases and validation errors
- ML recommendation algorithm correctness
- Frontend components
- Performance/load testing
- API response timing

## Common Patterns in Test Scripts

**Error Handling:**
```python
try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("   ✅ Login successful!")
    else:
        print(f"   ❌ Login failed: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Login error: {e}")
    exit(1)
```

**Conditional Handling:**
```python
elif response.status_code == 400 and "already" in response.json()["detail"]:
    print("   ⚠️  User already exists (that's OK, continuing...)")
```

**Database Testing:**
```python
from app.database import SessionLocal
from app.models_db import User, WatchlistItem

db = SessionLocal()
user_count = db.query(User).count()
watchlist_count = db.query(WatchlistItem).count()
db.close()
```

**API Response Validation:**
```python
response = requests.get(f"{BASE_URL}/user/watchlist", headers=headers)
if response.status_code == 200:
    watchlist = response.json()
    print(f"   ✅ Watchlist retrieved: {len(watchlist)} movies")
```

## Async Testing

**Pattern:** Not used - all tests are synchronous

Test scripts use blocking HTTP requests via `requests` library. No async/await testing patterns found.

## Frontend Testing

**Status:** No testing framework or tests implemented

**Manual Testing Approach:**
- Start dev server: `npm run dev`
- Open http://localhost:3000 in browser
- Manually interact with UI
- Check browser console for errors

## Running All Tests

**Current Workflow:**
```bash
# Terminal 1: Start backend
cd backend
python -m app.main

# Terminal 2: Run verification tests
cd backend
python test_setup.py   # Verify environment
python test_auth.py    # Run auth tests

# Terminal 3: Test frontend (manual)
cd frontend
npm run dev            # Open http://localhost:3000
```

---

*Testing analysis: 2026-02-21*
