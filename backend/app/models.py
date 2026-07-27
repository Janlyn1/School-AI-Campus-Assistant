from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[str] = mapped_column(Date, index=True)
    product: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    customer_segment: Mapped[str] = mapped_column(String(80), index=True)


class InventoryItem(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    product: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(80))
    stock_remaining: Mapped[int] = mapped_column(Integer)
    reorder_level: Mapped[int] = mapped_column(Integer)
    supplier: Mapped[str] = mapped_column(String(120))


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    department: Mapped[str] = mapped_column(String(80), index=True)
    performance_score: Mapped[float] = mapped_column(Float)
    open_tasks: Mapped[int] = mapped_column(Integer)
    manager: Mapped[str] = mapped_column(String(120))


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    segment: Mapped[str] = mapped_column(String(80), index=True)
    lifetime_value: Mapped[float] = mapped_column(Float)
    churn_risk: Mapped[float] = mapped_column(Float)
    region: Mapped[str] = mapped_column(String(80))


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    source_type: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)


class AgentFeedback(Base):
    __tablename__ = "agent_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(80), index=True)
    helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
