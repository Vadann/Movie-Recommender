# Architecture Research

**Domain:** Movie Recommender — brownfield feature expansion (10 features added to existing React + FastAPI app)
**Researched:** 2026-02-21
**Confidence:** HIGH — based on direct source code inspection of all relevant files

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite + Tailwind)           │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────┐  │
│  │   Contexts   │  │  Custom Hooks  │  │       Utilities          │  │
│  │ AuthContext  │  │ useSearchHist  │  │  formatters.js           │  │
│  │ WatchlstCtx  │  │ useRecentView  │  │  exportData.js           │  │
│  │ ThemeContext  │  │                │  │                          │  │
│  └──────┬───────┘  └───────┬────────┘  └────────────┬─────────────┘  │
│         │                  │                         │               │
│  ┌──────┴──────────────────┴─────────────────────────┴─────────────┐ │
│  │                         Pages                                   │ │
│  │  Home  │  Recommendations  │  Watchlist  │  Statistics           │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                       Components                                 │ │
│  │  MovieCard  │  LoadingSpinner  │  GenreFilter  │  RecentlyViewed │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                   Services (Axios)                               │ │
│  │            api.js                 authAPI.js                     │ │
│  └──────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│                      BACKEND (FastAPI + SQLAlchemy)                  │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ routes.py  │  │ user_routes  │  │ auth_routes  │                  │
│  │ GET /movies│  │ GET/POST/PUT │  │ POST /login  │                  │
│  │ /genres    │  │ /watchlist   │  │ POST /signup │                  │
│  └─────┬──────┘  └──────┬───────┘  └──────────────┘                  │
│        │                │                                            │
│  ┌─────┴────────────────┴──────────────────────────────────────────┐ │
│  │         MovieRecommender (singleton, loaded at startup)          │ │
│  │  search_movies │ get_popular │ filter_by_genre │ filter_by_decade │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │               SQLAlchemy ORM + SQLite/PostgreSQL                 │ │
│  │     User │ WatchlistItem (+watch_status col) │ MovieRating       │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### New Components / Modules Added by the 10 Features

| Component / Module | Responsibility | Layer | File Location |
|-------------------|----------------|-------|---------------|
| `ThemeContext.jsx` | Manages dark/light theme state; persists preference to localStorage; exposes `theme` + `toggleTheme` | Frontend Context | `frontend/src/context/ThemeContext.jsx` |
| `LoadingSpinner.jsx` | Accessible animated spinner with optional message prop; replaces bare `.loader` CSS divs currently inlined across pages | Frontend Component | `frontend/src/components/common/LoadingSpinner.jsx` |
| `useSearchHistory.js` | Custom hook: reads/writes to localStorage key `searchHistory`; exposes `history`, `addSearch`, `clearHistory` | Frontend Hook | `frontend/src/hooks/useSearchHistory.js` |
| `useRecentlyViewed.js` | Custom hook: reads/writes to localStorage key `recentlyViewed`; max 20 entries; exposes `recentMovies`, `addRecentMovie` | Frontend Hook | `frontend/src/hooks/useRecentlyViewed.js` |
| `formatters.js` | Pure utility: `formatRuntime(minutes)` → "2h 15m"; no side effects | Frontend Utility | `frontend/src/utils/formatters.js` |
| `exportData.js` | Pure utility: `exportWatchlistCSV(watchlist)`, `exportWatchlistJSON(watchlist)`; triggers browser download | Frontend Utility | `frontend/src/utils/exportData.js` |
| `GenreFilter.jsx` | Multi-select chip component; receives `genres[]` + `selectedGenres[]` + `onChange` prop; stateless | Frontend Component | `frontend/src/components/GenreFilter.jsx` |
| `RecentlyViewed.jsx` | Display component: consumes `useRecentlyViewed` hook; renders horizontal scroll row of MovieCards | Frontend Component | `frontend/src/components/RecentlyViewed.jsx` |

#### Existing Files Modified by the 10 Features

