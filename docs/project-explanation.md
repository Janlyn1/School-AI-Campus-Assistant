# School AI Campus Assistant

School AI Campus Assistant is an agentic chatbot for a school or Computer Engineering department. It helps students, faculty, or lab assistants ask natural-language questions about student activity records, lab supplies, at-risk students, school policies, and academic reports.

The architecture uses a React frontend and a FastAPI backend. The backend stores structured school data in a SQL database, runs record queries through tool-like service functions, searches school documents, and exposes REST API endpoints for chat, dashboards, document search, adding school data, and forecasting. The demo runs on SQLite for portability, but the SQLAlchemy database layer can be switched to PostgreSQL through `DATABASE_URL`.

The agent workflow classifies each user question, chooses the right tool, executes the query or retrieval step, and returns an answer with evidence. For example, lab supply questions call the low-supply records tool, project score questions call the student activity records tool, document questions call the school document search service, and forecast questions call the forecasting service.

My specific contribution was building the full prototype end to end: FastAPI routes, database schema, seeded school sample data, record-query tools, school document search, forecast logic, and the React dashboard. I also designed the interface so the user can see the generated evidence, source snippets, charts, returned rows, confidence indicator, and agent workflow steps instead of receiving a black-box answer.

I also added an Add School Data page so users can insert new school records, documents, forecast inputs, and AI notes directly from the dashboard. After a record is saved, the app shows a notification; clicking it opens the exact added item and notes. The Indexed Documents panel can also be hidden or shown so the interface stays clean.

To make the assistant feel more natural, I added Tagalog/Taglish-aware routing for common school questions such as lab supplies, tracked students, project scores, forecasts, and report generation. The chat widget avoids clutter by hiding recommended questions after the first chat and showing them again only when the user asks for recommendations.

This project demonstrates practical experience with LLM-style agents, SQL databases, FastAPI, school data workflows, retrieval, REST APIs, charts, downloadable report generation, and machine learning predictions. It is intentionally close to an AI assistant a school department could use for academic monitoring, lab inventory tracking, and student support.
