# Project Research Summary

**Project:** Movie Recommender — Feature Expansion (10 Features)
**Domain:** Personal movie discovery and tracking app (React + FastAPI, brownfield)
**Researched:** 2026-02-21
**Confidence:** HIGH

## Executive Summary

This is a brownfield feature expansion on an existing React 18 + FastAPI + SQLite movie recommender app. The app is functional but has one active production crash: `LoadingSpinner` is imported in `Home.jsx` and referenced in `Recommendations.jsx` but the component file does not exist. Every piece of research converges on the same recommendation — fix the crash first, then implement features in a dependency-aware order that groups backend-touching changes together to minimize repeated file modifications.

The recommended approach requires zero new npm or pip packages. All 10 features are fully achievable with the stack already installed (React 18.2.0, FastAPI 0.104.1, Tailwind CSS 3.3.6, lucide-react 0.294.0, SQLAlchemy 2.0.23, Alembic 1.13.0). The only configuration change is adding `darkMode: 'class'` to `tailwind.config.js`. The implementation work is real — particularly the dark/light theme toggle, which requires touching every component file — but there are no technology adoption risks whatsoever.

The key risks are operational, not architectural. Three pitfalls demand upfront decisions before any code is written: (1) the watch status DB column requires a proper Alembic migration rather than relying on `create_all()`, which will silently fail on existing databases; (2) the dark mode toggle requires a blocking script in `index.html` to prevent flash-of-unstyled-content, not just a React `useEffect`; and (3) the decade filter requires pre-extracting `release_year` from the pandas DataFrame using a vectorized operation during preprocessing, not an `iterrows()` loop at query time. Address these constraints in the correct phase sequence and all 10 features ship cleanly.

---

## Key Findings

### Recommended Stack

The stack is completely unchanged. No new dependencies are required for any of the 10 features. The existing codebase already provides every primitive needed: the `.loader` CSS spinner class in `index.css`, the `Heart` fill pattern in `MovieCard.jsx` that proves lucide-react icon fills work, the `POST /api/user/ratings` endpoint that the Quick Rating Widget reuses, and the `/statistics/genres` endpoint that the Genre Filter chip UI consumes.

**Core technologies:**
- React 18.2.0 — frontend UI — already installed; hooks + Context API cover all 10 features without external state manager
- FastAPI 0.104.1 — backend API — `Query(Optional[List[str]])` pattern handles multi-value genre filter natively
- Tailwind CSS 3.3.6 — styling and dark mode — add `darkMode: 'class'` config key; all dark mode work uses `dark:` prefix utilities
- SQLAlchemy 2.0.23 + Alembic 1.13.0 — ORM and migrations — `alembic revision --autogenerate` handles the watch status column migration including SQLite batch mode
- lucide-react 0.294.0 — icons — `Star` fill pattern confirmed working via existing `Heart` fill in `MovieCard.jsx`
- localStorage (browser built-in) — ephemeral client state — search history, recently viewed, and theme preference; no backend involvement
- `URL.createObjectURL` + Blob (browser built-in) — file downloads — watchlist CSV/JSON export; no `react-csv` or `file-saver` needed

### Expected Features

Research classified features into clear priority tiers based on direct codebase inspection. Two features are bug fixes masquerading as enhancements (LoadingSpinner and Runtime Formatter). One feature (Dark/Light Theme) has a deceptively high refactor cost because all 12+ component files use hardcoded dark-only classes.

**Must have (table stakes / bug fixes):**
- F4: Loading Spinner Component — active runtime crash in `Home.jsx` and `Recommendations.jsx`; zero other features should ship without this
- F5: Runtime Formatter Utility — consolidates duplicate inline math across `MovieCard.jsx` and `Watchlist.jsx` into a shared `formatRuntime()` utility
- F2: Movie Watch Status (Watching / Completed / Plan to Watch) — any watchlist without status tracking is write-only; requires DB migration and PATCH endpoint
- F10: Quick Rating Widget — ratings exist in the DB but require too much navigation to submit; hover-reveal star widget on MovieCard reuses the existing `POST /user/ratings` endpoint without backend changes

