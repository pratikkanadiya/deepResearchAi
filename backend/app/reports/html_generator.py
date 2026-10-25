from html import escape
from urllib.parse import urlparse

from app.schemas.report import FinalReport


class HTMLReportGenerator:

    @staticmethod
    def _safe_url(value: str) -> str | None:
        parsed = urlparse(value)
        return value if parsed.scheme in {"http", "https"} and parsed.netloc else None

    def generate(
        self,
        report: FinalReport
    ) -> str:

        sections = []

        for section in report.sections:

            claims = []

            for claim in section.get(
                "claims",
                []
            ):

                sources = []

                for url in claim.get(
                    "source_urls",
                    []
                ):

                    safe_url = self._safe_url(url)
                    if not safe_url:
                        continue

                    safe_url = escape(safe_url, quote=True)

                    sources.append(
                        f'<li><a href="{safe_url}" '
                        f'target="_blank">'
                        f'{safe_url}</a></li>'
                    )

                claims.append(
                    f"""
                    <div>
                        <p>
                            <strong>Claim:</strong>
                            {escape(
                                claim.get(
                                    "statement",
                                    ""
                                )
                            )}
                        </p>

                        <ul>
                            {''.join(sources)}
                        </ul>
                    </div>
                    """
                )

            sections.append(
                f"""
                <section>
                    <h2>
                        {escape(
                            section.get(
                                "heading",
                                ""
                            )
                        )}
                    </h2>

                    <p>
                        {escape(
                            section.get(
                                "content",
                                ""
                            )
                        )}
                    </p>

                    {''.join(claims)}
                </section>
                """
            )

        limitations = "".join(
            f"<li>{escape(item)}</li>"
            for item in report.limitations
        )

        sources = "".join(
            f'<li><a href="{escape(self._safe_url(url), quote=True)}">'
            f'{escape(url)}</a></li>'
            for url in report.sources
            if self._safe_url(url)
        )

        return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
{escape(report.metadata.title)}
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
    line-height: 1.6;
}}

h1 {{
    margin-bottom: 5px;
}}

section {{
    margin-top: 30px;
}}

</style>

</head>

<body>

<h1>
{escape(report.metadata.title)}
</h1>

<p>
<strong>Topic:</strong>
{escape(report.metadata.topic)}
</p>

<h2>
Executive Summary
</h2>

<p>
{escape(report.executive_summary)}
</p>

{''.join(sections)}

<h2>
Conclusion
</h2>

<p>
{escape(report.conclusion)}
</p>

<h2>
Limitations
</h2>

<ul>
{limitations}
</ul>

<h2>
Sources
</h2>

<ul>
{sources}
</ul>

</body>

</html>
"""
