# CampusIQ - Enterprise AI Assistant for Higher Education

An enterprise-style agentic AI assistant using a school and Computer Engineering campus dataset. It routes natural-language requests across structured records, lab inventory, knowledge documents, forecasting, and report tools.

**Portfolio description:** A full-stack agentic AI chatbot built with React, FastAPI, SQLAlchemy, record-query tools, document retrieval, forecasting, and an evidence-focused chat interface. The assistant routes each question to the right tool, shows workflow steps, displays record evidence, supports Tagalog/Taglish questions, and lets users add new data with notifications.

## Live Demo

- Frontend: https://school-ai-campus-assistant.vercel.app
- Backend health check: https://school-ai-campus-assistant.onrender.com/health

## Why This Project

This portfolio project is built to demonstrate AI agent, backend API, database, retrieval, and ML workflow skills using a context that is easy to explain as a Computer Engineering student:

- LLM-style agent workflows
- FastAPI REST APIs
- SQL databases and generated record evidence
- School/campus data workflows
- Retrieval-Augmented Generation over school documents
- Machine learning forecasting with scikit-learn
- React dashboard and charts

## Why It Matches the Junior AI/ML Engineer Role

- Builds an interactive chatbot/agent experience
- Connects the chat interface to structured database records
- Retrieves evidence from unstructured school documents and notes
- Integrates forecasting logic through a backend API
- Shows model/tool outputs inside the workflow instead of hiding them
- Documents the architecture, deployment, and project explanation

## Features

- AI chat interface for school questions
- School record tools for student activity, lab supplies, performance, and student risk
- School document search over policies and notes
- Forecasting endpoint using `scikit-learn` when available
- Automated school report generation
- Dashboard metrics and charts
- Add School Data page for records, documents, forecast inputs, and AI notes
- Chat-based inventory writing, for example: `add records lab supplies lma-302 rpi embedded system 9 stock 10 level engineering lab`
- Clickable save notifications that open the newly added item and notes
- Hide/show Indexed Documents panel
- Visible agent workflow steps for each answer
- Explainability panel with selected agent, data path, role context, confidence, and response time
- Demo role switcher for Student, Registrar, and Admin perspectives
- Helpful/not-helpful feedback persisted through the backend
- Ticket escalation for answers that need registrar review
- Confidence, SQL, row, and retrieved-source evidence
- Downloadable AI school report
- Tagalog/Taglish-aware routing for core school questions
- Cleaner chat widget with on-demand recommended questions and no visible chat history

## Architecture

```text
React + Vite frontend
        |
FastAPI backend
        |
Campus router and specialized tool services
        |
SQLAlchemy database layer
        |
SQLite demo database or PostgreSQL via DATABASE_URL
        |
School document search + scikit-learn forecast model
```

## Multi-Agent Routing

CampusIQ exposes a clear agent identity for every response:

- **Records Agent** for SQLAlchemy-backed school and inventory records
- **Knowledge Agent** for retrieved school document evidence
- **Forecast Agent** for time-series prediction
- **Report Agent** for combined records, retrieval, and forecast workflows
- **Campus Router** for general capability guidance

The public demo uses deterministic intent routing so it remains reliable without requiring a paid API key. The service boundaries are ready for an LLM or LangGraph router as a future production integration.

## Honest Demo Scope

The Student, Registrar, and Admin selector demonstrates role context in the explainability and escalation workflow; it is not production authentication. Production deployment would add JWT or an identity provider, PostgreSQL/pgvector, document page extraction, and permission enforcement.

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will run at `http://127.0.0.1:5173`.

## Deployment Environment Variables

### Render Backend

Use **Web Service** with root directory `backend`.

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Environment variables:

```text
FRONTEND_ORIGINS=https://school-ai-campus-assistant.vercel.app
DATABASE_URL=sqlite:///./enterprise_ai_agent.db
```

The deployed backend URL should look like:

```text
https://school-ai-campus-assistant.onrender.com
```

Test it with:

```text
https://school-ai-campus-assistant.onrender.com/health
```

### Vercel Frontend

Use root directory `frontend`.

```text
Build Command: npm run build
Output Directory: dist
```

Environment variable:

```text
VITE_API_BASE=https://school-ai-campus-assistant.onrender.com
```

The frontend URL should look like:

```text
https://school-ai-campus-assistant.vercel.app
```

## Sample Questions

- Aling lab supplies ang paubos na?
- Add records lab supplies lma-302 rpi embedded system 9 stock 10 level engineering lab
- Which courses have the most student activity?
- Show project scores greater than 85.
- Show students with low performance.
- Which students are at risk?
- Predict next month's enrollment activity.
- Generate a school report.

## PostgreSQL Setup

For the demo, SQLite is used by default. To use PostgreSQL, set:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Then install a PostgreSQL driver such as `psycopg`.

## Application Explanation

Use [`docs/project-explanation.md`](docs/project-explanation.md) for the short written explanation requested by the job application.
