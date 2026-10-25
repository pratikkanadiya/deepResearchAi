from typing import Any, Dict, List
import os
import re


from app.agents.planner import create_research_plan
from app.agents.web_researcher import WebResearchAgent
from app.agents.academic_researcher import AcademicResearchAgent
from app.agents.news_researcher import NewsResearchAgent
from app.agents.source_preprocessor import SourcePreprocessor
from app.agents.source_batcher import SourceBatcher
from app.agents.source_evaluator import SourceEvaluatorAgent
from app.agents.document_reader_agent import DocumentReaderAgent
from app.agents.evidence_extractor import EvidenceExtractorAgent
from app.agents.research_synthesizer import ResearchSynthesizerAgent
from app.agents.citation_verifier import CitationVerifierAgent
from app.agents.critic import CriticAgent
from app.agents.revision_manager import RevisionManager


from app.rag.postgres_evidence_store import PostgresEvidenceStore
from app.rag.retriever import EvidenceRetriever


from app.reports.report_generator import ReportGenerator


class LazyComponent:

    def __init__(self, factory):
        self.factory = factory
        self.instance = None

    def __getattr__(self, name):
        if self.instance is None:
            self.instance = self.factory()
        return getattr(self.instance, name)


web_researcher = LazyComponent(WebResearchAgent)
academic_researcher = LazyComponent(AcademicResearchAgent)
news_researcher = LazyComponent(NewsResearchAgent)
source_preprocessor = SourcePreprocessor(max_content_chars=3000)
source_batcher = SourceBatcher(max_chars_per_batch=7000,
                                max_sources_per_batch=4,
                                max_tokens_per_batch=1800,)
source_evaluator = LazyComponent(SourceEvaluatorAgent)
document_reader = LazyComponent(DocumentReaderAgent)

evidence_extractor = LazyComponent(EvidenceExtractorAgent)

research_synthesizer = LazyComponent(ResearchSynthesizerAgent)
citation_verifier = LazyComponent(CitationVerifierAgent)
critic_agent = LazyComponent(CriticAgent)

revision_manager = LazyComponent(RevisionManager)

report_generator = LazyComponent(ReportGenerator)


postgres_evidence_store = LazyComponent(PostgresEvidenceStore)
evidence_retriever = EvidenceRetriever(evidence_store=postgres_evidence_store)


MAX_SEARCH_QUERIES = int(os.getenv("MAX_SEARCH_QUERIES", "3"))
MAX_RESULTS_PER_QUERY = int(os.getenv("MAX_RESULTS_PER_QUERY", "2"))
MAX_SOURCES_PER_PROVIDER = int(os.getenv("MAX_SOURCES_PER_PROVIDER", "5"))
MAX_SOURCES_FOR_EVALUATION = int(os.getenv("MAX_SOURCES_FOR_EVALUATION", "15"))
MAX_DOCUMENTS_FOR_EVIDENCE = int(os.getenv("MAX_DOCUMENTS_FOR_EVIDENCE", "3"))
MAX_DOCUMENT_CHARS_FOR_EVIDENCE = int(os.getenv("MAX_DOCUMENT_CHARS_FOR_EVIDENCE", "1000"))


def add_error(state: dict, message: str) -> List[str]:

    return [message]


def planner_node(state: dict) -> dict:

    print("\n==============================")
    print("PLANNER")
    print("==============================")

    topic = state.get("topic", "").strip()

    if not topic:
        return {
            "status": "failed",
            "errors": add_error(
                state,
                "Research topic is empty."
            )
        }

    try:

        result = create_research_plan(topic)

        print("Research plan created.")

        return {
            "objective": result.objective,
            "research_questions": result.research_questions,
            "subtopics": result.subtopics,
            "search_queries": result.search_queries[:MAX_SEARCH_QUERIES],
            "source_types": result.source_types,
            "status": "planned"
        }

    except Exception as exc:

        print(f"Planner error: {exc}")

        return {
            "status": "failed",
            "errors": add_error(
                state,
                f"Planner failed: {exc}"
            )
        }


