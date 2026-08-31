"""Simple Aurora/RDS PostgreSQL connectivity test."""

from transaction_tool import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user, version()")
        db, user, version = cur.fetchone()
        print("Database:", db)
        print("User:", user)
        print("PostgreSQL:", version.split(",")[0])

        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("pgvector extension is not installed. Run sql/schema.sql.")
        print("pgvector:", row[0])

print("SUCCESS: database connectivity is working.")
