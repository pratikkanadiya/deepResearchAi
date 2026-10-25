from app.agents.research_synthesizer import ResearchSynthesizerAgent
from app.schemas.revision import RevisionResult


class RevisionManager:

    def __init__(self, max_revisions: int = 2):

        self.max_revisions = max_revisions

        self.synthesizer = ResearchSynthesizerAgent()

    def should_revise(
        self,
        critic_result: dict,
        revision_count: int
    ) -> bool:

        if revision_count >= self.max_revisions:
            return False

        if critic_result.get("passed", False):
            return False

        return True

    def revise(
        self,
        topic: str,
        question: str,
        evidence: list[dict],
        critic_result: dict,
        revision_count: int,
        previous_report: dict
    ) -> RevisionResult:

        instructions = critic_result.get(
            "revision_instructions",
            []
        )

        revision_number = revision_count + 1

        revision_prompt = f"""
Original research question:

{question}


Previous report:

{previous_report}


Critic score:

{critic_result.get("overall_score", 0)}


Critic issues:

{critic_result.get("issues", [])}


Revision instructions:

{instructions}


Rewrite the research report.

Requirements:

1. Fix the issues identified by the critic.
2. Preserve supported factual claims.
3. Remove unsupported claims.
4. Correct citation problems.
5. Improve completeness where possible.
6. Improve coherence.
7. Use ONLY the supplied evidence.
8. Do not invent new evidence.
9. Keep evidence IDs and source URLs traceable.
"""

        result = self.synthesizer.synthesize(
            topic=topic,
            question=revision_prompt,
            evidence=evidence
        )

        return RevisionResult(
            revision_number=revision_number,
            completed=True,
            report=result.model_dump(),
            changes_made=instructions
        )