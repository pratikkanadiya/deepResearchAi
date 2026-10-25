from app.schemas.report import FinalReport


class MarkdownReportGenerator:

    def generate(
        self,
        report: FinalReport
    ) -> str:

        output = []

        output.append(
            f"# {report.metadata.title}"
        )

        output.append("")

        output.append(
            f"**Topic:** {report.metadata.topic}"
        )

        output.append(
            f"**Generated:** "
            f"{report.metadata.generated_at}"
        )

        output.append("")

        output.append(
            "## Executive Summary"
        )

        output.append(
            report.executive_summary
        )

        output.append("")

        for section in report.sections:

            output.append(
                f"## {section.get('heading', '')}"
            )

            output.append(
                section.get("content", "")
            )

            output.append("")

            for claim in section.get(
                "claims",
                []
            ):

                output.append(
                    f"**Claim:** "
                    f"{claim.get('statement', '')}"
                )

                for url in claim.get(
                    "source_urls",
                    []
                ):

                    output.append(
                        f"- Source: {url}"
                    )

                output.append("")

        output.append(
            "## Conclusion"
        )

        output.append(
            report.conclusion
        )

        output.append("")

        output.append(
            "## Limitations"
        )

        for limitation in report.limitations:

            output.append(
                f"- {limitation}"
            )

        output.append("")

        output.append(
            "## Sources"
        )

        for source in report.sources:

            output.append(
                f"- {source}"
            )

        return "\n".join(output)