import json
import os
from typing import Any


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def _grounding_context(result: dict[str, Any]) -> str:
    payload = {
        "tool_answer": result.get("answer"),
        "intent": result.get("intent"),
        "sql_evidence": result.get("sql"),
        "rows": result.get("rows", [])[:8],
        "sources": result.get("sources", [])[:4],
        "workflow": result.get("workflow", []),
    }
    return json.dumps(payload, ensure_ascii=False, default=str)


def generate_grounded_answer(
    message: str,
    role: str,
    result: dict[str, Any],
) -> dict[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
    if not api_key:
        return {
            "answer": result["answer"],
            "provider": "Tool-grounded fallback",
            "model": "No external LLM configured",
            "status": "not_configured",
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = (
            f"User role: {role}\n"
            f"User question: {message}\n\n"
            f"Verified tool context:\n{_grounding_context(result)}"
        )
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Ari, the professional and friendly Ari Campus AI services assistant. "
                    "Answer using only the verified tool context. Never invent school policies, stock, "
                    "student status, SQL results, sources, or approvals. Preserve request IDs and exact "
                    "status values. Match the user's language: English, Filipino, Tagalog, or Taglish. "
                    "Use concise plain text in no more than three short paragraphs. If the tool context "
                    "does not contain an answer, clearly say that staff review is needed."
                ),
                temperature=0.2,
                max_output_tokens=450,
            ),
        )
        generated = (response.text or "").strip()
        if not generated:
            raise ValueError("Gemini returned an empty response.")
        return {"answer": generated, "provider": "Google Gemini", "model": model, "status": "active"}
    except Exception as exc:
        error_text = str(exc).lower()
        if any(term in error_text for term in ["401", "403", "permission", "api key", "unauthenticated"]):
            status = "authentication_failed"
        elif any(term in error_text for term in ["429", "quota", "resource_exhausted"]):
            status = "quota_exceeded"
        elif any(term in error_text for term in ["404", "model", "not found"]):
            status = "model_unavailable"
        else:
            status = "request_failed"
        return {
            "answer": result["answer"],
            "provider": "Tool-grounded fallback",
            "model": "Gemini unavailable",
            "status": status,
        }
