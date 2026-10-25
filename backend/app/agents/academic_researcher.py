from typing import List

from pydantic import BaseModel

from app.tools.academic_search import AcademicSearchTool


class AcademicPaper(BaseModel):
    title: str
    abstract: str | None = None
    url: str | None = None
    year: int | None = None
    authors: List[str] = []
    citation_count: int | None = None
    venue: str | None = None


class AcademicResearchResult(BaseModel):
    question: str
    papers: List[AcademicPaper]


class AcademicResearchAgent:

    def __init__(self):

        self.search_tool = AcademicSearchTool()

    def research(
        self,
        question: str,
        max_results: int = 5
    ) -> AcademicResearchResult:

        results = self.search_tool.search(
            query=question,
            max_results=max_results
        )

        papers = []

        for paper in results:

            papers.append(
                AcademicPaper(
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract"),
                    url=paper.get("url"),
                    year=paper.get("year"),
                    authors=paper.get("authors", []),
                    citation_count=paper.get("citation_count"),
                    venue=paper.get("venue")
                )
            )

        return AcademicResearchResult(
            question=question,
            papers=papers
        )


if __name__ == "__main__":

    agent = AcademicResearchAgent()

    result = agent.research(
        "How does artificial intelligence improve medical diagnosis?"
    )

    print("\nQUESTION:")
    print(result.question)

    print("\nACADEMIC PAPERS:")

    for paper in result.papers:

        print("\n-----------------------------")
        print("TITLE:", paper.title)
        print("YEAR:", paper.year)
        print("AUTHORS:", paper.authors)
        print("CITATIONS:", paper.citation_count)
        print("VENUE:", paper.venue)
        print("URL:", paper.url)

        if paper.abstract:
            print("ABSTRACT:")
            print(paper.abstract[:500])