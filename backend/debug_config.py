"""
Debug script to check your configuration
Run: python debug_config.py
"""

print("🔍 Checking Configuration...\n")
print("=" * 50)

# Check 1: Environment file
import os
from pathlib import Path

env_file = Path(".env")
if env_file.exists():
    print("✅ .env file exists")
    with open(env_file, 'r') as f:
        content = f.read()
        if "SECRET_KEY" in content:
            if "change-this" in content or "your-secret-key" in content:
                print("❌ SECRET_KEY not set properly!")
                print("\n🔧 FIX:")
                print("1. Run this command:")
                print('   python -c "import secrets; print(secrets.token_urlsafe(32))"')
                print("2. Copy the output")
                print("3. Add to .env file: SECRET_KEY=<paste_here>")
            else:
                print("✅ SECRET_KEY is set")
        else:
            print("❌ SECRET_KEY not found in .env")
else:
    print("❌ .env file not found!")
    print("\n🔧 FIX: Create a .env file with:")
    print("SECRET_KEY=your_secret_key_here")
    print("DATABASE_URL=sqlite:///./movie_recommender.db")

# Check 2: Try to import config
print("\n" + "=" * 50)
print("Checking app configuration...")
try:
    from app.config import get_settings
    settings = get_settings()
    print("✅ Config loaded successfully")
    
    if settings.SECRET_KEY and settings.SECRET_KEY != "your-secret-key-change-this-in-production":
        print("✅ SECRET_KEY is configured")
    else:
        print("❌ SECRET_KEY is not properly set!")
        print("\n🔧 URGENT FIX NEEDED:")
        import secrets
        new_key = secrets.token_urlsafe(32)
        print(f"\nAdd this to your .env file:")
        print(f"SECRET_KEY={new_key}")
        
    print(f"✅ Database: {settings.DATABASE_URL}")
    
except Exception as e:
    print(f"❌ Config error: {e}")

# Check 3: Database
print("\n" + "=" * 50)
print("Checking database...")
try:
    from app.database import SessionLocal, init_db
    from app.models_db import User
    
    # Try to initialize
    init_db()
    print("✅ Database initialized")
    
    # Try to query
    db = SessionLocal()
    user_count = db.query(User).count()
    print(f"✅ Database accessible ({user_count} users)")
    db.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
    print("\n🔧 FIX: Make sure you installed all dependencies:")
    print("pip install sqlalchemy passlib bcrypt")

# Check 4: Auth modules
print("\n" + "=" * 50)
print("Checking authentication modules...")
try:
    from app.auth.security import get_password_hash, verify_password
    
    # Test password hashing
    test_password = "test123"
    hashed = get_password_hash(test_password)
    is_valid = verify_password(test_password, hashed)
    
    if is_valid:
        print("✅ Password hashing works")
    else:
        print("❌ Password hashing failed")
        
except Exception as e:
    print(f"❌ Auth module error: {e}")
    print("\n🔧 FIX: Install missing packages:")
    print("pip install passlib bcrypt")

# Check 5: JWT
print("\n" + "=" * 50)
print("Checking JWT token creation...")
try:
    from app.auth.security import create_access_token
    
    test_token = create_access_token(data={"sub": 1})
    if test_token:
        print("✅ JWT token creation works")
        print(f"   Sample token: {test_token[:30]}...")
    else:
        print("❌ JWT token creation failed")
        
except Exception as e:
    print(f"❌ JWT error: {e}")
    print("\n🔧 FIX:")
    if "SECRET_KEY" in str(e) or "NoneType" in str(e):
        print("SECRET_KEY is missing or invalid!")
        import secrets
        new_key = secrets.token_urlsafe(32)
        print(f"\nAdd this to your .env file:")
        print(f"SECRET_KEY={new_key}")
    else:
        print("Install JWT package:")
        print("pip install PyJWT")

# Summary
print("\n" + "=" * 50)
print("SUMMARY:")
print("=" * 50)
print("\nIf you see any ❌ above, follow the 🔧 FIX instructions!")
print("\nOnce all checks pass, restart your backend:")
print("  python -m app.main")
print("\nThen try signing up again!")

