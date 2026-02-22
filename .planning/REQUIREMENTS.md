# Requirements: Movie Recommender — Feature Expansion v1

**Defined:** 2026-02-21
**Core Value:** A personal movie discovery tool that makes it easy to find, track, and rate movies worth watching — without friction.

## v1 Requirements

Requirements for the 10-feature expansion. Grouped by implementation phase.

### Foundations (Bug Fixes & Shared Infrastructure)

- [ ] **FOUND-01**: App shows an accessible animated loading spinner with support for custom messages (fixes active crash in `Home.jsx` and `Recommendations.jsx` where `LoadingSpinner` is imported but the component file does not exist)
- [ ] **FOUND-02**: Movie runtime displays in human-readable format (e.g., "2h 15m", "45m") instead of raw minutes; edge cases handled (0 min shows nothing, null handled)
- [ ] **FOUND-03**: User can toggle between dark and light theme via a button in the navigation bar; selected theme persists across page reloads; no flash-of-unstyled-content on load

### localStorage Features (No Backend Required)

- [ ] **LOCAL-01**: User sees a search history dropdown below the search bar showing the last 10 unique searches; clicking a history item re-runs that search; a clear button removes all history
- [ ] **LOCAL-02**: User sees a "Recently Viewed" horizontal scrollable section on the home page showing the last 20 movies clicked; most recent appears first; duplicate clicks move the movie to the front
- [ ] **LOCAL-03**: User can export their watchlist as a CSV file (columns: title, genres, rating, runtime, added_date) or as a JSON file; download triggers immediately on button click

### Backend Features (API + DB Changes)

- [ ] **BACK-01**: User can mark each watchlist item as "Watching", "Completed", or "Plan to Watch"; status is saved to the database; user can filter the watchlist page by status; status badge is visible on watchlist movie cards
- [ ] **BACK-02**: User can filter the movie grid by genre using multi-select chip buttons; available genres are fetched from the backend; selecting multiple genres shows the union of results; deselecting all returns the full list
- [ ] **BACK-03**: User can filter movies by decade (e.g., 1970s, 1980s, 1990s, 2000s, 2010s, 2020s); selecting multiple decades shows movies from all selected decades; movies with no release year are excluded without error

### Quick Rating

- [ ] **RATE-01**: User can rate a movie (1-5 stars) directly on any movie card via a hover-revealed star overlay; authenticated users only; rating saves to the backend on click (not on hover); cards show the existing rating filled in if already rated; users who are not logged in see stars disabled or hidden

## v2 Requirements

Deferred — not in current roadmap. Will be revisited after v1 ships.

### Advanced Features

- Features 11-22 from the mini-features backlog (Collaborative Watchlist, Movie Comparison, Advanced Search, Recommendation Explanations, Statistics Dashboard, Trailers, Personalized ML, Social, Notifications, Movie Details Page, Comments, Quiz)

### DevOps & Data

- Features 27-33 from the mini-features backlog (Auto-Refresh, Analytics, Dedup, Email Digest, Health Dashboard, Request Logging, Automated Backups)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Client-side genre filtering of home page movies | Returns 0 results for many genres with only 20 loaded movies — must hit backend |
| Auto-saving ratings on hover | Fires 5+ API calls per hover sweep across stars; save on click only |
| Syncing search history or recently viewed to backend | Disproportionate backend cost for a single-user personal tool; localStorage is sufficient |
| Mobile app | Web-first; mobile later |
| OAuth / social login | Email/password sufficient for single-user personal use |
| Admin panel | Single user; no admin role needed |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Pending |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Pending |
| LOCAL-01 | Phase 2 | Pending |
| LOCAL-02 | Phase 2 | Pending |
| LOCAL-03 | Phase 2 | Pending |
| BACK-01 | Phase 3 | Pending |
| BACK-02 | Phase 3 | Pending |
| BACK-03 | Phase 3 | Pending |
| RATE-01 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-02-21*
*Last updated: 2026-02-21 after roadmap creation — all 10 requirements confirmed mapped*