| Existing File | What Changes | Why |
|---------------|--------------|-----|
| `tailwind.config.js` | Add `darkMode: 'class'` | Enables class-based dark mode toggling |
| `App.jsx` | Wrap with `ThemeProvider`; apply `dark` class to root `<div>` based on theme context | Theme pivot point |
| `index.css` | Add dark mode CSS variable overrides (bg, text, border colors) | Tailwind dark: class variants applied globally |
| `MovieCard.jsx` | Add hover-reveal star rating widget (Feature 10); add `onClick` → `addRecentMovie` call (Feature 6); replace inline runtime formatter with `formatRuntime()` (Feature 5) | Three features converge on this file |
| `Recommendations.jsx` | Uncomment `LoadingSpinner` import (already imported but commented out); integrate `useSearchHistory` to save queries + render search history dropdown (Features 3, 4); add `GenreFilter` + decade filter UI (Features 7, 9) | Most feature-dense page |
| `Home.jsx` | Add `<RecentlyViewed />` section below hero (Feature 6); add `<GenreFilter />` for filtering popular movies display (Feature 7) | Receives 2 new sections |
| `Watchlist.jsx` | Add watch status filter tabs + per-card status dropdown (Feature 2); add export button calling `exportData.js` (Feature 8) | Watch status + export land here |
| `backend/app/models_db.py` | Add `watch_status` column to `WatchlistItem` (Feature 2) | Schema change — needs Alembic migration |
| `backend/app/api/user_routes.py` | Add `PUT /watchlist/{movie_id}/status` endpoint (Feature 2); update `WatchlistItemResponse` Pydantic model to include `watch_status` | Backend for watch status |
| `backend/app/api/routes.py` | Add `GET /movies/genres` endpoint returning sorted unique genres list (Feature 7); add `decade` query param to `/movies/popular` or expose new `/movies/filter` endpoint (Feature 9) | Two new GET endpoints |
| `backend/app/ml/recommender.py` | Add `get_all_genres()` method returning sorted unique genre list from `movies_df` (Feature 7); add `filter_movies_by_decade(decade)` method (Feature 9) | Recommender extended, not replaced |

---

## Recommended Project Structure (Post-Feature-Expansion)

```
frontend/src/
├── context/
│   ├── AuthContext.jsx          # existing
│   ├── WatchlistContext.jsx     # existing
│   └── ThemeContext.jsx         # NEW — Feature 1
├── hooks/
│   ├── useSearchHistory.js      # NEW — Feature 3
│   └── useRecentlyViewed.js     # NEW — Feature 6
├── utils/
│   ├── formatters.js            # NEW — Feature 5
│   └── exportData.js            # NEW — Feature 8
├── components/
│   ├── common/
│   │   └── LoadingSpinner.jsx   # NEW — Feature 4 (move into common/ subdir)
│   ├── GenreFilter.jsx          # NEW — Feature 7
│   ├── RecentlyViewed.jsx       # NEW — Feature 6
│   ├── MovieCard.jsx            # existing — modified (Features 5, 6, 10)
│   └── ParticlesBackground.jsx  # existing — unchanged
├── pages/
│   ├── Home.jsx                 # existing — modified (Features 6, 7)
│   ├── Recommendations.jsx      # existing — modified (Features 3, 4, 7, 9)
│   ├── Watchlist.jsx            # existing — modified (Features 2, 8)
│   ├── Statistics.jsx           # existing — unchanged
│   ├── Login.jsx                # existing — unchanged
│   ├── Signup.jsx               # existing — unchanged
│   └── Documentation.jsx        # existing — unchanged
├── services/
│   ├── api.js                   # existing — add getGenres(), getMoviesByDecade()
│   └── authAPI.js               # existing — add updateWatchStatus()
├── App.jsx                      # existing — modified (Feature 1 ThemeProvider wrap)
├── main.jsx                     # existing — unchanged
└── index.css                    # existing — modified (Feature 1 dark mode vars)

backend/app/
├── api/
│   ├── routes.py                # existing — add GET /movies/genres, decade filter
│   ├── user_routes.py           # existing — add PUT /watchlist/{id}/status
│   └── auth_routes.py           # existing — unchanged
├── ml/
│   └── recommender.py           # existing — add get_all_genres(), filter_by_decade()
├── models_db.py                 # existing — add watch_status col to WatchlistItem
└── models.py                    # existing — update Pydantic WatchlistItemResponse
```

