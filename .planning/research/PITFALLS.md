# Pitfalls Research

**Domain:** Feature expansion for React 18 + FastAPI Movie Recommender app
**Researched:** 2026-02-21
**Confidence:** HIGH (codebase directly inspected; specific pitfalls traced to actual files)

---

## Critical Pitfalls

### Pitfall 1: Dark Mode Flash of Unstyled Content (FOUC)

**What goes wrong:**
The page loads with the hardcoded dark gradient background (`index.css` line 8-9) for a visible instant before JavaScript reads `localStorage` and applies the user's preferred theme class to `<html>`. On subsequent page loads, users see a white flash (if light mode) or an inverted-color flicker.

**Why it happens:**
The current `tailwind.config.js` has no `darkMode` configuration at all — dark mode is not yet enabled. When it is added using the `class` strategy, React's effect-based approach reads localStorage inside `useEffect`, which runs *after* the first paint. The body also has a hardcoded `background: linear-gradient(135deg, #0f172a ...)` in `index.css` that completely bypasses Tailwind's `dark:` variant system.

**How to avoid:**
1. Set `darkMode: 'class'` in `tailwind.config.js`.
2. Inject a blocking `<script>` inside `<head>` of `index.html` (before any React bundle) that reads `localStorage` and adds/removes the `dark` class on `<html>` synchronously.
3. Remove the hardcoded CSS background from `index.css` and replace with Tailwind `dark:` variants so the theme-aware colors apply before paint.
4. Do NOT read `localStorage` only inside a React `useEffect` — that is guaranteed to flash on every page load.

**Warning signs:**
- Theme toggle "works" but you see a brief flash on hard refresh.
- Light mode background appears for ~100ms before switching to dark.
- Theme is "remembered" but the transition feels wrong.

**Phase to address:**
Feature 1 (Dark/Light Theme Toggle) — must be the very first implementation decision because it affects global CSS architecture.

---

### Pitfall 2: Watch Status Column Breaking Existing SQLite Schema (No Alembic)

**What goes wrong:**
The project explicitly has "No Database Migrations" listed as a critical missing feature (`CONCERNS.md` line 257). `CONCERNS.md` confirms Alembic is in requirements but not configured. Adding a `watch_status` column to `WatchlistItem` by modifying `models_db.py` and restarting will silently do nothing if the `watchlist_items` table already exists — SQLAlchemy's `create_all()` does not alter existing tables, it only creates missing ones.

**Why it happens:**
`database.py` line 29 calls `Base.metadata.create_all(bind=engine)` on startup. This creates missing tables but never modifies columns in existing ones. If a user has an existing `watchlist_items` table from a previous session, the new `watch_status` column simply will not exist, and every subsequent INSERT that omits it will fail silently or crash with a database error.

**How to avoid:**
Choose one approach and commit to it:
- **Option A (preferred for production path):** Configure Alembic properly with `alembic init alembic`, set `target_metadata = Base.metadata`, and generate a migration with `alembic revision --autogenerate -m "add_watch_status"`. Run `alembic upgrade head` on startup.
- **Option B (acceptable for single-dev SQLite only):** Add the column with SQLite's `ALTER TABLE watchlist_items ADD COLUMN watch_status VARCHAR DEFAULT 'plan_to_watch'`. Execute this idempotently on startup (check if column exists before adding).
- **Never:** Drop and recreate the table to apply schema changes — this destroys user watchlist data.

**Warning signs:**
- App starts without error but watch status is never saved.
- `OperationalError: table watchlist_items has no column named watch_status` appears on first write after restart.
- Watchlist items disappear after restarting app (if drop-and-recreate was used).

**Phase to address:**
Feature 2 (Movie Watch Status) — this is the only feature in this milestone requiring a schema change and must be addressed before any code using `watch_status` is merged.

---

### Pitfall 3: `LoadingSpinner` Import is Commented Out in Recommendations.jsx

**What goes wrong:**
`Recommendations.jsx` line 4 reads `//import LoadingSpinner from '../components/LoadingSpinner'` — the import is commented out but `<LoadingSpinner>` is used at lines 128 and 171. This means the app is currently broken: any loading state in Recommendations renders `undefined` as a component and throws a React runtime error.

**Why it happens:**
The component file `frontend/src/components/LoadingSpinner.jsx` does not exist. Someone commented out the import to make the file parse without error, but left the JSX references in place. `Home.jsx` imports it successfully (line 4) expecting it to exist, which means `Home` is also broken until the component file is created.

