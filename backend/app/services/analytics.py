from collections import defaultdict
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ..models import Customer, Employee, InventoryItem, Sale


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(row._mapping) if hasattr(row, "_mapping") else row.__dict__ for row in rows]


def dashboard_summary(db: Session) -> dict[str, Any]:
    total_revenue = db.scalar(select(func.sum(Sale.amount))) or 0
    total_students = db.scalar(select(func.sum(Sale.quantity))) or 0
    sales_count = db.scalar(select(func.count(Sale.id))) or 0
    low_stock_count = db.scalar(
        select(func.count(InventoryItem.id)).where(InventoryItem.stock_remaining <= InventoryItem.reorder_level)
    ) or 0
    high_risk_customers = db.scalar(select(func.count(Customer.id)).where(Customer.churn_risk >= 0.5)) or 0

    monthly = monthly_revenue(db)
    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_students": int(total_students),
        "sales_count": sales_count,
        "low_stock_count": low_stock_count,
        "high_risk_customers": high_risk_customers,
        "monthly_revenue": monthly,
    }


def monthly_revenue(db: Session) -> list[dict[str, Any]]:
    sales = db.scalars(select(Sale).order_by(Sale.date)).all()
    bucket: dict[str, float] = defaultdict(float)
    for sale in sales:
        bucket[sale.date.strftime("%Y-%m")] += sale.amount
    return [{"month": month, "revenue": round(revenue, 2)} for month, revenue in bucket.items()]


def total_revenue(db: Session) -> tuple[str, list[dict[str, Any]]]:
    query = select(
        func.sum(Sale.quantity).label("total_students"),
        func.count(Sale.id).label("activity_records"),
        func.round(func.avg(Sale.amount), 2).label("average_score"),
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def sales_records_summary(db: Session) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(
            Sale.date,
            Sale.product.label("activity"),
            Sale.category.label("department"),
            Sale.quantity.label("students"),
            Sale.amount.label("score"),
            Sale.customer_segment.label("year_level"),
        )
        .order_by(desc(Sale.date))
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def top_products(db: Session, limit: int = 5) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(
            Sale.product.label("course_or_activity"),
            func.sum(Sale.quantity).label("students"),
            func.round(func.avg(Sale.amount), 2).label("average_score"),
        )
        .group_by(Sale.product)
        .order_by(desc("students"))
        .limit(limit)
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def low_stock_products(db: Session) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(
            InventoryItem.sku,
            InventoryItem.product,
            InventoryItem.stock_remaining,
            InventoryItem.reorder_level,
            InventoryItem.supplier,
        )
        .where(InventoryItem.stock_remaining <= InventoryItem.reorder_level)
        .order_by(InventoryItem.stock_remaining)
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def high_value_sales(db: Session, threshold: float = 5000) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(
            Sale.date,
            Sale.product.label("activity"),
            Sale.category.label("department"),
            Sale.quantity.label("students"),
            Sale.amount.label("score"),
            Sale.customer_segment.label("year_level"),
        )
        .where(Sale.amount > threshold)
        .order_by(desc(Sale.amount))
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def low_performers(db: Session, threshold: float = 75) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(Employee.name, Employee.department, Employee.performance_score, Employee.open_tasks, Employee.manager)
        .where(Employee.performance_score < threshold)
        .order_by(Employee.performance_score)
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows


def churn_risk_customers(db: Session, threshold: float = 0.5) -> tuple[str, list[dict[str, Any]]]:
    query = (
        select(Customer.name, Customer.segment, Customer.lifetime_value, Customer.churn_risk, Customer.region)
        .where(Customer.churn_risk >= threshold)
        .order_by(desc(Customer.churn_risk))
    )
    rows = rows_to_dicts(db.execute(query).all())
    return str(query.compile(compile_kwargs={"literal_binds": True})), rows
