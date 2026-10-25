from typing import List

from pydantic import BaseModel


class ReportMetadata(BaseModel):

    title: str

    topic: str

    generated_at: str

    revision_count: int


class FinalReport(BaseModel):

    metadata: ReportMetadata

    executive_summary: str

    sections: List[dict]

    conclusion: str

    limitations: List[str]

    sources: List[str]