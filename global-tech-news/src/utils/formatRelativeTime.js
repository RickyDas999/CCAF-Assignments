const UNITS = [
  { limit: 60, divisor: 1, label: "s" },
  { limit: 3600, divisor: 60, label: "m" },
  { limit: 86400, divisor: 3600, label: "h" },
  { limit: 604800, divisor: 86400, label: "d" },
  { limit: 2629800, divisor: 604800, label: "w" },
  { limit: 31557600, divisor: 2629800, label: "mo" },
]

export function formatRelativeTime(isoString, now = Date.now()) {
  const then = new Date(isoString).getTime()
  if (Number.isNaN(then)) return ""

  const seconds = Math.max(0, Math.floor((now - then) / 1000))
  if (seconds < 60) return "just now"

  for (const unit of UNITS) {
    if (seconds < unit.limit) {
      const value = Math.floor(seconds / unit.divisor)
      return `${value}${unit.label} ago`
    }
  }

  const years = Math.floor(seconds / 31557600)
  return `${years}y ago`
}