### Structure Rationale

- **`hooks/` (new directory):** React custom hooks belong separate from context. `useSearchHistory` and `useRecentlyViewed` are pure localStorage hooks with no backend dependency — they should not live in `context/` (no Provider needed) nor in `components/` (they render nothing).
- **`utils/` (new directory):** Pure functions with no React dependency. `formatters.js` and `exportData.js` are framework-agnostic — placing them in utils/ makes them independently testable and importable from any component without coupling.
- **`components/common/` (new subdirectory):** `LoadingSpinner` is a generic primitive used across multiple pages. A `common/` subdirectory signals "shared primitives" vs feature-specific components like `GenreFilter`.
- **Existing directories preserved:** Adding new dirs without restructuring existing ones avoids gratuitous churn on files that work.

---

## Architectural Patterns

### Pattern 1: localStorage-Only State for Ephemeral Client Data

**What:** Features 1 (theme), 3 (search history), and 6 (recently viewed) store data exclusively in `localStorage` via custom hooks or context. No backend involvement.

**When to use:** Data that is (a) user-specific but not requiring cross-device sync, (b) acceptable to lose on clear-browser, and (c) single-user app (the PROJECT.md confirms this).

**Trade-offs:** Zero backend cost, zero auth requirement, instant reads. Cost: clears on browser data wipe, not portable across devices.

**Example:**
```javascript
// frontend/src/hooks/useSearchHistory.js
const STORAGE_KEY = 'searchHistory'
const MAX_HISTORY = 20

export function useSearchHistory() {
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []
    } catch {
      return []
    }
  })

  const addSearch = (query) => {
    setHistory(prev => {
      const updated = [query, ...prev.filter(q => q !== query)].slice(0, MAX_HISTORY)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
      return updated
    })
  }

  const clearHistory = () => {
    localStorage.removeItem(STORAGE_KEY)
    setHistory([])
  }

  return { history, addSearch, clearHistory }
}
```

### Pattern 2: Database Column Addition with Alembic Migration

**What:** Feature 2 (watch status) requires a new `watch_status` column on the existing `WatchlistItem` table. The column must default to a value so existing rows are not broken.

**When to use:** Any feature that needs data persisted across sessions and is tied to a user account. The PROJECT.md explicitly decided "Watch Status as DB column" because localStorage is insufficient.

**Trade-offs:** Requires migration script and deployment step. Correct approach: add column with `nullable=True` or `server_default` so existing rows get a value without manual backfill.

**Example:**
```python
# backend/app/models_db.py — add to WatchlistItem class
watch_status = Column(
    String,
    nullable=True,
    default="plan_to_watch",
    server_default="plan_to_watch"
)
# Values: "plan_to_watch", "watching", "completed"

# Migration (Alembic auto-generate or manual):
# alembic revision --autogenerate -m "add_watch_status_to_watchlist_items"
# alembic upgrade head
```

### Pattern 3: Extending the MovieRecommender Singleton (Not Replacing It)

**What:** Features 7 (genre filter) and 9 (decade filter) need new query methods on `MovieRecommender`. Add methods to the existing class; do not instantiate a second recommender or load a second DataFrame.

**When to use:** Any new backend data query that operates on the existing 5000-movie CSV dataset. The recommender owns the DataFrame; all queries go through it.

**Trade-offs:** Keeps the single in-memory dataset. The recommender is already a singleton loaded once at startup. New methods are pure functions on `self.movies_df` — no re-loading, no pickle changes.

**Example:**
```python
# backend/app/ml/recommender.py — methods to add to MovieRecommender class

def get_all_genres(self) -> list[str]:
    """Return sorted unique genres from dataset"""
    genres = set()
    for genre_list in self.movies_df['genres']:
        genres.update(genre_list)
    return sorted(genres)

def get_popular_movies_by_genre(self, genres: list[str], n: int = 20) -> list[dict]:
    """Filter popular movies by any of the specified genres"""
    filtered = self.movies_df[
        self.movies_df['genres'].apply(
            lambda g: any(genre in g for genre in genres)
        )
    ].sort_values('vote_average', ascending=False)
    return [self._format_movie(row) for _, row in filtered.head(n).iterrows()]

def get_movies_by_decade(self, decade: int, n: int = 20) -> list[dict]:
    """Filter movies by release decade (e.g., decade=1990 for 1990-1999)"""
    filtered = self.movies_df[
        (self.movies_df['release_year'] >= decade) &
        (self.movies_df['release_year'] < decade + 10)
    ].sort_values('vote_average', ascending=False)
    return [self._format_movie(row) for _, row in filtered.head(n).iterrows()]
```

