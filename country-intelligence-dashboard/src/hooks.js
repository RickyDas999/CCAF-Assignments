import { useCallback, useEffect, useState } from 'react'

const FAVORITES_KEY = 'cid:favorites'
const THEME_KEY = 'cid:theme'

export function useFavorites() {
  const [favorites, setFavorites] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(FAVORITES_KEY)) || []
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites))
  }, [favorites])

  const isFavorite = useCallback((cca3) => favorites.includes(cca3), [favorites])

  const toggle = useCallback((cca3) => {
    setFavorites((prev) =>
      prev.includes(cca3) ? prev.filter((c) => c !== cca3) : [...prev, cca3]
    )
  }, [])

  const remove = useCallback((cca3) => {
    setFavorites((prev) => prev.filter((c) => c !== cca3))
  }, [])

  return { favorites, isFavorite, toggle, remove }
}

export function useDarkMode() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored) return stored === 'dark'
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
  }, [dark])

  const toggle = useCallback(() => setDark((d) => !d), [])

  return { dark, toggle }
}