**How to avoid:**
Create `LoadingSpinner.jsx` as the very first task before any other feature work. The existing `.loader` CSS class in `index.css` (lines 86-98) provides a ready-made spinner — the component just needs to wrap it. Uncomment the import in `Recommendations.jsx` immediately after.

**Warning signs:**
- Running the dev server and navigating to `/recommendations` throws `TypeError: LoadingSpinner is not a function`.
- Searching for a movie causes the UI to go blank with a console error.
- `Home.jsx` similarly breaks because it also imports from the non-existent path.

**Phase to address:**
Feature 4 (Loading Spinner) — must be built and imported before any other feature that displays a loading state. Zero other features should be developed assuming a working Recommendations page until this is fixed.

---

### Pitfall 4: Genres Stored as Comma-Separated String — Genre Filter Will Break

**What goes wrong:**
`WatchlistItem.genres` is stored as a comma-joined string (e.g., `"Action,Drama,Comedy"`) — see `user_routes.py` line 101: `genres=",".join(item.genres)`. The `Watchlist.jsx` page works around this by splitting on commas (line 163). The Genre Filter feature (Feature 7) needs to query movies from the recommender DataFrame, not from the `WatchlistItem` table, but genre inconsistency across these two data stores creates a subtle contract mismatch: the ML data uses Python lists, the DB stores comma strings, and the frontend receives either depending on code path.

**Why it happens:**
The watchlist endpoint stores genres as a comma-separated string for simplicity. The ML recommender returns genres as a Python list. Two different representations of the same data exist simultaneously with no schema enforcement. The `CONCERNS.md` (line 121) explicitly flags this as a SQL injection-adjacent fragile area.

**How to avoid:**
For Feature 7 (Genre Filter), query genres exclusively from the `recommender.movies_df` (the ML data), not from `WatchlistItem`. The filter endpoint should read the genre list from the DataFrame and filter by comparing list membership. Do not rely on the comma-string format in `WatchlistItem.genres` for any filtering logic. When the genre filter chips send selected genres to the backend, compare against the DataFrame's list-typed `genres` column, not the DB string.

**Warning signs:**
- Genre filter returns no results even when matching movies exist.
- Genre filter correctly filters some movies but misses others due to whitespace around the comma separator.
- Genre chip UI shows duplicate genres (e.g., `" Drama"` and `"Drama"` as separate options).

**Phase to address:**
Feature 7 (Movie Genres Filter) — the backend filter endpoint must source genres from the DataFrame, not the DB table.

---

## Moderate Pitfalls

### Pitfall 5: Quick Rating Widget Triggers on Every Mouse Move (Debounce Missing)

**What goes wrong:**
The Quick Rating Widget (Feature 10) uses hover-to-reveal stars. If the rating is saved on every `mouseenter` or `mouseover` event rather than on an explicit click, the app fires API calls on every star the user hovers across. With no debouncing, hovering left-to-right across 5 stars fires 5 `POST /api/user/ratings` calls in rapid succession.

**Why it happens:**
Hover interactions in React fire on every pixel movement. The `rate_movie` endpoint in `user_routes.py` (lines 198-233) updates the rating on every call — it does not validate that the value changed. Five simultaneous calls for the same movie will race to update the same row, and the "last write wins" outcome is non-deterministic.

**How to avoid:**
Save the rating only on `mouseup` (click) — not on `mouseover` or `mouseenter`. The hover state should update local visual state only (which star is highlighted); the API call fires only when the user clicks a star. This matches the UX pattern users expect from star rating widgets (hover = preview, click = confirm).

**Warning signs:**
- Backend logs show multiple rapid rating requests for the same movie within milliseconds.
- Rating reverts to a previous value after a quick hover-and-move-away.
- Network tab shows 5 POST requests when the user simply passes the mouse over the stars.

**Phase to address:**
Feature 10 (Quick Rating Widget).

---

### Pitfall 6: Decade Filter Requires `release_year` That Doesn't Exist in the DataFrame

**What goes wrong:**
The Movie Decade Filter (Feature 9) needs to filter movies by decade (1970s, 1980s, etc.). The ML recommender DataFrame currently stores `release_date` as a full date string (or similar). There is no `release_year` column pre-extracted. Filtering by decade in a pandas `iterrows()` loop — the existing pattern in `recommender.py` — is extremely slow because it parses strings on every row evaluation.

