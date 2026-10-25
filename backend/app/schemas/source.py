from typing import List

from pydantic import BaseModel, Field


class SourceEvaluation(BaseModel):

    url: str

    title: str = ""

    source_type: str = ""

    authority_score: float = Field(
        ge=0,
        le=10,
    )

    relevance_score: float = Field(
        ge=0,
        le=10,
    )

    recency_score: float = Field(
        ge=0,
        le=10,
    )

    specificity_score: float = Field(
        ge=0,
        le=10,
    )

    overall_score: float = Field(
        ge=0,
        le=10,
    )

    strengths: List[str] = Field(
        default_factory=list
    )

    weaknesses: List[str] = Field(
        default_factory=list
    )

    recommendation: str = ""


class SourceEvaluationResult(BaseModel):

    evaluations: List[SourceEvaluation] = Field(
        default_factory=list
    )
