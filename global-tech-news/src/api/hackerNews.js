import { normalizeArticle } from "../utils/normalizeArticle"

const HN_BASE = "https://hacker-news.firebaseio.com/v0"
const STORY_LIMIT = 30

function stripHtml(html) {
  return html
    .replace(/<[^>]*>/g, " ")
    .replace(/&#x2F;/g, "/")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, " ")
    .trim()
}

export async function fetchHackerNewsArticles(limit = STORY_LIMIT) {
  const idsResponse = await fetch(`${HN_BASE}/topstories.json`)
  if (!idsResponse.ok) {
    throw new Error(`Hacker News request failed: ${idsResponse.status}`)
  }
  const ids = (await idsResponse.json()).slice(0, limit)

  const items = await Promise.all(
    ids.map((id) =>
      fetch(`${HN_BASE}/item/${id}.json`)
        .then((res) => (res.ok ? res.json() : null))
        .catch(() => null),
    ),
  )

  return items
    .filter((item) => item && item.type === "story" && !item.dead && !item.deleted && item.title)
    .map((item) =>
      normalizeArticle({
        id: `hn-${item.id}`,
        title: item.title,
        url: item.url ?? `https://news.ycombinator.com/item?id=${item.id}`,
        source: "Hacker News",
        sourceId: "hackernews",
        publishedAt: new Date(item.time * 1000).toISOString(),
        description: item.text ? stripHtml(item.text) : "",
        image: null,
        categories: [],
      }),
    )
}
