from typing import Any, Dict, List

from dotenv import load_dotenv

from app.services.model import get_llm

from langchain_core.prompts import (
    ChatPromptTemplate
)

from app.schemas.synthesis import (
    ResearchSynthesis
)


load_dotenv()


class ResearchSynthesizerAgent:

    def __init__(self):

        self.llm = get_llm()

        self.structured_llm = (
            self.llm.with_structured_output(
                ResearchSynthesis,
                # Validate JSON locally instead of letting Groq's constrained
                # JSON Schema decoder reject the entire synthesis response.
                method="json_mode",
            )
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are the Research Synthesizer Agent.

Your job is to create a research report from
the provided evidence.

STRICT RULES:

1. Use only the provided evidence.

2. Do not invent facts.

3. Do not introduce unsupported claims.

4. Every important factual claim must reference
   one or more evidence IDs.

5. Preserve source URLs.

6. Distinguish evidence from interpretation.

7. Mention important limitations.

8. Do not cite a source merely because it is
   present. Use it only when it supports the claim.

9. Do not fabricate evidence IDs or URLs.

10. Produce a coherent research report.

The output must remain traceable to the evidence.

Return exactly one valid JSON object matching this structure:
{{"title":"...","executive_summary":"...","sections":[{{"heading":"...","content":"...","claims":[{{"statement":"...","evidence_ids":["..."],"source_urls":["..."]}}]}}],"conclusion":"...","limitations":["..."]}}
Do not include markdown fences or text outside the JSON object. Keep claims and
citations inside their corresponding section. Every evidence_ids value must be
copied exactly from the supplied evidence.
"""
            ),
            (
                "human",
                """
Research topic:

{topic}

Research question:

{question}

Retrieved evidence:

{evidence}
"""
            )
        ])

    def synthesize(
        self,
        topic: str,
        question: str,
        evidence: List[dict]
    ) -> ResearchSynthesis:

        formatted_evidence = []

        for index, item in enumerate(
            evidence
        ):

            payload = item.get(
                "payload",
                {}
            )

            formatted_evidence.append(
                f"""
EVIDENCE {index + 1}

Evidence ID:
{item.get("id", "")}

Similarity Score:
{item.get("score", "")}

Claim:
{payload.get("claim", "")}

Supporting Text:
{payload.get("supporting_text", "")}

Source URL:
{payload.get("source_url", "")}

Evidence Type:
{payload.get("evidence_type", "")}

Confidence:
{payload.get("confidence", "")}

Limitations:
{payload.get("limitations", [])}
"""
            )

        evidence_text = "\n".join(
            formatted_evidence
        )

        chain = self.prompt | self.structured_llm
        inputs = {
            "topic": topic,
            "question": question,
            "evidence": evidence_text,
        }

        # Retry once for malformed JSON or a transient provider error. If both
        # attempts fail, preserve a useful report directly from retrieved
        # evidence rather than failing the entire research run.
        for attempt in range(2):
            try:
                result = chain.invoke(inputs)
                if isinstance(result, ResearchSynthesis):
                    return result
                return ResearchSynthesis.model_validate(result)
            except Exception as exc:
                if attempt == 0:
                    print(f"Synthesis attempt 1 failed; retrying: {exc}")
                else:
                    print(f"Synthesis model failed after retry: {exc}")

        return self._evidence_fallback(topic, evidence)

    @staticmethod
    def _evidence_fallback(
        topic: str,
        evidence: List[dict],
    ) -> ResearchSynthesis:
        """Build a traceable evidence summary without unsupported synthesis."""
        sections = []
        for item in evidence:
            payload: Dict[str, Any] = item.get("payload") or {}
            evidence_id = str(item.get("id") or "").strip()
            claim_text = str(payload.get("claim") or "").strip()
            supporting_text = str(payload.get("supporting_text") or "").strip()
            source_url = str(payload.get("source_url") or "").strip()
            statement = claim_text or supporting_text
            if not statement:
                continue

            sections.append({
                "heading": f"Retrieved evidence {len(sections) + 1}",
                "content": supporting_text or claim_text,
                "claims": [{
                    "statement": statement,
                    "evidence_ids": [evidence_id] if evidence_id else [],
                    "source_urls": [source_url] if source_url else [],
                }],
            })

        if not sections:
            raise ValueError(
                "Synthesis failed and no usable retrieved evidence was available."
            )

        return ResearchSynthesis.model_validate({
            "title": f"Evidence summary: {topic}",
            "executive_summary": (
                "The model could not produce a valid structured synthesis. "
                f"This report presents {len(sections)} retrieved evidence item(s) "
                "individually and does not infer conclusions across them."
            ),
            "sections": sections,
            "conclusion": (
                "The retrieved evidence is listed above with its available "
                "citations. Cross-source conclusions were not generated."
            ),
            "limitations": [
                "The model-generated synthesis was unavailable after a retry.",
                "Evidence is presented individually; findings were not reconciled across sources.",
                "Some retrieved items may not include a source URL or supporting text.",
            ],
        })


if __name__ == "__main__":

    agent = ResearchSynthesizerAgent()

    evidence = [
        {
            "id": "evidence-001",
            "score": 0.91,
            "payload": {
                "claim": (
                    "AI systems are being evaluated "
                    "for medical diagnosis."
                ),
                "supporting_text": (
                    "Artificial intelligence systems "
                    "are being evaluated for medical "
                    "diagnosis and clinical decision support."
                ),
                "source_url": (
                    "https://example.com/paper"
                ),
                "evidence_type": "research_finding",
                "confidence": 0.92,
                "limitations": [
                    "Evaluation depends on dataset "
                    "and clinical setting."
                ]
            }
        }
    ]

    result = agent.synthesize(
        topic="AI in Healthcare",
        question=(
            "How is AI being used in "
            "medical diagnosis?"
        ),
        evidence=evidence
    )

    print("\nTITLE:")
    print(result.title)

    print("\nEXECUTIVE SUMMARY:")
    print(result.executive_summary)

    print("\nSECTIONS:")

    for section in result.sections:

        print(
            f"\n### {section.heading}"
        )

        print(section.content)

        for claim in section.claims:

            print(
                "\nClaim:",
                claim.statement
            )

            print(
                "Evidence:",
                claim.evidence_ids
            )

            print(
                "Sources:",
                claim.source_urls
            )

    print("\nCONCLUSION:")
    print(result.conclusion)