def web_research_node(state: dict) -> dict:

    print("\n==============================")
    print("WEB RESEARCH")
    print("==============================")

    queries = state.get("search_queries", [])

    all_sources = []

    try:

        for query in queries:

            result = web_researcher.research(query, max_results=MAX_RESULTS_PER_QUERY)

            for source in result.sources:

                all_sources.append(
                    source.model_dump()
                )

        return {
            "web_sources": all_sources
        }

    except Exception as exc:

        print(f"Web research error: {exc}")

        return {
            "web_sources": all_sources,
            "errors": add_error(
                state,
                f"Web research failed: {exc}"
            )
        }


def academic_research_node(state: dict) -> dict:

    print("\n==============================")
    print("ACADEMIC RESEARCH")
    print("==============================")

    queries = state.get("search_queries", [])

    papers = []

    try:

        for query in queries:

            result = academic_researcher.research(query, max_results=MAX_RESULTS_PER_QUERY)

            for paper in result.papers:

                papers.append(
                    paper.model_dump()
                )

        print(f"Academic papers found: {len(papers)}")

        return {
            "academic_papers": papers
        }

    except Exception as exc:

        print(f"Academic research error: {exc}")

        return {
            "academic_papers": papers,
            "errors": add_error(
                state,
                f"Academic research failed: {exc}"
            )
        }


def news_research_node(state: dict) -> dict:

    print("\n==============================")
    print("NEWS RESEARCH")
    print("==============================")

    queries = state.get("search_queries", [])

    articles = []

    try:

        for query in queries:

            result = news_researcher.research(query, max_results=MAX_RESULTS_PER_QUERY)

            for article in result.articles:

                articles.append(
                    article.model_dump()
                )

        print(f"News articles found: {len(articles)}")

        return {
            "news_articles": articles
        }

    except Exception as exc:

        print(f"News research error: {exc}")

        return {
            "news_articles": articles,
            "errors": add_error(
                state,
                f"News research failed: {exc}"
            )
        }


def merge_sources_node(state: dict) -> dict:

    print("\n==============================")
    print("MERGING SOURCES")
    print("==============================")

    web_sources = state.get("web_sources", [])[:MAX_SOURCES_PER_PROVIDER]
    academic_papers = state.get("academic_papers", [])[:MAX_SOURCES_PER_PROVIDER]
    news_articles = state.get("news_articles", [])[:MAX_SOURCES_PER_PROVIDER]

    print(
        "Provider source caps: "
        f"web={len(web_sources)}, academic={len(academic_papers)}, "
        f"news={len(news_articles)} (max {MAX_SOURCES_PER_PROVIDER} each)."
    )

    sources = []

    sources.extend(web_sources)
    sources.extend(academic_papers)
    sources.extend(news_articles)

    if state.get("status") == "failed":
        return {
            "sources": [],
            "status": "failed",
        }


    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source.get("url")

        if not url:
            continue

        if url not in seen_urls:

            seen_urls.add(url)
            unique_sources.append(source)

    print(f"Total unique sources: {len(unique_sources)}")

    if not unique_sources:
        return {
            "sources": [],
            "status": "failed",
            "errors": add_error(
                state,
                "No research sources were returned by the configured search providers.",
            ),
        }

    return {
        "sources": unique_sources,
        "status": "sources_merged"
    }


def source_preprocessing_node(state: dict) -> dict:
    print("\n==============================")
    print("SOURCE PREPROCESSING")
    print("==============================")

    sources = state.get("sources", [])

    try:
        if not sources:
            print("No sources available for preprocessing.")
            return {"sources": []}

        processed_sources = source_preprocessor.process(sources)

        print(f"Original sources: {len(sources)}")
        print(f"Processed sources: {len(processed_sources)}")

        return {
            "sources": processed_sources,
        }
    except Exception as exc:
        print(f"Source preprocessing error: {exc}")

        return {
            "sources": [],
            "errors": add_error(
                state,
                f"Source preprocessing failed: {exc}",
            ),
        }


