from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from app.schemas.report import FinalReport


class PDFReportGenerator:

    def generate(
        self,
        report: FinalReport,
        output_path
    ):

        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]

        body_style = styles["BodyText"]

        story = []

        story.append(
            Paragraph(
                escape(report.metadata.title),
                title_style
            )
        )

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                f"<b>Topic:</b> "
                f"{escape(report.metadata.topic)}",
                body_style
            )
        )

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "Executive Summary",
                heading_style
            )
        )

        story.append(
            Paragraph(
                escape(report.executive_summary),
                body_style
            )
        )

        for section in report.sections:

            story.append(
                Spacer(1, 15)
            )

            story.append(
                Paragraph(
                    escape(section.get(
                        "heading",
                        ""
                    )),
                    heading_style
                )
            )

            story.append(
                Paragraph(
                    escape(section.get(
                        "content",
                        ""
                    )),
                    body_style
                )
            )

            for claim in section.get(
                "claims",
                []
            ):

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        "<b>Claim:</b> "
                        + escape(claim.get(
                            "statement",
                            ""
                        )),
                        body_style
                    )
                )

                for url in claim.get(
                    "source_urls",
                    []
                ):

                    story.append(
                        Paragraph(
                            f"Source: {escape(url)}",
                            body_style
                        )
                    )

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "Conclusion",
                heading_style
            )
        )

        story.append(
            Paragraph(
                escape(report.conclusion),
                body_style
            )
        )

        document.build(story)
        if hasattr(output_path, "getvalue"):
            return output_path.getvalue()