**Why it happens:**
The data preprocessing pipeline (`preprocessing.py`) does not extract year from `release_date`. The `_format_movie` method does not include `release_year` in its output dict. Decade filtering added naively as a loop will behave like the existing `get_mood_based_recommendations` function (which already uses `iterrows()` and is flagged as a performance problem in `CONCERNS.md` line 153-158).

**How to avoid:**
Extract `release_year` as a derived integer column in `preprocessing.py` during data loading: `df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year`. Then the decade filter becomes a vectorized boolean mask: `df[df['release_year'].between(start_year, end_year)]`. This is orders of magnitude faster than iterating rows. No changes to the pickle format are needed — the column derives from data already present.

**Warning signs:**
- Decade filter endpoint takes 2+ seconds to respond with 5000 movies.
- Filter returns movies from the wrong decade (off-by-one in the decade boundary calculation).
- `KeyError: 'release_year'` when the filter endpoint tries to access a column not in the DataFrame.

**Phase to address:**
Feature 9 (Movie Decade Filter) — add the `release_year` derivation in preprocessing, not in the endpoint handler.

---

### Pitfall 7: localStorage Race Condition Between Multiple Features

**What goes wrong:**
Features 3 (Search History), 6 (Recently Viewed), and 1 (Theme) all use `localStorage` independently. If multiple hooks or components read/write different localStorage keys on mount at the same time, and one of them fails (e.g., localStorage is full — 5MB browser limit), the error is uncaught and silently corrupts other localStorage state because bare `localStorage.getItem()` / `setItem()` calls throw `DOMException` when storage is full but the app has no error handlers for this.

**Why it happens:**
`WatchlistContext.jsx` already uses `localStorage.getItem('watchlist')` with a simple `JSON.parse()` and no try-catch. If `localStorage.setItem` throws, the current pattern does not recover. Adding three more localStorage consumers without wrapping them in a try-catch pattern multiplies this risk.

**How to avoid:**
Create a single `useLocalStorage(key, defaultValue)` custom hook that wraps all `localStorage` operations in try-catch, has a consistent fallback to `defaultValue` on failure, and is used by all three new features. This hook exists as a well-known React pattern. Do not write raw `localStorage.getItem/setItem` in each feature component.

**Warning signs:**
- App silently loses theme preference or search history after a session with many movies viewed.
- Console shows `QuotaExceededError: Failed to execute 'setItem' on 'Storage'`.
- Recently Viewed section shows stale data that doesn't update on navigation.

**Phase to address:**
Feature 3 (Search History) — build the shared hook at this point; Features 6 and 1 then consume it.

---

### Pitfall 8: Hardcoded `http://localhost:8000` Throughout WatchlistContext

**What goes wrong:**
`WatchlistContext.jsx` has `http://localhost:8000/api/user/watchlist` hardcoded directly in the file (lines 46 and 101). This bypasses the `API_BASE_URL` constant defined in `api.js`. When adding new features, developers will likely follow the same pattern (copy-paste the hardcoded URL) rather than using the centralized API service.

**Why it happens:**
The `WatchlistContext` was written with direct `axios` calls rather than using the `movieAPI` service module. This established a dual-import pattern: some API calls go through `api.js` (which has the base URL once), others use raw `axios` with hardcoded URLs. New features copying `WatchlistContext` as a template inherit this anti-pattern.

**How to avoid:**
Any new endpoint (Watch Status update, Genre Filter, Decade Filter, Quick Rating) must use the `api.js` service module or `authAPI.js` rather than raw `axios` with hardcoded URLs. Do not copy the `WatchlistContext.jsx` pattern when building new features.

**Warning signs:**
- A new feature's API calls work locally but silently fail after deploying to a staging environment.
- Search for `localhost:8000` in the codebase and find it in more than 2-3 files (it should be 1).
- A feature's endpoint calls work but miss the interceptors (auth headers) that `api.js` provides.

**Phase to address:**
All new features — establish the rule at the start of the milestone: no raw `axios` calls with hardcoded URLs.

---

### Pitfall 9: Quick Rating and Existing Rating System Are Incompatible Scales

**What goes wrong:**
The existing `MovieRating` model stores `rating` as a float with no bounds checking (confirmed in `CONCERNS.md` line 113-117). The existing UI displays ratings as "X/10" scale (from TMDB `vote_average`). The Quick Rating Widget (Feature 10) will likely use a 1-5 star interface. If the stars map to 1-5 and the widget saves `rating=3` while the existing rating page saves `rating=7.5`, the two ratings coexist on the same `movie_id` for the same user with completely different scales.

