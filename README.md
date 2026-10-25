# DeepResearch AI

DeepResearch AI is a full-stack research assistant. A user submits a topic through the React dashboard; a FastAPI and LangGraph backend plans the research, searches web, academic, and news sources, evaluates a shortlist, reads accessible documents, extracts cited evidence, stores and retrieves that evidence in PostgreSQL, and generates a report with citation checks and a bounded critique/revision loop. The frontend presents the returned summary, findings, sources, report status, and a Markdown download. The design emphasizes evidence traceability, controlled model usage, and useful fallbacks when external providers or documents are unavailable.

## Project structure

```text
DeepResearch-AI/
├── backend/
│   ├── app/
│   │   ├── agents/          # Planner, researchers, evaluator, reader, evidence and review agents
│   │   ├── api/             # History and report routes
│   │   ├── database/        # PostgreSQL connection, SQLAlchemy models, repository
│   │   ├── graph/           # LangGraph state, nodes, and workflow
│   │   ├── observability/   # Optional LangSmith tracing
│   │   ├── rag/             # PostgreSQL evidence storage and retrieval
│   │   ├── reports/         # Final report and export formatters
│   │   ├── schemas/         # Pydantic API, evidence, state, and report models
│   │   ├── services/        # LLM client and research orchestration
│   │   ├── tools/           # Web, academic, news, and document access
│   │   └── main.py          # FastAPI application
│   ├── .env.example         # Backend environment template
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/              # Public static assets
│   ├── src/
│   │   ├── assets/          # Images and bundled assets
│   │   ├── components/      # Reusable dashboard components
│   │   ├── services/api.js  # Axios API client
│   │   ├── App.jsx          # Dashboard and research request state
│   │   ├── App.css          # Dashboard and responsive styles
│   │   └── main.jsx         # React entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Local PostgreSQL, API, and frontend services
└── README.md
```

## End-to-end workflow

```text
Topic → planning → parallel web/academic/news search → merge and deduplicate
→ relevance filtering → source evaluation → document reading
→ structured evidence → PostgreSQL storage and retrieval
→ report synthesis → citation verification → critique/revisions → final report
```

### Backend stages

1. **Planner** creates research questions and targeted queries.
2. **Web, academic, and news researchers** use Tavily, Semantic Scholar, and GNews in parallel.
3. **Merge and preparation** deduplicate URLs, normalize sources, and rank relevance.
4. **Source evaluator** reviews the strongest candidates in small batches.
5. **Document reader** retrieves accessible web pages and text PDFs; it can use abstracts/snippets when a publisher blocks full text.
6. **Evidence extractor** records claims with supporting text, URLs, confidence, evidence type, and limitations.
7. **PostgreSQL store/retriever** persists evidence and retrieves it for the current research ID only.
8. **Synthesizer and citation verifier** create a report and check its claims against evidence.
9. **Critic and revision manager** review quality and allow a bounded number of revisions.
10. **Report generator** returns the final report and supports Markdown, HTML, and PDF exports through the API.

### Frontend features

- Topic input and revision-count selection.
- Loading and error states while the backend runs.
- Research summary, key findings, source links, evidence highlights, report status, and coverage signals.
- Browser-generated Markdown download.
- Responsive dashboard layout.

The dashboard currently submits a synchronous research request. Its workflow illustration is not live per-agent progress, and the dashboard does not yet include a full run-history browser or buttons for the backend's HTML/PDF exports.

## Technology stack

| Layer                           | Technology                                          |
|---------------------------------|-----------------------------------------------------|
| User interface                  | React 19, Vite 8, Axios, CSS                        |
| API                             | Python 3.11+, FastAPI, Pydantic                     |
| Agent orchestration             | LangGraph and LangChain                             |
| Language model                  | Groq chat model configured by `GROQ_MODEL`          |
| Search providers                | Tavily, Semantic Scholar, GNews                     |
| Persistence and evidence search | PostgreSQL, SQLAlchemy, PostgreSQL full-text search |
| Local containers                | Docker Compose                                      |

**Database note:** the active evidence path uses PostgreSQL full-text search. It does not require a Qdrant server or the `pgvector` extension.

## Search and quota strategy

The current Desktop backend configuration aims to keep free-tier requests manageable:

| Limit                                  | Setting  |
|----------------------------------------|----------|
| Planner queries                        | 3        |
| Results per provider query             | 2        |
| Candidate sources per provider         | Up to 5  |
| Sources sent to evaluation             | Up to 15 |
| Documents sent to evidence extraction  | Up to 3  |
| Characters per document for extraction | 1,000    |
| Default report revisions               | 2        |

The limits reduce prompt size and provider calls but cannot guarantee that an external API never rate-limits a request. Transient model limits are retried where supported; fallbacks can preserve cited snippets or the last valid report when a model stage remains unavailable. Fallback evidence is labeled as lower confidence and should not be presented as independently verified extraction.

## Requirements and keys

- Python 3.11 or newer
- Node.js and npm
- PostgreSQL (or Docker Compose)
- Groq API key: `GROQ_API_KEY`
- Tavily API key: `TAVILY_API_KEY`
- GNews API key: `GNEWS_API_KEY`
- Optional Semantic Scholar key: `SEMANTIC_SCHOLAR_API_KEY`

Keep credentials in environment files on the backend or in the root Compose `.env`. Never put provider keys in frontend variables or commit `.env` files.

## Further documentation

- [Backend README](backend/README.md) — backend modules, agents, endpoints, configuration, and local setup.
- [Frontend README](frontend/README.md) — dashboard features, API client, environment configuration, and frontend scripts.