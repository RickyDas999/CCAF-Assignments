const TABS = [
  { id: 'search', label: 'Search' },
  { id: 'compare', label: 'Compare' },
  { id: 'favorites', label: 'Favorites' },
]

export function Header({ activeTab, onTabChange, dark, onToggleDark }) {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100">
          Country Intelligence Dashboard
        </h1>
        <div className="flex items-center gap-3">
          <TabNav activeTab={activeTab} onTabChange={onTabChange} />
          <DarkModeToggle dark={dark} onToggle={onToggleDark} />
        </div>
      </div>
    </header>
  )
}

export function TabNav({ activeTab, onTabChange }) {
  return (
    <nav className="flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-900">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            activeTab === tab.id
              ? 'bg-white text-slate-900 shadow dark:bg-slate-700 dark:text-slate-100'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}

export function DarkModeToggle({ dark, onToggle }) {
  return (
    <button
      onClick={onToggle}
      aria-label="Toggle dark mode"
      className="rounded-md border border-slate-200 px-2.5 py-1.5 text-sm dark:border-slate-700"
    >
      {dark ? '☀️ Light' : '🌙 Dark'}
    </button>
  )
}
