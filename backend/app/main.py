from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api import auth_routes, user_routes, analytics_routes
from app.database import init_db
import uvicorn

app = FastAPI(
    title="Movie Recommender API",
    description="ML-powered movie recommendation system with authentication and personalized features",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 Movie Recommender API started!")
    print("📚 API Docs: http://localhost:8000/docs")

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["movies"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["authentication"])
app.include_router(user_routes.router, prefix="/api/user", tags=["user"])
app.include_router(analytics_routes.router, prefix="/api", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "Movie Recommender API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

