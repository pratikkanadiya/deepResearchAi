from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=3,
        description="Research topic"
    )

    max_revisions: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum number of report revisions"
    )


class ResearchResponse(BaseModel):

    research_id: str

    status: str

    topic: str

    revision_count: int

    sources_count: int

    evidence_count: int

    sources: List[Dict[str, Any]] = Field(default_factory=list)

    report: Optional[Dict[str, Any]] = None

    errors: List[str] = Field(
        default_factory=list
    )


class HealthResponse(BaseModel):

    status: str

    service: str

    version: str
