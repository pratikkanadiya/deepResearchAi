from typing import List

from pydantic import BaseModel

from app.tools.news_search import NewsSearchTool


class NewsArticle(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    url: str
    published_at: str | None = None
    source: str | None = None


class NewsResearchResult(BaseModel):
    question: str
    articles: List[NewsArticle]


class NewsResearchAgent:

    def __init__(self):

        self.search_tool = NewsSearchTool()

    def research(
        self,
        question: str,
        max_results: int = 5
    ) -> NewsResearchResult:

        
        results = self.search_tool.search(
            query=question,
            max_results=max_results
        )
        
        articles = []

        for article in results:

            articles.append(
                NewsArticle(
                    title=article.get("title", ""),
                    description=article.get("description"),
                    content=article.get("content"),
                    url=article.get("url", ""),
                    published_at=article.get("published_at"),
                    source=article.get("source")
                )
            )

        return NewsResearchResult(
            question=question,
            articles=articles
        )


if __name__ == "__main__":

    agent = NewsResearchAgent()

    result = agent.research(
        "artificial intelligence healthcare"
    )

    print("\nQUESTION:")
    print(result.question)

    print("\nNEWS ARTICLES:")

    for article in result.articles:

        print("\n-----------------------------")
        print("TITLE:", article.title)
        print("SOURCE:", article.source)
        print("DATE:", article.published_at)
        print("URL:", article.url)

        if article.description:
            print("DESCRIPTION:")
            print(article.description[:500])