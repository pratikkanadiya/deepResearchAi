from datetime import datetime

from app.schemas.report import (
    FinalReport,
    ReportMetadata
)


class ReportGenerator:

    def generate(
        self,
        synthesis: dict,
        topic: str,
        revision_count: int = 0
    ) -> FinalReport:

        source_urls = []

        for section in synthesis.get(
            "sections",
            []
        ):

            for claim in section.get(
                "claims",
                []
            ):

                for url in claim.get(
                    "source_urls",
                    []
                ):

                    if url not in source_urls:
                        source_urls.append(url)

        metadata = ReportMetadata(
            title=synthesis.get(
                "title",
                topic
            ),
            topic=topic,
            generated_at=(
                datetime.utcnow()
                .isoformat()
            ),
            revision_count=revision_count
        )

        return FinalReport(
            metadata=metadata,
            executive_summary=synthesis.get(
                "executive_summary",
                ""
            ),
            sections=synthesis.get(
                "sections",
                []
            ),
            conclusion=synthesis.get(
                "conclusion",
                ""
            ),
            limitations=synthesis.get(
                "limitations",
                []
            ),
            sources=source_urls
        )