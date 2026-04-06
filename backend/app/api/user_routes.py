import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models_db import User, WatchlistItem, MovieRating
from app.auth.security import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic schemas
class WatchlistItemCreate(BaseModel):
    movie_id: int
    movie_title: str
    genres: List[str] = []
    vote_average: Optional[float] = None
    runtime: Optional[int] = None
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"

class WatchlistItemResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    genres: str
    vote_average: Optional[float] = None
    runtime: Optional[int] = None
    added_at: datetime
    
    class Config:
        from_attributes = True

class MovieRatingCreate(BaseModel):
    movie_id: int
    movie_title: str
    rating: float
    review: str = None

class MovieRatingResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    rating: float
    review: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/watchlist", response_model=List[WatchlistItemResponse])
async def get_user_watchlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's watchlist"""
    watchlist = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id
    ).order_by(WatchlistItem.added_at.desc()).all()
    
    return watchlist

@router.post("/watchlist", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a movie to user's watchlist"""
    
    # Check if already in watchlist
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == item.movie_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie already in watchlist"
        )
    
    try:
        watchlist_item = WatchlistItem(
            user_id=current_user.id,
            movie_id=item.movie_id,
            movie_title=item.movie_title,
            genres=",".join(item.genres) if item.genres else "",
            vote_average=item.vote_average if item.vote_average else None,
            runtime=item.runtime if item.runtime else None
        )
        
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)
        return watchlist_item

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to watchlist: {str(e)}"
        )

@router.delete("/watchlist/{movie_id}")
async def remove_from_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a movie from user's watchlist"""
    
    watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == movie_id
    ).first()
    
    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not in watchlist"
        )
    
    db.delete(watchlist_item)
    db.commit()
    
    return {"message": "Movie removed from watchlist"}

@router.get("/watchlist/stats")
async def get_watchlist_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics about user's watchlist"""
    
    watchlist = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id
    ).all()
    
    if not watchlist:
        return {
            "total_movies": 0,
            "total_runtime": 0,
            "genre_distribution": {},
            "average_rating": 0.0
        }
    
    total_runtime = sum(item.runtime for item in watchlist if item.runtime)
    ratings = [item.vote_average for item in watchlist if item.vote_average]
    average_rating = sum(ratings) / len(ratings) if ratings else 0.0

    genre_dist = {}
    for item in watchlist:
        if item.genres:
            for genre in item.genres.split(","):
                genre = genre.strip()
                if genre:
                    genre_dist[genre] = genre_dist.get(genre, 0) + 1
    
    return {
        "total_movies": len(watchlist),
        "total_runtime": total_runtime,
        "genre_distribution": genre_dist,
        "average_rating": round(average_rating, 2)
    }

@router.get("/ratings", response_model=List[MovieRatingResponse])
async def get_user_ratings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's movie ratings"""
    ratings = db.query(MovieRating).filter(
        MovieRating.user_id == current_user.id
    ).order_by(MovieRating.created_at.desc()).all()
    
    return ratings

