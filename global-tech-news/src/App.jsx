import { useEffect, useState } from "react"
import Header from "./components/Header"
import CategoryFilter from "./components/CategoryFilter"
import NewsGrid from "./components/NewsGrid"
import GitHubTrending from "./components/GitHubTrending"
import Footer from "./components/Footer"
import SkeletonCard from "./components/SkeletonCard"
import EmptyState from "./components/EmptyState"
import ErrorBanner from "./components/ErrorBanner"
import { useDarkMode } from "./hooks/useDarkMode"
import { useBookmarks } from "./hooks/useBookmarks"
import { useInfiniteScroll } from "./hooks/useInfiniteScroll"
import { fetchAllArticles } from "./api/newsService"
import { fetchTrendingRepositories } from "./api/githubTrending"
import { formatRelativeTime } from "./utils/formatRelativeTime"

function matchesArticleQuery(article, query) {
  if (!query.trim()) return true
  const haystack = `${article.title} ${article.description} ${article.source} ${article.categories.join(" ")}`.toLowerCase()
  return haystack.includes(query.trim().toLowerCase())
}

function matchesRepoQuery(repo, query) {
  if (!query.trim()) return true
  const haystack = `${repo.name} ${repo.fullName} ${repo.description} ${repo.language}`.toLowerCase()
  return haystack.includes(query.trim().toLowerCase())
}

function App() {
  const [searchQuery, setSearchQuery] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")
  const [articles, setArticles] = useState([])
  const [sourceCount, setSourceCount] = useState(0)
  const [failedSources, setFailedSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [repositories, setRepositories] = useState([])
  const [repoLoading, setRepoLoading] = useState(true)
  const [repoError, setRepoError] = useState(false)
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [refreshTick, setRefreshTick] = useState(0)
  const [, forceClockTick] = useState(0)
  const { theme, toggleTheme } = useDarkMode()
  const { bookmarks, addBookmark, removeBookmark, isBookmarked } = useBookmarks()

  async function loadNews() {
    const { articles: fetched, failedSources: failed, sourceCount: succeeded } =
      await fetchAllArticles()
    setArticles(fetched)
    setSourceCount(succeeded)
    setFailedSources(failed)
  }

  async function loadRepos() {
    try {
      const repos = await fetchTrendingRepositories()
      setRepositories(repos)
      setRepoError(false)
    } catch (error) {
      console.error("Failed to load GitHub trending repositories", error)
      setRepoError(true)
    }
  }

  useEffect(() => {
    Promise.all([
      loadNews().finally(() => setLoading(false)),
      loadRepos().finally(() => setRepoLoading(false)),
    ]).then(() => setLastUpdated(new Date()))
  }, [])

  // Keeps the header's "Updated Xm ago" label fresh without waiting for
  // some unrelated re-render to happen to trigger it.
  useEffect(() => {
    const interval = setInterval(() => forceClockTick((tick) => tick + 1), 60000)
    return () => clearInterval(interval)
  }, [])

  function handleRefresh() {
    setRefreshing(true)
    Promise.all([loadNews(), loadRepos()])
      .then(() => {
        setLastUpdated(new Date())
        setRefreshTick((tick) => tick + 1)
      })
      .finally(() => setRefreshing(false))
  }

  function handleToggleBookmark(article) {
    if (isBookmarked(article.id)) {
      removeBookmark(article.id)
    } else {
      addBookmark(article)
    }
  }

  const categoryFiltered =
    activeCategory === "All"
      ? articles
      : articles.filter((article) => article.categories.includes(activeCategory))

  const bookmarkFiltered = bookmarkedOnly
    ? categoryFiltered.filter((article) => isBookmarked(article.id))
    : categoryFiltered

  const visibleArticles = bookmarkFiltered.filter((article) =>
    matchesArticleQuery(article, searchQuery),
  )
  const visibleRepositories = repositories.filter((repo) => matchesRepoQuery(repo, searchQuery))

  const { visibleCount, sentinelRef } = useInfiniteScroll(
    visibleArticles.length,
    `${activeCategory}|${bookmarkedOnly}|${searchQuery}|${refreshTick}`,
  )
  const paginatedArticles = visibleArticles.slice(0, visibleCount)

  const lastUpdatedLabel = lastUpdated
    ? `Updated ${formatRelativeTime(lastUpdated.toISOString())}`
    : "Updating…"

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        searchValue={searchQuery}
        onSearchChange={setSearchQuery}
        lastUpdatedLabel={lastUpdatedLabel}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      <CategoryFilter
        activeCategory={activeCategory}
        onSelect={setActiveCategory}
        bookmarkedOnly={bookmarkedOnly}
        onToggleBookmarkedOnly={() => setBookmarkedOnly((current) => !current)}
        bookmarkCount={bookmarks.length}
      />

      <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 px-4 py-6 lg:flex-row lg:items-start">
        <section aria-label="Trending news" className="lg:w-[70%]">
          <h2 className="mb-4 text-xl font-semibold text-neutral-900 dark:text-neutral-100">
            Trending News
          </h2>
          {loading ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {Array.from({ length: 8 }, (_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : sourceCount === 0 ? (
            <EmptyState
              title="Unable to load news right now"
              description="All sources failed to respond. Try refreshing below."
            />
          ) : (
            <>
              {failedSources.length > 0 && (
                <ErrorBanner
                  message={`${failedSources.length} source${failedSources.length > 1 ? "s" : ""} unavailable: ${failedSources.join(", ")}`}
                />
              )}
              {visibleArticles.length === 0 ? (
                <EmptyState
                  title={bookmarkedOnly ? "No bookmarks yet." : "No stories match your filters."}
                />
              ) : (
                <>
                  <NewsGrid
                    articles={paginatedArticles}
                    isBookmarked={isBookmarked}
                    onToggleBookmark={handleToggleBookmark}
                  />
                  {visibleCount < visibleArticles.length && (
                    <div ref={sentinelRef} className="h-1" aria-hidden="true" />
                  )}
                </>
              )}
            </>
          )}
        </section>

        <GitHubTrending
          repositories={visibleRepositories}
          loading={repoLoading}
          error={repoError}
        />
      </main>

      <Footer
        totalCount={articles.length}
        sourceCount={sourceCount}
        onRefresh={handleRefresh}
        refreshing={refreshing}
      />
    </div>
  )
}

export default App
