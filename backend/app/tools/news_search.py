import os
import time
import requests

from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class NewsSearchTool:

    BASE_URL = "https://gnews.io/api/v4/search"

    REQUEST_INTERVAL = 1.1

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 2

    def __init__(self):

        self.api_key = os.getenv("GNEWS_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GNEWS_API_KEY is missing from .env"
            )

        # Track last request time
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

        query = " ".join(query.split())

        query = query[:200]

        return query.strip()


    def _wait_for_rate_limit(self):


        elapsed = time.monotonic() - self._last_request_time

        if elapsed < self.REQUEST_INTERVAL:

            sleep_time = (
                self.REQUEST_INTERVAL - elapsed
            )

            print(
                f"[News] Waiting "
                f"{sleep_time:.2f}s before next request..."
            )

            time.sleep(sleep_time)


    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:

        query = self.normalize_query(query)

        if not query:

            print(
                "[News] Empty search query. Skipping."
            )

            return []

        max_results = max(
            1,
            min(max_results, 10)
        )

        params = {
            "q": query,
            "lang": "en",
            "max": max_results,
            "apikey": self.api_key,
            "sortby": "publishedAt",
        }

        backoff_time = self.INITIAL_BACKOFF

        for attempt in range(
            1,
            self.MAX_RETRIES + 1
        ):

            try:

                self._wait_for_rate_limit()

                print(
                    f"[News] Searching GNews: "
                    f"'{query}'"
                )

                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=20
                )

                self._last_request_time = (
                    time.monotonic()
                )


                if response.status_code == 200:

                    data = response.json()

                    results = []

                    for article in data.get(
                        "articles",
                        []
                    ):

                        if not isinstance(
                            article,
                            dict
                        ):
                            continue

                        source = article.get(
                            "source"
                        ) or {}

                        results.append(
                            {
                                "title": (
                                    article.get("title")
                                    or ""
                                ),
                                "description": (
                                    article.get(
                                        "description"
                                    )
                                    or ""
                                ),
                                "content": (
                                    article.get(
                                        "content"
                                    )
                                    or ""
                                ),
                                "url": (
                                    article.get("url")
                                    or ""
                                ),
                                "published_at": (
                                    article.get(
                                        "publishedAt"
                                    )
                                    or ""
                                ),
                                "source": (
                                    source.get("name")
                                    or ""
                                ),
                                "source_type": "news",
                            }
                        )

                    print(
                        f"[News] Found "
                        f"{len(results)} articles."
                    )

                    return results


                if response.status_code == 400:

                    print(
                        "[News] 400 Bad Request."
                    )

                    print(
                        f"[News] Query: {query}"
                    )

                    print(
                        "[News] API response:",
                        response.text[:500]
                    )

                    # Don't retry malformed queries
                    return []


                if response.status_code == 401:

                    print(
                        "[News] 401 Unauthorized."
                    )

                    print(
                        "[News] Check GNEWS_API_KEY "
                        "in your .env file."
                    )

                    return []


                if response.status_code == 403:

                    print(
                        "[News] 403 Forbidden."
                    )

                    print(
                        "[News] GNews daily quota "
                        "may have been exhausted."
                    )

                    return []


                if response.status_code == 429:

                    print(
                        f"[News] 429 Rate Limit "
                        f"(Attempt "
                        f"{attempt}/{self.MAX_RETRIES})."
                    )

                    if attempt < self.MAX_RETRIES:

                        print(
                            f"[News] Retrying in "
                            f"{backoff_time}s..."
                        )

                        time.sleep(
                            backoff_time
                        )

                        backoff_time *= 2

                        continue

                    print(
                        "[News] Rate limit retries "
                        "exhausted."
                    )

                    return []


                if response.status_code >= 500:

                    print(
                        f"[News] Server error "
                        f"{response.status_code}."
                    )

                    if attempt < self.MAX_RETRIES:

                        print(
                            f"[News] Retrying in "
                            f"{backoff_time}s..."
                        )

                        time.sleep(
                            backoff_time
                        )

                        backoff_time *= 2

                        continue

                    return []


                print(
                    f"[News] Unexpected HTTP "
                    f"status: {response.status_code}"
                )

                print(
                    response.text[:500]
                )

                return []


            except requests.exceptions.Timeout:

                print(
                    f"[News] Request timeout "
                    f"(Attempt "
                    f"{attempt}/{self.MAX_RETRIES})."
                )

                if attempt < self.MAX_RETRIES:

                    time.sleep(
                        backoff_time
                    )

                    backoff_time *= 2


            except requests.exceptions.ConnectionError as e:

                print(
                    f"[News] Connection error: {e}"
                )

                if attempt < self.MAX_RETRIES:

                    time.sleep(
                        backoff_time
                    )

                    backoff_time *= 2


            except requests.exceptions.RequestException as e:

                print(
                    f"[News] Request error: {e}"
                )

                return []


            except ValueError as e:

                print(
                    f"[News] Invalid JSON response: {e}"
                )

                return []

        print(
            f"[News] Search failed after "
            f"{self.MAX_RETRIES} attempts."
        )

        return []


if __name__ == "__main__":

    tool = NewsSearchTool()

    results = tool.search(
        "artificial intelligence healthcare",
        max_results=5
    )

    print("\n")
    print("=" * 70)
    print("GNEWS SEARCH RESULTS")
    print("=" * 70)

    if not results:
        print("No news articles found.")

    for index, article in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"RESULT #{index}"
        )

        print(
            "TITLE:",
            article["title"]
        )

        print(
            "SOURCE:",
            article["source"]
        )

        print(
            "DATE:",
            article["published_at"]
        )

        print(
            "URL:",
            article["url"]
        )

        print(
            "CONTENT:"
        )

        print(
            article["content"][:500]
        )