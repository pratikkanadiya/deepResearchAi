from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.api import (
    ResearchRequest,
    ResearchResponse,
    HealthResponse
)

from app.graph.workflow import research_graph

from app.services.research_service import ResearchService
from app.database.repository import ResearchRepository
from app.api.history import router as history_router
from app.api.reports import router as reports_router

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.connection import (
    get_db,
    create_tables
)

from app.services.research_service import (
    ResearchService
)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables()

    yield


app = FastAPI(
    title="DeepResearch-AI API",
    description="Multi-agent research platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(history_router)
app.include_router(reports_router)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


@app.get("/")
def root():

    return {
        "project": "DeepResearch-AI",
        "status": "running",
        "message": "DeepResearch-AI API is running"
    }


@app.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return HealthResponse(
        status="healthy",
        service="DeepResearch-AI API",
        version="1.0.0"
    )


@app.post(
    "/research",
    response_model=ResearchResponse
)
def research(
    request: ResearchRequest,
    db: Session = Depends(get_db)
):

    try:

        service = ResearchService(db)

        result = service.run_research(
            topic=request.topic,
            max_revisions=request.max_revisions
        )


        if result.get("status") == "failed":

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Research workflow failed.",
                    "errors": result.get(
                        "errors",
                        []
                    )
                }
            )


        return ResearchResponse(
            research_id=result.get("research_id", ""),
            status=result.get(
                "status",
                "completed"
            ),

            topic=result.get(
                "topic",
                request.topic
            ),

            revision_count=result.get(
                "revision_count",
                0
            ),

            sources_count=len(
                result.get(
                    "sources",
                    []
                )
            ),

            evidence_count=len(
                result.get(
                    "evidence",
                    []
                )
            ),

            sources=result.get("sources", []),

            report=result.get(
                "final_report"
            ),

            errors=result.get(
                "errors",
                []
            )
        )

    except HTTPException:

        raise

    except Exception as exc:

        print(
            f"Research API error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unexpected research error.",
                "errors": [str(exc)],
                "error": str(exc)
            }
        )
        
@app.get("/research/architecture")
def research_architecture():

    return {
        "workflow": [
            {"stage": "Research Planner", "node": "planner"},
            {"stage": "Research Questions and search plan", "node": "planner"},
            {
                "stage": "Parallel Researchers",
                "nodes": ["web_research", "academic_research", "news_research"],
            },
            {"stage": "Raw Sources", "node": "merge_sources"},
            {
                "stage": "Source preparation and quality assessment",
                "nodes": ["source_preprocessing", "source_relevance_filter", "source_batching", "source_evaluator"],
            },
            {"stage": "Full document reading", "node": "document_reader"},
            {"stage": "Structured evidence extraction", "node": "evidence_extractor"},
            {"stage": "PostgreSQL evidence storage and retrieval", "nodes": ["postgres_evidence_store", "retrieval"]},
            {"stage": "Synthesis and citation verification", "nodes": ["synthesizer", "citation_verifier"]},
            {"stage": "Critique and bounded revision", "nodes": ["critic", "revision"]},
            {"stage": "Final report", "node": "report_generator"},
        ],
        "parallel_nodes": ["web_research", "academic_research", "news_research"],
    }
    
@app.get(
    "/research/{research_id}"
)
def get_research(
    research_id: str,
    db: Session = Depends(get_db)
):

    repository = ResearchRepository(db)

    research = repository.get_research(
        research_id
    )

    if not research:

        raise HTTPException(
            status_code=404,
            detail="Research not found"
        )

    return {
        "research_id": research.id,
        "topic": research.topic,
        "objective": research.objective,
        "status": research.status,
        "revision_count": research.revision_count,
        "max_revisions": research.max_revisions,
        "created_at": research.created_at,
        "updated_at": research.updated_at,
        "sources_count": len(
            research.sources
        ),
        "evidence_count": len(
            research.evidence
        ),
        "reports_count": len(
            research.reports
        ),
        "errors": research.errors
    }
