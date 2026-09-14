import { useEffect, useRef, useState } from "react"

const PAGE_SIZE = 20

export function useInfiniteScroll(totalCount, resetKey, pageSize = PAGE_SIZE) {
  const [visibleCount, setVisibleCount] = useState(pageSize)
  const sentinelRef = useRef(null)

  // Filters (category/search/bookmarks) change the underlying list, so
  // start pagination over whenever the active filter set changes.
  useEffect(() => {
    setVisibleCount(pageSize)
  }, [resetKey, pageSize])

  useEffect(() => {
    const node = sentinelRef.current
    if (!node) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setVisibleCount((current) => Math.min(current + pageSize, totalCount))
        }
      },
      { rootMargin: "200px" },
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [totalCount, pageSize])

  return { visibleCount, sentinelRef }
}
