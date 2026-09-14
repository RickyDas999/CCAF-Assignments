import { normalizeArticle } from "../utils/normalizeArticle"

const RSS2JSON_ENDPOINT = "https://api.rss2json.com/v1/api.json"

function stripHtml(html = "") {
  return html
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim()
}

// rss2json returns pubDate as "YYYY-MM-DD HH:MM:SS" with no timezone marker
// but the underlying values are UTC, so normalize it to a parseable ISO string.
function parsePubDate(pubDate) {
  const isoLike = pubDate.includes("T") ? pubDate : `${pubDate.replace(" ", "T")}Z`
  const parsed = new Date(isoLike)
  return Number.isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString()
}

function normalizeRssItem(item, { source, sourceId }) {
  return normalizeArticle({
    id: `${sourceId}-${item.guid || item.link}`,
    title: item.title,
    url: item.link,
    source,
    sourceId,
    publishedAt: parsePubDate(item.pubDate),
    description: stripHtml(item.description || item.content || "").slice(0, 300),
    image: item.thumbnail || item.enclosure?.link || null,
    categories: [],
  })
}

export async function fetchRSS({ source, sourceId, feedUrl }) {
  const url = `${RSS2JSON_ENDPOINT}?rss_url=${encodeURIComponent(feedUrl)}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`${source} RSS request failed: ${response.status}`)
  }

  const data = await response.json()
  if (data.status !== "ok") {
    throw new Error(`${source} RSS request failed: ${data.message ?? "unknown error"}`)
  }

  return data.items.map((item) => normalizeRssItem(item, { source, sourceId }))
}