**Why it happens:**
There is no existing rating scale convention enforced in the codebase. The `MovieRating.rating` column accepts any float. The movie cards already show `vote_average.toFixed(1)` (a TMDB 0-10 scale) under the same star icon that the Quick Rating widget would use for user ratings (1-5 scale). The two will visually conflict.

**How to avoid:**
Decide the user rating scale once and enforce it everywhere. The simplest choice: use 1-5 stars, store as integers 1-5, display distinctly (not alongside `vote_average`). Add a `Field(ge=1, le=5)` Pydantic constraint to `MovieRatingCreate.rating`. The Quick Rating widget and any future rating UI must use this same scale.

**Warning signs:**
- A user rates a movie 5 stars via the new widget and the watchlist stats show their "average rating" suddenly jumps from 7.5 to 3.
- The movie card shows two different "star" numbers simultaneously (one from TMDB, one from user).
- The `/api/user/ratings` endpoint returns a mix of 0-10 and 1-5 values for the same user.

**Phase to address:**
Feature 10 (Quick Rating Widget) — define and enforce the scale as the very first step before building the UI.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Using `create_all()` instead of Alembic for Watch Status column | Ships faster, no migration setup | Schema drift becomes unrecoverable across environments; prod vs dev diverge silently | Never — even on SQLite, use an idempotent `ALTER TABLE` check |
| Reading localStorage in `useEffect` for theme toggle | Simple React pattern | FOUC on every page load; perceived as broken by users | Never for theme — use blocking script in `<head>` |
| Storing genres as comma-string in DB | No schema change needed | Genre filter logic must handle two formats; bugs at edge cases (comma in name, whitespace) | Acceptable for now IF all new code reads from DataFrame, not DB |
| Hardcoded `localhost:8000` in context files | Quick to write | Breaks in any non-local environment; duplicates base URL in multiple files | Never — use the existing `api.js` constant |
| `iterrows()` for decade filter | Familiar Python loop | 2-10x slower than vectorized pandas; will visibly lag with 5000+ movies | Never — extract `release_year` as a column instead |
| No `URL.revokeObjectURL()` after CSV/JSON export | Saves one line of code | Memory leak per export click; accumulates across session | Never — always revoke after the download is triggered |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Tailwind dark mode + existing CSS | Adding `darkMode: 'class'` without auditing existing hardcoded hex colors in `index.css` | Replace hardcoded background gradients with Tailwind `dark:` variants before enabling the toggle |
| SQLAlchemy + new column | Editing `models_db.py` and expecting `create_all()` to add the column to an existing table | Use Alembic migration or an idempotent `ALTER TABLE` check on startup |
| WatchlistContext + new auth-gated features | Copying the direct `axios` + `authAPI.getAccessToken()` pattern from `WatchlistContext.jsx` | Route all new calls through `api.js` which centralizes the base URL |
| Pandas DataFrame + genre/decade filter | Using `.str.contains()` or `iterrows()` for multi-value genre filter | Use `.apply(lambda row: any(g in row['genres'] for g in selected))` with `.isin()` on pre-extracted year column |
| localStorage + JSON data | Using `JSON.parse(localStorage.getItem(key))` without null-check or try-catch | Wrap in a shared `useLocalStorage` hook with try-catch and default value fallback |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| `iterrows()` in mood/decade filter | Decade filter takes 2-5 seconds with 5000 movies | Vectorized pandas: extract `release_year`, use boolean mask | Immediately at current dataset size |
| MovieCard fetching poster on every render | Grid of 20 movies fires 20 sequential poster requests, UI feels slow | Already has `useEffect` with `movie.movie_id` dep — acceptable; but Recently Viewed (20 cards) will make this worse | When Recently Viewed section renders 20 cards on home page load |
| WatchlistContext `clearWatchlist` n+1 deletes | Clearing 50 watchlist items fires 50 sequential DELETE requests | Batch delete endpoint or `Promise.all()` (parallel) | When watchlist exceeds ~20 items |
| No debounce on Quick Rating hover | 5 API calls fired when hovering across stars | Save rating only on click, not on hover state change | Immediately on first use |
| Full watchlist reload after every add/remove | Each watchlist mutation triggers GET all items; grows with watchlist size | Optimistic local state update + sync in background | When watchlist exceeds ~100 items |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| No bounds validation on Quick Rating `rating` field | User can POST `rating=999.9` or `rating=-1`; corrupts stats calculations | Add `Field(ge=1, le=5, description="User rating 1-5 stars")` to `MovieRatingCreate` Pydantic model |
| Export watchlist CSV/JSON includes raw DB fields | Exposes internal `id`, `user_id`, `added_at` columns the user doesn't need | Serialize only `movie_title`, `genres`, `watch_status`, `vote_average`, `runtime` in the export |
| Watch Status values not validated as enum | Free-text status field could accept `"hacked"` or very long strings | Use Python `enum.Enum` with `Literal["watching", "completed", "plan_to_watch"]` in the Pydantic schema |
| localStorage data treated as trusted on hydration | Search history and recently viewed items from localStorage rendered without sanitization | Always treat localStorage strings as untrusted; `movie.title` from history should be escaped before DOM insertion (React handles this by default, but `dangerouslySetInnerHTML` must never be used here) |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Hover-only stars on mobile (Feature 10) | Touch users cannot rate movies — hover never fires on touch devices | Add `onClick` as the primary interaction; hover is visual preview only |
| Recently Viewed capped at 20 with no visual indicator | User doesn't know which older movies have been dropped from the list | Show "Last 20 movies" label; newest-first ordering (push to front, pop from end) |
| Search History shows raw queries including typos | Clutters history with accidental searches like `"titainc"` | Save to history only on results returned (not on every Enter press), or deduplicate by exact match |
| Theme toggle with no transition | Dark → light mode snaps abruptly, feels broken | Add `transition-colors duration-300` to `body` or root element |
| Genre filter chips with no "clear all" | User selects 5 genres, can't quickly reset without un-selecting each | Add a "Clear filters" button that appears when any chip is selected |
| Runtime formatted before data exists | `"0h 0m"` shown when runtime is null instead of hiding the field | Guard: `{movie.runtime && <p>{formatRuntime(movie.runtime)}</p>}` — `MovieCard.jsx` already does this at line 119 but the new utility must handle `null`/`undefined` explicitly |