def source_relevance_filter_node(state: dict) -> dict:
    print("\n==============================")
    print("SOURCE RELEVANCE FILTER")
    print("==============================")

    sources = state.get("sources", [])
    if not sources:
        return {
            "sources": [],
            "status": "failed",
            "errors": add_error(state, "No sources were available for relevance filtering."),
        }

    stop_words = {
        "about", "after", "against", "among", "because", "before", "being",
        "between", "could", "does", "from", "have", "into", "more", "most",
        "other", "over", "should", "some", "such", "than", "that", "their",
        "there", "these", "they", "this", "through", "under", "using", "what",
        "when", "where", "which", "while", "with", "would", "your", "the",
        "and", "for", "are", "was", "were", "how", "why", "who", "all",
        "any", "can", "its", "our", "not", "use", "via", "of", "to",
        "in", "on", "it", "by", "be", "do", "as", "we", "or", "if",
        "an", "is", "at",
    }

    def terms(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-z0-9]+", (text or "").lower())
            if len(token) > 1 and token not in stop_words
        }

    intents = [state.get("topic", "")]
    for field in ("research_questions", "subtopics", "search_queries"):
        value = state.get(field, [])
        intents.extend(value if isinstance(value, list) else [str(value)])
    intent_terms = [terms(intent) for intent in intents]
    intent_terms = [item for item in intent_terms if item]

    ranked_sources = []
    for order, source in enumerate(sources):
        title = source.get("title") or ""
        content = source.get("evaluation_content") or source.get("content") or ""
        title_terms = terms(title)
        content_terms = terms(content)

        score = 0.0
        if intent_terms:
            for wanted in intent_terms:
                title_coverage = len(wanted & title_terms) / len(wanted)
                content_coverage = len(wanted & content_terms) / len(wanted)
                score = max(score, 0.65 * title_coverage + 0.35 * content_coverage)

        normalized_title = " ".join(re.findall(r"[a-z0-9]+", title.lower()))
        for intent in intents:
            phrase = " ".join(re.findall(r"[a-z0-9]+", (intent or "").lower()))
            if len(phrase) > 5 and phrase in normalized_title:
                score = max(score, 1.0)

        ranked = dict(source)
        ranked["prefilter_relevance"] = round(score, 4)
        ranked_sources.append((score, order, ranked))

    ranked_sources.sort(key=lambda item: (-item[0], item[1]))
    shortlist = [
        item[2]
        for item in ranked_sources[:max(1, MAX_SOURCES_FOR_EVALUATION)]
    ]

    print(
        f"Kept {len(shortlist)} of {len(sources)} sources for evaluator "
        f"(limit={MAX_SOURCES_FOR_EVALUATION}; "
        f"best relevance={shortlist[0]['prefilter_relevance'] if shortlist else 0})."
    )
    return {"sources": shortlist, "status": "sources_filtered"}


def source_batching_node(state: dict) -> dict:
    print("\n==============================")
    print("SOURCE BATCHING")
    print("==============================")

    sources = state.get("sources", [])

    try:
        if not sources:
            print("No sources available for batching.")
            return {"batches": []}

        batches = source_batcher.create_batches(sources)

        print(f"Total sources: {len(sources)}")
        print(f"Total batches: {len(batches)}")

        for index, batch in enumerate(batches, start=1):
            print(f"Batch {index}: {len(batch)} sources")

        return {
            "batches": batches,
        }

    except Exception as exc:
        print(f"Source batching error: {exc}")

        return {
            "batches": [],
            "errors": add_error(
                state,
                f"Source batching failed: {exc}",
            ),
        }


