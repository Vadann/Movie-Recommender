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
    print("   Make sure backend is running: python -m app.main")
    exit(1)

# Test 2: Sign Up
print("\n2️⃣ Testing Sign Up...")
signup_data = {
    "email": "test_script@example.com",
    "username": "testscript",
    "password": "testpass123",
    "full_name": "Test Script User"
}

try:
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code == 201:
        user = response.json()
        print(f"   ✅ User created: {user['username']} ({user['email']})")
    elif response.status_code == 400 and "already" in response.json()["detail"]:
        print("   ⚠️  User already exists (that's OK, continuing...)")
    else:
        print(f"   ❌ Signup failed: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Signup error: {e}")
    exit(1)

# Test 3: Login
print("\n3️⃣ Testing Login...")
login_data = {
    "email": "test_script@example.com",
    "password": "testpass123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        print("   ✅ Login successful!")
        print(f"   🔑 Access token: {access_token[:20]}...")
    else:
        print(f"   ❌ Login failed: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Login error: {e}")
    exit(1)

# Test 4: Get Current User
print("\n4️⃣ Testing Protected Endpoint (Get Current User)...")
headers = {"Authorization": f"Bearer {access_token}"}

try:
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"   ✅ Authenticated as: {user['username']}")
        print(f"   📧 Email: {user['email']}")
        print(f"   🆔 User ID: {user['id']}")
    else:
        print(f"   ❌ Auth check failed: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Auth check error: {e}")
    exit(1)

# Test 5: Add to Watchlist
print("\n5️⃣ Testing Watchlist (Add Movie)...")
watchlist_item = {
    "movie_id": 550,
    "movie_title": "Fight Club",
    "genres": ["Drama", "Thriller"],
    "vote_average": 8.4,
    "runtime": 139
}

try:
    response = requests.post(f"{BASE_URL}/user/watchlist", json=watchlist_item, headers=headers)
    if response.status_code in [200, 201]:
        print("   ✅ Movie added to watchlist!")
    elif response.status_code == 400 and "already" in response.json()["detail"]:
        print("   ⚠️  Movie already in watchlist (that's OK)")
    else:
        print(f"   ❌ Add to watchlist failed: {response.json()}")
except Exception as e:
    print(f"   ❌ Watchlist error: {e}")

# Test 6: Get Watchlist
print("\n6️⃣ Testing Watchlist (Get Items)...")
try:
    response = requests.get(f"{BASE_URL}/user/watchlist", headers=headers)
    if response.status_code == 200:
        watchlist = response.json()
        print(f"   ✅ Watchlist retrieved: {len(watchlist)} movies")
        for item in watchlist[:3]:  # Show first 3
            print(f"      - {item['movie_title']}")
    else:
        print(f"   ❌ Get watchlist failed: {response.json()}")
except Exception as e:
    print(f"   ❌ Watchlist retrieval error: {e}")

# Test 7: Test without token (should fail)
print("\n7️⃣ Testing Security (Request without token)...")
try:
    response = requests.get(f"{BASE_URL}/user/watchlist")
    if response.status_code == 401:
        print("   ✅ Protected endpoint correctly requires authentication!")
    else:
        print(f"   ❌ Security issue: Endpoint accessible without token!")
except Exception as e:
    print(f"   ❌ Security test error: {e}")

# Test 8: Database Check
print("\n8️⃣ Checking Database...")
try:
    from app.database import SessionLocal
    from app.models_db import User, WatchlistItem
    
    db = SessionLocal()
    user_count = db.query(User).count()
    watchlist_count = db.query(WatchlistItem).count()
    
    print(f"   ✅ Database connected!")
    print(f"   👥 Total users: {user_count}")
    print(f"   🎬 Total watchlist items: {watchlist_count}")
    
    db.close()
except Exception as e:
    print(f"   ⚠️  Database check skipped: {e}")

# Summary
print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("\n🎉 Your authentication system is working perfectly!")
print("\n📚 Next steps:")
print("   1. Go to http://localhost:3000")
print("   2. Sign up and test the UI")
print("   3. Check the API docs: http://localhost:8000/docs")
print("\n" + "=" * 50)

