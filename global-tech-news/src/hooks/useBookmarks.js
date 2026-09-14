import { useCallback, useEffect, useState } from "react"

const STORAGE_KEY = "global-tech-news-bookmarks"

function readBookmarks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState(readBookmarks)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks))
  }, [bookmarks])

  const addBookmark = useCallback((article) => {
    setBookmarks((current) => {
      if (current.some((bookmark) => bookmark.id === article.id)) return current
      const { id, title, url, source } = article
      return [...current, { id, type: "article", title, url, source }]
    })
  }, [])

  const removeBookmark = useCallback((id) => {
    setBookmarks((current) => current.filter((bookmark) => bookmark.id !== id))
  }, [])

  const isBookmarked = useCallback(
    (id) => bookmarks.some((bookmark) => bookmark.id === id),
    [bookmarks],
  )

  return { bookmarks, addBookmark, removeBookmark, isBookmarked }
}