def source_evaluator_node(state: dict) -> dict:

    print("\n==============================")
    print("SOURCE EVALUATION")
    print("==============================")

    sources = state.get("sources", [])
    
    question = state.get(
            "research_questions",
            [state.get("topic", "")]
    )
    
    if isinstance(question, list):
    
        question_text = "\n".join(question)
    
    else:
    
        question_text = str(question)

    
    try:

        result = source_evaluator.evaluate(
            sources=sources,
            question=question_text
        )

        evaluations = [
            item.model_dump()
            for item in result.evaluations
        ]

        print(
            f"Sources evaluated: {len(evaluations)}"
        )

        return {
            "evaluated_sources": evaluations,
            "status": "sources_evaluated"
        }

    except Exception as exc:

        print(f"Source evaluation error: {exc}")

        return {
            "errors": add_error(
                state,
                f"Source evaluation failed: {exc}"
            )
        }


def document_reader_node(state: dict) -> dict:

    print("\n==============================")
    print("DOCUMENT READER")
    print("==============================")

    sources = sorted(
        state.get("evaluated_sources", []),
        key=lambda item: float(item.get("overall_score") or 0),
        reverse=True,
    )[:MAX_DOCUMENTS_FOR_EVIDENCE]

    if not sources:
        return {
            "documents": [],
            "status": "failed",
            "errors": add_error(state, "No sources were successfully evaluated; document reading cannot continue."),
        }

    urls = []

    for source in sources:

        url = source.get("url")

        if url:
            urls.append(url)

    urls = list(dict.fromkeys(urls))

    try:

        result = document_reader.read_documents(urls)

        documents = [
            item.model_dump()
            for item in result.documents
        ]

        documents_by_url = {item.get("url"): item for item in documents}
        source_by_url = {
            item.get("url"): item
            for item in state.get("sources", [])
            if item.get("url")
        }
        used_snippets = 0
        for url in urls:
            if url in documents_by_url:
                continue
            source = source_by_url.get(url, {})
            snippet = (source.get("content") or "").strip()
            if len(snippet) >= 100:
                fallback_document = {
                    "url": url,
                    "title": source.get("title") or "Search result abstract",
                    "content": snippet,
                    "content_length": len(snippet),
                    "status_code": 0,
                }
                documents.append(fallback_document)
                documents_by_url[url] = fallback_document
                used_snippets += 1

        print(
            f"Documents read: {len(documents)}"
        )

        if not documents:
            return {
                "documents": [],
                "status": "failed",
                "errors": add_error(state, "The document reader could not retrieve any full documents."),
            }

        if used_snippets:
            print(f"Used search-result abstracts/snippets for {used_snippets} blocked sources.")

        return {
            "documents": documents,
            "status": "documents_read",
            **({"errors": add_error(state, f"Used available search-result abstracts/snippets for {used_snippets} blocked sources.")} if used_snippets else {}),
        }

    except Exception as exc:

        print(f"Document reader error: {exc}")

        return {
            "documents": [],
            "errors": add_error(
                state,
                f"Document reader failed: {exc}"
            )
        }


