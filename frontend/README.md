# DeepResearch AI Frontend

The DeepResearch AI frontend is a responsive React dashboard for submitting a research topic to the backend and reviewing the resulting report. It lets users choose a revision limit, shows the returned research status and source/evidence counts, highlights report claims and source links, displays report coverage signals, handles API errors, and downloads the report as Markdown. The frontend communicates with the FastAPI backend through Axios and does not call research providers or LLMs directly.

## Project structure

```text
frontend/
├── public/                    # Static public assets
├── src/
│   ├── assets/                # Images and bundled assets
│   ├── components/            # Reusable research form, status, report, source UI
│   ├── services/
│   │   └── api.js             # Axios client and backend request functions
│   ├── App.jsx                # Main dashboard, state, submit flow, panels, export
│   ├── App.css                # Dashboard layout, panels, responsive styling
│   ├── index.css              # Global styles and base typography
│   └── main.jsx               # React application entry point
├── index.html                 # Vite HTML entry point
├── package.json               # Scripts and dependencies
├── package-lock.json          # Locked npm dependency versions
└── vite.config.js              # Vite and React plugin configuration
```

## Frontend functionalities

### 1. Research submission

- The search form accepts a research topic and a maximum revision count from 0 to 5.
- The submit button is disabled for an empty topic or while a request is running.
- While the backend works, the dashboard displays a loading state and prevents duplicate submissions.
- The form calls `POST /research` with `{ "topic": "...", "max_revisions": 2 }`.

### 2. Dashboard results

- **Research summary:** displays the report executive summary and topic.
- **Key findings:** shows up to four unique claims from the report and their linked-source counts.
- **Sources:** lists returned source records and provides safe external links.
- **Evidence highlights:** displays cited claims from the report.
- **Coverage chart:** summarizes claims by report section. This is a report-coverage visualization, not a publication or live analytics chart.
- **Report panel:** shows completion status and a Markdown download action.
- **Analysis panel:** shows status and a simple evidence-traceability summary.
- Empty states explain what will appear before a run has completed.

### 3. API integration

`src/services/api.js` creates one Axios client and provides helpers:

- `startResearch(topic, maxRevisions)` calls `POST /research`.
- `healthCheck()` calls `GET /health`.

The current dashboard uses `startResearch`; the other helpers are available for future run-history or health UI. The backend base URL is set by `VITE_API_BASE_URL`, defaulting to `http://localhost:8000`.

### 4. Report handling and safety

- The dashboard reads the report fields returned by the backend: metadata, executive summary, sections, claims, conclusion, and limitations.
- Markdown export is generated in the browser from the report response; it does not require a second backend request.
- External source links are accepted only when they use `http:` or `https:`.
- API errors are shown in an error banner. The frontend uses the backend error detail when available and otherwise gives a setup-oriented message.

### 5. Responsive interface

- The sidebar and dashboard panels are styled for desktop and narrow screens.
- Reusable visual components and inline SVG icons keep the interface consistent without a charting or icon dependency.
- The workflow sidebar describes pipeline stages, but the backend currently returns the completed run response synchronously; the UI does not receive live progress for each stage.

## Technology

- React 19 for the interface and local component state.
- Vite 8 for development server and production bundling.
- Axios for HTTP requests.
- Plain CSS for dashboard styling, responsive layout, and visualizations.
- Oxlint for linting.

## Configuration

Set the backend URL with a Vite environment variable when it is not running at the default address:

```text
VITE_API_BASE_URL=http://localhost:8000
```

For local development, put this in a `.env.local` file in the frontend directory. Vite exposes only variables prefixed with `VITE_` to browser code. Never put Groq, Tavily, GNews, or Semantic Scholar API keys in frontend environment variables; those belong in the backend `.env`.

The FastAPI backend must allow the frontend origin through CORS. The current local Vite origins are `http://localhost:5173` and `http://127.0.0.1:5173`.

## Run locally

From the `frontend` directory:

```sh
npm ci
npm run dev
```

Open the local Vite URL printed in the terminal (normally `http://localhost:5173`). Start the backend separately and confirm `http://localhost:8000/health` responds before submitting research.

## Available scripts

| Command           | Purpose                                 |
|-------------------|-----------------------------------------|
| `npm run dev`     | Start the Vite development server       |
| `npm run build`   | Create the production bundle in `dist/` |
| `npm run preview` | Preview the production bundle locally   |
| `npm run lint`    | Run Oxlint                              |

## Production build

```sh
npm run build
npm run preview
```

Deploy the generated `dist/` directory to a static web host and set `VITE_API_BASE_URL` to the deployed API origin at build time. Configure the backend CORS allowlist for the deployed frontend domain.