import { useEffect, useState } from 'react'
import { useCountriesData } from '../CountriesContext'
import { getCoatOfArms } from '../data'
import { useFavorites } from '../hooks'
import { FavoriteButton, FlagImage, StatCard } from './common'
import { CountryMap } from './CountryMap'

function Section({ title, children }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {title}
      </h3>
      {children}
    </section>
  )
}

function Field({ label, value }) {
  return (
    <div className="flex justify-between gap-4 py-1 text-sm">
      <span className="text-slate-500 dark:text-slate-400">{label}</span>
      <span className="text-right font-medium text-slate-900 dark:text-slate-100">{value}</span>
    </div>
  )
}

export function CountryDetail({ cca3, onSelect }) {
  const { byCca3Map } = useCountriesData()
  const { isFavorite, toggle } = useFavorites()
  const [coatOfArms, setCoatOfArms] = useState(null)

  const country = byCca3Map.get(cca3)

  useEffect(() => {
    setCoatOfArms(null)
    if (!country) return
    let cancelled = false
    getCoatOfArms(country.name.common).then((url) => {
      if (!cancelled) setCoatOfArms(url)
    })
    return () => {
      cancelled = true
    }
  }, [country])

  if (!country) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Country not found.</p>
  }

  const languages = Object.entries(country.languages || {})
  const currencies = Object.entries(country.currencies || {})
  const nativeNames = Object.values(country.name.nativeName || {})
  const borders = (country.borders || []).map((code) => byCca3Map.get(code)).filter(Boolean)

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <FlagImage
            src={country.flagPng}
            alt={`Flag of ${country.name.common}`}
            className="h-16 w-24 rounded object-cover shadow"
          />
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {country.name.common}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">{country.name.official}</p>
          </div>
        </div>
        <FavoriteButton
          active={isFavorite(country.cca3)}
          onToggle={() => toggle(country.cca3)}
          className="text-3xl"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Section title="Overview">
          <Field label="Capital" value={country.capital?.[0] ?? '—'} />
          <Field label="Population" value={country.population?.toLocaleString() ?? '—'} />
          <Field label="Area" value={country.area ? `${country.area.toLocaleString()} km²` : '—'} />
          <Field label="Region" value={country.region} />
          <Field label="Subregion" value={country.subregion || '—'} />
        </Section>

        <Section title="Languages & Currency">
          <Field
            label="Official language(s)"
            value={languages.map(([, name]) => name).join(', ') || '—'}
          />
          <Field label="Native name(s)" value={nativeNames.map((n) => n.common).join(', ') || '—'} />
          <Field
            label="Currency"
            value={
              currencies.length
                ? currencies.map(([code, cur]) => `${cur.name} (${cur.symbol ?? code})`).join(', ')
                : '—'
            }
          />
        </Section>

        <Section title="National Info">
          <div className="mb-3 flex items-center gap-3">
            {coatOfArms ? (
              <img src={coatOfArms} alt={`Coat of arms of ${country.name.common}`} className="h-16 w-16 object-contain" />
            ) : (
              <div className="flex h-16 w-16 items-center justify-center rounded bg-slate-100 text-[10px] text-slate-400 dark:bg-slate-800">
                N/A
              </div>
            )}
            <FlagImage src={country.flagPng} alt={`Flag of ${country.name.common}`} className="h-16 w-24 rounded object-cover" />
          </div>
          <Field
            label="Calling code"
            value={country.idd?.root ? `${country.idd.root}${country.idd.suffixes?.[0] ?? ''}` : '—'}
          />
          <Field label="Internet domain" value={country.tld?.join(', ') || '—'} />
          <Field label="Driving side" value={country.drivingSide ?? '—'} />
        </Section>

        <Section title="Geography">
          <Field label="Continent" value={country.continent ?? '—'} />
          <Field label="Coordinates" value={country.latlng ? country.latlng.join(', ') : '—'} />
          <Field label="Coastline" value={country.coastline != null ? `${country.coastline} km` : '—'} />
          <div className="mt-3">
            <span className="text-sm text-slate-500 dark:text-slate-400">Borders</span>
            {borders.length === 0 ? (
              <p className="mt-1 text-sm text-slate-900 dark:text-slate-100">No land borders</p>
            ) : (
              <div className="mt-2 flex flex-wrap gap-2">
                {borders.map((b) => (
                  <button
                    key={b.cca3}
                    onClick={() => onSelect(b.cca3)}
                    className="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs hover:border-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-500"
                  >
                    <FlagImage src={b.flagPng} alt="" className="h-3.5 w-5 rounded-sm object-cover" />
                    {b.name.common}
                  </button>
                ))}
              </div>
            )}
          </div>
        </Section>
      </div>

      <Section title="Map">
        <CountryMap
          cca3={country.cca3}
          lat={country.latlng?.[0]}
          lng={country.latlng?.[1]}
          label={country.name.common}
        />
      </Section>

      <Section title="Statistics">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard
            label="Density"
            value={country.density != null ? `${Math.round(country.density)}/km²` : '—'}
          />
          <StatCard label="Area" value={country.area ? `${country.area.toLocaleString()} km²` : '—'} />
          <StatCard label="Borders" value={country.borders?.length ?? 0} />
          <StatCard label="Languages" value={languages.length} />
        </div>
      </Section>
    </div>
  )
}
