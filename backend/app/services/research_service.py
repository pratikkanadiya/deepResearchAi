from typing import Any, Dict

from sqlalchemy.orm import Session

from app.graph.workflow import research_graph
from app.database.repository import ResearchRepository

from langsmith import traceable


class ResearchService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = ResearchRepository(
            db
        )
    
    @traceable(
        name="DeepResearch Pipeline",
        run_type="chain"
    )
    def run_research(
        self,
        topic: str,
        max_revisions: int = 2
    ) -> Dict[str, Any]:


        research = self.repository.create_research(
            topic=topic,
            max_revisions=max_revisions
        )

        research_id = research.id


        initial_state = {

            "research_id": research_id,

            "topic": topic,

            "objective": "",

            "research_questions": [],

            "subtopics": [],

            "search_queries": [],

            "source_types": [],

            "web_sources": [],

            "academic_papers": [],

            "news_articles": [],

            "sources": [],

            "evaluated_sources": [],

            "documents": [],

            "evidence": [],

            "evidence_ids": [],

            "retrieved_evidence": [],

            "draft_report": None,

            "final_report": None,

            "citation_verification": None,

            "critic_result": None,

            "revision_count": 0,

            "revision_attempt_count": 0,

            "max_revisions": max_revisions,

            "status": "initialized",

            "errors": [],
        }


        try:

            result = research_graph.invoke(
                initial_state
            )


            self.repository.save_sources(
                research_id,
                result.get(
                    "sources",
                    []
                )
            )


            critic_result = result.get(
                "critic_result"
            )

            if critic_result:

                revision_count = result.get(
                    "revision_count",
                    0
                )

                self.repository.save_revision(
                    research_id,
                    revision_count,
                    critic_result
                )


            final_report = result.get(
                "final_report"
            )

            if final_report:

                self.repository.save_report(
                    research_id,
                    final_report,
                    result.get(
                        "revision_count",
                        0
                    )
                )


            self.repository.update_research(

                research_id,

                status=result.get(
                    "status",
                    "completed"
                ),

                revision_count=result.get(
                    "revision_count",
                    0
                ),

                errors=result.get(
                    "errors",
                    []
                )
            )


            result["research_id"] = research_id

            return result

        except Exception as exc:

            self.repository.update_research(

                research_id,

                status="failed",

                errors=[
                    str(exc)
                ]
            )

            raise
