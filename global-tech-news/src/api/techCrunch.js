import { fetchRSS } from "./rssClient"

const FEED_URL = "https://techcrunch.com/feed/"

export function fetchTechCrunchArticles() {
  return fetchRSS({ source: "TechCrunch", sourceId: "techcrunch", feedUrl: FEED_URL })
}
