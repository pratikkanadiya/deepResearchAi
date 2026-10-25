from typing import List
from pydantic import BaseModel


class Evidence(BaseModel):

    claim: str

    supporting_text: str

    source_url: str

    evidence_type: str

    confidence: float

    limitations: List[str]


class EvidenceExtractionResult(BaseModel):

    question: str

    evidence: List[Evidence]