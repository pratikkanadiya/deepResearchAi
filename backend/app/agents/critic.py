import json
import re
from typing import Any, Dict, List

from dotenv import load_dotenv

from app.services.model import get_llm

from langchain_core.prompts import (
    ChatPromptTemplate
)

from app.schemas.critic import CriticResult


load_dotenv()


class CriticAgent:

    def __init__(self):

        self.llm = get_llm()

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are the final quality-control critic
for a deep research system.

Evaluate the research report against the
provided evidence and citation verification.

Evaluate:

1. Factual accuracy
2. Evidence quality
3. Citation quality
4. Completeness
5. Coherence

Rules:

- Do not invent facts.
- Do not introduce new evidence.
- Identify unsupported claims.
- Identify missing citations.
- Identify contradictions.
- Identify important missing aspects.
- Give concrete revision instructions.
- Distinguish serious issues from minor issues.

The report passes only when it is sufficiently
supported by the available evidence and citations.

Return one JSON object. Put all five numeric scores at the top level:
{{"overall_score":7,"passed":true,"factual_accuracy":7,"evidence_quality":7,"citation_quality":7,"completeness":7,"coherence":7,"issues":[],"revision_instructions":[],"strengths":[]}}
Do not nest these fields under a "properties" key. Do not include markdown.
"""
            ),
            (
                "human",
                """
Research topic:

{topic}

Research question:

{question}

Research report:

{report}

Citation verification:

{citation_verification}

Available evidence:

{evidence}
"""
            )
        ])

    def evaluate(
        self,
        topic: str,
        question: str,
        report: dict,
        citation_verification: dict,
        evidence: List[dict]
    ) -> CriticResult:

        evidence_text = []

        for item in evidence:

            payload = item.get(
                "payload",
                {}
            )

            evidence_text.append(
                f"""
Evidence ID:
{item.get("id", "")}

Claim:
{payload.get("claim", "")}

Supporting text:
{payload.get("supporting_text", "")}

Source:
{payload.get("source_url", "")}
"""
            )

        chain = self.prompt | self.llm
        inputs = {
            "topic": topic,
            "question": question,
            "report": str(report),
            "citation_verification": str(
                citation_verification
            ),
            "evidence": "\n".join(
                evidence_text
            )
        }

        last_error = None
        for attempt in range(2):
            try:
                response = chain.invoke(inputs)
                raw = getattr(response, "content", response)
                parsed = self._parse_json(raw)

                # Some Groq completions wrap the actual score fields in a
                # schema-like "properties" object. Promote those scores.
                nested = parsed.get("properties")
                if isinstance(nested, dict):
                    parsed = {**nested, **parsed}

                return CriticResult.model_validate(parsed)
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    print(f"Critic output invalid; retrying once: {exc}")

        raise ValueError(f"Critic returned invalid output after retry: {last_error}")

    @staticmethod
    def _parse_json(raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return raw

        if isinstance(raw, list):
            raw = "".join(
                str(part.get("text", "")) if isinstance(part, dict) else str(part)
                for part in raw
            )
        text = str(raw).strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

        # Decode the first JSON object, allowing harmless leading/trailing text.
        decoder = json.JSONDecoder()
        for index, character in enumerate(text):
            if character == "{":
                value, _ = decoder.raw_decode(text[index:])
                if not isinstance(value, dict):
                    raise ValueError("Critic output must be a JSON object.")
                return value
        raise ValueError("Critic output did not contain a JSON object.")


if __name__ == "__main__":

    agent = CriticAgent()

    result = agent.evaluate(
        topic="AI in Healthcare",
        question=(
            "How is AI being used "
            "in medical diagnosis?"
        ),
        report={
            "title": "AI in Healthcare",
            "sections": []
        },
        citation_verification={
            "overall_valid": True,
            "checks": []
        },
        evidence=[]
    )

    print(result.model_dump_json(indent=2))


