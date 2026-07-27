import re
from typing import Any

from sqlalchemy.orm import Session

from ..models import InventoryItem, KnowledgeDocument
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
        "paano",
        "pwede",
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


def _clean_phrase(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.replace("_", " ").replace("-", " ")).strip(" .,;:")
    return cleaned.title() if cleaned else ""


def _parse_inventory_add(message: str) -> dict[str, Any] | None:
    text = message.lower()
    add_terms = ["add", "insert", "save", "create", "dagdag", "magdagdag", "ilagay", "lagay"]
    inventory_terms = ["record", "records", "lab supplies", "lab supply", "stock", "inventory", "supply"]
    if not (_has_any(text, add_terms) and _has_any(text, inventory_terms)):
        return None

    sku_match = re.search(r"\b([a-z]{2,}[-_]?\d{2,})\b", message, flags=re.IGNORECASE)
    stock_match = re.search(r"\b(\d+)\s*(?:stock|stocks|pcs|pieces|qty|quantity|remaining)\b", text)
    reorder_match = re.search(r"\b(\d+)\s*(?:level|reorder\s*level|reorder)\b", text)
    if not (sku_match and stock_match and reorder_match):
        return None

    product_segment = message[sku_match.end() : stock_match.start()]
    product_segment = re.sub(r"\b(?:lab supplies?|inventory|record|records|item|product)\b", " ", product_segment, flags=re.IGNORECASE)
    product = _clean_phrase(product_segment) or sku_match.group(1).upper()

    supplier_segment = message[reorder_match.end() :]
    supplier_segment = re.sub(r"\b(?:note|notes|example|sample)\b.*$", "", supplier_segment, flags=re.IGNORECASE)
    supplier = _clean_phrase(supplier_segment) or "Engineering Lab"

    category = "Embedded Systems" if "embedded" in text or "rpi" in text else "Lab Supplies"
    note_match = re.search(r"\b(?:note|notes)\s+(.+)$", message, flags=re.IGNORECASE)
    note = note_match.group(1).strip() if note_match else f"Added through AI chat command: {message}"

    return {
        "sku": sku_match.group(1).upper().replace("_", "-"),
        "product": product,
        "category": category,
        "stock_remaining": int(stock_match.group(1)),
        "reorder_level": int(reorder_match.group(1)),
        "supplier": supplier,
        "note": note,
    }


def _add_inventory_from_chat(db: Session, message: str) -> dict[str, Any] | None:
    payload = _parse_inventory_add(message)
    if not payload:
        return None

    item = db.query(InventoryItem).filter(InventoryItem.sku == payload["sku"]).first()
    action = "updated"
    if not item:
        action = "added"
        item = InventoryItem(
            sku=payload["sku"],
            product=payload["product"],
            category=payload["category"],
            stock_remaining=payload["stock_remaining"],
            reorder_level=payload["reorder_level"],
            supplier=payload["supplier"],
        )
        db.add(item)
    else:
        item.product = payload["product"]
        item.category = payload["category"]
        item.stock_remaining = payload["stock_remaining"]
        item.reorder_level = payload["reorder_level"]
        item.supplier = payload["supplier"]

    db.add(
        KnowledgeDocument(
            title=f"Inventory note: {payload['product']}",
            source_type="AI_NOTE",
            content=payload["note"],
        )
    )
    db.commit()
    db.refresh(item)

    row = {
        "id": item.id,
        "sku": item.sku,
        "product": item.product,
        "category": item.category,
        "stock_remaining": item.stock_remaining,
        "reorder_level": item.reorder_level,
        "supplier": item.supplier,
        "note": payload["note"],
    }
    return {
        "intent": "inventory_write_agent",
        "answer": (
            f"Saved. {item.product} ({item.sku}) was {action} with {item.stock_remaining} stock, "
            f"reorder level {item.reorder_level}, supplier {item.supplier}."
        ),
        "sql": "INSERT OR UPDATE inventory SET sku, product, category, stock_remaining, reorder_level, supplier",
        "rows": [row],
        "confidence": 0.91,
        "workflow": [
            "Classified as add inventory command",
            "Extracted SKU, product, stock, reorder level, and supplier",
            "Saved the lab supply record",
            "Created an AI note for audit context",
        ],
    }


