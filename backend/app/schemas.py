from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, examples=["Which products are almost out of stock?"])


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


class UploadResponse(BaseModel):
    filename: str
    stored_characters: int
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
