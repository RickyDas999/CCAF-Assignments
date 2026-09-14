import { fetchRSS } from "./rssClient"

const FEED_URL = "https://www.theverge.com/rss/index.xml"

export function fetchTheVergeArticles() {
  return fetchRSS({ source: "The Verge", sourceId: "theverge", feedUrl: FEED_URL })
}