def evidence_extractor_node(state: dict) -> dict:

    print("\n==============================")
    print("EVIDENCE EXTRACTION")
    print("==============================")

    if state.get("status") == "failed":
        return {
            "evidence": [],
            "status": "failed",
            "errors": add_error(state, "Evidence extraction stopped because an earlier workflow stage failed."),
        }

    documents = [
        {**document, "content": (document.get("content") or "")[:MAX_DOCUMENT_CHARS_FOR_EVIDENCE]}
        for document in state.get("documents", [])[:MAX_DOCUMENTS_FOR_EVIDENCE]
    ]

    question = state.get(
        "research_questions",
        [state.get("topic", "")]
    )

    if isinstance(question, list):

        question_text = "\n".join(question)

    else:

        question_text = str(question)

    try:

        result = evidence_extractor.extract(
            question=question_text,
            documents=documents
        )

        evidence = [
            item.model_dump()
            for item in result.evidence
        ]

        if not evidence:
            return {
                "evidence": [],
                "status": "failed",
                "errors": add_error(
                    state,
                    "No evidence could be extracted from the retrieved documents.",
                ),
            }

        print(
            f"Evidence extracted: {len(evidence)}"
        )

        return {
            "evidence": evidence,
            "status": "evidence_extracted"
        }

    except Exception as exc:

        excerpt_evidence = []
        for document in documents:
            url = str(document.get("url") or "").strip()
            excerpt = " ".join(str(document.get("content") or "").split())[:900]
            if not url or not excerpt:
                continue
            excerpt_evidence.append({
                "claim": excerpt,
                "supporting_text": excerpt,
                "source_url": url,
                "evidence_type": "source_excerpt_unreviewed",
                "confidence": 0.35,
                "limitations": [
                    "This is a source excerpt, not an LLM-extracted or independently verified claim.",
                ],
            })

        if excerpt_evidence:
            print(
                "Evidence extraction model unavailable; continuing with "
                f"{len(excerpt_evidence)} cited source excerpt(s)."
            )
            return {
                "evidence": excerpt_evidence,
                "status": "evidence_extracted_fallback",
                "errors": add_error(
                    state,
                    "Evidence extraction used cited source excerpts because structured extraction was unavailable.",
                ),
            }

        print("Evidence extraction failed and no source excerpts were available.")
        return {
            "evidence": [],
            "status": "failed",
            "errors": add_error(
                state,
                f"Evidence extraction failed; no source excerpts were available ({type(exc).__name__}).",
            ),
        }


def postgres_evidence_store_node(state: dict) -> dict:

    print("\n==============================")
    print("POSTGRESQL EVIDENCE STORE")
    print("==============================")

    evidence = state.get("evidence", [])

    if not evidence:

        return {
            "evidence_ids": [],
            "status": "evidence_store_skipped"
        }

    try:

        evidence_ids = postgres_evidence_store.add_evidence_batch(
            evidence,
            research_id=state.get("research_id", ""),
        )

        print(
            f"Stored evidence: {len(evidence_ids)}"
        )

        return {
            "evidence_ids": evidence_ids,
            "status": "evidence_stored"
        }

    except Exception as exc:

        print(f"PostgreSQL evidence store error: {exc}")

        return {
            "evidence_ids": [],
            "status": "failed",
            "errors": add_error(
                state,
                f"PostgreSQL evidence storage failed: {exc}"
            )
        }


def retrieval_node(state: dict) -> dict:

    print("\n==============================")
    print("EVIDENCE RETRIEVAL")
    print("==============================")

    topic = state.get("topic", "")

    questions = state.get(
        "research_questions",
        []
    )

    query = topic

    if questions:

        query += "\n" + "\n".join(questions)

    try:

        retrieved = evidence_retriever.retrieve(
            query=query,
            research_id=state.get("research_id", ""),
            limit=8
        )

        print(
            f"Retrieved evidence: {len(retrieved)}"
        )

        if not retrieved:
            evidence = state.get("evidence", [])[:8]
            if evidence:
                retrieved = [
                    {
                        "id": item.get("evidence_id") or f"evidence-{index + 1}",
                        "score": item.get("confidence", 0),
                        "payload": {
                            "claim": item.get("claim", ""),
                            "supporting_text": item.get("supporting_text", ""),
                            "source_url": item.get("source_url", ""),
                            "evidence_type": item.get("evidence_type", ""),
                            "confidence": item.get("confidence", 0),
                            "limitations": item.get("limitations", []),
                        },
                    }
                    for index, item in enumerate(evidence)
                ]
                print("PostgreSQL returned no matches; using this run's extracted evidence directly.")

        if not retrieved:
            return {
                "retrieved_evidence": [],
                "status": "failed",
                "errors": add_error(state, "PostgreSQL returned no evidence for this research run."),
            }

        return {
            "retrieved_evidence": retrieved,
            "status": "evidence_retrieved"
        }

    except Exception as exc:

        print(f"PostgreSQL evidence search error: {exc}")

        # Keep the current run usable if its database full-text query fails.
        evidence = state.get("evidence", [])[:8]
        if evidence:
            print("PostgreSQL search unavailable; using this run's extracted evidence directly.")
            return {
                "retrieved_evidence": [
                    {
                        "id": item.get("evidence_id") or f"evidence-{index + 1}",
                        "score": item.get("confidence", 0),
                        "payload": {
                            "claim": item.get("claim", ""),
                            "supporting_text": item.get("supporting_text", ""),
                            "source_url": item.get("source_url", ""),
                            "evidence_type": item.get("evidence_type", ""),
                            "confidence": item.get("confidence", 0),
                            "limitations": item.get("limitations", []),
                        },
                    }
                    for index, item in enumerate(evidence)
                ],
                "status": "evidence_retrieved",
                "errors": add_error(state, "PostgreSQL search unavailable; used this run's evidence directly."),
            }

        return {
            "retrieved_evidence": [],
            "status": "failed",
            "errors": add_error(state, f"Evidence retrieval failed: {exc}"),
        }
        

