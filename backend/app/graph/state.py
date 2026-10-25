from typing import Annotated, Any, Dict, List, Optional
from operator import add

from typing_extensions import TypedDict


class ResearchGraphState(TypedDict, total=False):


    topic: str
    research_id: str
    objective: str


    research_questions: List[str]
    subtopics: List[str]
    search_queries: List[str]
    source_types: List[str]


    web_sources: List[Dict[str, Any]]
    academic_papers: List[Dict[str, Any]]
    news_articles: List[Dict[str, Any]]


    sources: List[Dict[str, Any]]
    batches: List[List[Dict[str, Any]]]


    evaluated_sources: List[Dict[str, Any]]


    documents: List[Dict[str, Any]]


    evidence: List[Dict[str, Any]]
    evidence_ids: List[str]


    retrieved_evidence: List[Dict[str, Any]]


    draft_report: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]


    citation_verification: Optional[Dict[str, Any]]


    critic_result: Optional[Dict[str, Any]]


    revision_count: int
    revision_attempt_count: int
    max_revisions: int


    status: str
    errors: Annotated[List[str], add]
