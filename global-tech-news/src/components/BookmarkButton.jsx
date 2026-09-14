function BookmarkButton({ isBookmarked, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isBookmarked ? "Remove bookmark" : "Bookmark this article"}
      aria-pressed={isBookmarked}
      className={`flex size-8 items-center justify-center rounded-lg border text-sm transition-colors ${
        isBookmarked
          ? "border-amber-500 bg-amber-50 text-amber-500 dark:border-amber-400 dark:bg-amber-500/10 dark:text-amber-400"
          : "border-neutral-200 hover:bg-neutral-50 dark:border-neutral-800 dark:hover:bg-neutral-800"
      }`}
    >
      {isBookmarked ? "★" : "☆"}
    </button>
  )
}

export default BookmarkButton
