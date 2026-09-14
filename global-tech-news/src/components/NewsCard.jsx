import { formatRelativeTime } from "../utils/formatRelativeTime"
import BookmarkButton from "./BookmarkButton"

function NewsCard({ article, isBookmarked, onToggleBookmark }) {
  const { title, url, source, publishedAt, description, image, categories, readingTime } =
    article

  return (
    <article className="flex flex-col overflow-hidden rounded-xl border border-neutral-200 bg-white transition-shadow hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900">
      <div className="aspect-video w-full shrink-0 bg-neutral-100 dark:bg-neutral-800">
        {image ? (
          <img
            src={image}
            alt=""
            loading="lazy"
            className="size-full object-cover"
          />
        ) : (
          <div className="flex size-full items-center justify-center text-sm font-medium text-neutral-400 dark:text-neutral-600">
            {source}
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <h3 className="text-base leading-snug font-semibold text-neutral-900 dark:text-neutral-100">
          {title}
        </h3>

        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          {source} • {formatRelativeTime(publishedAt)} • {readingTime} min read
        </p>

        {categories?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {categories.map((category) => (
              <span
                key={category}
                className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-medium text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
              >
                {category}
              </span>
            ))}
          </div>
        )}

        {description && (
          <p className="line-clamp-2 text-sm text-neutral-600 dark:text-neutral-400">
            {description}
          </p>
        )}

        <div className="mt-auto flex items-center justify-between pt-2">
          <BookmarkButton isBookmarked={isBookmarked} onToggle={onToggleBookmark} />

          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Read: ${title}`}
            className="text-sm font-medium text-neutral-900 hover:underline dark:text-neutral-100"
          >
            Read →
          </a>
        </div>
      </div>
    </article>
  )
}

export default NewsCard
