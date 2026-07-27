from app.services.vector_store import _chunk_document, vector_store_status


def test_document_chunking_preserves_page_metadata():
    chunks = _chunk_document("Page 18. " + ("Enrollment requirements and policies. " * 80))

    assert len(chunks) > 1
    assert chunks[0][0] == 18
    assert all(len(content) <= 900 for _, content in chunks)


def test_sqlite_reports_honest_retrieval_fallback():
    status = vector_store_status()

    assert status["provider"] == "TF-IDF fallback"
    assert status["schema_ready"] is False
