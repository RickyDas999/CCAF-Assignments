import GitHubCard from "./GitHubCard"
import EmptyState from "./EmptyState"

function RepoSkeleton() {
  return (
    <div className="h-24 animate-pulse rounded-xl border border-neutral-200 bg-neutral-100 motion-reduce:animate-none dark:border-neutral-800 dark:bg-neutral-800" />
  )
}

function GitHubTrending({ repositories, loading, error }) {
  return (
    <aside aria-label="GitHub trending repositories" className="lg:sticky lg:top-20 lg:w-[30%]">
      <h2 className="mb-4 text-xl font-semibold text-neutral-900 dark:text-neutral-100">
        GitHub Trending
      </h2>
      <div className="flex flex-col gap-3">
        {loading ? (
          Array.from({ length: 5 }, (_, i) => <RepoSkeleton key={i} />)
        ) : error ? (
          <EmptyState
            title="GitHub Trending is unavailable"
            description="Try refreshing in a moment."
          />
        ) : repositories.length === 0 ? (
          <EmptyState title="No repositories match right now." />
        ) : (
          repositories.map((repo) => <GitHubCard key={repo.id} repo={repo} />)
        )}
      </div>
    </aside>
  )
}

export default GitHubTrending
