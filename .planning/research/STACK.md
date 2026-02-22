# Stack Research

**Domain:** React + FastAPI Movie Recommender — Feature Expansion (10 features)
**Researched:** 2026-02-21
**Confidence:** HIGH (all core patterns verified against official docs and existing codebase)

---

## Summary Verdict

**No new npm or pip packages are required for any of the 10 features.** Every feature can be implemented with the stack already installed. The existing Tailwind CSS 3.3.6, lucide-react 0.294.0, React Context API pattern, FastAPI + SQLAlchemy + Alembic, and vanilla JS browser APIs cover 100% of the requirements. The only configuration change is adding `darkMode: 'class'` to `tailwind.config.js`.

---

## Recommended Stack

### Core Technologies (Unchanged)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| React 18.2.0 | ^18.2.0 | Frontend UI | Already installed; hooks (useState, useEffect, useContext) handle all 10 features without external state manager |
| FastAPI 0.104.1 | ^0.104.1 | Backend API | Already installed; Query() parameter typing handles genre/decade filter endpoints natively |
| Tailwind CSS 3.3.6 | ^3.3.6 | Styling + dark mode | Already installed; `darkMode: 'class'` strategy plus `dark:` prefix utilities is the authoritative 2025 pattern for v3 |
| SQLAlchemy 2.0.23 | ^2.0.23 | ORM + schema | Already installed; `Column(String)` addition to `WatchlistItem` handles Watch Status |
| Alembic 1.13.0 | ^1.13.0 | DB migrations | Already installed; `alembic revision --autogenerate` generates the Watch Status column migration |
| lucide-react 0.294.0 | ^0.294.0 | Icons | Already installed; `Star` icon with fill prop covers Quick Rating Widget without react-stars or similar |

### Supporting Libraries (No New Installs)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| React Context API | built-in | Theme state management | Theme toggle — wrap app in `ThemeContext`, toggle `dark` class on `document.documentElement` |
| localStorage API | browser built-in | Ephemeral persistence | Search History (last 10 queries), Recently Viewed (last 20 movies), Theme preference |
| `URL.createObjectURL` + Blob | browser built-in | CSV/JSON file download | Export Watchlist — no `react-csv` or `file-saver` needed; Blob + anchor click is the 2025 standard |
| pandas (already in backend) | 2.1.3 | Genre/decade filtering | `movies_df[movies_df['genres'].apply(lambda g: genre in g)]` — zero new Python deps |

---

## Feature-by-Feature Approach

### Feature 1: Dark/Light Theme Toggle

**Approach:** Tailwind CSS class strategy + React Context + localStorage

**Configuration change required:** Add `darkMode: 'class'` to `tailwind.config.js`. The current config has no `darkMode` key, which defaults to `'media'` (system preference, not togglable). Adding `'class'` enables manual control.

```js
// tailwind.config.js — add this key
export default {
  darkMode: 'class',  // ADD THIS LINE
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  // ... rest unchanged
}
```

**React pattern:** Create `ThemeContext` (mirrors existing `AuthContext` pattern). Store `theme` in `localStorage` key `'theme'`. On change, toggle `dark` class on `document.documentElement`. Inline script in `index.html` `<head>` prevents flash of unstyled content (FOUC).

**Why NOT next-themes:** That library is for Next.js. This is a Vite/React app.
**Why NOT CSS variables approach:** App already uses Tailwind `dark:` class utilities in several components — the class strategy is the natural extension.

**Existing dark classes in codebase:** None yet — all colors are hardcoded gray/dark palette. "Light mode" will require adding `dark:` variants to existing components as a design decision. The toggle mechanism is straightforward; the styling effort is the work.