---

## "Looks Done But Isn't" Checklist

- [ ] **Dark Mode Toggle:** Theme class applied to `<html>`, not just a component wrapper — verify: open DevTools, check `<html class="dark">` is present, not `<div class="dark">`.
- [ ] **Dark Mode Toggle:** No FOUC on hard refresh — verify: open incognito, set dark mode, press Ctrl+Shift+R. Watch for white flash.
- [ ] **Watch Status:** Status persists after page refresh — verify: set a movie to "Watching", refresh, confirm it shows "Watching" not the default.
- [ ] **Watch Status:** Status filter UI actually filters the list (not just a display label) — verify: add 3 movies with different statuses, select "Completed" filter, only completed movies visible.
- [ ] **Loading Spinner:** Import uncommented in `Recommendations.jsx` (line 4) — verify: search for a movie, spinner appears during fetch.
- [ ] **Loading Spinner:** Spinner is accessible — verify: spinner has `role="status"` and `aria-label="Loading"` for screen readers.
- [ ] **Search History:** History persists across page reload — verify: search "Inception", refresh page, "Inception" appears in history list.
- [ ] **Search History:** History is cleared properly — verify: clicking "Clear" removes all entries from both UI and `localStorage`.
- [ ] **Recently Viewed:** List updates when a movie is clicked (not when it's just visible) — verify: click a movie card, navigate back, movie appears at top of Recently Viewed.
- [ ] **Recently Viewed:** 20-item cap enforced — verify: view 21+ movies, confirm only 20 in localStorage.
- [ ] **Genre Filter:** Multi-select (not single-select) — verify: selecting "Action" then "Drama" shows movies with either genre, not just the last-clicked.
- [ ] **Export CSV:** CSV opens correctly in Excel/Sheets — verify: export, open in spreadsheet app, check column headers match data.
- [ ] **Export CSV:** `URL.revokeObjectURL()` called after download — verify: export 3 times in a row, check DevTools Memory tab for blob: URL accumulation.
- [ ] **Decade Filter:** Boundary years correct (1980s = 1980-1989 inclusive) — verify: "1980s" filter includes `1989` but not `1990`.
- [ ] **Quick Rating:** Rating saves on click, not hover — verify: hover over stars without clicking; no network request fires.
- [ ] **Quick Rating:** Rating widget is accessible on mobile — verify: on a touch device, tap a star, confirm rating saves.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| FOUC on dark mode | LOW | Add blocking `<script>` to `index.html` head; no data loss |
| Watch Status column missing from existing DB | MEDIUM | Run manual `ALTER TABLE` SQL on SQLite file; or configure Alembic, generate migration, run `alembic upgrade head` |
| `LoadingSpinner` crash | LOW | Create the component file; uncomment the import in `Recommendations.jsx` — 15 minutes max |
| localStorage corruption / quota exceeded | LOW | Clear localStorage for the domain; re-implement with try-catch hook going forward |
| Rating scale inconsistency in DB | HIGH | Write a migration to normalize all existing ratings to the new scale; requires knowing which ratings were entered at which scale — nearly impossible retroactively |
| Genre format inconsistency | MEDIUM | One-time data migration: read all `WatchlistItem` rows, parse `genres` string, re-save consistently; or accept dual-format and add parsing to both code paths |
| Memory leak from un-revoked Blob URLs | LOW | Revoke immediately after triggering download; already-leaked URLs cleared on tab close |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Dark mode FOUC | Feature 1 (Theme Toggle) | Hard refresh in incognito after setting dark mode — zero flash |
| Watch Status schema migration | Feature 2 (Watch Status) | Restart app with existing DB — status column present, data intact |
| LoadingSpinner import broken | Feature 4 (Loading Spinner) | Navigate to `/recommendations`, search a movie — spinner appears, no console error |
| Genres stored as string vs list | Feature 7 (Genre Filter) | Genre filter returns correct movies from ML data; watchlist genres display correctly |
| Decade filter needs `release_year` column | Feature 9 (Decade Filter) | Filter endpoint responds in under 500ms; correct boundary movies included |
| Quick Rating fires on hover | Feature 10 (Quick Rating) | Hover across 5 stars — zero network requests; click one star — exactly one POST request |
| Rating scale conflict | Feature 10 (Quick Rating) | `POST /api/user/ratings` with `rating=6` returns 422 Validation Error |
| Hardcoded localhost URLs | All features | `grep -r "localhost:8000" frontend/src` returns only legacy context files, not new feature files |
| localStorage error handling | Feature 3 (Search History) | Fill localStorage to quota, attempt to save search — app degrades gracefully, no crash |
| Blob URL memory leak | Feature 8 (Export Watchlist) | Export 10 times; DevTools Memory shows no accumulated blob: URLs |

---

## Sources

- Tailwind CSS dark mode documentation: [https://tailwindcss.com/docs/dark-mode](https://tailwindcss.com/docs/dark-mode)
- FOUC prevention (blocking script in head): [https://cruip.com/implementing-tailwind-css-dark-mode-toggle-with-no-flicker/](https://cruip.com/implementing-tailwind-css-dark-mode-toggle-with-no-flicker/)
- SQLite ALTER TABLE limitations (Alembic batch mode): [https://alembic.sqlalchemy.org/en/latest/batch.html](https://alembic.sqlalchemy.org/en/latest/batch.html)
- FastAPI + sync SQLAlchemy deadlock: [https://github.com/fastapi/fastapi/discussions/6628](https://github.com/fastapi/fastapi/discussions/6628)
- React localStorage hydration pitfalls: [https://github.com/astoilkov/use-local-storage-state](https://github.com/astoilkov/use-local-storage-state)
- Blob URL memory leak prevention: [https://jsdev.space/howto/blob-file-handling-guide/](https://jsdev.space/howto/blob-file-handling-guide/)
- React context re-render and localStorage pitfalls: [https://www.tenxdeveloper.com/blog/optimizing-react-context-performance](https://www.tenxdeveloper.com/blog/optimizing-react-context-performance)
- Star rating accessibility and mobile touch: [https://github.com/smastrom/react-rating](https://github.com/smastrom/react-rating)
- Codebase direct inspection: `backend/app/models_db.py`, `backend/app/api/user_routes.py`, `backend/app/ml/recommender.py`, `frontend/src/context/WatchlistContext.jsx`, `frontend/src/pages/Recommendations.jsx`, `frontend/tailwind.config.js`, `frontend/src/index.css`
- Known concerns: `.planning/codebase/CONCERNS.md` (2026-02-21 audit)

---
*Pitfalls research for: React + FastAPI Movie Recommender feature expansion (Features 1-10)*
*Researched: 2026-02-21*
