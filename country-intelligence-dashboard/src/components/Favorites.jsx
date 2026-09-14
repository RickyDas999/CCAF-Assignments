import { useCountriesData } from '../CountriesContext'
import { useFavorites } from '../hooks'
import { FlagImage } from './common'

export function Favorites({ onSelect }) {
  const { byCca3Map } = useCountriesData()
  const { favorites, remove } = useFavorites()

  const countries = favorites.map((cca3) => byCca3Map.get(cca3)).filter(Boolean)

  if (countries.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No favorites yet — star a country from Search to save it here.
      </p>
    )
  }

  return (
    <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {countries.map((c) => (
        <li
          key={c.cca3}
          className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900"
        >
          <button onClick={() => onSelect(c.cca3)} className="flex min-w-0 flex-1 items-center gap-3 text-left">
            <FlagImage src={c.flagPng} alt={`Flag of ${c.name.common}`} />
            <div className="min-w-0">
              <div className="truncate font-medium text-slate-900 dark:text-slate-100">
                {c.name.common}
              </div>
              <div className="truncate text-xs text-slate-500 dark:text-slate-400">
                {c.capital?.[0] ?? '—'} · {c.region}
              </div>
            </div>
          </button>
          <button
            onClick={() => remove(c.cca3)}
            aria-label={`Remove ${c.name.common} from favorites`}
            className="text-xl leading-none text-amber-500"
          >
            ★
          </button>
        </li>
      ))}
    </ul>
  )
}