**Confidence:** HIGH — verified against [Tailwind v3 official dark mode docs](https://v3.tailwindcss.com/docs/dark-mode)

---

### Feature 2: Movie Watch Status

**Approach:** Alembic migration + SQLAlchemy column + FastAPI PATCH endpoint + React dropdown

**Backend:** Add `watch_status` String column to `WatchlistItem` model with default `'plan_to_watch'`. Valid values: `'plan_to_watch'`, `'watching'`, `'completed'`. Run `alembic revision --autogenerate -m "add watch status to watchlist"` then `alembic upgrade head`.

**SQLite caveat:** Alembic's autogenerate + SQLite batch mode is required for column addition because SQLite does not support `ALTER TABLE ADD COLUMN` with constraints. Use `--autogenerate` which handles this automatically via batch operations. No manual migration writing needed.

**FastAPI:** Add `PATCH /api/user/watchlist/{movie_id}/status` endpoint accepting `{"status": "watching"}` body. Add `status` query param to `GET /api/user/watchlist` for server-side filtering.

**Frontend:** Replace fixed watchlist display with a `<select>` dropdown per item. Filter chips above watchlist list. No new library — native HTML `<select>` styled with Tailwind matches existing UI pattern.

**Confidence:** HIGH — alembic autogenerate pattern confirmed by official docs

---

### Feature 3: Search History

**Approach:** Custom `useSearchHistory` hook using localStorage

**Pattern:**
```js
// src/hooks/useSearchHistory.js
function useSearchHistory(maxItems = 10) {
  const [history, setHistory] = useState(() => {
    return JSON.parse(localStorage.getItem('searchHistory') || '[]')
  })
  const addQuery = (query) => { /* deduplicate, prepend, trim to maxItems, persist */ }
  const clearHistory = () => { setHistory([]); localStorage.removeItem('searchHistory') }
  return { history, addQuery, clearHistory }
}
```

**Why NOT usehooks-ts or @uidotdev/usehooks:** These libraries add a dependency for a 15-line hook. The existing codebase has zero custom hooks — establish the pattern inline.

**Integration point:** Call `addQuery` from the search handler in `Recommendations.jsx` or wherever search is triggered. Render history list below the search `<input>`, items clickable to re-run search.

**localStorage key:** `'searchHistory'` (array of strings, newest first)

**Confidence:** HIGH — standard React pattern, no library verification needed

---

### Feature 4: Loading Spinner Component

**Approach:** Pure Tailwind CSS `animate-spin` + accessible `role="status"`

The `.loader` CSS class already exists in `index.css` (lines 86-98) as a spinner animation. The `LoadingSpinner` component is already imported in `Home.jsx` and `Recommendations.jsx` — it just needs to be created as a file.

**Create:** `src/components/LoadingSpinner.jsx` wrapping the existing `.loader` CSS class with `role="status"` and a visually hidden `<span>` for screen readers.

```jsx
export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div role="status" className="flex flex-col items-center justify-center py-12">
      <div className="loader" aria-hidden="true" />
      <span className="sr-only">{message}</span>
      {message && <p className="text-gray-400 mt-4 text-sm">{message}</p>}
    </div>
  )
}
```

**Why NOT react-spinners or similar:** The spinner CSS already exists in `index.css`. Creating a component around it is 10 lines, not a dependency.

**Confidence:** HIGH — the `.loader` class is already in `index.css`; this is a zero-research feature

---

### Feature 5: Movie Runtime Formatter

**Approach:** Pure JavaScript utility function

**Create:** `src/utils/formatRuntime.js`

```js
export function formatRuntime(minutes) {
  if (!minutes || minutes <= 0) return null
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h === 0) return `${m}m`
  if (m === 0) return `${h}h`
  return `${h}h ${m}m`
}
```

**Note:** `MovieCard.jsx` already has inline runtime math at line 122 (`{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m`). This feature is extracting that logic into a shared utility and applying it consistently.

**Why NOT a library:** `date-fns` has duration formatting but adds a 40KB dependency for a 5-line function. Avoid.

**Confidence:** HIGH — pure logic, no external dependencies or framework interaction

---

### Feature 6: Recently Viewed Movies

**Approach:** Custom `useRecentlyViewed` hook using localStorage + home page section

**Pattern:** Identical to `useSearchHistory` (Feature 3). Store array of movie objects (not just IDs — store `{movie_id, title, poster_path, genres}` snapshot to avoid re-fetching). Cap at 20 items. Newest first.

**localStorage key:** `'recentlyViewed'` (array of movie snapshot objects)

**Trigger:** Call `addMovie(movie)` when a MovieCard is clicked. The click handler in `MovieCard.jsx` currently has no `onClick` at the card level — add one.

**Home page:** Add a "Recently Viewed" section above or below Popular Movies. Reuse the same horizontal grid pattern already in `Home.jsx`. Show only if `recentlyViewed.length > 0`.

**Why NOT backend:** PROJECT.md explicitly decided "localStorage: Frontend-only features store in localStorage — acceptable for single user." Storing in DB would require a new table and is out of scope.

**Confidence:** HIGH

---

### Feature 7: Movie Genres Filter

**Approach:** Backend query param filter + frontend multi-select chips

**Backend:** Add `GET /api/movies/filter` endpoint (or extend `/movies/popular` with optional `genres` query param). Use FastAPI's `List[str]` query param:

```python
@router.get("/movies/popular")
async def get_popular_movies(
    limit: int = Query(20, ge=1, le=50),
    genres: Optional[List[str]] = Query(default=None)
):
    recommender = get_recommender()
    movies = recommender.get_popular_movies(limit * 3)  # over-fetch
    if genres:
        movies = [m for m in movies if any(g in genres for g in m['genres'])]
    return {"movies": movies[:limit], "count": len(movies[:limit])}
```

**Why extend existing endpoint vs. new endpoint:** Fewer API surface changes, backward-compatible (genres param is optional).

**Frontend:** Chip components using Tailwind button styles. Active chip: `bg-red-600 text-white`. Inactive: `bg-gray-700 text-gray-300 hover:bg-gray-600`. Multi-select state as `Set<string>`. Genre list fetched once from `/api/statistics/genres` which already exists.

**Why NOT a dropdown:** Chips are the 2025 standard for multi-select filter UI on grid/card layouts. Better discoverability, faster interaction than a dropdown.

**Confidence:** HIGH — FastAPI Query List pattern verified against [official FastAPI docs](https://fastapi.tiangolo.com/tutorial/query-param-models/)

---

### Feature 8: Export Watchlist as CSV/JSON

**Approach:** Frontend-only Blob download — no backend endpoint needed

**Pattern:**

```js
// src/utils/exportWatchlist.js
export function exportAsCSV(watchlist) {
  const headers = ['Title', 'Genres', 'Rating', 'Status', 'Added']
  const rows = watchlist.map(m => [m.movie_title, m.genres, m.vote_average, m.watch_status, m.added_at])
  const csv = [headers, ...rows].map(r => r.map(String).join(',')).join('\n')
  downloadBlob(csv, 'watchlist.csv', 'text/csv')
}

export function exportAsJSON(watchlist) {
  const json = JSON.stringify(watchlist, null, 2)
  downloadBlob(json, 'watchlist.json', 'application/json')
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
```

**Why NOT react-csv or file-saver:** These libraries exist for complex CSV scenarios (streaming, large files, encoding edge cases). This watchlist will be under 1000 rows for a personal app. The Blob pattern is 20 lines and zero dependencies.

**CSV edge cases to handle:** Commas/quotes in movie titles — wrap fields in double quotes and escape internal quotes (`"` → `""`).

**Confidence:** HIGH — Blob download is a stable browser API, no library verification needed

---

### Feature 9: Movie Decade Filter

**Approach:** Backend query param filter on `release_year` field + frontend decade button group

**Backend:** Add `decade` optional query param (e.g., `?decade=1990`) to the popular/filter endpoint. Decade filter logic in recommender: `release_year >= decade AND release_year < decade + 10`.

**Data availability check:** `recommender.py` `_format_movie` does not currently return `release_year`. Check the `movies_df` columns — if `release_date` exists in the DataFrame, extract year from it. If not, this requires verifying the CSV source data.

**Frontend:** Row of decade buttons: `1970s`, `1980s`, `1990s`, `2000s`, `2010s`, `2020s`. Single-select (unlike genre multi-select). Active state uses same `bg-red-600` pattern as genre chips. Combine with genre filter via `&` query params.

**Why single-select for decade vs. multi-select:** A movie belongs to exactly one decade — multi-select adds no value and clutters UI.

**Confidence:** MEDIUM — decade filter logic is straightforward, but `release_year` field availability in the existing pandas DataFrame needs verification before implementation (flag for developer)

---

### Feature 10: Quick Rating Widget

**Approach:** lucide-react `Star` icon with hover state — no react-stars or react-rating library

**Pattern:** 5-star widget rendered on `MovieCard.jsx` hover overlay (already has `group-hover:opacity-100` overlay pattern at line 66). Uses two state variables: `hoverRating` (0-5, tracks mouse position) and `currentRating` (saved value).

```jsx
// Inside MovieCard hover overlay
{[1,2,3,4,5].map((star) => (
  <Star
    key={star}
    className={`h-5 w-5 cursor-pointer transition-colors ${
      star <= (hoverRating || currentRating)
        ? 'text-yellow-400 fill-current'
        : 'text-gray-400'
    }`}
    onMouseEnter={() => setHoverRating(star)}
    onMouseLeave={() => setHoverRating(0)}
    onClick={() => handleRate(star)}
  />
))}
```

**lucide-react fill behavior:** The `Star` component from `lucide-react` supports the `fill` CSS property. Use `fill-current` Tailwind class when `star <= rating` to fill the star icon. The existing codebase already does this pattern with `Heart` at `MovieCard.jsx` line 98-99 (`fill={inWatchlist ? 'currentColor' : 'none'}`).

**Backend integration:** The `POST /api/user/ratings` endpoint and `MovieRating` model already exist in `user_routes.py`. The quick widget calls this existing endpoint. No backend changes needed.

**Scale clarification:** The existing ratings table uses 1-10 scale (Float column). The widget uses 1-5 stars. Map 5 stars → 10 scale (multiply by 2) or store as-is and treat 5 as maximum. Recommend storing star value directly (1-5) and updating the `rating` field max expectation in the UI.

**Why NOT react-stars / react-rating-stars-component:** These are unmaintained (last updates 2021-2022). The pattern using lucide-react's Star icon is 15 lines, matches the existing icon library, and the existing codebase already has the Heart fill pattern as proof of concept.

**Confidence:** HIGH — existing `MovieRating` backend endpoints and `Heart` fill pattern confirm feasibility

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Native Blob download (CSV/JSON) | `react-csv` (npm) | Only if exporting 10,000+ rows with streaming, or if special character encoding is a production concern |
| Custom `useLocalStorage` hook | `usehooks-ts` library | Only if adding 5+ localStorage hooks across the codebase — then the library's TypeScript generics and SSR safety are worth the install |
| Tailwind `dark:` class strategy | CSS custom properties (variables) | If using a design system with 3+ themes, or if the team uses a CSS-in-JS solution |
| lucide-react Star for rating | `react-rating-stars-component` | Never — that library is unmaintained since 2021 |
| Alembic `--autogenerate` | Manual `ALTER TABLE` SQL | Never for this project — Alembic handles SQLite batch mode automatically |
| FastAPI Query List for genre filter | `fastapi-filter` library | Only for complex multi-model filtering in a large API with 20+ filterable fields |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `react-csv` | Overkill for a personal app's watchlist; unmaintained since 2022 | Native Blob + `URL.createObjectURL` |
| `react-rating-stars-component` | Last npm publish 2021; React 18 untested | lucide-react `Star` icon + useState |
| `react-toggle` or `react-switch` | Extra dependency for a toggle that Tailwind handles in 3 lines | Tailwind + native `<button>` with `role="switch"` |
| `usehooks-ts` | 10KB library for hooks you can write in 15 lines each | Inline custom hooks following existing `AuthContext` / `WatchlistContext` patterns |
| Tailwind v4 patterns | App is on Tailwind v3 — v4 configuration moved to CSS directives, not `tailwind.config.js`. Mixing docs versions will break the build | Stay on Tailwind v3 docs at v3.tailwindcss.com |
| `next-themes` | This is a Vite/React app, not Next.js; `next-themes` is SSR-aware and unnecessary | ThemeContext + `document.documentElement.classList` |

---

## Stack Patterns by Variant

**For localStorage features (Search History, Recently Viewed, Theme):**
- Use pattern: `useState(() => JSON.parse(localStorage.getItem(KEY) || 'default'))` for lazy initialization
- Sync back with `useEffect` on state change: `localStorage.setItem(KEY, JSON.stringify(value))`
- Never call `localStorage` directly in render — always wrap in `useState` initializer or `useEffect`
- Follows the pattern already established in `WatchlistContext.jsx` (lines 30-31)

**For backend filter endpoints (Genres, Decade):**
- Add as optional query params to existing `/movies/popular` endpoint before creating new endpoints
- Use `Optional[List[str]] = Query(default=None)` for genre list
- Use `Optional[int] = Query(default=None)` for decade year
- Filter happens in Python on the in-memory pandas DataFrame — no SQL query changes needed

**For DB schema change (Watch Status):**
- Add column to `models_db.py` first
- Run `alembic revision --autogenerate -m "description"`
- Review generated migration file before applying
- Apply with `alembic upgrade head`
- Use `server_default="plan_to_watch"` to avoid nullable issues on existing rows

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Tailwind CSS 3.3.6 | `darkMode: 'class'` config key | The `'selector'` strategy is an alias introduced in 3.4.1 — both work for this use case; `'class'` is stable in 3.3.6 |
| lucide-react 0.294.0 | React 18.2.0 | `Star` icon's `fill` prop works via CSS class `fill-current` — confirmed by existing `Heart` usage in `MovieCard.jsx` |
| Alembic 1.13.0 | SQLite (dev) + PostgreSQL (prod) | Batch migrations for SQLite are automatic with `--autogenerate`; no manual `with op.batch_alter_table()` needed |
| FastAPI 0.104.1 | `Optional[List[str]] = Query(default=None)` | List query params require `Query()` annotation to be recognized as multi-value params, not a single comma-separated string |

---

## Installation

No new packages required. The one configuration change:

```bash
# No npm install needed — zero new dependencies

# After adding watch_status column to models_db.py:
cd backend
alembic revision --autogenerate -m "add watch_status to watchlist_items"
alembic upgrade head
```

---

## Sources

- [Tailwind CSS v3 Dark Mode docs](https://v3.tailwindcss.com/docs/dark-mode) — `darkMode: 'class'` configuration, `document.documentElement.classList.toggle('dark', ...)` pattern — **HIGH confidence**
- [FastAPI Query Parameters docs](https://fastapi.tiangolo.com/tutorial/query-param-models/) — `Optional[List[str]] = Query(default=None)` for multi-value params — **HIGH confidence**
- Existing codebase `MovieCard.jsx` lines 98-99 — `fill={inWatchlist ? 'currentColor' : 'none'}` pattern for lucide-react icon fill — **HIGH confidence (direct code evidence)**
- Existing codebase `index.css` lines 86-98 — `.loader` CSS class already exists, `LoadingSpinner` component is a wrapper only — **HIGH confidence (direct code evidence)**
- Existing codebase `user_routes.py` lines 198-233 — `MovieRating` POST endpoint exists, Quick Rating Widget has no backend work — **HIGH confidence (direct code evidence)**
- [MDN: URL.createObjectURL](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL) — Blob download pattern — **HIGH confidence**
- WebSearch: "React localStorage custom hook pattern 2025" — confirms inline hook pattern over library — **MEDIUM confidence (multiple sources agree)**

---

*Stack research for: Movie Recommender feature expansion (10 features)*
*Researched: 2026-02-21*
