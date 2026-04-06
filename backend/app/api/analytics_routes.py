import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fastapi import APIRouter
from fastapi.responses import Response

from app.ml.recommender import get_recommender

router = APIRouter()

BG_DARK = "#0f0f1a"
BG_PANEL = "#1a1a2e"
ACCENT = "#e94560"
ACCENT2 = "#f5a623"
TEXT = "white"


def _apply_dark_theme(fig, ax):
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")


def _fig_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor=BG_DARK)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


@router.get("/statistics/chart/genres", response_class=Response, responses={200: {"content": {"image/png": {}}}})
async def genre_ratings_chart():
    recommender = get_recommender()
    genre_stats = recommender.get_genre_statistics()

    sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1], reverse=True)[:15]
    genres = [g[0] for g in sorted_genres]
    ratings = [g[1] for g in sorted_genres]

    fig, ax = plt.subplots(figsize=(11, 6))
    _apply_dark_theme(fig, ax)

    colors = plt.cm.RdPu(np.linspace(0.35, 0.9, len(genres)))
    bars = ax.barh(genres, ratings, color=colors, edgecolor="#222", height=0.65)

    ax.set_xlabel("Average Rating (out of 10)", fontsize=11)
    ax.set_title("Average Movie Rating by Genre", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlim(0, 10.5)

    for bar, rating in zip(bars, ratings):
        ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2,
                f"{rating:.2f}", va="center", color=TEXT, fontsize=9)

    ax.invert_yaxis()
    plt.tight_layout()
    return Response(content=_fig_to_png(fig), media_type="image/png")


@router.get("/statistics/chart/ratings", response_class=Response, responses={200: {"content": {"image/png": {}}}})
async def ratings_distribution_chart():
    recommender = get_recommender()
    vote_averages = recommender.movies_df["vote_average"].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))
    _apply_dark_theme(fig, ax)

    n, bins, patches = ax.hist(vote_averages, bins=25, color=ACCENT, edgecolor="#222", alpha=0.85)

    for patch, left_edge in zip(patches, bins[:-1]):
        patch.set_facecolor(plt.cm.RdPu(0.3 + (left_edge / 10) * 0.6))

    mean_val = vote_averages.mean()
    ax.axvline(mean_val, color=ACCENT2, linestyle="--", linewidth=2, label=f"Mean: {mean_val:.2f}")

    ax.set_xlabel("Vote Average", fontsize=11)
    ax.set_ylabel("Number of Movies", fontsize=11)
    ax.set_title("TMDB 5000 Movie Rating Distribution", fontsize=14, fontweight="bold", pad=12)
    ax.legend(facecolor=BG_PANEL, edgecolor="#444", labelcolor=TEXT)

    plt.tight_layout()
    return Response(content=_fig_to_png(fig), media_type="image/png")
