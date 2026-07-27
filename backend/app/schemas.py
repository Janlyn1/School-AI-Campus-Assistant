from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, examples=["Which products are almost out of stock?"])
    role: str = "Student"
    student_name: str = "Janlyn Rustila"


class ChatResponse(BaseModel):
    answer: str
    intent: str
    sql: str | None = None
    rows: list[dict[str, Any]] = []
    chart: dict[str, Any] | None = None
    sources: list[dict[str, Any]] = []
    confidence: float = 0.86
    workflow: list[str] = []
    report_markdown: str | None = None
    agent_name: str = "Ari Campus AI Agent"
    data_path: str = "Campus database"
    response_time_ms: int = 0
    model_trace: dict[str, Any] | None = None
    llm_provider: str = "Tool-grounded fallback"
    llm_model: str = "No external LLM configured"
    llm_status: str = "not_configured"


class UploadResponse(BaseModel):
    filename: str
    stored_characters: int
    indexed_chunks: int = 0
    message: str


class InventoryCreate(BaseModel):
    sku: str
    product: str
    category: str
    stock_remaining: int
    reorder_level: int
    supplier: str
    note: str | None = None


class SaleCreate(BaseModel):
    date: str
    product: str
    category: str
    quantity: int
    amount: float
    customer_segment: str
    note: str | None = None


class ForecastPointCreate(BaseModel):
    month: str = Field(..., examples=["2026-08"])
    revenue: float
    note: str | None = None


class DocumentCreate(BaseModel):
    title: str
    source_type: str = "NOTE"
    content: str
    note: str | None = None


class DataCreateResponse(BaseModel):
    kind: str
    message: str
    item: dict[str, Any]


class FeedbackCreate(BaseModel):
    question: str
    answer: str
    intent: str
    helpful: bool | None = None
    escalated: bool = False
    note: str | None = None


class RequestAction(BaseModel):
    reviewer: str
