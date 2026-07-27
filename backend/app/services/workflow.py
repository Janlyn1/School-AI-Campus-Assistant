from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from .agent import answer_question
from .intent_classifier import classify_inquiry


class AgentState(TypedDict, total=False):
    db: Session
    message: str
    role: str
    student_name: str
    ml_route: dict[str, Any]
    result: dict[str, Any]


def _classify_intent(state: AgentState) -> AgentState:
    return {"ml_route": classify_inquiry(state["message"])}


def _run_campus_tools(state: AgentState) -> AgentState:
    result = answer_question(
        state["db"],
        state["message"],
        role=state["role"],
        student_name=state["student_name"],
    )
    workflow = [
        "LangGraph received the request",
        f"ML classifier selected {state['ml_route']['label']}",
        *result.get("workflow", []),
    ]
    return {"result": {**result, "workflow": workflow, "model_trace": state["ml_route"]}}


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", _classify_intent)
    graph.add_node("run_campus_tools", _run_campus_tools)
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "run_campus_tools")
    graph.add_edge("run_campus_tools", END)
    return graph.compile()


AGENT_GRAPH = build_agent_graph()


def run_agent_workflow(
    db: Session,
    message: str,
    role: str = "Student",
    student_name: str = "Janlyn Rustila",
) -> dict[str, Any]:
    state = AGENT_GRAPH.invoke(
        {
            "db": db,
            "message": message,
            "role": role,
            "student_name": student_name,
        }
    )
    return state["result"]
