import os
from typing import List, Dict

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


class WebSearchTool:

    def __init__(self):

        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is missing from .env"
            )

        self.client = TavilyClient(
            api_key=api_key
        )


    @staticmethod
    def normalize_query(query: str) -> str:

        if not query:
            return ""

        # Normalize different dash characters
        query = (
            query
            .replace("-", " ")
            .replace("–", " ")
            .replace("—", " ")
            .replace("−", " ")
            .replace("\u00a0", " ")
        )

        # Remove extra spaces
        query = " ".join(query.split())

        return query.strip()


    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:

        query = self.normalize_query(query)

        if not query:
            print("[Web] Empty search query. Skipping.")

            return []

        max_results = max(
            1,
            min(max_results, 10)
        )

        try:

            print(
                f"[Web] Searching Tavily: '{query}'"
            )

            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False
            )

        except Exception as e:

            print(
                f"[Web] Tavily search failed: {e}"
            )

            return []

        results = []

        for item in response.get("results", []):

            if not isinstance(item, dict):
                continue

            results.append({
                "title": item.get("title") or "",
                "url": item.get("url") or "",
                "content": item.get("content") or "",
                "score": item.get("score"),
                "source_type": "web"
            })

        print(
            f"[Web] Tavily returned "
            f"{len(results)} results."
        )

        return results


if __name__ == "__main__":

    tool = WebSearchTool()

    results = tool.search(
        "impact of artificial intelligence on healthcare",
        max_results=5
    )

    print("\n")
    print("=" * 60)
    print("TAVILY SEARCH RESULTS")
    print("=" * 60)

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n-----------------------------"
        )

        print(
            f"RESULT #{index}"
        )

        print(
            "TITLE:",
            result["title"]
        )

        print(
            "URL:",
            result["url"]
        )

        print(
            "SCORE:",
            result["score"]
        )

        print(
            "SOURCE TYPE:",
            result["source_type"]
        )