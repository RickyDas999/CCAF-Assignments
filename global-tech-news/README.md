# Global Tech News

A frontend-only dashboard that aggregates technology news and trending GitHub
repositories into a single searchable, filterable interface. No backend, no
database, no authentication — data is pulled client-side from public feeds
and APIs, with bookmarks and theme preference stored in `localStorage`.

## Features

- Trending news aggregated from Hacker News, TechCrunch, Ars Technica, and
  The Verge, deduplicated and sorted newest-first
- Keyword-based category filtering (AI, Programming, Startups, Cybersecurity,
  Cloud, Mobile, Web Dev), instant and client-side
- Global search across news (title/description/source/category) and GitHub
  repositories (name/description/language)
- GitHub trending repositories
- Persistent bookmarks and dark/light theme, stored in `localStorage`
- Infinite scroll via `IntersectionObserver`
- Skeleton loading states and graceful per-source failure handling — one
  feed going down never blocks the rest of the dashboard
- Responsive from 390px mobile up through desktop

## Data sources

| Source | Method |
| --- | --- |
| Hacker News | Official [Firebase API](https://github.com/HackerNews/API) |
| TechCrunch / Ars Technica / The Verge | RSS feeds converted to JSON via [rss2json.com](https://rss2json.com) |
| GitHub Trending | GitHub's official [Search API](https://docs.github.com/en/rest/search), scoped to recently-created repos sorted by stars, since no public GitHub Trending JSON mirror was reachable at build time. `starsToday` is an average-per-day-since-creation estimate, not a true 24h snapshot. See `src/api/githubTrending.js`. |

Each source adapter lives in `src/api/` and is isolated behind a normalized
article/repository shape (`src/utils/normalizeArticle.js`), so components
never know which source data came from, and any adapter can be swapped
without touching the UI.

## Stack

React, Tailwind CSS, Fetch API, localStorage.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Lint

```bash
npm run lint
```
