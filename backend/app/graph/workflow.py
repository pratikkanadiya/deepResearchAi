from langgraph.graph import StateGraph, START, END
import uuid

from app.graph.state import ResearchGraphState

from app.graph.nodes import (
    planner_node,
    web_research_node,
    academic_research_node,
    news_research_node,

    merge_sources_node,

    source_preprocessing_node,
    source_relevance_filter_node,
    source_batching_node,
    source_evaluator_node,
    document_reader_node,

    evidence_extractor_node,
    postgres_evidence_store_node,
    retrieval_node,

    synthesizer_node,
    citation_verifier_node,
    critic_node,

    revision_node,
    report_generator_node,

    critic_router,
    revision_router,
    source_router,
)


def build_research_graph():

    graph = StateGraph(ResearchGraphState)

    graph.add_node(
        "planner",
        planner_node
    )

    graph.add_node(
        "web_research",
        web_research_node
    )

    graph.add_node(
        "academic_research",
        academic_research_node
    )

    graph.add_node(
        "news_research",
        news_research_node
    )

    graph.add_node(
        "merge_sources",
        merge_sources_node
    )
    
    graph.add_node(
        "source_preprocessing",
        source_preprocessing_node,
    )

    graph.add_node(
        "source_relevance_filter",
        source_relevance_filter_node,
    )

    graph.add_node(
        "source_batching",
        source_batching_node,
    )
    
    graph.add_node(
        "source_evaluator",
        source_evaluator_node
    )

    graph.add_node(
        "document_reader",
        document_reader_node
    )

    graph.add_node(
        "evidence_extractor",
        evidence_extractor_node
    )

    graph.add_node(
        "postgres_evidence_store",
        postgres_evidence_store_node
    )

    graph.add_node(
        "retrieval",
        retrieval_node
    )

    graph.add_node(
        "synthesizer",
        synthesizer_node
    )

    graph.add_node(
        "citation_verifier",
        citation_verifier_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    graph.add_node(
        "revision",
        revision_node
    )

    graph.add_node(
        "report_generator",
        report_generator_node
    )

    graph.add_edge(
        START,
        "planner"
    )

    graph.add_edge(
        "planner",
        "web_research"
    )

    graph.add_edge(
        "planner",
        "academic_research"
    )

    graph.add_edge(
        "planner",
        "news_research"
    )

    graph.add_edge(
        "web_research",
        "merge_sources"
    )

    graph.add_edge(
        "academic_research",
        "merge_sources"
    )

    graph.add_edge(
        "news_research",
        "merge_sources"
    )

    graph.add_conditional_edges(
        "merge_sources",
        source_router,
        {
            "continue": "source_preprocessing",
            "failed": END,
        }
    )
    
    graph.add_edge("source_preprocessing", "source_relevance_filter")

    graph.add_conditional_edges(
        "source_relevance_filter",
        source_router,
        {
            "continue": "source_batching",
            "failed": END,
        },
    )
    
    graph.add_edge(
        "source_batching", 
        "source_evaluator"
    )

    graph.add_edge(
        "source_evaluator",
        "document_reader"
    )

    graph.add_edge(
        "document_reader",
        "evidence_extractor"
    )

    graph.add_conditional_edges(
        "evidence_extractor",
        source_router,
        {
            "continue": "postgres_evidence_store",
            "failed": END,
        }
    )

    graph.add_edge(
        "postgres_evidence_store",
        "retrieval"
    )

    graph.add_edge(
        "retrieval",
        "synthesizer"
    )

    graph.add_conditional_edges(
        "synthesizer",
        source_router,
        {"continue": "citation_verifier", "failed": END},
    )

    graph.add_conditional_edges(
        "citation_verifier",
        source_router,
        {"continue": "critic", "failed": END},
    )

    graph.add_conditional_edges(
        "critic",
        critic_router,
        {
            "revision": "revision",
            "report": "report_generator",
            "failed": END,
        }
    )
    
    graph.add_conditional_edges(
        "revision",
        revision_router,
        {
            "retry": "revision",
            "verify": "citation_verifier",
            "report": "report_generator",
            "failed": END,
        },
    )

    graph.add_edge(
        "report_generator",
        END
    )

    return graph.compile()

research_graph = build_research_graph()

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("DEEPRESEARCH-AI LANGGRAPH WORKFLOW")
    print("=" * 70)

    topic = input(
        "\nEnter research topic: "
    ).strip()

    if not topic:

        print("Topic cannot be empty.")

        raise SystemExit(1)

    initial_state: ResearchGraphState = {

        "research_id": str(uuid.uuid4()),

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

        "max_revisions": 2,

        "status": "initialized",

        "errors": [],
    }

    print("\nStarting research workflow...\n")

    result = research_graph.invoke(
        initial_state
    )

    print("\n")
    print("=" * 70)
    print("RESEARCH COMPLETE")
    print("=" * 70)

    print(
        "\nStatus:",
        result.get("status")
    )

    print(
        "Revision count:",
        result.get("revision_count")
    )

    print(
        "Sources:",
        len(result.get("sources", []))
    )

    print(
        "Evidence:",
        len(result.get("evidence", []))
    )

    print(
        "Errors:",
        len(result.get("errors", []))
    )

    if result.get("errors"):

        print("\nErrors:")

        for error in result["errors"]:

            print(
                "-",
                error
            )

    if result.get("final_report"):

        print("\nFinal report created.")

        print(
            result["final_report"].get(
                "metadata",
                {}
            )
        )
