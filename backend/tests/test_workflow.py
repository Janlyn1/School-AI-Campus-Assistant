from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import KnowledgeDocument
from app.services.workflow import run_agent_workflow


def test_langgraph_workflow_adds_ml_trace_and_sources():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        KnowledgeDocument(
            title="Library Guide",
            source_type="PDF",
            content="Page 2. The library opens weekdays at 7:30 AM.",
        )
    )
    session.commit()

    result = run_agent_workflow(session, "What time does the library open?")

    assert result["intent"] == "library_domain_agent"
    assert result["model_trace"]["label"] == "Library"
    assert result["workflow"][0] == "LangGraph received the request"
    assert result["sources"][0]["title"] == "Library Guide"
