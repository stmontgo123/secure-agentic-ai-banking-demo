"""Role-filtered semantic policy retrieval using Aurora PostgreSQL + pgvector."""

from __future__ import annotations

from bedrock_models import embed_text
from transaction_tool import get_connection


def retrieve_policy(question: str, employee_role: str, limit: int = 3):
    """Filter authorization first, then rank permitted chunks by cosine distance."""
    query_vector = embed_text(question)
    limit = max(1, min(int(limit), 10))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT policy_id, title, chunk_text,
                       embedding <=> %s AS distance
                FROM policy_chunks
                WHERE embedding IS NOT NULL
                  AND (allowed_role = %s OR allowed_role = 'ALL')
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_vector, employee_role, query_vector, limit),
            )
            return cur.fetchall()


if __name__ == "__main__":
    import os
    role = os.getenv("EMPLOYEE_ROLE", "CUSTOMER_SERVICE")
    question = "What should I do when a customer's card is declined for unusual spending?"
    for policy_id, title, chunk_text, distance in retrieve_policy(question, role):
        print(f"{policy_id} | {title} | distance={distance}")
        print(chunk_text)
        print()
