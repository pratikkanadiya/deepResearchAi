from typing import List

from pydantic import BaseModel


class CitationCheck(BaseModel):

    claim: str

    evidence_ids: List[str]

    source_urls: List[str]

    supported: bool

    support_score: float

    explanation: str


class CitationVerificationResult(BaseModel):

    overall_valid: bool

    checks: List[CitationCheck]

    unsupported_claims: List[str]

    missing_citations: List[str]

    recommendations: List[str]