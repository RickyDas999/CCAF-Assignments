import { useMemo, useState } from 'react'
import { useCountriesData } from '../CountriesContext'
import { SEARCH_FNS } from '../data'
import { useFavorites } from '../hooks'
import { FavoriteButton, FlagImage, LoadingSpinner } from './common'

const FILTERS = [
  { id: 'name', label: 'Name' },
  { id: 'capital', label: 'Capital' },
  { id: 'region', label: 'Region' },
  { id: 'currency', label: 'Currency' },
  { id: 'language', label: 'Language' },
]

export function Search({ onSelect }) {
  const { data, loading, error } = useCountriesData()
  const { isFavorite, toggle } = useFavorites()
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('name')

  const results = useMemo(() => {
    if (!query.trim()) return []
    return SEARCH_FNS[filter](data, query).slice(0, 24)
  }, [data, query, filter])

  if (loading) return <LoadingSpinner label="Loading country data…" />
  if (error) return <div className="text-red-600 dark:text-red-400">Failed to load country data.</div>

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Search by ${filter}…`}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
        >
          {FILTERS.map((f) => (
            <option key={f.id} value={f.id}>
              {f.label}
            </option>
          ))}
        </select>
      </div>

      {query.trim() && results.length === 0 && (
        <p className="mt-6 text-sm text-slate-500 dark:text-slate-400">No countries found.</p>
      )}

      <ul className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {results.map((c) => (
          <li
            key={c.cca3}
            onClick={() => onSelect(c.cca3)}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 hover:border-slate-400 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-600"
          >
            <FlagImage src={c.flagPng} alt={`Flag of ${c.name.common}`} />
            <div className="min-w-0 flex-1">
              <div className="truncate font-medium text-slate-900 dark:text-slate-100">
                {c.name.common}
              </div>
              <div className="truncate text-xs text-slate-500 dark:text-slate-400">
                {c.capital?.[0] ?? '—'} · {c.region}
              </div>
            </div>
            <FavoriteButton active={isFavorite(c.cca3)} onToggle={() => toggle(c.cca3)} />
          </li>
        ))}
      </ul>
    </div>
  )
}
