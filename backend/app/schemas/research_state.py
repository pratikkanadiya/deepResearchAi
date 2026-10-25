from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchState(BaseModel):

    topic: str = ""

    objective: str = ""

    research_questions: List[str] = Field(
        default_factory=list
    )

    subtopics: List[str] = Field(
        default_factory=list
    )

    search_queries: List[str] = Field(
        default_factory=list
    )

    sources: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    evaluated_sources: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    documents: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    evidence: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    retrieved_evidence: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    draft_report: Optional[Dict[str, Any]] = None

    citation_verification: Optional[
        Dict[str, Any]
    ] = None

    critic_result: Optional[
        Dict[str, Any]
    ] = None

    revision_count: int = 0

    revision_attempt_count: int = 0

    max_revisions: int = 2

    final_report: Optional[
        Dict[str, Any]
    ] = None

    status: str = "initialized"

    errors: List[str] = Field(
        default_factory=list
    )
