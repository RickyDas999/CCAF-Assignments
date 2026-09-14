import { fetchRSS } from "./rssClient"

const FEED_URL = "https://feeds.arstechnica.com/arstechnica/index"

export function fetchArsTechnicaArticles() {
  return fetchRSS({ source: "Ars Technica", sourceId: "arstechnica", feedUrl: FEED_URL })
}
