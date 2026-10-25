# DeepResearch AI Backend

The DeepResearch AI backend is a Python API that turns a research topic into a source-backed report. It plans research questions, searches web, academic, and news providers, filters and evaluates sources, reads accessible documents, extracts cited evidence, stores and retrieves evidence in PostgreSQL, and produces a report with citation checks and a bounded review/revision loop. It is designed to preserve useful results when a provider is rate-limited or blocks document access, while labeling fallback evidence so it is not mistaken for verified analysis.

## Project structure

```text
backend/
├── app/
│   ├── agents/          # Planner, search, evaluation, reading, evidence, report agents
│   ├── api/             # History and report route modules
│   ├── database/        # SQLAlchemy connection, tables, and repository
│   ├── graph/           # LangGraph workflow, state, and node implementations
│   ├── observability/   # Optional LangSmith tracing setup
│   ├── rag/              # PostgreSQL evidence store and retrieval
│   ├── reports/          # Report formatting and Markdown/HTML/PDF exports
│   ├── schemas/          # Pydantic request, state, evidence, and report models
│   ├── services/         # LLM configuration and research-run orchestration
│   ├── tools/             # Tavily, Semantic Scholar, GNews, and document readers
│   └── main.py            # FastAPI application and primary routes
├── .env.example           # Environment variable template
├── Dockerfile             # Container build configuration
└── requirements.txt       # Python dependencies
```

## Backend functionalities

### 1. Multi-agent research workflow

LangGraph carries shared run state through these stages:

1. **Planner** creates focused research questions and search queries from the topic.

2. **Parallel search agents** retrieve web results from Tavily, academic papers from Semantic Scholar, and news from GNews.

3. **Source merge and preprocessing** combine provider results, remove duplicate URLs, normalize source metadata, and calculate topic relevance.

4. **Source batching and evaluation** score shortlisted sources in bounded batches to control model input size.

5. **Document reader** retrieves accessible pages and text-based PDFs. When a publisher blocks a page, the workflow can use a suitable search-result abstract or snippet.

6. **Evidence extractor** returns claims with supporting text, source URLs, confidence, evidence type, and limitations.

7. **PostgreSQL evidence storage and retrieval** persist evidence under the current research ID and retrieve relevant items for that same run.

8. **Synthesizer** creates a structured report grounded in retrieved evidence.

9. **Citation verifier** checks that report claims and citations are supported by the evidence.

10. **Critic and revision manager** assess completeness, coherence, evidence, and citations, then request revisions up to the configured maximum.

11. **Report generator** builds the final report and supports Markdown, HTML, and PDF output.

### 2. Search and model-usage controls

The current Desktop configuration is deliberately small for free-tier API quotas:

| Setting                  | Current value | Purpose                                                          |
|--------------------------|---------------|------------------------------------------------------------------|
| Search queries           | 3             | Limits provider calls per research run                           |
| Results per query        | 2             | Reduces candidates returned per provider call                    |
| Sources per provider     | Up to 5       | Caps web, academic, and news candidates separately               |
| Sources for evaluation   | Up to 15      | Bounds total evaluator input                                     |
| Documents for extraction | Up to 3       | Limits document text sent to the LLM                             |
| Characters per document  | 1,000         | Controls evidence-extraction prompt size                         |
| Maximum revisions        | 2 by default  | Prevents an unbounded critique loop; API requests may choose 0–5 |

These settings reduce token use; external services can still return rate limits. The workflow retries transient model rate limits where supported and can continue with a clearly labeled fallback when possible. News may legitimately return fewer than five results or none.

### 3. Evidence and persistence

- PostgreSQL stores research runs, sources, evidence, revisions, and reports through SQLAlchemy.
- Evidence records retain the claim, supporting passage, source URL, confidence, type, and limitations.
- PostgreSQL full-text search retrieves evidence, with a confidence-ordered fallback when query terms do not match.
- Retrieval filters by the active `research_id`, preventing evidence from another run from entering the report.
- No Qdrant service or `pgvector` extension is required.

### 4. Reliability and fallback behavior

- Search results are deduplicated and capped before document reading and model evaluation.
- Semantic Scholar and GNews tools include request pacing/retry handling for provider responses.
- For blocked publisher pages, an available abstract or snippet can replace the missing full text.
- Evidence extraction retries transient Groq TPM errors. If extraction remains unavailable, the workflow can retain short, cited source excerpts with low confidence and an explicit limitation; these excerpts are not model-verified claims.
- If structured synthesis or critique cannot be produced, the workflow preserves the last valid evidence-backed draft where possible and reports the limitation instead of discarding completed work.

## Configuration

1. Copy `.env.example` to `.env`.
2. Set API keys for `GROQ_API_KEY`, `TAVILY_API_KEY`, and `GNEWS_API_KEY`. `SEMANTIC_SCHOLAR_API_KEY` is optional but helps with Semantic Scholar access.
3. Set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` for your local PostgreSQL instance.
4. Keep the search/document settings above low if using a free-tier LLM quota. Increase them gradually only after checking provider limits.

Do not commit `.env` or put API keys in frontend code.

## Run locally on Windows PowerShell

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, make sure PostgreSQL is running on the configured port, and start the API:

```powershell
python -m uvicorn app.main:app --reload
```