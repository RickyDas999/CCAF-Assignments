const SOURCE_NAMES = ["Hacker News", "TechCrunch", "Ars Technica", "The Verge"]

function Footer({ totalCount = 0, sourceCount = 0, onRefresh, refreshing = false }) {
  return (
    <footer className="border-t border-neutral-200 dark:border-neutral-800">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-3 px-4 py-8 text-center">
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          {totalCount} stories loaded from {sourceCount} sources
        </p>

        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          className="rounded-lg border border-neutral-200 px-4 py-1.5 text-sm font-medium text-neutral-900 hover:bg-neutral-50 disabled:opacity-50 dark:border-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-900"
        >
          {refreshing ? "Refreshing…" : "Refresh"}
        </button>

        <p className="text-xs text-neutral-400 dark:text-neutral-500">
          {SOURCE_NAMES.join(" • ")}
        </p>
      </div>
    </footer>
  )
}

export default Footer
