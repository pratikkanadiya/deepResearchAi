from __future__ import annotations

from typing import Any


class SourceBatcher:
    

    def __init__(
        self,
        max_chars_per_batch: int = 7000,
        max_sources_per_batch: int = 4,
        max_tokens_per_batch: int = 1800,
    ):
        if max_chars_per_batch < 1:
            raise ValueError("max_chars_per_batch must be positive.")

        if max_sources_per_batch < 1:
            raise ValueError("max_sources_per_batch must be positive.")

        if max_tokens_per_batch < 1:
            raise ValueError("max_tokens_per_batch must be positive.")

        self.max_chars_per_batch = max_chars_per_batch
        self.max_sources_per_batch = max_sources_per_batch
        self.max_tokens_per_batch = max_tokens_per_batch


    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough estimate: approximately 4 characters per token.

        This is not an exact tokenizer.
        """
        if not text:
            return 0

        return (len(text) + 3) // 4


    @staticmethod
    def get_evaluation_content(
        source: dict[str, Any],
    ) -> str:

        content = source.get("evaluation_content")

        if content is None:
            content = source.get("content", "")

        return str(content or "")

    def estimate_source_chars(
        self,
        source: dict[str, Any],
    ) -> int:
        title = str(source.get("title", "") or "")
        url = str(source.get("url", "") or "")
        source_type = str(source.get("source_type", "") or "")
        content = self.get_evaluation_content(source)

        return len(title) + len(url) + len(source_type) + len(content)

    def estimate_source_tokens(
        self,
        source: dict[str, Any],
    ) -> int:
        title = str(source.get("title", "") or "")
        url = str(source.get("url", "") or "")
        source_type = str(source.get("source_type", "") or "")
        content = self.get_evaluation_content(source)

        text = f"{title}\n{url}\n{source_type}\n{content}"

        return self.estimate_tokens(text)

    def prepare_source(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:

        prepared = dict(source)

        evaluation_content = self.get_evaluation_content(source)

        title = str(prepared.get("title", "") or "")
        url = str(prepared.get("url", "") or "")
        source_type = str(prepared.get("source_type", "") or "")

        metadata_chars = len(title) + len(url) + len(source_type)

        content_budget = max(
            0,
            self.max_chars_per_batch - metadata_chars,
        )

        if len(evaluation_content) > content_budget:
            shortened = evaluation_content[:content_budget]

            # Avoid cutting in the middle of a word when possible.
            last_space = shortened.rfind(" ")

            if last_space > 0:
                shortened = shortened[:last_space]

            if shortened:
                shortened += "..."

            evaluation_content = shortened

        prepared["evaluation_content"] = evaluation_content

        return prepared

    def create_batches(
        self,
        sources: list[dict[str, Any]],
    ) -> list[list[dict[str, Any]]]:

        batches: list[list[dict[str, Any]]] = []

        current_batch: list[dict[str, Any]] = []
        current_chars = 0
        current_tokens = 0

        for original_source in sources:
            if not isinstance(original_source, dict):
                continue

            source = self.prepare_source(original_source)

            source_chars = self.estimate_source_chars(source)
            source_tokens = self.estimate_source_tokens(source)

            exceeds_chars = (
                current_chars + source_chars
                > self.max_chars_per_batch
            )

            exceeds_tokens = (
                current_tokens + source_tokens
                > self.max_tokens_per_batch
            )

            exceeds_count = (
                len(current_batch)
                >= self.max_sources_per_batch
            )

            if current_batch and (
                exceeds_chars
                or exceeds_tokens
                or exceeds_count
            ):
                batches.append(current_batch)

                current_batch = []
                current_chars = 0
                current_tokens = 0

            current_batch.append(source)
            current_chars += source_chars
            current_tokens += source_tokens

        if current_batch:
            batches.append(current_batch)

        return batches