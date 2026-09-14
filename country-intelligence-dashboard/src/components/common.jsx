export function StatCard({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">{value}</div>
    </div>
  )
}

export function FlagImage({ src, alt, className = 'h-8 w-12 rounded object-cover' }) {
  return <img src={src} alt={alt} className={className} loading="lazy" />
}

export function LoadingSpinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-slate-500 dark:text-slate-400">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-600 dark:border-slate-700 dark:border-t-slate-300" />
      <span>{label}</span>
    </div>
  )
}

export function FavoriteButton({ active, onToggle, className = '' }) {
  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        onToggle()
      }}
      aria-label={active ? 'Remove from favorites' : 'Add to favorites'}
      className={`text-xl leading-none ${className}`}
    >
      {active ? '★' : '☆'}
    </button>
  )
}

export function ErrorMessage({ message = 'Something went wrong.' }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
      {message}
    </div>
  )
}
