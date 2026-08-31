"""Minimal Oracle connectivity check."""

from transaction_tool import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT USER FROM dual")
        print("Connection SUCCESS")
        print("User:", cur.fetchone()[0])
        cur.execute("SELECT transaction_id, merchant, amount, status FROM transactions WHERE transaction_id=847291")
        print("Demo transaction:", cur.fetchone())
