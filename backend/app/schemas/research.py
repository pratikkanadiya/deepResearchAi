from typing import TypedDict

class ResearchState(TypedDict):

    topic: str

    research_plan: list

    search_results: list

    documents: list

    evidence: list

    report: str

    citations: list

    critique: dict

    revision_count: int