def synthesizer_node(state: dict) -> dict:

    print("\n==============================")
    print("RESEARCH SYNTHESIZER")
    print("==============================")

    topic = state.get("topic", "")

    questions = state.get(
        "research_questions",
        []
    )

    evidence = state.get(
        "retrieved_evidence",
        []
    )

    if not evidence:
        return {
            "status": "failed",
            "errors": add_error(state, "Synthesis stopped because no evidence was available."),
        }

    question = "\n".join(questions)

    try:

        result = research_synthesizer.synthesize(
            topic=topic,
            question=question,
            evidence=evidence
        )

        report = result.model_dump()

        print("Draft report created.")

        return {
            "draft_report": report,
            "status": "draft_created"
        }

    except Exception as exc:

        print(f"Synthesis error: {exc}")

        return {
            "errors": add_error(
                state,
                f"Synthesis failed: {exc}"
            ),
            "status": "failed",
        }


def citation_verifier_node(state: dict) -> dict:

    print("\n==============================")
    print("CITATION VERIFICATION")
    print("==============================")

    report = state.get(
        "draft_report",
        {}
    )

    if not report:
        return {
            "status": "failed",
            "errors": add_error(state, "Citation verification skipped because synthesis produced no report."),
        }

    evidence = state.get(
        "retrieved_evidence",
        []
    )

    question = state.get(
            "research_questions",
            [state.get("topic", "")]
        )
    
    if isinstance(question, list):
    
        question_text = "\n".join(question)
    
    else:
    
        question_text = str(question)
    
    try:

        result = citation_verifier.verify(
            report=report,
            evidence=evidence,
            question=question_text
        )

        verification = result.model_dump()

        print(
            f"Citations valid: "
            f"{verification.get('overall_valid')}"
        )

        return {
            "citation_verification": verification,
            "status": "citations_verified"
        }

    except Exception as exc:

        print(f"Citation verification error: {exc}")

        return {
            "errors": add_error(
                state,
                f"Citation verification failed: {exc}"
            ),
            "status": "failed",
        }


def critic_node(state: dict) -> dict:

    print("\n==============================")
    print("CRITIC")
    print("==============================")

    topic = state.get("topic", "")

    questions = state.get(
        "research_questions",
        []
    )

    report = state.get(
        "draft_report",
        {}
    )

    if not report:
        return {
            "status": "failed",
            "errors": add_error(state, "Critic skipped because synthesis produced no report."),
        }

    citation_verification = state.get(
        "citation_verification",
        {}
    )

    evidence = state.get(
        "retrieved_evidence",
        []
    )

    question = "\n".join(questions)

    try:

        result = critic_agent.evaluate(
            topic=topic,
            question=question,
            report=report,
            citation_verification=citation_verification,
            evidence=evidence
        )

        critic_result = result.model_dump()

        critic_result["previous_report"] = report

        print(
            f"Critic score: "
            f"{critic_result.get('overall_score')}"
        )

        print(
            f"Passed: "
            f"{critic_result.get('passed')}"
        )

        return {
            "critic_result": critic_result,
            "status": "critic_completed"
        }

    except Exception as exc:

        print(f"Critic error: {exc}")

        return {
            "errors": add_error(
                state,
                f"Critic failed: {exc}"
            ),

            "status": "critic_unavailable",
        }


