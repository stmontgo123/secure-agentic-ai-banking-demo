"""Create embeddings for policy chunks and store them in Oracle VECTOR columns."""

from __future__ import annotations

import array
import os

import requests
from dotenv import load_dotenv

from transaction_tool import get_connection

load_dotenv()


def as_text(value):
    return value.read() if hasattr(value, "read") else str(value)


def embed(text: str) -> array.array:
    base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    response = requests.post(
        f"{base}/api/embed",
        json={"model": os.environ.get("EMBED_MODEL", "nomic-embed-text"), "input": text},
        timeout=120,
    )
    response.raise_for_status()
    values = response.json()["embeddings"][0]
    return array.array("f", values)


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
                vector = embed(as_text(chunk_text))
                if len(vector) != 768:
                    raise RuntimeError(f"Expected 768 embedding dimensions, got {len(vector)}")
                cur.execute(
                    """
                    UPDATE policy_chunks
                    SET embedding = :embedding
                    WHERE chunk_id = :chunk_id
                    """,
                    embedding=vector,
                    chunk_id=chunk_id,
                )
                print(f"Embedded policy chunk {chunk_id} ({len(vector)} dimensions)")
        conn.commit()

    print("Policy embeddings loaded.")


if __name__ == "__main__":
    main()
