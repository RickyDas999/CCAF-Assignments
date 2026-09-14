const WORDS_PER_MINUTE = 200

export function calculateReadingTime(text = "", wordsPerMinute = WORDS_PER_MINUTE) {
  const words = text.trim().split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.round(words / wordsPerMinute))
}
