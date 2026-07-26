import re
from typing import Any

from sqlalchemy.orm import Session

from .analytics import (
    churn_risk_customers,
    dashboard_summary,
    high_value_sales,
    low_performers,
    low_stock_products,
    sales_records_summary,
    top_products,
    total_revenue,
)
from .forecast import forecast_next_month
from .rag import search_documents


def _format_money(value: float) -> str:
    return f"${value:,.2f}"


def _format_number(value: float) -> str:
    return f"{value:,.0f}"


def _extract_threshold(message: str, fallback: float = 5000) -> float:
    match = re.search(r"\$?\s?([0-9][0-9,]*(?:\.\d+)?)", message)
    if not match:
        return fallback
    return float(match.group(1).replace(",", ""))


def _has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _is_tagalog(text: str) -> bool:
    tagalog_terms = [
        "ano",
        "alin",
        "magkano",
        "kita",
        "benta",
        "produkto",
        "empleyado",
        "mababa",
        "gumawa",
        "ulat",
        "buod",
        "hulaan",
        "susunod",
    ]
    return _has_any(text, tagalog_terms)


def _answer(text: str, english: str, tagalog: str) -> str:
    return tagalog if _is_tagalog(text) else english


def answer_question(db: Session, message: str) -> dict[str, Any]:
    text = message.lower()

    revenue_terms = [
        "total revenue",
        "overall revenue",
        "revenue total",
        "tracked students",
        "total students",
        "how many students",
        "ilang students",
        "ilang estudyante",
        "kabuuang kita",
        "total kita",
        "magkano ang kita",
        "magkano revenue",
        "total ingresos",
        "chiffre d'affaires total",
        "total pendapatan",
    ]
    sales_record_terms = [
        "sales records",
        "show all sales",
        "recent sales",
        "sales data",
        "student activity records",
        "school activity records",
        "activity records",
        "student records",
        "listahan ng sales",
        "listahan ng benta",
        "mga benta",
        "ventas",
        "ventes",
        "penjualan",
    ]
    inventory_terms = [
        "stock",
        "inventory",
        "lab supplies",
        "lab supply",
        "school supplies",
        "reorder",
        "out of stock",
        "low stock",
        "mababa stock",
        "mababa ang stock",
        "kulang stock",
        "paubos",
        "imbentaryo",
        "inventario",
        "inventaire",
        "stok",
        "persediaan",
    ]
    top_product_terms = [
        "top",
        "best",
        "sold most",
        "products sold",
        "highest revenue",
        "courses",
        "course",
        "most student activity",
        "student activity",
        "pinakamaraming students",
        "pinakamabenta",
        "pinaka mabenta",
        "pinakamataas na benta",
        "mas mabenta",
        "productos mas vendidos",
        "meilleures ventes",
        "terlaris",
    ]
    threshold_terms = ["greater than", "over", "above", "higit sa", "lampas", "mas mataas sa", "mayor que", "lebih dari"]
    sales_terms = ["sale", "sales", "amount", "revenue", "score", "scores", "project", "activity", "benta", "kita", "ventas", "ventes", "penjualan"]
    employee_terms = [
        "low performance",
        "underperform",
        "performance",
        "employees",
        "empleyado",
        "mababa performance",
        "mababang performance",
        "rendimiento",
        "employes",
        "karyawan",
    ]
    churn_terms = [
        "churn",
        "risk",
        "customer",
        "customers",
        "high risk",
        "customer risk",
        "panganib",
        "delikado",
        "customer na risky",
        "cliente",
        "risque",
        "pelanggan",
    ]
    forecast_terms = [
        "predict",
        "forecast",
        "next month",
        "prediction",
        "hulaan",
        "prediksyon",
        "susunod na buwan",
        "prévision",
        "prediccion",
        "perkiraan",
    ]
    report_terms = [
        "report",
        "summary",
        "recommendation",
        "business review",
        "ulat",
        "buod",
        "rekomendasyon",
        "gumawa ng report",
        "informe",
        "rapport",
        "laporan",
    ]

    if _has_any(text, revenue_terms):
        sql, rows = total_revenue(db)
        value = rows[0]["total_students"] if rows else 0
        count = rows[0]["activity_records"] if rows else 0
        average_score = rows[0]["average_score"] if rows else 0
        answer = _answer(
            text,
            f"There are {int(value)} tracked students across {count} school activity records. Average score is {average_score}.",
            f"May {int(value)} tracked students sa {count} school activity records. Ang average score ay {average_score}.",
        )
        return {
            "intent": "revenue_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "confidence": 0.98,
            "workflow": ["Classified as student count question", "Selected school records tool", "Aggregated student activity records", "Returned count with average score"],
        }

    if _has_any(text, sales_record_terms):
        sql, rows = sales_records_summary(db)
        answer = _answer(
            text,
            f"I found {len(rows)} student activity records. The latest records are shown below.",
            f"Nakakita ako ng {len(rows)} student activity records. Nasa ibaba ang pinaka-latest na records.",
        )
        chart = {
            "type": "bar",
            "x": [row["activity"] for row in rows[:5]],
            "y": [row["score"] for row in rows[:5]],
            "label": "Recent activity scores",
        }
        return {
            "intent": "sales_records_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "chart": chart,
            "confidence": 0.97,
            "workflow": ["Classified as school records request", "Selected student activity table", "Sorted records by latest date", "Rendered rows and chart"],
        }

    if _has_any(text, inventory_terms):
        sql, rows = low_stock_products(db)
        if rows:
            products = ", ".join(row["product"] for row in rows[:4])
            answer = _answer(
                text,
                f"{len(rows)} lab supplies are at or below reorder level. Highest priority: {products}.",
                f"May {len(rows)} lab supplies na nasa reorder level or mas mababa. Priority ay: {products}.",
            )
        else:
            answer = _answer(text, "No lab supplies are currently below reorder level.", "Walang lab supplies na below reorder level ngayon.")
        return {
            "intent": "inventory_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "confidence": 0.96,
            "workflow": ["Classified as lab inventory question", "Selected low-supply records tool", "Filtered stock <= reorder level", "Prioritized lowest lab supplies"],
        }

    if _has_any(text, top_product_terms):
        sql, rows = top_products(db)
        top = rows[0] if rows else None
        answer = (
            _answer(
                text,
                f"{top['course_or_activity']} has the most student activity with {top['students']} tracked students.",
                f"Ang may pinakamaraming student activity ay {top['course_or_activity']} na may {top['students']} tracked students.",
            )
            if top
            else _answer(text, "I could not find school activity records.", "Wala akong nahanap na school activity records.")
        )
        chart = {
            "type": "bar",
            "x": [row["course_or_activity"] for row in rows],
            "y": [row["students"] for row in rows],
            "label": "Students by activity",
        }
        return {
            "intent": "sales_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "chart": chart,
            "confidence": 0.95,
            "workflow": ["Classified as course/activity analytics", "Selected grouped school records tool", "Summed students by activity", "Returned ranked chart"],
        }

    if _has_any(text, threshold_terms) and _has_any(text, sales_terms):
        threshold = _extract_threshold(message)
        sql, rows = high_value_sales(db, threshold)
        answer = _answer(
            text,
            f"I found {len(rows)} project scores greater than {threshold:g}.",
            f"Nakakita ako ng {len(rows)} project scores na mas mataas sa {threshold:g}.",
        )
        return {
            "intent": "sales_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "confidence": 0.96,
            "workflow": ["Extracted score threshold", "Selected student activity records tool", "Filtered score values", "Returned matching records"],
        }

    if _has_any(text, employee_terms):
        sql, rows = low_performers(db)
        answer = _answer(
            text,
            f"{len(rows)} students have performance scores below 75.",
            f"May {len(rows)} students na may performance score below 75.",
        )
        return {
            "intent": "employee_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "confidence": 0.94,
            "workflow": ["Classified as student performance analytics", "Selected performance records tool", "Applied score threshold", "Returned adviser-visible rows"],
        }

    if _has_any(text, churn_terms):
        sql, rows = churn_risk_customers(db)
        answer = _answer(
            text,
            f"{len(rows)} students have risk level at or above 50%.",
            f"May {len(rows)} students na may risk level na 50% pataas.",
        )
        return {
            "intent": "customer_sql_agent",
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "confidence": 0.94,
            "workflow": ["Classified as student risk question", "Selected student support records tool", "Filtered risk >= 0.50", "Returned support priorities"],
        }

    if _has_any(text, forecast_terms):
        forecast = forecast_next_month(db)
        answer = (
            _answer(
                text,
                f"Next month school activity is forecast at {_format_number(forecast['prediction'])} using {forecast['method']}.",
                f"Ang forecast na school activity sa susunod na buwan ay {_format_number(forecast['prediction'])} gamit ang {forecast['method']}.",
            )
            if forecast["prediction"]
            else _answer(text, "I need more monthly history before forecasting.", "Kailangan ko pa ng mas maraming monthly history bago mag-forecast.")
        )
        chart = {
            "type": "line",
            "x": [item["month"] for item in forecast["history"]] + ["Next"],
            "y": [item["revenue"] for item in forecast["history"]] + ([forecast["prediction"]] if forecast["prediction"] else []),
            "label": "School activity forecast",
        }
        return {
            "intent": "ml_forecast_agent",
            "answer": answer,
            "rows": [forecast],
            "chart": chart,
            "confidence": 0.82,
            "workflow": ["Classified as forecasting request", "Loaded monthly school activity history", "Ran ML/trend forecast tool", "Returned prediction chart"],
        }

    if _has_any(text, report_terms):
        summary = dashboard_summary(db)
        forecast = forecast_next_month(db)
        sql, low_stock = low_stock_products(db)
        sources = search_documents(db, message)
        forecast_text = _format_number(forecast["prediction"]) if forecast["prediction"] else "not available"
        answer = _answer(
            text,
            (
                "School report: "
                f"{summary['total_students']} students are tracked; "
                f"{summary['low_stock_count']} lab supplies need attention; "
                f"{summary['high_risk_customers']} students are at risk; "
                f"next month activity forecast is {forecast_text}. "
                "Recommendation: prioritize low lab supplies and schedule adviser reviews for at-risk students."
            ),
            (
                "School report: "
                f"may {summary['total_students']} tracked students; "
                f"may {summary['low_stock_count']} lab supplies na kailangan bantayan; "
                f"may {summary['high_risk_customers']} at-risk students; "
                f"ang next month activity forecast ay {forecast_text}. "
                "Recommendation: unahin ang low lab supplies at mag-schedule ng adviser reviews para sa at-risk students."
            ),
        )
        report_markdown = (
            "# AI School Report\n\n"
            f"## Executive Summary\nThe assistant is tracking {summary['total_students']} students across school activity records. "
            f"It found {summary['low_stock_count']} low lab supplies and {summary['high_risk_customers']} at-risk students.\n\n"
            f"## Forecast\nNext month school activity forecast: **{forecast_text}**.\n\n"
            "## Recommendations\n"
            "- Prioritize lab supply follow-up for embedded systems and electronics materials.\n"
            "- Schedule adviser reviews for students with risk above 50%.\n"
            "- Review lab access and pending tasks for capstone groups.\n"
        )
        return {
            "intent": "report_generator_agent",
            "answer": answer,
            "sql": sql,
            "rows": low_stock,
            "chart": {"type": "line", "x": [m["month"] for m in summary["monthly_revenue"]], "y": [m["revenue"] for m in summary["monthly_revenue"]], "label": "Monthly school activity"},
            "sources": sources,
            "confidence": 0.9,
            "workflow": ["Classified as school report request", "Combined school KPIs", "Pulled lab inventory evidence", "Retrieved school policy context", "Generated adviser-ready report"],
            "report_markdown": report_markdown,
        }

    sources = search_documents(db, message)
    if sources:
        answer = _answer(
            text,
            f"I found relevant company knowledge in {sources[0]['title']}: {sources[0]['snippet']}",
            f"May nakita akong related company knowledge sa {sources[0]['title']}: {sources[0]['snippet']}",
        )
        return {
            "intent": "rag_document_agent",
            "answer": answer,
            "sources": sources,
            "confidence": 0.84,
            "workflow": ["Classified as document question", "Embedded/searched knowledge documents", "Ranked relevant snippets", "Answered with retrieved source"],
        }

    summary = dashboard_summary(db)
    return {
        "intent": "general_dashboard_agent",
        "answer": _answer(
            text,
            (
                "I can help with student records, lab supplies, student performance, at-risk students, school documents, forecasts, and reports. "
                f"Current tracked students: {summary['total_students']}. Try asking in English, Tagalog, or Taglish."
            ),
            (
                "Pwede mo akong tanungin tungkol sa student records, lab supplies, student performance, at-risk students, school documents, forecasts, at reports. "
                f"Current tracked students: {summary['total_students']}. Pwede kang magtanong in Tagalog, English, or Taglish."
            ),
        ),
        "rows": [summary],
        "confidence": 0.78,
        "workflow": ["No specialized intent matched", "Loaded dashboard summary", "Returned capability guidance"],
    }
