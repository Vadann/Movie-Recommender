# Feature Research

**Domain:** Personal movie discovery and tracking app (React + FastAPI)
**Researched:** 2026-02-21
**Confidence:** HIGH — based on direct codebase inspection and established UX patterns for this feature category

---

## Context: What the App Already Has

Before assessing new features, the baseline state matters for every implementation decision.

The app is **entirely dark-mode**, hardcoded. Every component uses `bg-gray-800`, `bg-gray-900`, `text-white`, `text-gray-400`. The Tailwind config has no `darkMode` key. The body has a fixed dark gradient (`linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)`) baked into `index.css`. There is no `dark:` prefix anywhere in the codebase.

The `WatchlistItem` model has: `id`, `user_id`, `movie_id`, `movie_title`, `genres` (comma-separated string), `vote_average`, `runtime`, `added_at`. No status column exists.

`LoadingSpinner` is imported in `Home.jsx` and `Recommendations.jsx` (line 128, 171) but the component file does not exist — this is a live runtime crash.

The `MovieCard` already has an inline runtime formatter: `{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m` — but it renders raw without the utility function being shared.

---

## Feature Landscape

### Table Stakes (Users Expect These / Missing = Feels Broken)

| Feature | Why Expected | Complexity | Implementation Scope |
|---------|--------------|------------|----------------------|
| Loading Spinner Component (F4) | App crashes at runtime — `LoadingSpinner` imported but file doesn't exist. This is an active bug, not a polish item. | LOW | Frontend-only. New `components/LoadingSpinner.jsx`. No backend. No DB. |
| Movie Runtime Formatter Utility (F5) | Runtime already renders in `MovieCard` and `Watchlist.jsx` as inline math. Inconsistency across components is a bug waiting to happen. | LOW | Frontend-only. New `utils/formatRuntime.js`. Replace 2 existing inline occurrences. No backend. No DB. |
| Movie Watch Status — Watching/Completed/Plan to Watch (F2) | Any watchlist UI without status tracking feels like a to-do list with no checkboxes. Users add movies intending to track progress; without status, the watchlist is write-only. | MEDIUM | Backend + DB migration required. Add `status` column (String, default `"Plan to Watch"`) to `WatchlistItem`. New PATCH endpoint `/user/watchlist/{movie_id}/status`. Frontend: status badge on card + filter UI in Watchlist page. |
| Quick Rating Widget on Card (F10) | Rating exists in the DB (`MovieRating` model, `/user/ratings` endpoints) but requires navigating to a separate flow. Inline star rating on a movie card is the expected interaction pattern for any rating feature. | MEDIUM | Frontend-heavy. New hover star widget in `MovieCard`. Reuses existing POST/PUT `/user/ratings` endpoint. No DB change. Requires auth-awareness (unauthenticated users see no widget). |

### Differentiators (Competitive Advantage / Polish That Builds Habit)

