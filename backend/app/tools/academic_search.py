import os
import time
from typing import List, Dict

import requests
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


class AcademicSearchTool:

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    REQUEST_INTERVAL = 1.1

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 3

    def __init__(self):
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        self.headers = {
            "Accept": "application/json",
            "User-Agent": "DeepResearchAI/1.0",
        }

        if api_key:
            self.headers["x-api-key"] = api_key
            print("[Academic] Semantic Scholar API key loaded.")
        else:
            print(
                "[Academic] WARNING: "
                "SEMANTIC_SCHOLAR_API_KEY not found."
            )

        self._last_request_time = 0.0


    @staticmethod
    def normalize_query(query: str) -> str:

        if not query:
            return ""

        query = (
            query
            .replace("-", " ")  
            .replace("–", " ")   
            .replace("—", " ")   
            .replace("−", " ")   
            .replace("\u00a0", " ")  
        )

        # Remove unnecessary whitespace
        query = " ".join(query.split())

        return query.strip()

    # ---------------------------------------------------------
    # Rate limiting
    # ---------------------------------------------------------

    def _wait_for_rate_limit(self):

        elapsed = time.monotonic() - self._last_request_time

        if elapsed < self.REQUEST_INTERVAL:
            sleep_time = self.REQUEST_INTERVAL - elapsed

            print(
                f"[Academic] Waiting {sleep_time:.2f}s "
                "before next Semantic Scholar request..."
            )

            time.sleep(sleep_time)


    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:

        query = self.normalize_query(query)

        if not query:
            print("[Academic] Empty query. Skipping search.")
            return []

        # Keep results within API limits
        max_results = max(1, min(max_results, 100))

        params = {
            "query": query,
            "limit": max_results,
            "fields": (
                "title,"
                "abstract,"
                "url,"
                "year,"
                "authors,"
                "citationCount,"
                "venue"
            ),
        }

        backoff_time = self.INITIAL_BACKOFF

        for attempt in range(1, self.MAX_RETRIES + 1):

            try:

                # Respect Semantic Scholar rate limit
                self._wait_for_rate_limit()

                print(
                    f"[Academic] Searching Semantic Scholar: "
                    f"'{query}'"
                )

                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=20,
                )

                # Record request time
                self._last_request_time = time.monotonic()


                if response.status_code == 200:
                    data = response.json()

                    results = []

                    for paper in data.get("data", []):

                        authors = [
                            author.get("name")
                            for author in paper.get("authors", [])
                            if author.get("name")
                        ]

                        results.append(
                            {
                                "title": paper.get("title"),
                                "abstract": paper.get("abstract"),
                                "url": paper.get("url"),
                                "year": paper.get("year"),
                                "authors": authors,
                                "citation_count": paper.get(
                                    "citationCount"
                                ),
                                "venue": paper.get("venue"),
                                "source_type": "academic",
                            }
                        )

                    print(
                        f"[Academic] Found "
                        f"{len(results)} papers."
                    )

                    return results


                if response.status_code == 429:

                    print(
                        f"[Academic] 429 Rate Limit "
                        f"(Attempt {attempt}/{self.MAX_RETRIES}). "
                        f"Retrying in {backoff_time}s..."
                    )

                    time.sleep(backoff_time)

                    backoff_time *= 2

                    continue


                if response.status_code == 400:

                    print(
                        "[Academic] 400 Bad Request."
                    )

                    print(
                        f"[Academic] Query: {query}"
                    )

                    print(
                        f"[Academic] Response: "
                        f"{response.text[:500]}"
                    )

                    return []


                if response.status_code == 401:

                    print(
                        "[Academic] 401 Unauthorized. "
                        "Check SEMANTIC_SCHOLAR_API_KEY."
                    )

                    return []


                if response.status_code == 403:

                    print(
                        "[Academic] 403 Forbidden. "
                        "Check Semantic Scholar API access."
                    )

                    return []


                print(
                    f"[Academic] HTTP {response.status_code}"
                )

                print(
                    f"[Academic] Response: "
                    f"{response.text[:500]}"
                )

                # Retry server-side errors
                if response.status_code >= 500:

                    print(
                        f"[Academic] Server error. "
                        f"Retrying in {backoff_time}s..."
                    )

                    time.sleep(backoff_time)

                    backoff_time *= 2

                    continue

                return []


            except requests.exceptions.Timeout:

                print(
                    f"[Academic] Request timeout "
                    f"(Attempt {attempt}/{self.MAX_RETRIES})."
                )

                if attempt < self.MAX_RETRIES:
                    time.sleep(backoff_time)
                    backoff_time *= 2

            except requests.exceptions.ConnectionError as e:

                print(
                    f"[Academic] Connection error: {e}"
                )

                if attempt < self.MAX_RETRIES:
                    time.sleep(backoff_time)
                    backoff_time *= 2

            except requests.exceptions.RequestException as e:

                print(
                    f"[Academic] Request error: {e}"
                )

                return []

            except ValueError as e:

                print(
                    f"[Academic] Invalid JSON response: {e}"
                )

                return []

        print(
            "[Academic] Search failed after "
            f"{self.MAX_RETRIES} attempts."
        )

        return []


if __name__ == "__main__":

    tool = AcademicSearchTool()

    results = tool.search(
        "artificial intelligence healthcare",
        max_results=5
    )

    print("\n")
    print("=" * 70)
    print("ACADEMIC SEARCH RESULTS")
    print("=" * 70)

    if not results:
        print("No academic papers found.")

    for index, paper in enumerate(results, start=1):

        print("\n" + "-" * 70)

        print(f"RESULT #{index}")

        print("TITLE:")
        print(paper.get("title"))

        print("\nYEAR:")
        print(paper.get("year"))

        print("\nAUTHORS:")
        print(", ".join(paper.get("authors", [])))

        print("\nCITATIONS:")
        print(paper.get("citation_count"))

        print("\nVENUE:")
        print(paper.get("venue"))

        print("\nURL:")
        print(paper.get("url"))

        print("\nABSTRACT:")
        abstract = paper.get("abstract")

        if abstract:
            print(abstract[:1000])
        else:
            print("No abstract available.")