import { useState } from 'react'
import { CountriesProvider } from './CountriesContext'
import { useDarkMode } from './hooks'
import { Header } from './components/Layout'
import { Search } from './components/Search'
import { CountryDetail } from './components/CountryDetail'
import { Compare } from './components/Compare'
import { Favorites } from './components/Favorites'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [activeTab, setActiveTab] = useState('search')
  const [selectedCca3, setSelectedCca3] = useState(null)

  const handleSelect = (cca3) => {
    setSelectedCca3(cca3)
    setActiveTab('search')
  }

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    if (tab !== 'search') setSelectedCca3(null)
  }

  return (
    <CountriesProvider>
      <Header activeTab={activeTab} onTabChange={handleTabChange} dark={dark} onToggleDark={toggle} />
      <main className="mx-auto max-w-5xl px-4 py-6">
        {activeTab === 'search' &&
          (selectedCca3 ? (
            <div>
              <button
                onClick={() => setSelectedCca3(null)}
                className="mb-4 text-sm text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100"
              >
                ← Back to search
              </button>
              <CountryDetail cca3={selectedCca3} onSelect={handleSelect} />
            </div>
          ) : (
            <Search onSelect={handleSelect} />
          ))}
        {activeTab === 'compare' && <Compare />}
        {activeTab === 'favorites' && <Favorites onSelect={handleSelect} />}
      </main>
    </CountriesProvider>
  )
}
