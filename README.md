# Ari Campus AI - Agentic Assistant for Higher Education

An enterprise-style agentic AI assistant using a school and Computer Engineering campus dataset. It routes natural-language requests across structured records, lab inventory, knowledge documents, forecasting, and report tools.

**Portfolio description:** A full-stack agentic AI chatbot built with React, FastAPI, SQLAlchemy, record-query tools, document retrieval, forecasting, and an evidence-focused chat interface. The assistant routes each question to the right tool, shows workflow steps, displays record evidence, supports Tagalog/Taglish questions, and lets users add new data with notifications.

## Live Demo

- Frontend: https://school-ai-campus-assistant.vercel.app
- Backend health check: https://school-ai-campus-assistant.onrender.com/health

## Why This Project

This portfolio project is built to demonstrate AI agent, backend API, database, retrieval, and ML workflow skills using a context that is easy to explain as a Computer Engineering student:

- LLM-style agent workflows
- LangGraph orchestration
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

- Recruiter landing page with live demo, GitHub, documentation, features, and architecture
- Three distinct responsive experiences:
  - Student portal with announcements, calendar, program details, and quick campus services
  - Registrar workspace with question queue, knowledge health, tickets, and document tools
  - Admin control center with AI request analytics, service status, latency, and feedback metrics
- AI chat interface for school questions
- Specialized Registrar, Finance, Guidance, Library, and IT agent routing
- Genuine scikit-learn inquiry classifier integrated into every chat response
- Persisted interaction logging and backend-derived Admin monitoring metrics
- **Ari, Campus Services Assistant** for student enrollment and equipment borrowing
- Google Gemini grounded generation on the backend, with deterministic tool fallback
- Enrollment workflow: Student asks Ari → request enters Registrar queue → Registrar confirms enrollment
- Borrowing workflow: Student asks Ari with SKU/product → inventory is checked → Admin approves release → Admin records return
- Automatic distinction between insufficient stock and items the school does not stock
- Student request tracking without exposing raw school records or administrative analytics
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
LangGraph workflow
        |
ML intent classifier and specialized tool services
        |
Gemini grounded response generation (when configured)
        |
SQLAlchemy database layer
        |
SQLite local fallback or PostgreSQL via DATABASE_URL
        |
School document search + scikit-learn forecast model
```

## Multi-Agent Routing

Ari Campus AI exposes a clear agent identity for every response:

- **Records Agent** for SQLAlchemy-backed school and inventory records
- **Knowledge Agent** for retrieved school document evidence
- **Forecast Agent** for time-series prediction
- **Report Agent** for combined records, retrieval, and forecast workflows
- **Campus Router** for general capability guidance

LangGraph runs the classifier and campus-tool nodes for every chat request. Tool execution remains deterministic for reliability. When `GEMINI_API_KEY` is configured, Google Gemini converts the verified tool result into a natural English, Filipino, or Taglish answer. Gemini cannot approve requests, modify inventory directly, or invent SQL/RAG evidence.

## Machine Learning Model

Ari Campus AI includes a real student inquiry classification model, not a decorative metric:

- **Task:** multi-class intent classification
- **Classes:** Finance, Guidance, IT Support, Laboratory, Library, Registrar, Scholarship
- **Dataset:** 294 labeled synthetic campus inquiries in English, Filipino, and Taglish
- **Preprocessing:** lowercase normalization, Unicode accent normalization, TF-IDF word unigrams and bigrams
- **Model:** Logistic Regression with a fixed random seed
- **Evaluation:** stratified 70% train / 30% held-out test split
- **Held-out accuracy:** 95.5%
- **Macro precision:** 96.1%
- **Macro recall:** 95.6%
- **Macro F1:** 95.6%

The full evaluation, labels, split details, and confusion matrix are generated by the backend at [`/ml/evaluation`](https://school-ai-campus-assistant.onrender.com/ml/evaluation). Metrics are calculated from the held-out test set; after evaluation, the deployed classifier is refit on all labeled examples.

Because this is a synthetic portfolio dataset, these scores demonstrate the implementation and evaluation workflow rather than expected performance on a university's real production traffic. Real deployment would retrain and re-evaluate on anonymized, staff-reviewed inquiries.

## Monitoring and Evidence

Every chat interaction stores its role, selected intent, agent, measured backend latency, number of retrieved sources, and timestamp. The Admin dashboard reads actual aggregates from `/admin/metrics`; it does not display invented uptime, accuracy, hallucination, or confidence percentages.

RAG answers show qualitative retrieval relevance alongside document type, filename, page number, and excerpt. ML percentages appear only in the explicitly labeled held-out evaluation panel.

## Honest Demo Scope

The public portfolio provides realistic role-specific demo experiences; it does not claim production authentication. Production deployment would add JWT or an identity provider, email verification and password recovery, pgvector embeddings, and server-side permission enforcement. LangGraph is used for the deployed chat workflow. Document retrieval currently uses TF-IDF cosine similarity, not vector embeddings.

The demo uses synthetic campus records only. SQL operations go through predefined SQLAlchemy tools, and student-facing navigation does not expose raw administrative data. Uploads are limited to 5 MB and validated to TXT, PDF, DOCX, or PPTX before text extraction.

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

### Docker Compose

Docker Compose starts the frontend, backend, and PostgreSQL together:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The backend health endpoint at `http://localhost:8000/health` reports the active database backend and orchestration engine.

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
DATABASE_URL=postgresql://user:password@host:5432/database
GEMINI_API_KEY=your-secret-key
GEMINI_MODEL=gemini-2.5-flash
```

Store `GEMINI_API_KEY` only in Render's Environment settings. Never prefix it with `VITE_`, place it in the frontend, or commit it to GitHub. If Gemini is unavailable, Ari returns the verified SQL/RAG/tool answer and labels the provider as `Tool-grounded fallback`.

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

- Enroll me for the upcoming term.
- Borrow 2 pcs LAB-100 Arduino Uno Kit.
- Borrow a quantum oscilloscope.
- Aling lab supplies ang paubos na?
- Add records lab supplies lma-302 rpi embedded system 9 stock 10 level engineering lab
- Which courses have the most student activity?
- Show project scores greater than 85.
- Show students with low performance.
- Which students are at risk?
- Predict next month's enrollment activity.
- Generate a school report.

## Campus Service Workflow

```text
Student asks Ari
        |
        +-- Enrollment request --> Registrar confirms --> Enrolled
        |
        +-- Borrow request --> Inventory check --> Admin confirms --> Borrowed
                                                         |
                                                         +--> Mark returned --> Stock restored
```

The public demo uses a fixed student identity (`Janlyn Rustila`) until production authentication is added. Request records, approval status, reviewer, timestamps, borrower, SKU, product, and quantity are persisted in the SQL database.

## PostgreSQL Setup

For the demo, SQLite is used by default. To use PostgreSQL, set:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Then install a PostgreSQL driver such as `psycopg`.

## Application Explanation

Use [`docs/project-explanation.md`](docs/project-explanation.md) for the short written explanation requested by the job application.
