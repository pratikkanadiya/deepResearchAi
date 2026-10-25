from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse
from typing import Any


class SourcePreprocessor:

    def __init__(
        self,
        max_content_chars: int = 4000,
    ):
        self.max_content_chars = max_content_chars

    def process(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:

        sources = self.remove_invalid(sources)

        sources = self.normalize_urls(sources)

        sources = self.deduplicate(sources)

        sources = self.clean_content(sources)

        sources = self.truncate_content(sources)

        return sources

    def remove_invalid(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        valid_sources = []

        for source in sources:

            if not isinstance(source, dict):
                continue

            url = source.get("url")

            if not url:
                continue

            if not isinstance(url, str):
                continue

            url = url.strip()

            if not url.startswith(("http://", "https://")):
                continue

            valid_sources.append(source)

        return valid_sources

    def normalize_urls(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        processed = []

        for source in sources:

            source = dict(source)

            url = source.get("url", "").strip()

            try:
                parsed = urlparse(url)

                normalized = urlunparse(
                    (
                        parsed.scheme.lower(),
                        parsed.netloc.lower(),
                        parsed.path.rstrip("/"),
                        "",
                        parsed.query,
                        "",
                    )
                )

                source["url"] = normalized

            except Exception:
                pass

            processed.append(source)

        return processed

    def deduplicate(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        seen_urls = set()
        unique_sources = []

        for source in sources:

            url = source.get("url", "").lower().strip()

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            unique_sources.append(source)

        return unique_sources

    def clean_content(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        processed = []

        for source in sources:

            source = dict(source)

            content = source.get("content", "")

            if content is None:
                content = ""

            content = str(content)

            content = re.sub(r"\s+", " ", content)

            content = re.sub(r"\.{4,}", "...", content)

            content = content.strip()

            source["content"] = content

            processed.append(source)

        return processed

    def truncate_content(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        processed = []

        for source in sources:
            source = dict(source)

            original_content = source.get("content", "")
            original_content = str(original_content)

            evaluation_content = original_content

            if len(evaluation_content) > self.max_content_chars:
                evaluation_content = evaluation_content[
                    :self.max_content_chars
                ]

                last_space = evaluation_content.rfind(" ")

                if last_space > 0:
                    evaluation_content = evaluation_content[:last_space]

                evaluation_content += "..."

            source["evaluation_content"] = evaluation_content

            source["content"] = original_content

            processed.append(source)

        return processed