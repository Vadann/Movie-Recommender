# Movie Recommender

## What This Is

A personal movie discovery and tracking tool built on a FastAPI backend with a React frontend. Users (currently just the developer) can search movies, get content-based and mood-based recommendations, manage a watchlist, and rate films. The v1 milestone adds 10 quality-of-life features to make the app genuinely useful day-to-day.

## Core Value

A personal movie discovery tool that makes it easy to find, track, and rate movies worth watching — without friction.

## Requirements

### Validated

<!-- Existing capabilities already built and working. -->

- ✓ User can register and log in with email/password (JWT auth) — existing
- ✓ User can get content-based movie recommendations by title — existing
- ✓ User can get mood-based recommendations (happy, sad, action, etc.) — existing
- ✓ User can search for movies by title — existing
- ✓ User can add and remove movies from their watchlist — existing
- ✓ User can rate movies (1-5 stars) — existing
- ✓ Sessions persist across browser refresh via refresh token — existing

### Active

<!-- Features 1-10 from the mini-features backlog. -->

- [ ] User can toggle between dark and light theme, with preference persisted across reloads
- [ ] User can mark watchlist items as "Watching", "Completed", or "Plan to Watch" and filter by status
- [ ] User sees recent search history below search bar and can re-run or clear past searches
- [ ] App shows an accessible animated loading spinner (currently missing, referenced but not implemented)
- [ ] Movie runtime displays in human-readable format ("2h 15m") instead of raw minutes
- [ ] User sees a "Recently Viewed" section on home page tracking last 20 movies clicked
- [ ] User can filter movies by genre using multi-select chips on the main page
- [ ] User can export their watchlist as CSV or JSON file
- [ ] User can filter movies by decade (1970s, 1980s, 1990s, etc.)
- [ ] User can quickly rate movies with star icons directly on movie cards (hover to reveal)

### Out of Scope

- Features 11-33 from the backlog (Collaborative Watchlist Sharing, Movie Comparison, Social Features, etc.) — deferred to future milestones
- Mobile app — web-first
- Admin panel — single user, no admin needed
- Real-time features (WebSockets, push notifications) — not needed for personal use

## Context

- Brownfield project: core backend (FastAPI + SQLAlchemy + scikit-learn ML) and frontend (React + Vite + Tailwind) already exist and are functional
- `LoadingSpinner` is referenced in `Recommendations.jsx` but the component file does not exist — fix is included as Feature 4
- Backend uses SQLite locally; PostgreSQL in production via `DATABASE_URL`
- TMDB API key optional; app degrades gracefully if absent
- Movie data loaded from CSV at startup, preprocessed into pickle for performance
- Single user (developer); no multi-tenancy concerns for this milestone

## Constraints

- **Tech Stack**: Python/FastAPI backend, React/Vite/Tailwind frontend — no framework changes
- **Database**: Features requiring schema changes (Watch Status) need Alembic migration or SQLAlchemy table update
- **No external services**: Features must work without new paid APIs or services
- **localStorage**: Frontend-only features (Search History, Recently Viewed) store in localStorage — acceptable for single user

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build features 1-10 first | Ordered by complexity (easy → medium), quick wins first | — Pending |
| localStorage for ephemeral data | Search history, recently viewed, theme — no backend needed | — Pending |
| Watch Status as DB column | Needs persistence across sessions; localStorage insufficient | — Pending |

---
*Last updated: 2026-02-21 after initialization*