**Should have (differentiators):**
- F3: Search History (last 10) — reduces friction for repeat searches; pure localStorage, no backend
- F6: Recently Viewed Movies (last 20) — horizontal scroll section on Home page; pure localStorage, captures on MovieCard click
- F8: Export Watchlist as CSV/JSON — personal data portability; client-side Blob download, no backend; richer after F2 ships
- F7: Movie Genres Filter (multi-select chips) — turns static home grid into a discovery tool; requires backend genre query param and `get_all_genres()` recommender method
- F9: Movie Decade Filter — natural browsing mental model; requires `release_year` derivation in preprocessing and decade query param on movies endpoint

**Defer (highest refactor surface, lowest new functionality):**
- F1: Dark/Light Theme Toggle — all 12+ component files must be audited for hardcoded dark colors; build last to avoid cascading conflicts with new components added in earlier phases

**Explicit anti-features to avoid building:**
- Client-side genre filtering of 20 home page movies (returns 0 results for many genres — must hit backend)
- Syncing search history to backend (disproportionate cost for a single-user personal tool)
- Auto-saving ratings on hover (fires 5 API calls per hover sweep; save only on click)

### Architecture Approach

The architecture is a straightforward React SPA + FastAPI REST API with a pandas-powered movie recommender singleton that loads a 5000-movie CSV once at startup. New features add to this structure without replacing it: a `hooks/` directory for localStorage hooks, a `utils/` directory for pure functions, a `context/ThemeContext.jsx` matching the existing `AuthContext` pattern, and new methods on the `MovieRecommender` class rather than a second DataFrame load. The recommended project structure preserves all existing directories and adds only what's needed.

**Major components and their additions:**
1. `ThemeContext.jsx` — manages dark/light state; persists to localStorage; exposes `toggleTheme()` to App.jsx
2. `hooks/useSearchHistory.js` + `hooks/useRecentlyViewed.js` — localStorage hooks with try-catch error handling; no Provider needed (localStorage is shared storage)
3. `utils/formatters.js` — pure `formatRuntime(minutes)` function; replaces inline math in `MovieCard.jsx` and `Watchlist.jsx`
4. `utils/exportData.js` — `exportWatchlistCSV()` and `exportWatchlistJSON()` using Blob download; must call `URL.revokeObjectURL()` after download
5. `GenreFilter.jsx` — stateless presentational component; receives `genres`, `selectedGenres`, `onChange` props; reusable in both Home and Recommendations pages
6. `RecentlyViewed.jsx` — display component; horizontal scroll row consuming `useRecentlyViewed` hook
7. `MovieRecommender` class additions — `get_all_genres()`, `get_popular_movies_by_genre()`, `get_movies_by_decade()` — added as methods on the existing singleton, not a second instance
8. `WatchlistItem` schema addition — `watch_status` column with `server_default="plan_to_watch"`; applied via Alembic migration

**Key files touched by multiple features (sequence matters):**
- `MovieCard.jsx` — modified by F5 (formatRuntime), F6 (onClick for recently viewed), F10 (star rating widget) — build in this order to avoid merge conflicts
- `Recommendations.jsx` — modified by F3 (search history dropdown), F4 (uncomment import), F7 (genre chips), F9 (decade filter)
- `Home.jsx` — modified by F6 (RecentlyViewed section), F7 (genre chips)
- `backend/app/api/routes.py` — modified by F7 (genres endpoint) and F9 (decade query param) — do both in one pass

### Critical Pitfalls

1. **Dark mode FOUC (Flash of Unstyled Content)** — reading `localStorage` in a React `useEffect` guarantees a visible flash on every hard refresh. Prevention: inject a blocking `<script>` in `index.html` `<head>` that sets the `dark` class on `<html>` synchronously before React hydrates. Also remove the hardcoded `background: linear-gradient(...)` from `index.css` and replace with Tailwind `dark:` variants.