| Feature | Value Proposition | Complexity | Implementation Scope |
|---------|-------------------|------------|----------------------|
| Dark/Light Theme Toggle (F1) | A personal tool used at different times of day benefits from theme choice. Most personal apps have this today. | MEDIUM | Frontend-only + significant refactor cost. The entire app uses hardcoded dark classes. Enabling Tailwind `darkMode: 'class'` and adding `dark:` prefixes to every component is the correct approach. Theme stored in `localStorage`. Toggle button in navbar. **No backend. No DB. High refactor surface area.** |
| Search History — Last 10 Searches (F3) | Reduces friction for repeated searches. Users often search the same title to find new recommendations. | LOW | Frontend-only. `localStorage` key `search_history`. Dropdown below search bar in `Recommendations.jsx`. Clear button. No backend. No DB. |
| Recently Viewed Movies — Last 20 (F6) | Closing the browser loses context. "Where was I?" is a real friction point. Horizontal scroll section on Home page. | LOW | Frontend-only. `localStorage` key `recently_viewed`. Track on every `MovieCard` click/view. Home page section renders last 20. No backend. No DB. |
| Movie Genres Filter — Multi-Select Chips (F7) | The existing genre stats endpoint (`/statistics/genres`) already returns genre data. Adding filter chips makes the home page grid actually useful for discovery rather than just browsing. | MEDIUM | Frontend + backend. Backend: add `GET /movies/?genres=Action,Drama` query param filtering to the popular movies or a new filtered endpoint. Frontend: fetch genres from `/statistics/genres`, render multi-select chip UI, filter movie grid. |
| Movie Decade Filter — 1970s, 1980s, etc. (F9) | Decade browsing is a natural mental model for movie discovery. "What are the best 80s films?" is a common intent. | MEDIUM | Backend + frontend. Backend: add `decade` query param to movies endpoint (filter by `release_year`). Frontend: dropdown or chip UI, state update triggers re-fetch. No DB migration needed — `release_year` data exists in CSV/DataFrame. |
| Export Watchlist as CSV/JSON (F8) | Power-user feature. Personal data portability. Builds trust and habit. Low effort relative to value. | LOW | Frontend-only. Client-side `Blob` + `URL.createObjectURL` download. Two buttons on Watchlist page. Formats data from existing `watchlist` state. No backend. No DB. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Sync search history to backend | "My search history should persist across devices" | Single-user personal tool. Adding a backend table + migration + API endpoint for what is effectively ephemeral UI state is disproportionate complexity. localStorage is sufficient. | Keep in localStorage. If multi-device sync becomes needed in v2, add it then. |
| Real-time genre filter without re-fetch | Filtering entirely client-side against the 20-movie home page grid | The home page only loads 20 popular movies. Filtering 20 items client-side gives a false sense of filtering — user picks "Horror" and gets 0 results because none of the 20 are Horror. | Genre filter must trigger a backend query against the full dataset. Client-side filtering is an anti-pattern here. |
| Infinite scroll on Recently Viewed | "Show all history" | Adds complexity, pagination state, and removes the clarity of "last 20". The feature's value is quick recall, not a full history log. | Hard cap at 20. If user wants full history, that's a separate "Watch History" page feature — out of scope for this milestone. |
| Theme toggle that affects ParticlesBackground | The particle animation uses hardcoded dark colors in `ParticlesBackground.jsx` | Requires passing theme props into the particle system or using CSS variables — significant complexity for marginal UX benefit. | In light mode, simply hide or reduce opacity of the particles. Do not attempt to recolor them dynamically. |
| Auto-save rating on hover (no confirmation) | "Instant feedback" | Mouse hover is not intent. A user hovering through stars to select one will fire multiple save calls. This creates noise in ratings data and wastes API calls. | Save only on click. Show hover preview visually (filled stars on hover) but persist only on confirmed click. |

---

## Feature Dependencies

```
[F4: LoadingSpinner Component]
    └──blocks──> [F1: Dark/Light Theme] (theme must work with spinner)
    └──blocks──> Any page that currently crashes (Home.jsx, Recommendations.jsx)

[F5: Runtime Formatter Utility]
    └──enhances──> [F6: Recently Viewed] (recently viewed cards show runtime)
    └──enhances──> [F10: Quick Rating Widget] (if card shows runtime alongside rating)

[F2: Watch Status]
    └──requires──> DB migration (add status column to watchlist_items)
    └──enhances──> [F8: Export Watchlist] (export should include status field)

[F7: Genre Filter]
    └──requires──> Backend endpoint change (genres query param)
    └──enhances──> [F9: Decade Filter] (both are filters, can share filter state/UI)

[F9: Decade Filter]
    └──requires──> Backend endpoint change (decade query param)
    └──can share UI with──> [F7: Genre Filter]

[F10: Quick Rating Widget]
    └──requires──> User authentication (hide widget if not logged in)
    └──reuses──> Existing POST /user/ratings endpoint (no backend change)

[F3: Search History]
    └──standalone (no dependencies)

[F6: Recently Viewed]
    └──standalone (no dependencies)

[F8: Export Watchlist]
    └──depends on──> [F2: Watch Status] for complete export data
    └──note──> Can be built before F2; just won't include status field until F2 lands
```

### Dependency Notes

