"""Create policy embeddings with Amazon Bedrock and store them in pgvector."""

from __future__ import annotations

from bedrock_models import embed_text
from transaction_tool import get_connection


def main() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chunk_id, chunk_text
                FROM policy_chunks
                WHERE embedding IS NULL
                ORDER BY chunk_id
                """
            )
            rows = cur.fetchall()

            for chunk_id, chunk_text in rows:
                vector = embed_text(str(chunk_text))
                cur.execute(
                    """
                    UPDATE policy_chunks
                    SET embedding = %s
                    WHERE chunk_id = %s
                    """,
                    (vector, chunk_id),
                )
                print(f"Embedded policy chunk {chunk_id} ({len(vector)} dimensions)")

    print("Policy embeddings loaded into Aurora PostgreSQL / pgvector.")


if __name__ == "__main__":
    main()