**Note:** Verify `release_year` column exists in `movies_df` from the preprocessed CSV. If not, it must be extracted from `release_date` in `preprocessing.py` before the pickle is regenerated.

### Pattern 4: Stateless Presentational Component for Filters

**What:** `GenreFilter.jsx` receives all its data via props (`genres`, `selectedGenres`, `onChange`). It holds zero local state. Selecting a genre calls `onChange(updatedSelection)` and the parent page manages the selection array.

**When to use:** UI elements that are pure display + interaction with no async calls. Keeps the component easily testable and reusable in Home and Recommendations pages without duplication.

**Example:**
```jsx
// frontend/src/components/GenreFilter.jsx
export default function GenreFilter({ genres, selectedGenres, onChange }) {
  const toggle = (genre) => {
    const updated = selectedGenres.includes(genre)
      ? selectedGenres.filter(g => g !== genre)
      : [...selectedGenres, genre]
    onChange(updated)
  }

  return (
    <div className="flex flex-wrap gap-2">
      {genres.map(genre => (
        <button
          key={genre}
          onClick={() => toggle(genre)}
          className={`px-3 py-1 rounded-full text-sm transition-all ${
            selectedGenres.includes(genre)
              ? 'bg-red-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          {genre}
        </button>
      ))}
    </div>
  )
}
```

---

## Data Flow

### Feature 1 — Dark/Light Theme Toggle

```
User clicks toggle button (in Nav or Settings)
    ↓
ThemeContext.toggleTheme()
    ↓
Updates theme state + writes to localStorage('theme')
    ↓
App.jsx reads theme from ThemeContext
    ↓
Applies/removes 'dark' class on root <div>
    ↓
Tailwind dark: variants re-apply across all components
```

**Key constraint:** `tailwind.config.js` must add `darkMode: 'class'`. The existing dark-only styles (`bg-gray-800`, `text-gray-300`) will need companion `dark:` variants on all affected components — or the current defaults stay and only accent colors swap.

**Simplification option:** Since the app is already dark-themed, implement light theme as the "alternate" mode. The existing styles remain default; light mode overrides them. This avoids touching every component class.

---

### Feature 2 — Movie Watch Status

```
Backend: WatchlistItem.watch_status (DB column, default "plan_to_watch")
    ↑
PUT /api/user/watchlist/{movie_id}/status  {status: "watching"|"completed"|"plan_to_watch"}
    ↑
authAPI.updateWatchStatus(movieId, status)  [services/authAPI.js — new method]
    ↑
Status dropdown in Watchlist.jsx per-movie card
    ↓ (filter)
Watchlist.jsx maintains selectedStatus filter state
    ↓
Renders filtered subset of watchlist[]
```

**DB write:** `PUT` endpoint updates the `watch_status` field, commits, returns updated item.
**Frontend read:** `WatchlistContext.watchlist` array already contains the full WatchlistItem — add `watch_status` to `WatchlistItemResponse` Pydantic model so the field is serialized.

---

### Feature 3 — Search History

```
User types query + presses Enter/Search in Recommendations.jsx
    ↓
Existing handleSearch() fires
    ↓
After successful search: addSearch(query)  [useSearchHistory hook]
    ↓
localStorage('searchHistory') updated
    ↓
History list re-renders below search bar
    ↓
User clicks history item → setSearchQuery(item) + handleSearch()
```

**Data store:** localStorage only. No backend. Persists across reloads.

---

### Feature 4 — Loading Spinner Component

```
Create: frontend/src/components/common/LoadingSpinner.jsx
    ↓
Receives: { message: string }
    ↓
