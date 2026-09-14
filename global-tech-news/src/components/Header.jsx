import SearchBar from "./SearchBar"
import ThemeToggle from "./ThemeToggle"

function Header({ searchValue, onSearchChange, lastUpdatedLabel, theme, onToggleTheme }) {
  return (
    <header className="sticky top-0 z-20 border-b border-neutral-200 bg-white/90 backdrop-blur-sm dark:border-neutral-800 dark:bg-neutral-950/90">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3 lg:flex-nowrap">
        <h1 className="shrink-0 text-lg font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
          Global Tech
        </h1>

        <div className="order-3 w-full lg:order-2 lg:w-auto lg:flex-1">
          <SearchBar value={searchValue} onChange={onSearchChange} />
        </div>

        <div className="ml-auto flex items-center gap-3 lg:order-3">
          <span className="hidden text-xs text-neutral-500 sm:inline dark:text-neutral-400">
            {lastUpdatedLabel}
          </span>
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </div>
      </div>
    </header>
  )
}

export default Header
