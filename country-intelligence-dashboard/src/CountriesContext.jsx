import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { loadCountries } from './data'

const CountriesContext = createContext(null)

export function CountriesProvider({ children }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    loadCountries()
      .then((countries) => {
        if (!cancelled) setData(countries)
      })
      .catch((err) => {
        if (!cancelled) setError(err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const byCca3Map = useMemo(() => new Map(data.map((c) => [c.cca3, c])), [data])

  const value = useMemo(
    () => ({ data, byCca3Map, loading, error }),
    [data, byCca3Map, loading, error]
  )

  return <CountriesContext.Provider value={value}>{children}</CountriesContext.Provider>
}

export function useCountriesData() {
  const ctx = useContext(CountriesContext)
  if (!ctx) throw new Error('useCountriesData must be used within CountriesProvider')
  return ctx
}
