from sqlalchemy.orm import Session

from app.database.models import (
    Research,
    Source,
    Evidence,
    Report,
    Revision,
)


class ResearchRepository:

    def __init__(self, db: Session):

        self.db = db


    def create_research(
        self,
        topic: str,
        objective: str = "",
        max_revisions: int = 2
    ):

        research = Research(
            topic=topic,
            objective=objective,
            max_revisions=max_revisions,
            status="initialized"
        )

        self.db.add(research)
        self.db.commit()
        self.db.refresh(research)

        return research


    def update_research(
        self,
        research_id: str,
        **kwargs
    ):

        research = self.db.get(
            Research,
            research_id
        )

        if not research:
            return None

        for key, value in kwargs.items():

            if hasattr(research, key):
                setattr(
                    research,
                    key,
                    value
                )

        self.db.commit()
        self.db.refresh(research)

        return research


    def save_sources(
        self,
        research_id: str,
        sources: list[dict]
    ):

        for item in sources:

            source = Source(
                research_id=research_id,
                title=item.get("title"),
                url=item.get("url", ""),
                source_type=item.get(
                    "source_type"
                ),
                score=item.get("score"),
                metadata_json=item
            )

            self.db.add(source)

        self.db.commit()


    def save_evidence(
        self,
        research_id: str,
        evidence_items: list[dict]
    ):

        for item in evidence_items:

            evidence = Evidence(
                research_id=research_id,
                claim=item.get(
                    "claim",
                    ""
                ),
                supporting_text=item.get(
                    "supporting_text",
                    ""
                ),
                source_url=item.get(
                    "source_url"
                ),
                evidence_type=item.get(
                    "evidence_type"
                ),
                confidence=item.get(
                    "confidence"
                ),
                limitations=item.get(
                    "limitations",
                    []
                )
            )

            self.db.add(evidence)

        self.db.commit()


    def save_report(
        self,
        research_id: str,
        report: dict,
        revision_count: int
    ):

        metadata = report.get(
            "metadata",
            {}
        )

        saved_report = Report(

            research_id=research_id,

            title=metadata.get(
                "title",
                "Research Report"
            ),

            report_data=report,

            revision_count=revision_count
        )

        self.db.add(saved_report)

        self.db.commit()

        self.db.refresh(saved_report)

        return saved_report


    def save_revision(
        self,
        research_id: str,
        revision_number: int,
        critic_result: dict
    ):

        revision = Revision(

            research_id=research_id,

            revision_number=revision_number,

            score=critic_result.get(
                "overall_score"
            ),

            passed=critic_result.get(
                "passed",
                False
            ),

            critic_data=critic_result,

            changes=critic_result.get(
                "revision_instructions",
                []
            )
        )

        self.db.add(revision)

        self.db.commit()


    def get_research(
        self,
        research_id: str
    ):

        return self.db.get(
            Research,
            research_id
        )

    def list_researches(self, limit: int = 20):
        return (
            self.db.query(Research)
            .order_by(Research.created_at.desc())
            .limit(limit)
            .all()
        )