- **F4 (LoadingSpinner) is a blocker**: App crashes in `Home.jsx` and `Recommendations.jsx` at runtime. Must be first. This is not optional polish.
- **F2 (Watch Status) requires a DB migration**: Adding a `status` column to `watchlist_items`. Must use `ALTER TABLE` or Alembic migration script. SQLite does support `ALTER TABLE ADD COLUMN` with a default value. The existing `create_all()` pattern in `database.py` will NOT auto-add the column to an existing database — migration is required.
- **F7 and F9 (Genre + Decade Filters) share backend surface**: Both need query param filtering on the movies endpoint. Build together in one backend pass to avoid touching the route twice.
- **F1 (Dark/Light Theme) has the highest hidden cost**: All 12 component/page files use hardcoded dark classes. Enabling Tailwind `darkMode: 'class'` and adding `dark:` variants requires touching every file. Budget accordingly.
- **F10 (Quick Rating Widget) reuses existing infrastructure**: The `MovieRating` model and `/user/ratings` endpoints are already complete. This is a purely frontend feature.

---

## MVP Definition (For This Milestone — All 10 Features Are In Scope)

### Build First (Blockers and Foundations)

- [x] **F4: Loading Spinner Component** — Active runtime crash. Zero other features should ship without this fixed.
- [x] **F5: Runtime Formatter Utility** — Establishes the shared utility pattern before F6 and F10 use runtime display.

### Build Second (Backend-Required Features Together)

- [x] **F2: Movie Watch Status** — Needs DB migration. Do this in one pass with the migration script before other DB work.
- [x] **F7: Movie Genres Filter** — Backend endpoint change. Pair with F9.
- [x] **F9: Movie Decade Filter** — Backend endpoint change. Pair with F7.

### Build Third (Frontend-Only, No Dependencies)

- [x] **F3: Search History** — Purely localStorage. No blockers.
- [x] **F6: Recently Viewed Movies** — Purely localStorage. No blockers.
- [x] **F8: Export Watchlist as CSV/JSON** — Client-side only. Richer if F2 is done first (includes status).
- [x] **F10: Quick Rating Widget** — Frontend-only, reuses existing API. Auth-aware.

### Build Last (Highest Refactor Surface)

- [x] **F1: Dark/Light Theme Toggle** — Touches every file. Build last to avoid cascading conflicts with new components added in earlier features. New components built in steps above should be written dark-mode-compatible from the start.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Scope |
|---------|------------|---------------------|----------|-------|
| F4: Loading Spinner | HIGH (bug fix) | LOW | P1 | Frontend-only |
| F5: Runtime Formatter | MEDIUM (consistency) | LOW | P1 | Frontend-only |
| F2: Watch Status | HIGH | MEDIUM | P1 | Backend + DB migration |
| F10: Quick Rating Widget | HIGH | MEDIUM | P1 | Frontend-only (reuses existing API) |
| F3: Search History | MEDIUM | LOW | P2 | Frontend-only |
| F6: Recently Viewed | MEDIUM | LOW | P2 | Frontend-only |
| F8: Export Watchlist | MEDIUM | LOW | P2 | Frontend-only |
| F7: Genre Filter | HIGH | MEDIUM | P2 | Backend + Frontend |
| F9: Decade Filter | MEDIUM | MEDIUM | P2 | Backend + Frontend |
| F1: Dark/Light Theme | MEDIUM | HIGH | P3 | Frontend-only (high refactor) |

**Priority key:**
- P1: Must have — either fixes bugs or delivers core tracking value
- P2: Should have — meaningful UX improvement, manageable cost
- P3: Nice to have — polish feature with high implementation surface

---

## UX Behavior Specifications (Per Feature)

### F1: Dark/Light Theme Toggle

**Table stake or differentiator:** Differentiator — the app is currently dark-only, which is fine for many users.

**Expected UX:**
- Toggle button in navbar (sun/moon icon from lucide-react — both are in the library)
- Clicking toggles a `dark` class on the `<html>` or `<body>` element
- Preference saved to `localStorage` key `theme`
- On load, read `localStorage.theme` — if absent, default to `dark` (existing behavior preserved)
- Smooth transition: `transition-colors duration-300` on body
- All hardcoded `bg-gray-800`, `bg-gray-900` must become `bg-white dark:bg-gray-900` etc.

**Must have (table stakes for this feature):**
- Persistence across page reload
- No flash of wrong theme on load (read localStorage before first paint — set class in `index.html` `<script>` before React hydrates)
- Navbar toggle button is visible in both modes

**Nice to have (differentiator within the feature):**
- System preference detection via `prefers-color-scheme` media query as fallback when no localStorage value
- Smooth color transition animation

**Implementation note:** Tailwind config needs `darkMode: 'class'`. The `ParticlesBackground` component uses hardcoded dark colors — either hide it in light mode or accept it as a known limitation.

