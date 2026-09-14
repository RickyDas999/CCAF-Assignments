function formatCount(n) {
  if (n >= 1000) return `${(n / 1000).toFixed(1).replace(/\.0$/, "")}k`
  return String(n)
}

function GitHubCard({ repo }) {
  const { fullName, url, description, language, stars, starsToday } = repo

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`${fullName} on GitHub`}
      className="block rounded-xl border border-neutral-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900"
    >
      <p className="truncate text-sm font-semibold text-neutral-900 dark:text-neutral-100">
        {fullName}
      </p>

      <div className="mt-1 flex items-center justify-between text-xs text-neutral-500 dark:text-neutral-400">
        <span>★ {formatCount(stars)}</span>
        {starsToday > 0 && <span>+{formatCount(starsToday)} today</span>}
      </div>

      {description && (
        <p className="mt-2 line-clamp-2 text-sm text-neutral-600 dark:text-neutral-400">
          {description}
        </p>
      )}

      <span className="mt-2 inline-block text-xs font-medium text-neutral-500 dark:text-neutral-400">
        {language}
      </span>
    </a>
  )
}

export default GitHubCard
