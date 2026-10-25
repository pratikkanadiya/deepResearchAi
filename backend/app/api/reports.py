from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repository import ResearchRepository
from app.reports.html_generator import HTMLReportGenerator
from app.reports.markdown_generator import MarkdownReportGenerator
from app.reports.pdf_generator import PDFReportGenerator
from app.schemas.report import FinalReport

router = APIRouter(tags=["reports"])


def _latest_report(research_id: str, db: Session) -> FinalReport:
    research = ResearchRepository(db).get_research(research_id)
    if research is None:
        raise HTTPException(status_code=404, detail="Research not found")
    if not research.reports:
        raise HTTPException(status_code=404, detail="No report is available for this research")
    latest = max(research.reports, key=lambda item: item.created_at)
    return FinalReport.model_validate(latest.report_data)


@router.get("/research/{research_id}/report")
def get_report(research_id: str, db: Session = Depends(get_db)):
    return _latest_report(research_id, db).model_dump(mode="json")


@router.get("/research/{research_id}/report/{format}")
def export_report(
    research_id: str,
    format: str,
    db: Session = Depends(get_db),
):
    report = _latest_report(research_id, db)
    filename = f"research-{research_id}"

    if format == "markdown":
        content = MarkdownReportGenerator().generate(report)
        return Response(
            content=content,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"'},
        )
    if format == "html":
        content = HTMLReportGenerator().generate(report)
        return Response(
            content=content,
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}.html"'},
        )
    if format == "pdf":
        output = BytesIO()
        PDFReportGenerator().generate(report, output)
        return Response(
            content=output.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported report format. Choose markdown, html, or pdf.",
    )