Renders: accessible <div role="status"> wrapping the existing .loader CSS class
         + optional message text below
    ↓
Fix: Recommendations.jsx uncomments the LoadingSpinner import
     (currently commented out on line 4, used on lines 128 and 171)
     Home.jsx already imports it correctly — just needs the file to exist
```

**This is the highest-priority fix.** `Home.jsx` will crash at render if `LoadingSpinner` is not created before any other code runs.

---

### Feature 5 — Runtime Formatter

```
Create: frontend/src/utils/formatters.js
    ↓
Export: formatRuntime(minutes: number): string  → "2h 15m"
    ↓
Replace in MovieCard.jsx line 122:
  BEFORE: {Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m
  AFTER:  {formatRuntime(movie.runtime)}
    ↓
Replace same pattern in Watchlist.jsx line 117 (total_runtime display)
```

**Confidence:** HIGH — direct code inspection confirms the duplicate inline pattern exists in both files.

---

### Feature 6 — Recently Viewed Movies

```
User clicks on a movie card (onClick handler added to MovieCard.jsx)
    ↓
addRecentMovie(movie)  [useRecentlyViewed hook, passed as prop or accessed via hook]
    ↓
localStorage('recentlyViewed') updated (max 20, FIFO, deduped by movie_id)
    ↓
Home.jsx renders <RecentlyViewed /> section
    ↓
RecentlyViewed.jsx calls useRecentlyViewed() → reads recentMovies[]
    ↓
Renders horizontal scrollable row of MovieCard components
```

**Design decision:** `useRecentlyViewed` is called from within `MovieCard.jsx` directly (hook call inside a component used everywhere). This avoids prop-drilling the `addRecentMovie` function from every parent page down to the card.

---

### Feature 7 — Movie Genre Filter

```
Backend data flow:
GET /api/movies/genres
    ↓
routes.py calls recommender.get_all_genres()
    ↓
Returns: { genres: ["Action", "Adventure", ...] }

Frontend data flow:
api.js.getGenres() fetches list on mount (Home.jsx + Recommendations.jsx)
    ↓
<GenreFilter genres={genres} selectedGenres={selected} onChange={setSelected} />
    ↓
User selects genres → selectedGenres[] updated in parent state
    ↓
Parent calls api.js.getMoviesByGenres(selectedGenres) or filters local movies[] array
```

**Recommendation:** Filter locally if `movies[]` is already fetched (avoids extra API calls for popular movies which are all in memory). For recommendation flows, pass genre filter as query param to the backend endpoint.

---

### Feature 8 — Export Watchlist

```
User clicks "Export CSV" or "Export JSON" button in Watchlist.jsx
    ↓
exportWatchlistCSV(watchlist) or exportWatchlistJSON(watchlist) [utils/exportData.js]
    ↓
Constructs data string in memory
    ↓
Creates Blob + temporary <a> element
    ↓
Triggers browser download dialog
    ↓
File saved to user's Downloads folder
```

**No backend needed.** The `watchlist` array is already in `WatchlistContext` on the Watchlist page. This is a pure frontend utility.

---

### Feature 9 — Movie Decade Filter

```
Backend data flow:
GET /api/movies/popular?decade=1990
    ↓
routes.py passes decade param to recommender.get_movies_by_decade(1990)
    ↓
Returns movies with release_year in [1990, 1999]

Frontend data flow:
Decade selector UI in Home.jsx or Recommendations.jsx
    ↓
User selects "1990s" → api.js.getPopularMovies({ decade: 1990 })
    ↓
movies[] state updated → grid re-renders
```

**Backend prerequisite:** `release_year` must exist as a column in `movies_df`. Inspect the preprocessed pickle. If the TMDB CSV has `release_date` (string like "1994-09-23"), `preprocessing.py` must extract year during preprocessing.

---

### Feature 10 — Quick Rating Widget

```
User hovers MovieCard → star overlay appears (CSS group-hover, already in card structure)
    ↓
User clicks a star (1-5 stars displayed inline)
    ↓
MovieCard internal state: hoveredRating, selectedRating
    ↓
On click: authAPI.rateMovie(movie.movie_id, movie.title, rating * 2)
          [existing POST /api/user/ratings endpoint — rating is 1-10, stars map to 1-2-3-4-5 → 2-4-6-8-10]
    ↓
WatchlistContext ratings cache updated (or re-fetched)
```

**Note:** The existing `POST /api/user/ratings` endpoint already exists in `user_routes.py` (lines 198-233). No backend changes needed — only the `MovieCard.jsx` frontend widget is new.

**Auth gating:** Rating requires authentication. The widget should render conditionally: if not authenticated, clicking a star should show a prompt or silently skip rather than throw a 401.

---

## Build Order (Feature Dependencies)

The 10 features have the following dependency relationships. Build in this order:

### Phase 1 — Foundation (no cross-feature dependencies)

These features have no dependencies on each other or on other new features. Build first.

| Order | Feature | Why First |
|-------|---------|-----------|
| 1 | **Feature 4: LoadingSpinner** | `Home.jsx` imports it at line 4 and crashes without it. `Recommendations.jsx` uses it but has the import commented out — the app partially works without it but Home is broken. This is a production bug fix, not just a feature. |
| 2 | **Feature 5: Runtime Formatter** | Pure function, zero dependencies. Replace two inline expressions with `formatRuntime()` call. Takes 15 minutes. |
| 3 | **Feature 1: Theme Toggle** | Isolated to ThemeContext + tailwind.config.js + App.jsx. No dependency on other new features. |

### Phase 2 — localStorage Features (depend on Phase 1 being stable)

| Order | Feature | Why This Order |
|-------|---------|----------------|
| 4 | **Feature 3: Search History** | Needs `useSearchHistory` hook (standalone), then Recommendations.jsx integration. No dependency on other hooks. |
| 5 | **Feature 6: Recently Viewed** | Needs `useRecentlyViewed` hook + `RecentlyViewed.jsx` component + `MovieCard.jsx` onClick integration. Should come after Feature 5 (uses formatRuntime in MovieCard) and Feature 4 (LoadingSpinner used nearby). |

### Phase 3 — Backend Features (depend on Phase 2)

| Order | Feature | Why This Order |
|-------|---------|----------------|
| 6 | **Feature 2: Watch Status** | Schema migration + new PUT endpoint + Watchlist.jsx UI. Build before export (Feature 8) so export includes status field in the CSV/JSON. |
| 7 | **Feature 7: Genre Filter** | New GET endpoint + GenreFilter component + integration in Home + Recommendations. Standalone — doesn't depend on watch status. Can be built in parallel with Feature 2. |
| 8 | **Feature 9: Decade Filter** | Extends the same pattern as Feature 7. Build after Feature 7 because both modify the same endpoints and Recommendations page — do them in sequence to avoid merge conflicts. Also requires verifying `release_year` column exists. |

### Phase 4 — Polish Features (depend on Phases 2-3)

| Order | Feature | Why Last |
|-------|---------|----------|
| 9 | **Feature 8: Export Watchlist** | Build after Feature 2 (watch status) so exported data includes status. Frontend utility only — no backend changes. |
| 10 | **Feature 10: Quick Rating Widget** | Modifies `MovieCard.jsx` which is also touched by Feature 6. Build last to minimize conflicts. Requires auth to be working (already is). |

### Dependency Graph (Summary)

```
Feature 4 (LoadingSpinner)    ─→ Required by Recommendations.jsx + Home.jsx
Feature 5 (formatters.js)     ─→ Used by MovieCard.jsx, Watchlist.jsx
Feature 1 (ThemeContext)       ─→ Wraps App.jsx — build before adding new components

Feature 3 (Search History)    ─→ Integrates into Recommendations.jsx (needs it stable)
Feature 6 (Recently Viewed)   ─→ Integrates into MovieCard.jsx (needs F4, F5 done first)

Feature 2 (Watch Status)      ─→ DB migration first; Watchlist.jsx + PUT endpoint
Feature 7 (Genre Filter)      ─→ New GET /movies/genres + GenreFilter component
Feature 9 (Decade Filter)     ─→ Builds on same endpoint pattern as F7; same page

Feature 8 (Export Watchlist)  ─→ After F2 (status in export); pure frontend util
Feature 10 (Quick Rating)     ─→ After F6 (MovieCard.jsx stabilized)
```

### Phase Groupings for Roadmap

| Phase | Features | Rationale |
|-------|---------|-----------|
| **Phase 1: Bug Fix + Foundation** | F4 (LoadingSpinner), F5 (formatters), F1 (Theme) | Fixes the production crash, adds shared utilities, zero backend risk |
| **Phase 2: localStorage Features** | F3 (Search History), F6 (Recently Viewed) | Pure frontend, no migrations, independently deliverable |
| **Phase 3: Backend Features** | F2 (Watch Status), F7 (Genre Filter), F9 (Decade Filter) | Backend changes, DB migration, new endpoints — group for single deployment |
| **Phase 4: Polish** | F8 (Export), F10 (Quick Rating) | Frontend polish; F8 is trivial, F10 requires care on MovieCard |

---

## Anti-Patterns

### Anti-Pattern 1: Putting useSearchHistory / useRecentlyViewed in Context

**What people do:** Create a `SearchHistoryContext` and `RecentlyViewedContext` to match the pattern of `AuthContext` and `WatchlistContext`.

**Why it's wrong:** These hooks don't need a Provider — they don't share state between sibling components at different levels. `useSearchHistory` is only used in `Recommendations.jsx`. `useRecentlyViewed` is called from `MovieCard.jsx` (which is used in many places, but each instance can independently call the hook since they all share the same `localStorage` key as ground truth).

**Do this instead:** Custom hooks (`hooks/` directory) that read/write `localStorage` directly. No Provider, no Context, no wrapper in `main.jsx`.

---

### Anti-Pattern 2: Adding a Second recommender.py or DataFrame Load for Genre/Decade Queries

**What people do:** Create a new utility file that loads `movie_data.pkl` again to answer genre or decade queries.

**Why it's wrong:** The pkl is ~50-100MB for 5000 movies. Loading it twice doubles memory usage and startup time. The existing `get_recommender()` singleton handles this via the global `_recommender_instance`.

**Do this instead:** Add methods directly to the `MovieRecommender` class. Call `get_recommender()` in the new route handlers exactly as existing routes do.

---

### Anti-Pattern 3: Skipping the Alembic Migration for Watch Status

**What people do:** Add `watch_status` column to the SQLAlchemy model and rely on `create_all()` or direct table inspection to pick it up.

**Why it's wrong:** The `database.py` uses `Base.metadata.create_all()` — which only creates tables that don't exist. It does NOT add new columns to existing tables. Existing users' `watchlist_items` table will have no `watch_status` column, causing `column not found` errors at query time.

**Do this instead:** Run `alembic revision --autogenerate -m "add_watch_status_to_watchlist_items"` then `alembic upgrade head`. If Alembic is not yet configured, set it up first (takes ~5 minutes) or write a one-time migration script using SQLAlchemy `ALTER TABLE` directly.

---

### Anti-Pattern 4: Calling MovieCard's onClick from Inside MovieCard Without Prop Contract

**What people do:** Import `useRecentlyViewed` inside `MovieCard.jsx` and call `addRecentMovie` directly — but also expect parents to pass `onClick` via props.

**Why it's wrong:** Creates confusion about who "owns" the click: does the parent get the click event? Does recently-viewed always fire? What if a page doesn't want recently-viewed tracking (e.g., the Watchlist page where movies are already known)?

**Do this instead:** Accept an optional `onMovieClick` prop on MovieCard. Pages that want recently-viewed tracking pass `(movie) => addRecentMovie(movie)`. The existing watchlist toggle uses `e.stopPropagation()` so it won't conflict with the card's onClick.

---

### Anti-Pattern 5: Modifying MovieCard.jsx for Features 5, 6, and 10 in Three Separate Commits Without a Clear Sequence

**What people do:** Feature branches that each independently modify `MovieCard.jsx`, leading to three-way merge conflicts.

**Why it's wrong:** `MovieCard.jsx` is touched by Features 5, 6, and 10. All three changes land in the same file. Out-of-order merges create conflicts.

**Do this instead:** Apply changes to `MovieCard.jsx` in build order: F5 (add `formatRuntime` import, replace inline expression) → F6 (add `onMovieClick` prop + call) → F10 (add hover star widget). Each step is additive.

---

## Integration Points

### Internal Boundaries

| Boundary | Communication Pattern | Notes |
|----------|-----------------------|-------|
| `ThemeContext` ↔ `App.jsx` | Context read (`useTheme()`) | App.jsx conditionally applies `dark` CSS class to root div |
| `ThemeContext` ↔ all components | Tailwind `dark:` class variants | Components don't import ThemeContext; they just use `dark:bg-...` classes |
| `useRecentlyViewed` ↔ `MovieCard.jsx` | Hook called inside component | No prop-drilling needed; localStorage is shared storage |
| `GenreFilter.jsx` ↔ `Home.jsx` | Props: `genres`, `selectedGenres`, `onChange` | Stateless child; parent owns state |
| `GenreFilter.jsx` ↔ `Recommendations.jsx` | Props: same interface | Reuse same component in two pages |
| `WatchlistContext` ↔ `Watchlist.jsx` | Context (`useWatchlist()`) | Watch status update goes through new `authAPI.updateWatchStatus()` → `loadWatchlist()` re-syncs |
| New `PUT /watchlist/{id}/status` ↔ `user_routes.py` | FastAPI + SQLAlchemy | Same auth dependency pattern as existing endpoints |
| `recommender.get_all_genres()` ↔ `GET /movies/genres` | Direct method call via `get_recommender()` | Follows existing pattern in `routes.py` |
| `exportData.js` ↔ `Watchlist.jsx` | Direct function call | Import utility, call with `watchlist` array, browser handles download |

### Prerequisite Verification

| Feature | Prerequisite to Verify Before Building |
|---------|---------------------------------------|
| Feature 9 (Decade Filter) | Does `movies_df` have a `release_year` or `release_date` column? Check `backend/app/ml/preprocessing.py` output columns. If `release_date` exists as string, extract year during preprocessing and regenerate pickle. |
| Feature 10 (Quick Rating) | Rating scale mapping: existing `MovieRating.rating` accepts float 1-10 (confirmed in `models_db.py` line 66). Star widget uses 1-5 stars → multiply by 2 for backend value. |
| Feature 1 (Theme) | Tailwind `darkMode: 'class'` not yet in `tailwind.config.js` — must be added before any `dark:` classes will work. |
| Feature 2 (Watch Status) | Alembic must be configured or a manual migration written. Check if `alembic.ini` and `migrations/` directory exist before starting. |

---

## Sources

- Direct inspection of `frontend/src/components/MovieCard.jsx` — confirmed runtime inline expression, hover overlay structure
- Direct inspection of `frontend/src/pages/Home.jsx` — confirmed LoadingSpinner import already present (line 4), crash risk without file
- Direct inspection of `frontend/src/pages/Recommendations.jsx` — confirmed LoadingSpinner import commented out (line 4), used uncommented on lines 128 and 171
- Direct inspection of `frontend/src/pages/Watchlist.jsx` — confirmed duplicate runtime formatter pattern (line 117)
- Direct inspection of `backend/app/models_db.py` — confirmed WatchlistItem has no watch_status column; MovieRating accepts float 1-10
- Direct inspection of `backend/app/api/user_routes.py` — confirmed existing rating endpoint (POST /ratings); no watch status endpoint
- Direct inspection of `backend/app/api/routes.py` — confirmed no /movies/genres or decade filter endpoint
- Direct inspection of `backend/app/ml/recommender.py` — confirmed get_all_genres() and decade filtering do not exist; `_format_movie()` returns `movie['runtime']` as int
- Direct inspection of `frontend/tailwind.config.js` — confirmed `darkMode` key is absent
- Direct inspection of `frontend/src/index.css` — confirmed `.loader` CSS class exists; no dark mode variables
- Direct inspection of `frontend/src/App.jsx` — confirmed Provider wrapping order; no ThemeProvider present
- `.planning/PROJECT.md` — confirmed localStorage decision for ephemeral data, DB column decision for watch status, single-user constraint

---

*Architecture research for: Movie Recommender — 10 Feature Expansion (v1 Milestone)*
*Researched: 2026-02-21*
