import NewsCard from "./NewsCard"

function NewsGrid({ articles, isBookmarked, onToggleBookmark }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {articles.map((article) => (
        <NewsCard
          key={article.id}
          article={article}
          isBookmarked={isBookmarked(article.id)}
          onToggleBookmark={() => onToggleBookmark(article)}
        />
      ))}
    </div>
  )
}

export default NewsGrid