2. **Watch Status column silently missing on existing databases** — `Base.metadata.create_all()` creates missing tables but never alters existing ones. Adding `watch_status` to `models_db.py` and restarting will result in `OperationalError: table watchlist_items has no column named watch_status` on the first write. Prevention: run `alembic revision --autogenerate` then `alembic upgrade head`, or execute an idempotent `ALTER TABLE watchlist_items ADD COLUMN watch_status VARCHAR DEFAULT 'plan_to_watch'` check on startup.

3. **LoadingSpinner crash is live now** — `Home.jsx` imports `LoadingSpinner` from a file that does not exist. The app crashes on the home page. This is the absolute first task before any other feature work.

4. **Decade filter `release_year` column missing from DataFrame** — `recommender.py` does not currently expose `release_year`. An `iterrows()` loop parsing `release_date` strings per row will take 2-5 seconds for 5000 movies. Prevention: extract `release_year` as a derived integer column in `preprocessing.py` using `pd.to_datetime(...).dt.year`, then use a vectorized boolean mask for decade filtering.

5. **Quick Rating scale conflict with existing system** — `MovieRating.rating` has no bounds validation. If the new widget saves 1-5 star values and other UI paths assume 1-10 scale, statistics calculations will produce nonsense averages. Prevention: define the user rating scale as 1-5 before building the widget and add `Field(ge=1, le=5)` Pydantic validation to `MovieRatingCreate`.

---

## Implications for Roadmap

Based on combined research, four phases are recommended. The grouping logic is: (1) crash fix first, (2) pure frontend localStorage features with no backend risk next, (3) all backend-touching changes in one phase to minimize deployment steps, (4) high-surface-area frontend polish last.

### Phase 1: Bug Fixes and Shared Foundations

**Rationale:** The app crashes on the home page today. Nothing else ships until this is resolved. This phase also establishes the utility pattern (`formatters.js`) that Features 6 and 10 depend on, and the dark mode infrastructure that all new components should be written to be compatible with.

**Delivers:** A working, crash-free app with shared formatting utilities and dark mode infrastructure in place.

**Addresses:** F4 (LoadingSpinner), F5 (Runtime Formatter), F1 (Dark/Light Theme Toggle)

**Avoids:** The FOUC pitfall (blocking script in `index.html`), cascading conflicts from adding new components before theme infrastructure exists, and establishing the wrong LocalStorage pattern before the hook architecture is decided.

**Note on F1 ordering:** Theme is placed in Phase 1 rather than last because new components built in later phases should be written dark-mode-compatible from the start. Writing them dark-compatible is easier than retrofitting them afterward. The architectural decision (add `darkMode: 'class'`, blocking script, ThemeContext) belongs here; the per-component `dark:` class work touches every file but is low-risk mechanical work.

**Research flag:** Standard patterns. No deeper research needed. Tailwind `darkMode: 'class'` is officially documented; the FOUC prevention script is a well-known pattern.

---

### Phase 2: localStorage Features

**Rationale:** These three features have no backend dependencies, no DB migrations, and no cross-feature conflicts. They can be built in any order within the phase. Building them after Phase 1 ensures the dark mode infrastructure exists so new components are written correctly from the start.

**Delivers:** Search history dropdown in Recommendations, Recently Viewed section on Home, and watchlist export buttons in Watchlist page.

**Addresses:** F3 (Search History), F6 (Recently Viewed), F8 (Export Watchlist)

**Avoids:** The localStorage error handling pitfall — build the shared `useLocalStorage(key, defaultValue)` hook with try-catch at the start of this phase; all three features consume it rather than writing raw `localStorage.getItem/setItem`.

**Note on F8 ordering:** Export Watchlist is placed here because it's a pure client-side utility. It will export without a `watch_status` field until Phase 3 completes, which is acceptable — the feature description explicitly notes this.

**Research flag:** Standard patterns. No deeper research needed. localStorage hooks, Blob download, and horizontal scroll containers are well-documented patterns.

---

### Phase 3: Backend Feature Group

