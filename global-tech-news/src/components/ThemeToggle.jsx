function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === "dark"

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-pressed={isDark}
      className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-neutral-200 text-base hover:bg-neutral-50 dark:border-neutral-800 dark:hover:bg-neutral-900"
    >
      {isDark ? "🌙" : "☀️"}
    </button>
  )
}

export default ThemeToggle
