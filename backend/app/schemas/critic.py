from typing import List

from pydantic import BaseModel, Field


class CriticIssue(BaseModel):

    category: str

    severity: str

    description: str

    affected_claim: str = ""


class CriticResult(BaseModel):

    overall_score: float = Field(
        ge=0,
        le=10
    )

    passed: bool

    factual_accuracy: float = Field(
        ge=0,
        le=10
    )

    evidence_quality: float = Field(
        ge=0,
        le=10
    )

    citation_quality: float = Field(
        ge=0,
        le=10
    )

    completeness: float = Field(
        ge=0,
        le=10
    )

    coherence: float = Field(
        ge=0,
        le=10
    )

    issues: List[CriticIssue] = Field(
        default_factory=list
    )

    revision_instructions: List[str] = Field(
        default_factory=list
    )

    strengths: List[str] = Field(
        default_factory=list
    )