---

### F2: Movie Watch Status

**Table stake or differentiator:** Table stake for any watchlist feature.

**Expected UX:**
- Status displayed as a colored badge on the watchlist card: "Plan to Watch" (gray), "Watching" (blue), "Completed" (green)
- Status is changeable via a dropdown or segmented button on the Watchlist page card
- Filter bar above watchlist grid: "All | Watching | Completed | Plan to Watch"
- Default status when adding to watchlist: "Plan to Watch"
- Status change saves immediately (optimistic UI update, then backend confirmation)

**Must have:**
- DB column `status` with default `"Plan to Watch"` on `WatchlistItem`
- PATCH `/user/watchlist/{movie_id}/status` endpoint
- Status visible on watchlist page
- Filter by status on watchlist page

**Nice to have:**
- Status badge on MovieCard when movie is in watchlist (not just on Watchlist page)
- Count badges on filter tabs ("Watching (3)")

**Implementation note:** SQLite supports `ALTER TABLE watchlist_items ADD COLUMN status VARCHAR DEFAULT 'Plan to Watch'`. The existing `create_all()` does NOT run ALTER statements on existing tables — migration script is mandatory. The `WatchlistItemResponse` Pydantic model must include `status`.

---

### F3: Search History

**Table stake or differentiator:** Differentiator — reduces friction for power use.

**Expected UX:**
- Dropdown appears below search bar when user focuses on the search input AND there is history
- Shows last 10 unique searches, most recent first
- Each item: search query text + "run again" behavior on click
- X button on each item to remove it individually
- "Clear all" at the bottom of the dropdown
- History updates on every successful search (after results return, not on keypress)
- Dropdown closes when user clicks outside or presses Escape

**Must have:**
- localStorage persistence of last 10 searches
- Click to re-run search
- Clear individual or all

**Nice to have:**
- Search timestamp displayed ("2 hours ago")
- Keyboard navigation through dropdown items (arrow keys)

**Implementation note:** localStorage key `movie_search_history`, value is JSON array of strings. Deduplicate on save (remove existing entry before prepending, cap at 10).

---

### F4: Loading Spinner Component

**Table stake or differentiator:** Table stake — this is a bug fix. The component is imported but does not exist, causing a runtime crash.

**Expected UX:**
- Centered spinner with optional message below it
- Matches existing `.loader` CSS class already defined in `index.css` (red spinning circle)
- Used via `<LoadingSpinner message="Loading popular movies..." />`
- Accessible: `role="status"` and `aria-label` on the container

**Must have:**
- Component file at `frontend/src/components/LoadingSpinner.jsx`
- Accepts optional `message` prop
- Uses existing `.loader` CSS class (do not create a new spinner style)
- `role="status"` for accessibility

**Nice to have:**
- `aria-live="polite"` on message text

**Implementation note:** `Home.jsx` imports from `../components/LoadingSpinner` and `Recommendations.jsx` has it commented out (`//import LoadingSpinner from '../components/LoadingSpinner'`). The uncommented import in `Home.jsx` is the active crash. `Recommendations.jsx` uses `<LoadingSpinner />` JSX on lines 128 and 171 despite the commented import — this means `Recommendations.jsx` also crashes when it hits those render paths.

---

### F5: Movie Runtime Formatter

**Table stake or differentiator:** Table stake — consistency fix. Runtime formatting already exists inline in two places but will diverge over time.

**Expected UX:**
- Input: integer minutes (e.g., `135`)
- Output: `"2h 15m"`
- Edge cases: `0` → `"0m"`, `60` → `"1h 0m"`, `null/undefined` → `""` or `null` (caller handles display)

**Must have:**
- Utility function `formatRuntime(minutes)` in `frontend/src/utils/formatRuntime.js`
- Replace inline `{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m` in `MovieCard.jsx` (line 122)
- Replace inline `${Math.floor(stats.total_runtime / 60)}h ${stats.total_runtime % 60}m` in `Watchlist.jsx` (line 117)

**Nice to have:**
- Handle `0` minutes gracefully: show `"0m"` not `"0h 0m"`
- TypeScript-style JSDoc comment for editor hints

**Implementation note:** This is a pure utility extraction. Two files to update. No backend. No DB.

---

### F6: Recently Viewed Movies

