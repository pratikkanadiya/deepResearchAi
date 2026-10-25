from typing import List

from pydantic import BaseModel
from app.services.model import get_llm
from langchain_core.prompts import ChatPromptTemplate

from app.tools.web_search import WebSearchTool


class WebSource(BaseModel):
    title: str
    url: str
    content: str
    relevance_score: float | None = None


class WebResearchResult(BaseModel):
    question: str
    sources: List[WebSource]


class WebResearchAgent:

    def __init__(self):

        self.search_tool = WebSearchTool()

        self.llm = get_llm()

    def research(
        self,
        question: str,
        max_results: int = 5
    ) -> WebResearchResult:

        search_results = self.search_tool.search(
            query=question,
            max_results=max_results
        )

        sources = []

        for result in search_results:

            sources.append(
                WebSource(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    relevance_score=result.get("score")
                )
            )

        return WebResearchResult(
            question=question,
            sources=sources
        )


if __name__ == "__main__":

    agent = WebResearchAgent()

    result = agent.research(
        "How is artificial intelligence being used in healthcare?"
    )

    print("\nQUESTION:")
    print(result.question)

    print("\nSOURCES:")

    for source in result.sources:

        print("\n-----------------------------")
        print("TITLE:", source.title)
        print("URL:", source.url)
        print("SCORE:", source.relevance_score)
        print("CONTENT:")
        print(source.content[:500])