from typing import List

from dotenv import load_dotenv

from app.services.model import get_llm

from langchain_core.prompts import (
    ChatPromptTemplate
)

from app.schemas.citation import (
    CitationVerificationResult
)


load_dotenv()


class CitationVerifierAgent:

    def __init__(self):

        self.llm = get_llm()

        self.structured_llm = (
            self.llm.with_structured_output(
                CitationVerificationResult,
                method="json_schema",
                strict=False,
            )
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are a Citation Verification Agent.

Your job is to verify whether the claims in a
research report are actually supported by the
provided evidence.

For every claim:

1. Determine whether the evidence supports it.

2. Check whether the cited evidence IDs exist.

3. Check whether the cited source URLs correspond
   to the supplied evidence.

4. Detect unsupported claims.

5. Detect missing citations.

6. Do not give credit merely because a citation
   exists. The evidence must actually support
   the claim.

7. Do not invent evidence.

8. Explain why a claim is supported or unsupported.

9. Use a support score from 0 to 1.

A claim should be considered supported only when
the provided evidence substantively supports it.
"""
            ),
            (
                "human",
                """
Research question:

{question}

Research report:

{report}

Available evidence:

{evidence}
"""
            )
        ])

    def verify(
        self,
        question: str,
        report: dict,
        evidence: List[dict]
    ) -> CitationVerificationResult:

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

Supporting Text:
{payload.get("supporting_text", "")}

Source:
{payload.get("source_url", "")}

Confidence:
{payload.get("confidence", "")}
"""
            )

        evidence_text = "\n".join(
            evidence_text
        )

        report_text = self._format_report(
            report
        )

        chain = (
            self.prompt
            | self.structured_llm
        )

        result = chain.invoke({
            "question": question,
            "report": report_text,
            "evidence": evidence_text
        })

        return result

    def _format_report(
        self,
        report: dict
    ) -> str:

        output = []

        output.append(
            f"TITLE:\n{report.get('title', '')}"
        )

        output.append(
            "EXECUTIVE SUMMARY:\n"
            + report.get(
                "executive_summary",
                ""
            )
        )

        for section in report.get(
            "sections",
            []
        ):

            output.append(
                f"""
SECTION:
{section.get('heading', '')}

CONTENT:
{section.get('content', '')}

CLAIMS:
"""
            )

            for claim in section.get(
                "claims",
                []
            ):

                output.append(
                    f"""
Statement:
{claim.get('statement', '')}

Evidence IDs:
{claim.get('evidence_ids', [])}

Source URLs:
{claim.get('source_urls', [])}
"""
                )

        output.append(
            "CONCLUSION:\n"
            + report.get(
                "conclusion",
                ""
            )
        )

        return "\n".join(output)


if __name__ == "__main__":

    agent = CitationVerifierAgent()

    evidence = [
        {
            "id": "evidence-001",
            "payload": {
                "claim": (
                    "AI systems are being evaluated "
                    "for medical diagnosis."
                ),
                "supporting_text": (
                    "Artificial intelligence systems "
                    "are being evaluated for medical "
                    "diagnosis."
                ),
                "source_url": (
                    "https://example.com/paper"
                ),
                "confidence": 0.92
            }
        }
    ]

    report = {
        "title": "AI in Healthcare",
        "executive_summary": (
            "AI systems are being evaluated "
            "for medical diagnosis."
        ),
        "sections": [
            {
                "heading": "Medical Diagnosis",
                "content": (
                    "AI systems are being evaluated "
                    "for medical diagnosis."
                ),
                "claims": [
                    {
                        "statement": (
                            "AI systems are being "
                            "evaluated for diagnosis."
                        ),
                        "evidence_ids": [
                            "evidence-001"
                        ],
                        "source_urls": [
                            "https://example.com/paper"
                        ]
                    }
                ]
            }
        ],
        "conclusion": (
            "AI has potential applications "
            "in healthcare."
        )
    }

    result = agent.verify(
        question=(
            "How is AI being used "
            "in medical diagnosis?"
        ),
        report=report,
        evidence=evidence
    )

    print("\nOVERALL VALID:")
    print(result.overall_valid)

    print("\nCHECKS:")

    for check in result.checks:

        print("\n--------------------")
        print("CLAIM:", check.claim)
        print("SUPPORTED:", check.supported)
        print(
            "SUPPORT SCORE:",
            check.support_score
        )
        print(
            "EXPLANATION:",
            check.explanation
        )

    print("\nUNSUPPORTED CLAIMS:")

    for claim in result.unsupported_claims:
        print("-", claim)

    print("\nMISSING CITATIONS:")

    for citation in result.missing_citations:
        print("-", citation)