def revision_node(state: dict) -> dict:

    print("\n==============================")
    print("REVISION")
    print("==============================")

    critic_result = state.get(
        "critic_result",
        {}
    )

    current_count = state.get(
        "revision_count",
        0
    )
    current_attempts = state.get(
        "revision_attempt_count",
        current_count,
    )
    max_revisions = state.get("max_revisions", 2)
    attempt_number = current_attempts + 1

    topic = state.get(
        "topic",
        ""
    )

    questions = state.get(
        "research_questions",
        []
    )

    evidence = state.get(
        "retrieved_evidence",
        []
    )

    previous_report = state.get(
        "draft_report",
        {}
    )

    if not previous_report:
        return {
            "status": "failed",
            "errors": add_error(state, "Cannot revise because no valid draft report exists."),
        }

    question = "\n".join(questions)

    try:

        result = revision_manager.revise(
            topic=topic,
            question=question,
            evidence=evidence,
            critic_result=critic_result,
            revision_count=current_count,
            previous_report=previous_report
        )

        new_count = current_count + 1

        print(
            f"Revision completed: {new_count}"
        )

        return {
            "draft_report": result.report,
            "revision_count": new_count,
            "revision_attempt_count": attempt_number,
            "status": "revised"
        }

    except Exception as exc:

        print(f"Revision error: {exc}")

        return {
            "revision_attempt_count": attempt_number,
            "status": "revision_failed",
            "errors": add_error(
                state,
                f"Revision attempt {attempt_number}/{max_revisions} failed: {exc}. The last valid draft is being kept."
            )
        }


def report_generator_node(state: dict) -> dict:

    print("\n==============================")
    print("REPORT GENERATOR")
    print("==============================")

    synthesis = state.get(
        "draft_report",
        {}
    )

    topic = state.get(
        "topic",
        ""
    )

    revision_count = state.get(
        "revision_count",
        0
    )

    try:

        final_report = report_generator.generate(
            synthesis=synthesis,
            topic=topic,
            revision_count=revision_count
        )

        report_dict = final_report.model_dump()

        print("Final report generated.")

        return {
            "final_report": report_dict,
            "status": "completed"
        }

    except Exception as exc:

        print(f"Report generation error: {exc}")

        return {
            "errors": add_error(
                state,
                f"Report generation failed: {exc}"
            ),
            "status": "failed"
        }


def critic_router(state: dict) -> str:

    if state.get("status") == "critic_unavailable":
        print("Critic unavailable; finalizing the last valid draft.")
        return "report"

    if state.get("status") == "failed":
        return "failed"

    critic_result = state.get(
        "critic_result",
        {}
    )

    passed = critic_result.get(
        "passed",
        False
    )

    revision_attempt_count = state.get(
        "revision_attempt_count",
        state.get("revision_count", 0),
    )

    max_revisions = state.get(
        "max_revisions",
        2
    )


    if passed:

        return "report"


    if revision_attempt_count >= max_revisions:

        return "report"


    return "revision"


def revision_router(state: dict) -> str:

    if state.get("status") == "failed":
        return "failed"

    if state.get("status") == "revision_failed":
        attempts = state.get("revision_attempt_count", 0)
        max_revisions = state.get("max_revisions", 2)
        if attempts >= max_revisions:
            print("Revision attempt limit reached; finalizing the last valid draft.")
            return "report"
        print("Revision failed; retrying with the same last valid draft.")
        return "retry"

    return "verify"


def source_router(state: dict) -> str:
    return "failed" if state.get("status") == "failed" else "continue"
