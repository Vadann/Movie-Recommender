# Roadmap: Movie Recommender — Feature Expansion v1

## Overview

The app is functional but has one active crash today (LoadingSpinner missing). This roadmap adds 10 quality-of-life features in four phases ordered by risk and dependency: fix the crash and establish shared infrastructure first, then add pure-frontend localStorage features with no backend risk, then group all backend/DB-touching changes together to minimize repeated file modifications, and finally add the Quick Rating Widget last because it modifies MovieCard.jsx after all earlier touches to that file are stable.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundations** - Fix the active crash and establish shared infrastructure (spinner, formatters, dark mode)
- [ ] **Phase 2: localStorage Features** - Search history, recently viewed, and watchlist export — no backend required
- [ ] **Phase 3: Backend Feature Group** - Watch status (DB migration), genre filter, and decade filter — all backend changes in one pass
- [ ] **Phase 4: Quick Rating Widget** - Inline 1-5 star rating on movie cards, built after MovieCard.jsx is stable

## Phase Details

### Phase 1: Foundations
**Goal**: The app runs without crashing and has shared infrastructure (loading states, runtime formatting, dark/light theme) that all later phases build on
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03
**Success Criteria** (what must be TRUE):
  1. The home page and recommendations page load without a JavaScript crash or missing-component error
  2. Movie runtime displays as human-readable text (e.g., "2h 15m", "45m") everywhere it appears, including edge cases (0 min shows nothing, null shows nothing)
  3. A toggle button in the navigation bar switches between dark and light theme with no visible flash on page load or refresh
  4. Theme preference survives a browser refresh and a new tab opened to the same URL
**Plans**: TBD

### Phase 2: localStorage Features
**Goal**: Users can use search history, recently viewed movies, and watchlist export — all stored client-side with no backend changes
**Depends on**: Phase 1
**Requirements**: LOCAL-01, LOCAL-02, LOCAL-03
**Success Criteria** (what must be TRUE):
  1. A dropdown below the search bar shows the last 10 unique searches; clicking any item re-runs that search; a clear button removes the entire history
  2. A "Recently Viewed" horizontal scrollable section on the home page shows the last 20 clicked movies, most-recent first; clicking a movie again moves it to the front
  3. Watchlist page has Export buttons that immediately download the watchlist as a valid CSV file (with title, genres, rating, runtime, added_date columns) or a valid JSON file
  4. Search history and recently viewed data persist across page reloads and browser sessions
**Plans**: TBD

### Phase 3: Backend Feature Group
**Goal**: Watch status tracking is saved to the database, and genre/decade filters fetch from the backend — all backend and DB changes completed in one pass
**Depends on**: Phase 2
**Requirements**: BACK-01, BACK-02, BACK-03
**Success Criteria** (what must be TRUE):
  1. Each watchlist item has a status badge ("Watching", "Completed", or "Plan to Watch") that persists across page reloads and browser sessions
  2. The watchlist page has a filter UI that shows only items matching the selected status; selecting no filter shows all items
  3. Multi-select genre chip buttons on the home page filter the movie grid by fetching from the backend; selecting multiple genres shows the union; deselecting all returns the full list
  4. Decade filter buttons (1970s through 2020s) filter the movie grid; selecting multiple decades shows movies from all selected decades; movies with no release year are excluded without an error
**Plans**: TBD

### Phase 4: Quick Rating Widget
**Goal**: Users can rate any movie directly from its card without navigating to a detail page
**Depends on**: Phase 3
**Requirements**: RATE-01
**Success Criteria** (what must be TRUE):
  1. Hovering over a movie card reveals a 5-star rating overlay; clicking a star saves the rating to the backend
  2. If a movie has already been rated, the existing rating is shown pre-filled when the overlay appears
  3. Stars update visually on hover (preview) but the rating is only saved on click, not on hover
  4. Unauthenticated users see the star overlay disabled or hidden; authenticated users can rate from any page that shows movie cards
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundations | 0/TBD | Not started | - |
| 2. localStorage Features | 0/TBD | Not started | - |
| 3. Backend Feature Group | 0/TBD | Not started | - |
| 4. Quick Rating Widget | 0/TBD | Not started | - |

---

## Implementation Notes

These notes are for downstream plan-phase consumption.

### Phase 1 Constraints
- FOUND-01 (LoadingSpinner) must be the first task — the app crashes on the home page today
- FOUND-02 (formatRuntime) establishes `utils/formatters.js`; MovieCard.jsx is modified here — LOCAL-02 and RATE-01 will modify it again in later phases, in that order
- FOUND-03 (dark mode) requires: (1) `darkMode: 'class'` in `tailwind.config.js`, (2) a blocking `<script>` in `index.html <head>` that applies the `dark` class before React hydrates, (3) `ThemeContext.jsx` following the existing `AuthContext` pattern
- All components built in Phases 2-4 must include `dark:` Tailwind variants from the start

### Phase 2 Constraints
- Build a shared `useLocalStorage(key, defaultValue)` hook with try-catch at the start of this phase; LOCAL-01, LOCAL-02, and LOCAL-03 all consume it
- LOCAL-02 requires a click handler added to MovieCard.jsx (second modification to that file)
- LOCAL-03 (export) will not include `watch_status` until Phase 3 completes — this gap is documented and acceptable

### Phase 3 Constraints
- BACK-01 (Watch Status): Verify `alembic.ini` and `migrations/` directory exist in `backend/` before starting; if not configured, run `alembic init` first; run `alembic revision --autogenerate` then `alembic upgrade head` before deploying any code that writes `watch_status`
- BACK-03 (Decade Filter): Verify `release_year` column availability in `movies_df` by inspecting `backend/app/ml/preprocessing.py` before writing the endpoint; if only `release_date` exists as a string, add vectorized year extraction using `pd.to_datetime(...).dt.year` and regenerate the pickle
- Both BACK-02 and BACK-03 touch `routes.py` and `recommender.py` — do both endpoints in one pass

### Phase 4 Constraints
- Confirm the rating scale is 1-5 and add `Field(ge=1, le=5)` Pydantic validation to `MovieRatingCreate` before writing any widget code
- If existing `MovieRating` rows have values outside 1-5 (possible if a 1-10 scale was used elsewhere), audit the data before enforcing the new constraint
- MovieCard.jsx receives its third and final modification here (first: formatRuntime in Ph1, second: onClick in Ph2, third: star overlay in Ph4)
- Save rating on click only — hover updates local visual state only, no API calls on hover
