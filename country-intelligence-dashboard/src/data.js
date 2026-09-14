// Single data module: fetch + merge + search + lookups.
// Data sources (all free, keyless, CORS-open):
// - mledoze/countries: core record (names, capital, region, area, latlng, borders, currencies, idd, tld, languages)
// - samayo/country-json: population, population density, coastline, continent, driving side
// - flagcdn.com: flag images (URL template, no fetch needed)
// - Wikipedia REST summary API: coat of arms (best-effort)
//
// Known gap: no free/keyless source provides timezones, so they're omitted rather than faked.

const MLEDOZE_URL = 'https://raw.githubusercontent.com/mledoze/countries/master/dist/countries.json'
const CJ_BASE = 'https://raw.githubusercontent.com/samayo/country-json/master/src'

// mledoze / country-json common-name mismatches that would otherwise fail to merge.
const NAME_ALIASES = {
  'Ivory Coast': "Côte d'Ivoire",
  'DR Congo': 'DR Congo',
  'Congo': 'Republic of the Congo',
  'North Korea': 'North Korea',
  'South Korea': 'South Korea',
  'Czech Republic': 'Czechia',
  'Cape Verde': 'Cabo Verde',
  'Swaziland': 'Eswatini',
  'Burma': 'Myanmar',
  'East Timor': 'Timor-Leste',
  'Laos': 'Laos',
  'Micronesia': 'Micronesia',
  'United States': 'United States',
  'Russia': 'Russia',
  'Vatican City': 'Holy See',
  'Palestine': 'Palestine',
}

function normalize(name) {
  return (NAME_ALIASES[name] || name).toLowerCase().trim()
}

function buildLookup(records, keyField, valueField) {
  const map = new Map()
  for (const r of records) {
    if (r[keyField] != null) map.set(normalize(r[keyField]), r[valueField])
  }
  return map
}

let cachedData = null
let loadPromise = null

export function loadCountries() {
  if (cachedData) return Promise.resolve(cachedData)
  if (loadPromise) return loadPromise

  loadPromise = Promise.all([
    fetch(MLEDOZE_URL).then((r) => r.json()),
    fetch(`${CJ_BASE}/country-by-population.json`).then((r) => r.json()),
    fetch(`${CJ_BASE}/country-by-population-density.json`).then((r) => r.json()),
    fetch(`${CJ_BASE}/country-by-coastline.json`).then((r) => r.json()),
    fetch(`${CJ_BASE}/country-by-continent.json`).then((r) => r.json()),
    fetch(`${CJ_BASE}/country-by-driving-side.json`).then((r) => r.json()),
  ]).then(([base, population, density, coastline, continent, driving]) => {
    const popMap = buildLookup(population, 'country', 'population')
    const densityMap = buildLookup(density, 'country', 'density')
    const coastlineMap = buildLookup(coastline, 'country', 'coastline')
    const continentMap = buildLookup(continent, 'country', 'continent')
    const drivingMap = buildLookup(driving, 'country', 'side')

    const merged = base.map((c) => {
      const key = normalize(c.name.common)
      const cca2 = c.cca2.toLowerCase()
      if (import.meta.env.DEV && !popMap.has(key)) {
        console.warn(`[data] no population match for "${c.name.common}"`)
      }
      return {
        ...c,
        population: popMap.get(key) ?? null,
        density: densityMap.get(key) ?? null,
        coastline: coastlineMap.get(key) ?? null,
        continent: continentMap.get(key) ?? c.region ?? null,
        drivingSide: drivingMap.get(key) ?? null,
        flagPng: `https://flagcdn.com/w320/${cca2}.png`,
        flagSvg: `https://flagcdn.com/${cca2}.svg`,
      }
    })

    cachedData = merged
    return merged
  })

  return loadPromise
}

// ---- Search / lookup helpers (all pure, client-side, over the in-memory dataset) ----

export function searchByName(data, q) {
  const query = q.toLowerCase().trim()
  if (!query) return []
  return data.filter(
    (c) =>
      c.name.common.toLowerCase().includes(query) ||
      c.name.official.toLowerCase().includes(query)
  )
}

export function searchByCapital(data, q) {
  const query = q.toLowerCase().trim()
  if (!query) return []
  return data.filter((c) => (c.capital || []).some((cap) => cap.toLowerCase().includes(query)))
}

export function searchByRegion(data, q) {
  const query = q.toLowerCase().trim()
  if (!query) return []
  return data.filter(
    (c) => c.region?.toLowerCase().includes(query) || c.subregion?.toLowerCase().includes(query)
  )
}

export function searchByCurrency(data, q) {
  const query = q.toLowerCase().trim()
  if (!query) return []
  return data.filter((c) =>
    Object.entries(c.currencies || {}).some(
      ([code, cur]) => code.toLowerCase().includes(query) || cur.name.toLowerCase().includes(query)
    )
  )
}

export function searchByLanguage(data, q) {
  const query = q.toLowerCase().trim()
  if (!query) return []
  return data.filter((c) =>
    Object.values(c.languages || {}).some((lang) => lang.toLowerCase().includes(query))
  )
}

export const SEARCH_FNS = {
  name: searchByName,
  capital: searchByCapital,
  region: searchByRegion,
  currency: searchByCurrency,
  language: searchByLanguage,
}

// ---- Coat of arms (best-effort, memoized) ----

const coatOfArmsCache = new Map()

export async function getCoatOfArms(commonName) {
  if (coatOfArmsCache.has(commonName)) return coatOfArmsCache.get(commonName)
  try {
    const title = encodeURIComponent(`Coat of arms of ${commonName}`)
    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${title}`)
    if (!res.ok) throw new Error('not found')
    const json = await res.json()
    const url = json.thumbnail?.source ?? null
    coatOfArmsCache.set(commonName, url)
    return url
  } catch {
    coatOfArmsCache.set(commonName, null)
    return null
  }
}
