import os
import time
from datetime import date
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import AgentFeedback, InventoryItem, KnowledgeDocument, Sale
from .schemas import (
    ChatRequest,
    ChatResponse,
    DataCreateResponse,
    DocumentCreate,
    ForecastPointCreate,
    FeedbackCreate,
    InventoryCreate,
    SaleCreate,
    UploadResponse,
)
from .services.agent import answer_question
from .services.analytics import dashboard_summary
from .services.forecast import forecast_next_month
from .services.seed import seed_database


DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://school-ai-campus-assistant.vercel.app",
]


def allowed_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "")
    extra_origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    return [*DEFAULT_ALLOWED_ORIGINS, *extra_origins]


app = FastAPI(
    title="School AI Campus Assistant",
    description="Agentic AI assistant for school records, document search, reports, and activity forecasting.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/")
def api_home() -> dict:
    return {
        "name": "School AI Campus Assistant API",
        "status": "ok",
        "frontend": "https://school-ai-campus-assistant.vercel.app",
        "health": "/health",
        "docs": "/docs",
        "chat": "/chat",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> dict:
    return dashboard_summary(db)


@app.get("/forecast/sales")
def get_sales_forecast(db: Session = Depends(get_db)) -> dict:
    return forecast_next_month(db)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> dict:
    started = time.perf_counter()
    result = answer_question(db, request.message)
    intent = result.get("intent", "")
    if "inventory" in intent or "sql" in intent:
        agent_name, data_path = "Records Agent", "SQLAlchemy structured records"
    elif "forecast" in intent:
        agent_name, data_path = "Forecast Agent", "scikit-learn forecast service"
    elif "rag" in intent:
        agent_name, data_path = "Knowledge Agent", "RAG document retrieval"
    elif "report" in intent:
        agent_name, data_path = "Report Agent", "Records + RAG + forecast tools"
    else:
        agent_name, data_path = "Campus Router", "Intent router + campus tools"
    result["agent_name"] = agent_name
    result["data_path"] = data_path
    result["response_time_ms"] = round((time.perf_counter() - started) * 1000)
    return result


@app.post("/feedback", response_model=DataCreateResponse)
def create_feedback(request: FeedbackCreate, db: Session = Depends(get_db)) -> dict:
    feedback = AgentFeedback(
        question=request.question,
        answer=request.answer,
        intent=request.intent,
        helpful=request.helpful,
        escalated=request.escalated,
        note=request.note,
        created_at=datetime.now(timezone.utc),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    message = "Support ticket created for registrar review." if feedback.escalated else "Feedback saved. Thank you."
    return {
        "kind": "ticket" if feedback.escalated else "feedback",
        "message": message,
        "item": {
            "id": feedback.id,
            "intent": feedback.intent,
            "helpful": feedback.helpful,
            "escalated": feedback.escalated,
            "status": "pending" if feedback.escalated else "reviewed",
        },
    }


@app.post("/data/inventory", response_model=DataCreateResponse)
def create_inventory_item(request: InventoryCreate, db: Session = Depends(get_db)) -> dict:
    existing = db.query(InventoryItem).filter(InventoryItem.sku == request.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists.")

    item = InventoryItem(
        sku=request.sku,
        product=request.product,
        category=request.category,
        stock_remaining=request.stock_remaining,
        reorder_level=request.reorder_level,
        supplier=request.supplier,
    )
    db.add(item)

    if request.note:
        db.add(
            KnowledgeDocument(
                title=f"Inventory note: {request.product}",
                source_type="AI_NOTE",
                content=request.note,
            )
        )

    db.commit()
    db.refresh(item)
    return {
        "kind": "inventory",
        "message": f"{item.product} was added to lab supply records.",
        "item": {
            "id": item.id,
            "sku": item.sku,
            "product": item.product,
            "category": item.category,
            "stock_remaining": item.stock_remaining,
            "reorder_level": item.reorder_level,
            "supplier": item.supplier,
            "note": request.note,
        },
    }


@app.post("/data/sales", response_model=DataCreateResponse)
def create_sale(request: SaleCreate, db: Session = Depends(get_db)) -> dict:
    try:
        sale_date = date.fromisoformat(request.date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Use date format YYYY-MM-DD.") from exc

    sale = Sale(
        date=sale_date,
        product=request.product,
        category=request.category,
        quantity=request.quantity,
        amount=request.amount,
        customer_segment=request.customer_segment,
    )
    db.add(sale)

    if request.note:
        db.add(
            KnowledgeDocument(
                title=f"Sales note: {request.product}",
                source_type="AI_NOTE",
                content=request.note,
            )
        )

    db.commit()
    db.refresh(sale)
    return {
        "kind": "sales",
        "message": f"{sale.product} was added to student activity records.",
        "item": {
            "id": sale.id,
            "date": sale.date.isoformat(),
            "product": sale.product,
            "category": sale.category,
            "quantity": sale.quantity,
            "amount": sale.amount,
            "customer_segment": sale.customer_segment,
            "note": request.note,
        },
    }


@app.post("/data/forecast-points", response_model=DataCreateResponse)
def create_forecast_point(request: ForecastPointCreate, db: Session = Depends(get_db)) -> dict:
    try:
        sale_date = date.fromisoformat(f"{request.month}-01")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Use month format YYYY-MM.") from exc

    sale = Sale(
        date=sale_date,
        product="Forecast Planning Input",
        category="Forecast",
        quantity=1,
        amount=request.revenue,
        customer_segment="Planning",
    )
    db.add(sale)

    if request.note:
        db.add(
            KnowledgeDocument(
                title=f"Forecast note: {request.month}",
                source_type="AI_NOTE",
                content=request.note,
            )
        )

    db.commit()
    db.refresh(sale)
    return {
        "kind": "forecast",
        "message": f"Forecast point for {request.month} was added to school activity history.",
        "item": {
            "id": sale.id,
            "month": request.month,
            "revenue": sale.amount,
            "note": request.note,
        },
    }


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)) -> list[dict]:
    docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.id).all()
    return [{"id": doc.id, "title": doc.title, "source_type": doc.source_type, "characters": len(doc.content)} for doc in docs]


@app.post("/documents/text", response_model=DataCreateResponse)
def create_text_document(request: DocumentCreate, db: Session = Depends(get_db)) -> dict:
    content = request.content
    if request.note:
        content = f"{content}\n\nInternal note: {request.note}"

    doc = KnowledgeDocument(title=request.title, source_type=request.source_type.upper(), content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "kind": "rag_document",
        "message": f"{doc.title} was added to the school document knowledge base.",
        "item": {
            "id": doc.id,
            "title": doc.title,
            "source_type": doc.source_type,
            "content": doc.content,
            "characters": len(doc.content),
            "note": request.note,
        },
    }


@app.post("/ai/notes", response_model=DataCreateResponse)
def create_ai_note(request: DocumentCreate, db: Session = Depends(get_db)) -> dict:
    doc = KnowledgeDocument(
        title=request.title,
        source_type="AI_NOTE",
        content=f"{request.content}\n\nWhy it matters: {request.note or 'No extra note provided.'}",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "kind": "ai_note",
        "message": f"AI note '{doc.title}' was saved and can be retrieved by RAG.",
        "item": {
            "id": doc.id,
            "title": doc.title,
            "source_type": doc.source_type,
            "content": doc.content,
            "characters": len(doc.content),
            "note": request.note,
        },
    }


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    raw = await file.read()
    content = raw.decode("utf-8", errors="ignore")
    doc = KnowledgeDocument(title=file.filename, source_type=file.filename.split(".")[-1].upper(), content=content)
    db.add(doc)
    db.commit()
    return {
        "filename": file.filename,
        "stored_characters": len(content),
        "message": "Document stored and available for RAG search.",
    }
