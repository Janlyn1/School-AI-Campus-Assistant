from sqlalchemy.orm import Session

from ..models import KnowledgeDocument


def search_documents(db: Session, question: str, limit: int = 3) -> list[dict]:
    documents = db.query(KnowledgeDocument).all()
    if not documents:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = [doc.content for doc in documents]
        vectors = TfidfVectorizer(stop_words="english").fit_transform([question, *corpus])
        scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        ranked = sorted(zip(documents, scores), key=lambda item: item[1], reverse=True)
    except Exception:
        terms = set(question.lower().split())
        ranked = []
        for doc in documents:
            score = len(terms.intersection(set(doc.content.lower().split()))) / max(len(terms), 1)
            ranked.append((doc, score))
        ranked.sort(key=lambda item: item[1], reverse=True)

    results = []
    for doc, score in ranked[:limit]:
        if score <= 0:
            continue
        results.append(
            {
                "title": doc.title,
                "source_type": doc.source_type,
                "score": round(float(score), 3),
                "snippet": doc.content[:280],
            }
        )
    return results
