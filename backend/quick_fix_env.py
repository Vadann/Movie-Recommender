"""
Quick script to create/fix your .env file
Run: python quick_fix_env.py
"""

import secrets
from pathlib import Path

print("🔧 Fixing .env configuration...\n")

# Generate a secure secret key
secret_key = secrets.token_urlsafe(32)

env_content = f"""# TMDB API Configuration (optional)
TMDB_API_KEY=

# Database Configuration
DATABASE_URL=sqlite:///./movie_recommender.db

# JWT Authentication (REQUIRED)
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Configuration (optional - for Google login)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
"""

env_file = Path(".env")

if env_file.exists():
    print("⚠️  .env file already exists!")
    response = input("Do you want to overwrite it? (yes/no): ")
    if response.lower() != 'yes':
        print("\n✅ Keeping existing .env file")
        print("But here's your new SECRET_KEY if you need it:")
        print(f"\nSECRET_KEY={secret_key}")
        exit()

with open(env_file, 'w') as f:
    f.write(env_content)

print("✅ .env file created successfully!")
print(f"\n📝 Your new SECRET_KEY: {secret_key}")
print("\n🎯 Next steps:")
print("1. If you have a TMDB API key, add it to the .env file")
print("2. Restart your backend: python -m app.main")
print("3. Try signing up again!")