**Table stake or differentiator:** Differentiator — valuable habit-building feature.

**Expected UX:**
- Horizontal scroll row labeled "Recently Viewed" on the Home page, above or below "Popular Movies"
- Shows last 20 movies the user has interacted with (clicked into, added to watchlist, or rated)
- Each item is a compact `MovieCard` (smaller than the main grid)
- Appears only when there is at least 1 recently viewed movie
- On first visit with no history, the section is hidden entirely
- Scrollable horizontally on desktop and mobile

**Must have:**
- localStorage key `recently_viewed`, JSON array of movie objects (capped at 20)
- Track on MovieCard interaction (watchlist toggle or a dedicated click handler)
- Horizontal scroll container with `overflow-x-auto` on Home page
- Section hidden when array is empty

**Nice to have:**
- "Clear history" button on the section header
- Visual differentiation from main grid (smaller cards, condensed view)

**Implementation note:** The trigger for "viewed" should be watchlist toggle (already exists) OR a new `onClick` wrapper on MovieCard. Storing full movie objects (not just IDs) avoids a re-fetch. Object shape: `{movie_id, title, genres, vote_average, poster_path, runtime}`. Cap storage at 20 by slicing array before saving.

---

### F7: Movie Genres Filter

**Table stake or differentiator:** Differentiator — turns a static list into a discovery tool.

**Expected UX:**
- Multi-select genre chips displayed above the movie grid on the Home page (or Recommendations page)
- Genre list fetched from existing `/statistics/genres` endpoint on page load
- Chips are toggleable: click to select/deselect, selected chip has distinct active style (red background)
- Multiple genres selected = OR logic (show movies matching any selected genre)
- Selecting genres triggers a new backend query, not client-side filtering of the existing 20 results
- "Clear filters" button appears when any genre is selected
- Loading spinner shows while filtered results load

**Must have:**
- Chip UI with active/inactive states
- OR filtering semantics
- Backend endpoint that accepts `genres` query param: `GET /api/movies/popular?genres=Action,Drama`
- Clear filters action

**Nice to have:**
- Genre chip count badge showing number of movies in that genre
- Animation when chips toggle (scale or color transition)

**Implementation note:** The existing `GET /statistics/genres` returns genre stats with counts. The popular movies endpoint needs a new `genres: Optional[List[str]]` query param that filters the recommender's DataFrame before returning results. Client-side filtering of 20 movies is explicitly an anti-pattern here (see Anti-Features).

---

### F8: Export Watchlist as CSV/JSON

**Table stake or differentiator:** Differentiator — personal data portability.

**Expected UX:**
- Two buttons on the Watchlist page header: "Export CSV" and "Export JSON"
- Clicking triggers immediate browser file download
- Filename: `watchlist-YYYY-MM-DD.csv` / `watchlist-YYYY-MM-DD.json`
- CSV columns: `title, genres, vote_average, runtime, added_at, status` (status if F2 is complete)
- JSON: array of objects with same fields
- Buttons are disabled (grayed out) when watchlist is empty
- No loading state needed — client-side only

**Must have:**
- Client-side `Blob` + `URL.createObjectURL` + `<a download>` pattern
- Both CSV and JSON formats
- Filename includes current date

**Nice to have:**
- Include the `status` field if F2 is complete
- Genres as a proper comma-separated field in CSV (escaped correctly for CSV format)

**Implementation note:** The watchlist data is already available in `WatchlistContext`. No API call needed. Use `JSON.stringify` for JSON. For CSV: build header row + data rows manually or use a minimal CSV utility. Watch for commas within genre strings — wrap genre field in quotes.

---

### F9: Movie Decade Filter

**Table stake or differentiator:** Differentiator — natural browsing mental model.

**Expected UX:**
- Dropdown or horizontal chip row with decade options: "All", "Pre-1970s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"
- Selecting a decade filters the movie grid
- Only one decade active at a time (single-select, unlike genres which are multi-select)
- "All" clears the decade filter
- Works in combination with genre filter (F7) if both are active

**Must have:**
- Single-select decade UI (dropdown is simpler; chips are more consistent with F7)
- Backend `decade` query param: `GET /api/movies/popular?decade=1980s`
- Backend filters DataFrame by `release_year` range

**Nice to have:**
- Combined filter state with F7 genre filter (single backend call with both params)
- "Pre-1970s" bucket for older classics

