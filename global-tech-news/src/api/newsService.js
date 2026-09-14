import { fetchHackerNewsArticles } from "./hackerNews"
import { fetchTechCrunchArticles } from "./techCrunch"
import { fetchArsTechnicaArticles } from "./arsTechnica"
import { fetchTheVergeArticles } from "./theVerge"
import { categorizeArticle } from "../utils/categorizeArticle"

const SOURCES = [
  { name: "Hacker News", fetcher: fetchHackerNewsArticles },
  { name: "TechCrunch", fetcher: fetchTechCrunchArticles },
  { name: "Ars Technica", fetcher: fetchArsTechnicaArticles },
  { name: "The Verge", fetcher: fetchTheVergeArticles },
]

function canonicalUrl(url) {
  try {
    const parsed = new URL(url)
    parsed.search = ""
    parsed.hash = ""
    return parsed.toString().replace(/\/$/, "").toLowerCase()
  } catch {
    return url.toLowerCase()
  }
}

function normalizedTitle(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
}

function dedupeArticles(articles) {
  const seenUrls = new Set()
  const seenTitles = new Set()
  const deduped = []

  for (const article of articles) {
    const urlKey = canonicalUrl(article.url)
    const titleKey = normalizedTitle(article.title)

    if (seenUrls.has(urlKey) || seenTitles.has(titleKey)) continue

    seenUrls.add(urlKey)
    seenTitles.add(titleKey)
    deduped.push(article)
  }

  return deduped
}

export async function fetchAllArticles() {
  const settled = await Promise.allSettled(SOURCES.map(({ fetcher }) => fetcher()))

  const articles = settled
    .filter((result) => result.status === "fulfilled")
    .flatMap((result) => result.value)
    .map((article) => ({ ...article, categories: categorizeArticle(article) }))

  const failedSources = settled
    .map((result, index) => ({ result, name: SOURCES[index].name }))
    .filter(({ result }) => result.status === "rejected")
    .map(({ name }) => name)

  const sorted = dedupeArticles(articles).sort(
    (a, b) => new Date(b.publishedAt) - new Date(a.publishedAt),
  )

  return {
    articles: sorted,
    failedSources,
    sourceCount: SOURCES.length - failedSources.length,
  }
}
