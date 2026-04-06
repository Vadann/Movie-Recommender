"""
Quick test script to check if your setup is working
Run this with: python test_setup.py
"""

import sys
from pathlib import Path

print("🔍 Checking Movie Recommender Setup...\n")

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")

# Check if required packages are installed
try:
    import fastapi
    print(f"✓ FastAPI installed: {fastapi.__version__}")
except ImportError:
    print("❌ FastAPI not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pandas
    print(f"✓ Pandas installed: {pandas.__version__}")
except ImportError:
    print("❌ Pandas not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import sklearn
    print(f"✓ scikit-learn installed: {sklearn.__version__}")
except ImportError:
    print("❌ scikit-learn not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Check if .env file exists
env_file = Path("../.env") if Path("../.env").exists() else Path(".env")
if env_file.exists():
    print(f"✓ .env file found at: {env_file}")
    with open(env_file, 'r') as f:
        content = f.read()
        if "TMDB_API_KEY" in content and len(content.split("=")[1].strip()) > 10:
            print("✓ TMDB_API_KEY is set")
        else:
            print("⚠️  TMDB_API_KEY is empty (app will still work with fallback)")
else:
    print("⚠️  .env file not found (app will work without TMDB images)")

# Check if data files exist
data_movies = Path("../../data/tmdb_5000_movies.csv")
data_credits = Path("../../data/tmdb_5000_credits.csv")

if data_movies.exists():
    print(f"✓ Movies dataset found")
else:
    print(f"❌ Movies dataset not found at: {data_movies}")

if data_credits.exists():
    print(f"✓ Credits dataset found")
else:
    print(f"❌ Credits dataset not found at: {data_credits}")

# Check if ML model exists
model_file = Path("app/ml/movie_data.pkl")
if model_file.exists():
    print(f"✓ ML model (movie_data.pkl) found")
    size_mb = model_file.stat().st_size / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")
else:
    print(f"❌ ML model not found. Run: python -m app.ml.preprocessing")

print("\n" + "="*50)

# Test loading the config
try:
    from app.config import get_settings
    settings = get_settings()
    print(f"✓ Config loaded successfully")
    print(f"  TMDB_BASE_URL: {settings.TMDB_BASE_URL}")
    if settings.TMDB_API_KEY:
        print(f"  TMDB_API_KEY: {settings.TMDB_API_KEY[:8]}...{settings.TMDB_API_KEY[-4:]}")
    else:
        print(f"  TMDB_API_KEY: (not set)")
except Exception as e:
    print(f"❌ Error loading config: {e}")

print("\n" + "="*50)
print("\n🚀 Next Steps:")

if not model_file.exists():
    print("1. Generate ML model: python -m app.ml.preprocessing")
    print("2. Start backend: python -m app.main")
else:
    print("1. Start backend: python -m app.main")
    print("2. In another terminal, start frontend: cd ../frontend && npm run dev")
    print("3. Open browser to: http://localhost:3000")

print("\nIf backend fails to load popular movies, it's normal!")
print("The app will use top-rated movies from the dataset instead.")