**Implementation note:** The movie DataFrame has a `release_year` or `release_date` column from the CSV. Backend decade mapping: `1980s` → `year >= 1980 AND year < 1990`. Build this alongside F7 to make one combined filter endpoint: `GET /api/movies/popular?genres=Action&decade=1980s&limit=20`.

---

### F10: Quick Rating Widget

**Table stake or differentiator:** Table stake for any app with ratings — the current path to rating is too friction-heavy.

**Expected UX:**
- Stars appear on hover over the MovieCard poster (overlay, like the existing watchlist button)
- 5 stars (mapping to 1-10 backend scale: star 1 = 2, star 2 = 4, ... star 5 = 10)
- Stars fill on hover to show preview of what rating will be saved
- Click on a star saves the rating immediately via API call
- After save: brief success indicator (star turns yellow/gold, or checkmark flash)
- If movie already rated: stars show existing rating by default (filled to current rating)
- Only visible to authenticated users — unauthenticated users see no widget

**Must have:**
- Hover-reveal star widget on MovieCard poster overlay
- Click to save via existing `POST /user/ratings` endpoint
- Show existing rating if already rated
- Auth-aware: hide for unauthenticated users

**Nice to have:**
- Loading indicator on the star during save
- Option to clear rating (click active star = unset)
- Tooltip showing numeric value on hover ("8/10")

**Implementation note:** Reuses existing `MovieRating` model and `POST /user/ratings` endpoint exactly as-is. The endpoint handles both create and update (checks for existing rating, updates if found). The `MovieCard` already imports `useWatchlist` — add `useAuth` to check authentication. The `WatchlistContext` already tracks ratings state — check if a similar pattern exists or if the widget needs local state. The 5-star to 1-10 conversion: `star_count * 2`.

---

## Complexity Summary Table

| # | Feature | Scope | DB Change | Backend Change | Frontend Files Touched |
|---|---------|-------|-----------|----------------|------------------------|
| F4 | Loading Spinner | Frontend-only | No | No | 1 new file (`LoadingSpinner.jsx`), uncomment in `Recommendations.jsx` |
| F5 | Runtime Formatter | Frontend-only | No | No | 1 new file (`utils/formatRuntime.js`), 2 edits |
| F8 | Export Watchlist | Frontend-only | No | No | 1 file (`Watchlist.jsx`) |
| F3 | Search History | Frontend-only | No | No | 1 file (`Recommendations.jsx`) |
| F6 | Recently Viewed | Frontend-only | No | No | `Home.jsx`, `MovieCard.jsx` |
| F10 | Quick Rating Widget | Frontend-only | No | No | `MovieCard.jsx` (uses existing endpoints) |
| F1 | Dark/Light Theme | Frontend-only | No | No | All 12+ component/page files + Tailwind config |
| F2 | Watch Status | Backend + DB | Yes — ALTER TABLE | New PATCH endpoint | `Watchlist.jsx`, `MovieCard.jsx` |
| F7 | Genre Filter | Backend + Frontend | No | Add query param to movies endpoint | `Home.jsx` (new chip UI) |
| F9 | Decade Filter | Backend + Frontend | No | Add query param to movies endpoint | `Home.jsx` (or shared filter UI) |

---

## Sources

- Direct codebase inspection: `frontend/src/components/MovieCard.jsx`, `frontend/src/pages/Home.jsx`, `frontend/src/pages/Watchlist.jsx`, `frontend/src/pages/Recommendations.jsx`, `frontend/src/App.jsx`, `frontend/src/index.css`, `frontend/tailwind.config.js`
- Backend inspection: `backend/app/models_db.py`, `backend/app/api/user_routes.py`, `backend/app/api/routes.py`, `backend/app/ml/recommender.py`
- Architecture context: `.planning/codebase/ARCHITECTURE.md`
- Project requirements: `.planning/PROJECT.md`
- UX patterns: Standard interaction patterns for movie/media tracking apps (Letterboxd, Trakt, IMDb) — MEDIUM confidence (training data, consistent with what was observed in codebase patterns)
- Tailwind dark mode: official Tailwind CSS documentation pattern (`darkMode: 'class'`) — HIGH confidence

---
*Feature research for: Movie Recommender — milestone v1 (10 features)*
*Researched: 2026-02-21*
