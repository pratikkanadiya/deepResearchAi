from typing import List

from pydantic import BaseModel


class RevisionRequest(BaseModel):

    revision_number: int

    instructions: List[str]

    issues: List[str]

    previous_score: float


class RevisionResult(BaseModel):

    revision_number: int

    completed: bool

    report: dict

    changes_made: List[str]