@router.post("/ratings", response_model=MovieRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_movie(
    rating_data: MovieRatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Rate a movie"""
    
    # Check if already rated
    existing = db.query(MovieRating).filter(
        MovieRating.user_id == current_user.id,
        MovieRating.movie_id == rating_data.movie_id
    ).first()
    
    if existing:
        existing.rating = rating_data.rating
        existing.review = rating_data.review
        db.commit()
        db.refresh(existing)
        return existing
    
    new_rating = MovieRating(
        user_id=current_user.id,
        movie_id=rating_data.movie_id,
        movie_title=rating_data.movie_title,
        rating=rating_data.rating,
        review=rating_data.review
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return new_rating

@router.delete("/ratings/{movie_id}")
async def delete_rating(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a movie rating"""

    rating = db.query(MovieRating).filter(
        MovieRating.user_id == current_user.id,
        MovieRating.movie_id == movie_id
    ).first()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    db.delete(rating)
    db.commit()

    return {"message": "Rating deleted"}


@router.get("/recommendations/personalized")
async def get_personalized_recommendations(
    n: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    from app.ml.recommender import get_recommender
    from app.ml.neural_recommender import get_ncf_model

    recommender = get_recommender()
    ncf = get_ncf_model()

    # Fetch this user's ratings
    ratings = (
        db.query(MovieRating)
        .filter(MovieRating.user_id == current_user.id)
        .all()
    )
    rated_movie_ids = {r.movie_id for r in ratings}

    if not ratings:
        return {
            "recommendations": recommender.get_popular_movies(n),
            "method": "popular",
            "rating_count": 0,
            "message": "Rate some movies to unlock personalized recommendations!",
        }

    all_movie_ids = recommender.movies_df["movie_id"].tolist()
    candidate_ids = [mid for mid in all_movie_ids if mid not in rated_movie_ids]

    if ncf.is_ready_for_user(current_user.id):
        ncf_scores = ncf.predict_for_user(current_user.id, candidate_ids)
        if ncf_scores:
            top_ids = sorted(ncf_scores, key=ncf_scores.get, reverse=True)[:n]
            movies = recommender.get_movies_by_ids(top_ids)
            return {
                "recommendations": movies,
                "method": "neural_collaborative_filtering",
                "rating_count": len(ratings),
                "message": f"Personalized via neural model using your {len(ratings)} ratings",
            }

    genre_weights: dict = {}
    for r in ratings:
        movie_data = recommender.movies_df[
            recommender.movies_df["movie_id"] == r.movie_id
        ]
        if movie_data.empty:
            continue
        weight = r.rating / 5.0
        for genre in movie_data.iloc[0]["genres"]:
            genre_weights[genre] = genre_weights.get(genre, 0.0) + weight

    scored = []
    for _, movie in recommender.movies_df.iterrows():
        if movie["movie_id"] in rated_movie_ids:
            continue
        genre_score = sum(genre_weights.get(g, 0.0) for g in movie["genres"])
        quality = (float(movie["vote_average"]) / 10.0
                   if pd.notna(movie["vote_average"]) else 0.0)
        final_score = genre_score * 0.65 + quality * 0.35
        scored.append((movie, final_score))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_movies = [recommender._format_movie(m) for m, _ in scored[:n]]

    return {
        "recommendations": top_movies,
        "method": "genre_weighted",
        "rating_count": len(ratings),
        "message": f"Based on your {len(ratings)} ratings",
    }


@router.post("/recommendations/train-model")
async def train_ncf_model(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    from app.ml.neural_recommender import get_ncf_model

    all_ratings = db.query(MovieRating).all()
    ratings_data = [
        {"user_id": r.user_id, "movie_id": r.movie_id, "rating": r.rating}
        for r in all_ratings
    ]

    ncf = get_ncf_model()
    success = ncf.train(ratings_data)

    if success:
        return {
            "trained": True,
            "total_ratings": len(ratings_data),
            "message": f"NCF model trained on {len(ratings_data)} ratings.",
        }
    return {
        "trained": False,
        "total_ratings": len(ratings_data),
        "message": f"Need at least 5 ratings to train (have {len(ratings_data)}).",
    }


@router.get(
    "/chart/watchlist",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
async def watchlist_genre_chart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    BG = "#0f0f1a"

    watchlist = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id)
        .all()
    )

    genre_counts: dict = {}
    for item in watchlist:
        if item.genres:
            for genre in item.genres.split(","):
                genre = genre.strip()
                if genre:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    if not genre_counts:
        ax.text(
            0.5, 0.5,
            "Add movies to your watchlist\nto see genre breakdown",
            transform=ax.transAxes,
            ha="center", va="center",
            color="white", fontsize=13,
        )
        ax.axis("off")
    else:
        labels = list(genre_counts.keys())
        sizes = list(genre_counts.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            pctdistance=0.82,
        )
        for t in texts:
            t.set_color("white")
        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")

        ax.set_title(
            f"Watchlist Genre Distribution ({current_user.username})",
            color="white", fontsize=13, fontweight="bold", pad=14,
        )

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