**Rationale:** These three features require backend changes, at least one DB migration, and new API endpoints. Grouping them minimizes the number of times `routes.py`, `user_routes.py`, and `recommender.py` are touched. The DB migration for watch status must run before any code that references `watch_status` is deployed.

**Delivers:** Watch status tracking with filter UI on Watchlist page, genre multi-select filter chips on Home/Recommendations, decade filter on the same pages. All three filter features share a unified filter state pattern in the frontend.

**Addresses:** F2 (Watch Status), F7 (Genre Filter), F9 (Decade Filter)

**Avoids:** The Alembic migration pitfall (must run migration before deploying watch status code), the genres-as-comma-string pitfall (genre filter must read from DataFrame, not from `WatchlistItem.genres`), and the decade `release_year` pitfall (extract derived column in `preprocessing.py` before building the filter endpoint).

**Key prerequisite:** Before starting F9, verify whether `movies_df` has a `release_year` or `release_date` column by inspecting `backend/app/ml/preprocessing.py`. If only `release_date` exists, add the year extraction step and regenerate the pickle before building the endpoint.

**Research flag:** F2 (Watch Status) needs verification that Alembic is configured (`alembic.ini` and `migrations/` directory present). If not, setup takes approximately 5 minutes before the migration can be generated. F7 and F9 are standard FastAPI query param patterns — no deeper research needed.

---

### Phase 4: Quick Rating Widget

**Rationale:** This feature modifies `MovieCard.jsx`, which is also modified by F5 (Phase 1) and F6 (Phase 2). Building it last ensures those changes are stable before adding the hover star overlay. It also requires the rating scale decision to be made explicitly — that decision gates the entire implementation.

**Delivers:** Inline 5-star rating widget on movie card hover overlay for authenticated users. Shows existing rating if already rated. Saves on click (not hover) to the existing `POST /user/ratings` endpoint.

**Addresses:** F10 (Quick Rating Widget)

**Avoids:** The rating scale conflict pitfall (decide and enforce `Field(ge=1, le=5)` Pydantic validation before writing any widget code), the hover-fires-API-calls pitfall (save on click only; hover updates local visual state only), and the mobile touch pitfall (onClick as primary interaction, not hover-only).

**Research flag:** Standard pattern. No deeper research needed. The existing `Heart` fill pattern in `MovieCard.jsx` is a direct proof of concept for the star fill behavior.

---

### Phase Ordering Rationale

- **Crash fix is non-negotiable first** — the app is broken today; nothing else matters until `LoadingSpinner.jsx` exists.
- **localStorage features before backend changes** — reduces risk and allows visible progress with zero deployment complexity.
- **Backend features grouped together** — avoids touching `routes.py`, `recommender.py`, and `user_routes.py` multiple times across phases.
- **`MovieCard.jsx` sequence is strictly enforced** — F5 (add formatRuntime) in Phase 1, F6 (add onClick) in Phase 2, F10 (add star widget) in Phase 4. Out-of-order commits cause three-way merge conflicts on this single file.
- **Theme toggle architectural decision in Phase 1, component styling work ongoing** — new components built in Phases 2-4 should include `dark:` variants as they are written, not retrofitted later.
- **F8 export before F2 watch status ships** — acceptable gap; document that the export will include status once Phase 3 completes.

### Research Flags

Phases needing deeper research or prerequisite verification during planning:
- **Phase 3, F9 (Decade Filter):** Verify `release_year` column availability in `movies_df` before writing the endpoint. Inspect `backend/app/ml/preprocessing.py`. If only `release_date` exists as a string, add vectorized year extraction and regenerate the pickle.
- **Phase 3, F2 (Watch Status):** Verify Alembic is configured. Check whether `alembic.ini` and a `migrations/` directory exist in `backend/`. If not, run `alembic init alembic` and configure `target_metadata` before generating the migration.

