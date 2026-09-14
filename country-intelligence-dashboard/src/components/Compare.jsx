import { useState } from 'react'
import { useCountriesData } from '../CountriesContext'
import { FlagImage } from './common'

const ROWS = [
  { label: 'Capital', get: (c) => c.capital?.[0] ?? '—' },
  { label: 'Region', get: (c) => c.region },
  { label: 'Subregion', get: (c) => c.subregion || '—' },
  { label: 'Population', get: (c) => c.population?.toLocaleString() ?? '—' },
  { label: 'Area (km²)', get: (c) => c.area?.toLocaleString() ?? '—' },
  { label: 'Density (/km²)', get: (c) => (c.density != null ? Math.round(c.density) : '—') },
  { label: 'Borders', get: (c) => c.borders?.length ?? 0 },
  {
    label: 'Languages',
    get: (c) => Object.values(c.languages || {}).join(', ') || '—',
  },
  {
    label: 'Currency',
    get: (c) =>
      Object.values(c.currencies || {})
        .map((cur) => `${cur.name} (${cur.symbol ?? ''})`)
        .join(', ') || '—',
  },
  { label: 'Driving side', get: (c) => c.drivingSide ?? '—' },
]

function CountryPicker({ label, value, onChange, data }) {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || null)}
      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
    >
      <option value="">{label}</option>
      {data.map((c) => (
        <option key={c.cca3} value={c.cca3}>
          {c.name.common}
        </option>
      ))}
    </select>
  )
}

export function Compare() {
  const { data, byCca3Map } = useCountriesData()
  const [leftCode, setLeftCode] = useState(null)
  const [rightCode, setRightCode] = useState(null)

  const left = leftCode ? byCca3Map.get(leftCode) : null
  const right = rightCode ? byCca3Map.get(rightCode) : null

  return (
    <div>
      <div className="grid grid-cols-2 gap-4">
        <CountryPicker label="Select first country" value={leftCode} onChange={setLeftCode} data={data} />
        <CountryPicker label="Select second country" value={rightCode} onChange={setRightCode} data={data} />
      </div>

      {left && right ? (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr>
                <th className="w-1/3 p-2 text-left text-slate-500 dark:text-slate-400"> </th>
                <th className="p-2 text-left">
                  <div className="flex items-center gap-2">
                    <FlagImage src={left.flagPng} alt="" />
                    {left.name.common}
                  </div>
                </th>
                <th className="p-2 text-left">
                  <div className="flex items-center gap-2">
                    <FlagImage src={right.flagPng} alt="" />
                    {right.name.common}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <tr key={row.label} className="border-t border-slate-200 dark:border-slate-800">
                  <td className="p-2 font-medium text-slate-500 dark:text-slate-400">{row.label}</td>
                  <td className="p-2">{row.get(left)}</td>
                  <td className="p-2">{row.get(right)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-6 text-sm text-slate-500 dark:text-slate-400">
          Select two countries to compare.
        </p>
      )}
    </div>
  )
}
