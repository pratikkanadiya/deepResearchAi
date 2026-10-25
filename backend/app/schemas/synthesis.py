from typing import List

from pydantic import BaseModel, Field


class ReportClaim(BaseModel):

    statement: str

    evidence_ids: List[str]

    source_urls: List[str]


class ResearchSection(BaseModel):

    heading: str

    content: str

    claims: List[ReportClaim]


class ResearchSynthesis(BaseModel):

    title: str

    executive_summary: str

    sections: List[ResearchSection]

    conclusion: str

    limitations: List[str]