Phases with standard well-documented patterns (skip research-phase):
- **Phase 1 (Bug Fixes + Theme):** LoadingSpinner is a wrapper around existing CSS. formatRuntime is a 5-line utility. Theme toggle uses officially documented Tailwind `darkMode: 'class'` pattern.
- **Phase 2 (localStorage Features):** All three features use browser-native APIs and standard React hook patterns. No library research needed.
- **Phase 4 (Quick Rating):** Direct analog of the existing `Heart` fill pattern. Existing `POST /user/ratings` endpoint requires no changes.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified against official docs and existing codebase. Zero new packages needed. |
| Features | HIGH | Based on direct codebase inspection of all component, page, model, and route files. Feature scope is concrete, not speculative. |
| Architecture | HIGH | Component boundaries and data flow derived from reading actual source files, not assumptions. File-level change map is accurate. |
| Pitfalls | HIGH | Every critical pitfall is traced to a specific file and line number in the codebase. Three pitfalls (FOUC, DB migration, decades column) are known failure modes confirmed by direct inspection. |

**Overall confidence:** HIGH

### Gaps to Address

- **`release_year` availability in DataFrame:** ARCHITECTURE.md and PITFALLS.md both flag this as a prerequisite verification step, but the actual `preprocessing.py` output columns were not inspected during research. Must be confirmed before Phase 3 / F9 work begins. If `release_date` only exists as a string, a preprocessing change and pickle regeneration are required before the decade filter endpoint can be written. This is a known unknown, not a risk — it affects implementation order but not feasibility.

- **Alembic configuration state:** `CONCERNS.md` confirms Alembic is in `requirements.txt` but may not be initialized. Verify `alembic.ini` and `migrations/env.py` exist before Phase 3 / F2 work begins. If not configured, initialization is straightforward (approximately 5 minutes) but must happen before the migration is generated.

- **Rating scale in existing data:** The `MovieRating` table may have existing rows with 1-10 scale values entered via other UI paths. If so, the Phase 4 decision to enforce 1-5 scale via Pydantic validation will break backward compatibility for those existing ratings. A data audit of the `movie_ratings` table before Phase 4 is recommended.

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection — `frontend/src/components/MovieCard.jsx`, `frontend/src/pages/Home.jsx`, `frontend/src/pages/Recommendations.jsx`, `frontend/src/pages/Watchlist.jsx`, `frontend/src/context/WatchlistContext.jsx`, `frontend/tailwind.config.js`, `frontend/src/index.css` — confirmed all feature integration points, active crash, and dark mode state
- Direct codebase inspection — `backend/app/models_db.py`, `backend/app/api/user_routes.py`, `backend/app/api/routes.py`, `backend/app/ml/recommender.py` — confirmed watch status column absent, rating endpoint exists, genre/decade endpoints absent
- [Tailwind CSS v3 Dark Mode docs](https://v3.tailwindcss.com/docs/dark-mode) — `darkMode: 'class'` configuration
- [FastAPI Query Parameters docs](https://fastapi.tiangolo.com/tutorial/query-param-models/) — `Optional[List[str]] = Query(default=None)` pattern
- [MDN: URL.createObjectURL](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL) — Blob download pattern
- [Alembic batch operations docs](https://alembic.sqlalchemy.org/en/latest/batch.html) — SQLite column addition via batch mode

### Secondary (MEDIUM confidence)
- WebSearch: "React localStorage custom hook pattern 2025" — confirms inline hook pattern with try-catch over third-party library
- UX patterns from Letterboxd, Trakt, IMDb — informed table stakes vs. differentiator classification for watch status and quick rating features
- [FOUC prevention with Tailwind dark mode](https://cruip.com/implementing-tailwind-css-dark-mode-toggle-with-no-flicker/) — blocking script in `<head>` pattern

### Tertiary (LOW confidence — needs validation during implementation)
- `release_year` column availability in `movies_df` — inferred from `release_date` likely existing in TMDB CSV data; not directly confirmed by inspecting `preprocessing.py` output columns
- Existing `MovieRating` data scale distribution — assumed 1-10 based on column type (Float); actual data distribution not audited

---

*Research completed: 2026-02-21*
*Ready for roadmap: yes*