def _specialized_domain_answer(db: Session, text: str, message: str) -> dict[str, Any] | None:
    domains = [
        {
            "intent": "registrar_domain_agent",
            "terms": ["enroll", "enrollment", "registrar", "transcript", "grade", "graduation", "units", "mag enroll", "paano mag enroll"],
            "query": "continuing students enroll registrar transcript grades",
            "english": "Continuing students should clear any holds, confirm subjects with their adviser, submit registration through the student portal, and download the assessment form.",
            "tagalog": "Para mag-enroll, i-clear muna ang academic o finance holds, ipa-confirm ang subjects sa adviser, isumite ang registration sa student portal, at i-download ang assessment form.",
        },
        {
            "intent": "finance_domain_agent",
            "terms": ["tuition", "payment", "balance", "scholarship", "financial assistance", "bayad", "scholar"],
            "query": "scholarship tuition financial assistance payment balance",
            "english": "Merit scholarships require a 1.75 or better weighted average with no failing grade. Financial assistance also requires proof of income and the latest grades.",
            "tagalog": "Para sa merit scholarship, kailangan ng 1.75 o mas mataas na weighted average at walang failing grade. Sa financial assistance, kailangan din ng proof of income at latest grades.",
        },
        {
            "intent": "guidance_domain_agent",
            "terms": ["counseling", "mental health", "guidance", "career", "internship", "resume", "stress"],
            "query": "confidential counseling academic coaching career internship",
            "english": "The Guidance Office provides confidential counseling, academic coaching, career support, resume review, mock interviews, and internship referrals.",
            "tagalog": "May confidential counseling, academic coaching, career support, resume review, mock interview, at internship referrals sa Guidance Office.",
        },
        {
            "intent": "library_domain_agent",
            "terms": ["library", "book", "borrow", "journal", "research", "aklat"],
            "query": "library hours borrow books online journals",
            "english": "The library is open weekdays from 7:30 AM to 7 PM and Saturday from 8 AM to 5 PM. Students may borrow three books for seven days.",
            "tagalog": "Bukas ang library weekdays, 7:30 AM hanggang 7 PM, at Saturday, 8 AM hanggang 5 PM. Puwedeng humiram ng tatlong libro sa loob ng pitong araw.",
        },
        {
            "intent": "it_domain_agent",
            "terms": ["wifi", "password", "email account", "campus account", "reset password", "internet"],
            "query": "reset campus wifi email password account recovery",
            "english": "Use the campus account recovery page, verify your student email, and create a new password. If recovery fails, bring your student ID to the IT Help Desk.",
            "tagalog": "Buksan ang campus account recovery page, i-verify ang student email, at gumawa ng bagong password. Kapag hindi gumana, dalhin ang student ID sa IT Help Desk.",
        },
    ]
    for domain in domains:
        if _has_any(text, domain["terms"]):
            sources = search_documents(db, domain["query"], limit=2)
            return {
                "intent": domain["intent"],
                "answer": _answer(text, domain["english"], domain["tagalog"]),
                "sources": sources,
                "confidence": 0.93,
                "workflow": [
                    "Detected campus service intent",
                    f"Routed request to {domain['intent'].replace('_domain_agent', '').title()} Agent",
                    "Retrieved relevant knowledge chunks",
                    "Generated a grounded answer with source evidence",
                ],
            }
    return None


def answer_question(db: Session, message: str) -> dict[str, Any]:
    text = message.lower()

    inventory_write = _add_inventory_from_chat(db, message)
    if inventory_write:
        return inventory_write

    specialized_answer = _specialized_domain_answer(db, text, message)
    if specialized_answer:
        return specialized_answer

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
