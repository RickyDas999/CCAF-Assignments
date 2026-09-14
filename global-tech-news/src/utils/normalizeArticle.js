import { calculateReadingTime } from "./calculateReadingTime"

// Maps any source adapter's raw fields onto the app's unified article model.
export function normalizeArticle({
  id,
  title,
  url,
  source,
  sourceId,
  publishedAt,
  description = "",
  image = null,
  categories = [],
  readingTime,
}) {
  return {
    id,
    title,
    url,
    source,
    sourceId,
    publishedAt,
    description,
    image,
    categories,
    readingTime: readingTime ?? calculateReadingTime(`${title} ${description}`),
  }
}
