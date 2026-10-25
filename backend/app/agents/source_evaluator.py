from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage

from app.services.model import get_llm
from app.agents.source_preprocessor import SourcePreprocessor
from app.agents.source_batcher import SourceBatcher

from app.schemas.source import (
    SourceEvaluationResult,
)


class SourceEvaluatorAgent:

    def __init__(
        self,
        max_content_chars: int = 4000,
        max_chars_per_batch: int = 7000,
        max_sources_per_batch: int = 4,
    ):

        self.llm = get_llm()

        self.preprocessor = SourcePreprocessor(
            max_content_chars=max_content_chars
        )

        self.batcher = SourceBatcher(
            max_chars_per_batch=max_chars_per_batch,
            max_sources_per_batch=max_sources_per_batch,
        )

        self.structured_llm = (
            self.llm.with_structured_output(
                SourceEvaluationResult,
                method="json_schema",
                strict=False,
            )
        )

    def evaluate(
        self,
        sources: list[dict[str, Any]],
        question: str = "",
        topic: str | None = None,
    ) -> SourceEvaluationResult:

        processed_sources = (
            self.preprocessor.process(
                sources
            )
        )

        if not processed_sources:
            return SourceEvaluationResult(evaluations=[])

        print(
            f"[Source Evaluator] "
            f"Sources after preprocessing: "
            f"{len(processed_sources)}"
        )

        batches = self.batcher.create_batches(
            processed_sources
        )

        print(
            f"[Source Evaluator] "
            f"Created {len(batches)} batches"
        )

        all_evaluations = []

        for index, batch in enumerate(
            batches,
            start=1,
        ):

            print(
                f"[Source Evaluator] "
                f"Evaluating batch "
                f"{index}/{len(batches)} "
                f"({len(batch)} sources)"
            )

            try:

                result = self._evaluate_batch(
                    topic=topic or question,
                    sources=batch,
                )

                all_evaluations.extend(
                    result.evaluations
                )

            except Exception as exc:

                print(
                    f"[Source Evaluator] "
                    f"Batch {index} failed: "
                    f"{exc}"
                )

                continue

        print(
            f"[Source Evaluator] "
            f"Completed evaluation: "
            f"{len(all_evaluations)} sources"
        )

        return SourceEvaluationResult(evaluations=all_evaluations)

    def _evaluate_batch(
        self,
        topic: str,
        sources: list[dict[str, Any]],
    ) -> SourceEvaluationResult:

        source_text = self._format_sources(
            sources
        )

        prompt = f"""
You are a research source evaluation agent.

Research topic:
{topic}

Evaluate the following sources.

IMPORTANT RULES:

1. Evaluate ONLY the provided sources.
2. Do not invent information.
3. Do not assume that a domain is authoritative automatically.
4. Evaluate authority based on the information actually available.
5. Evaluate relevance to the research topic.
6. Evaluate recency when publication information is available.
7. Evaluate specificity and usefulness.
8. Do not evaluate sources against each other merely because
   they have different source types.
9. Every evaluation MUST contain the exact source URL.
10. Do not create URLs.
11. Do not create sources that are not provided.
12. If information is insufficient, lower the relevant score
    instead of guessing.
13. Keep strengths and weaknesses concise.
14. Return exactly one evaluation for each supplied source.

Scoring:

authority_score:
0 = no meaningful authority information
10 = highly authoritative source based on available evidence

relevance_score:
0 = unrelated
10 = directly relevant to the research topic

recency_score:
0 = clearly outdated
10 = very recent or current when recency matters

specificity_score:
0 = vague/general
10 = highly specific and useful for the research question

overall_score:
Overall assessment from 0 to 10.

Sources:

{source_text}
"""

        return self.structured_llm.invoke(
            [
                HumanMessage(
                    content=prompt
                )
            ]
        )

    @staticmethod
    def _format_sources(
        sources: list[dict[str, Any]],
    ) -> str:

        formatted = []

        for index, source in enumerate(
            sources,
            start=1,
        ):

            title = source.get(
                "title",
                "Untitled",
            )

            url = source.get(
                "url",
                "",
            )

            content = source.get("evaluation_content")
            if content is None:
                content = source.get("content", "")

            source_type = source.get(
                "source_type",
                "unknown",
            )

            formatted.append(
                f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Source Type:
{source_type}

Content:
{content}
"""
            )

        return "\n".join(formatted)

def evaluate_sources(
    topic: str,
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    evaluator = SourceEvaluatorAgent()

    return evaluator.evaluate(
        topic=topic,
        sources=sources,
    )

if __name__ == "__main__":

    test_sources = [
        {
            "title": "AI Research Article",
            "url": "https://example.com/article",
            "content": (
                "Artificial intelligence research "
                "has expanded significantly."
            ),
            "source_type": "web",
        },
        {
            "title": "Machine Learning Paper",
            "url": "https://example.com/paper",
            "content": (
                "This paper examines machine learning "
                "methods and evaluation techniques."
            ),
            "source_type": "academic",
        },
    ]

    result = evaluate_sources(
        topic="Artificial Intelligence",
        sources=test_sources,
    )

    for item in result:
        print(item)