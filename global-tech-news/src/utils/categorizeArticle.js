const CATEGORY_KEYWORDS = {
  AI: ["ai", "artificial intelligence", "llm", "openai", "anthropic", "machine learning", "gemini"],
  Programming: ["javascript", "python", "java", "rust", "developer", "programming", "coding"],
  Startups: ["startup", "funding", "venture", "series a", "series b", "founder"],
  Cybersecurity: ["security", "cybersecurity", "hack", "breach", "malware", "ransomware", "vulnerability"],
  Cloud: ["aws", "azure", "cloud", "google cloud", "kubernetes", "serverless"],
  Mobile: ["iphone", "android", "ios", "mobile", "smartphone"],
  "Web Dev": ["react", "vue", "angular", "frontend", "web development", "browser", "css"],
}

export function categorizeArticle(article) {
  const haystack = `${article.title} ${article.description} ${article.source}`.toLowerCase()

  return Object.entries(CATEGORY_KEYWORDS)
    .filter(([, keywords]) => keywords.some((keyword) => haystack.includes(keyword)))
    .map(([category]) => category)
}
