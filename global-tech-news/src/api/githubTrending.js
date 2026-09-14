// GitHub doesn't expose an official Trending API, and the usual community
// JSON mirrors (huchenme/github-trending-api and friends) were unreachable
// at build time. This adapter substitutes the official Search API, scoped
// to recently-created repositories sorted by stars, which is stable,
// CORS-enabled, and needs no auth for light use. Swappable for a real
// trending mirror later without touching any other file.
const SEARCH_ENDPOINT = "https://api.github.com/search/repositories"
const LOOKBACK_DAYS = 7
const REPO_LIMIT = 25

function daysSince(dateString) {
  const days = (Date.now() - new Date(dateString).getTime()) / (1000 * 60 * 60 * 24)
  return Math.max(1, Math.round(days))
}

export async function fetchTrendingRepositories(limit = REPO_LIMIT) {
  const since = new Date(Date.now() - LOOKBACK_DAYS * 24 * 60 * 60 * 1000)
    .toISOString()
    .split("T")[0]

  const query = `created:>${since}`
  const url = `${SEARCH_ENDPOINT}?q=${encodeURIComponent(query)}&sort=stars&order=desc&per_page=${limit}`

  const response = await fetch(url, {
    headers: { Accept: "application/vnd.github+json" },
  })
  if (!response.ok) {
    throw new Error(`GitHub trending request failed: ${response.status}`)
  }

  const data = await response.json()

  return data.items.map((repo) => ({
    id: repo.id,
    name: repo.name,
    fullName: repo.full_name,
    url: repo.html_url,
    description: repo.description ?? "",
    language: repo.language ?? "Unknown",
    stars: repo.stargazers_count,
    // GitHub's search API has no daily star-delta field, so this is an
    // average-per-day-since-creation proxy for "growth today", not a
    // true 24h snapshot like the real Trending page provides.
    starsToday: Math.round(repo.stargazers_count / daysSince(repo.created_at)),
  }))
}
