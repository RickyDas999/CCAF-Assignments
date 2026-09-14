import { CATEGORIES } from "../constants/categories"

function CategoryFilter({
  activeCategory,
  onSelect,
  bookmarkedOnly,
  onToggleBookmarkedOnly,
  bookmarkCount,
}) {
  return (
    <nav
      aria-label="Filter by category"
      className="border-b border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-950"
    >
      <div className="mx-auto flex max-w-7xl gap-2 overflow-x-auto px-4 py-3">
        {CATEGORIES.map((category) => {
          const isActive = category === activeCategory
          return (
            <button
              key={category}
              type="button"
              onClick={() => onSelect(category)}
              aria-pressed={isActive}
              className={`shrink-0 rounded-full border px-3.5 py-1.5 text-sm font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? "border-neutral-900 bg-neutral-900 text-white dark:border-neutral-100 dark:bg-neutral-100 dark:text-neutral-900"
                  : "border-neutral-200 text-neutral-600 hover:border-neutral-300 hover:text-neutral-900 dark:border-neutral-800 dark:text-neutral-400 dark:hover:border-neutral-700 dark:hover:text-neutral-100"
              }`}
            >
              {category}
            </button>
          )
        })}

        <button
          type="button"
          onClick={onToggleBookmarkedOnly}
          aria-pressed={bookmarkedOnly}
          className={`ml-1 shrink-0 rounded-full border px-3.5 py-1.5 text-sm font-medium whitespace-nowrap transition-colors ${
            bookmarkedOnly
              ? "border-amber-500 bg-amber-500 text-white"
              : "border-neutral-200 text-neutral-600 hover:border-neutral-300 hover:text-neutral-900 dark:border-neutral-800 dark:text-neutral-400 dark:hover:border-neutral-700 dark:hover:text-neutral-100"
          }`}
        >
          ★ Bookmarked{bookmarkCount > 0 ? ` (${bookmarkCount})` : ""}
        </button>
      </div>
    </nav>
  )
}

export default CategoryFilter
