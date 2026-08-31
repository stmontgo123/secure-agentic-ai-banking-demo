"""Role-filtered semantic policy retrieval using Oracle VECTOR_DISTANCE."""

from __future__ import annotations

import array
import os

import requests
from dotenv import load_dotenv

from transaction_tool import get_connection

load_dotenv()


def embed_question(question: str) -> array.array:
    base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    response = requests.post(
        f"{base}/api/embed",
        json={"model": os.environ.get("EMBED_MODEL", "nomic-embed-text"), "input": question},
        timeout=120,
    )
    response.raise_for_status()
    return array.array("f", response.json()["embeddings"][0])


def retrieve_policy(question: str, employee_role: str, limit: int = 3):
    """Filter authorization first, then rank permitted chunks by cosine distance."""
    query_vector = embed_question(question)
    if len(query_vector) != 768:
        raise RuntimeError(f"Expected 768 embedding dimensions, got {len(query_vector)}")

    # FETCH FIRST does not accept a bind consistently across Oracle versions,
    # so validate and interpolate only the small integer limit.
    limit = max(1, min(int(limit), 10))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT policy_id, title, chunk_text,
                       VECTOR_DISTANCE(embedding, :query_vector, COSINE) AS distance
                FROM policy_chunks
                WHERE embedding IS NOT NULL
                  AND (allowed_role = :employee_role OR allowed_role = 'ALL')
                ORDER BY distance
                FETCH FIRST {limit} ROWS ONLY
                """,
                query_vector=query_vector,
                employee_role=employee_role,
            )
            return cur.fetchall()


if __name__ == "__main__":
    role = os.getenv("EMPLOYEE_ROLE", "CUSTOMER_SERVICE")
    question = "What should I do when a customer's card is declined for unusual spending?"
    for policy_id, title, chunk_text, distance in retrieve_policy(question, role):
        text = chunk_text.read() if hasattr(chunk_text, "read") else str(chunk_text)
        print(f"{policy_id} | {title} | distance={distance}")
        print(text)
        print()
