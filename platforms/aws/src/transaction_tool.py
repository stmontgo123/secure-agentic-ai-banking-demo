"""Database access helpers for the AWS-native secure banking-agent demo.

The key design point remains deterministic data minimization: callers receive
only fields appropriate for the employee role. Amazon Bedrock is never used
to decide what data a user is allowed to see.
"""

from __future__ import annotations

import json
import os
from typing import Any

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

from aws_clients import load_db_secret

load_dotenv()


def _db_config() -> dict:
    secret = load_db_secret()
    return {
        "host": secret.get("host") or os.getenv("DB_HOST"),
        "port": int(secret.get("port") or os.getenv("DB_PORT", "5432")),
        "dbname": secret.get("dbname") or secret.get("database") or os.getenv("DB_NAME"),
        "user": secret.get("username") or os.getenv("DB_USER"),
        "password": secret.get("password") or os.getenv("DB_PASSWORD"),
        "sslmode": os.getenv("DB_SSLMODE", "require"),
    }


def get_connection() -> psycopg.Connection:
    """Open a TLS PostgreSQL connection to Aurora PostgreSQL or RDS PostgreSQL."""
    cfg = _db_config()
    missing = [k for k in ("host", "dbname", "user", "password") if not cfg.get(k)]
    if missing:
        raise RuntimeError(
            "Missing required database settings: " + ", ".join(missing) +
            ". Set DB_* variables or DB_SECRET_ARN."
        )

    conn = psycopg.connect(**cfg)
    register_vector(conn)
    return conn


def write_audit(
    transaction_id: int,
    stage: str,
    outcome: str,
    details: Any,
    *,
    employee_id: str | None = None,
    employee_role: str | None = None,
) -> None:
    """Persist one auditable step without placing secrets in the log."""
    employee_id = employee_id or os.getenv("EMPLOYEE_ID", "UNKNOWN")
    employee_role = employee_role or os.getenv("EMPLOYEE_ROLE", "UNKNOWN")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_audit_log (
                    employee_id, employee_role, transaction_id,
                    stage, details, outcome
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    employee_id,
                    employee_role,
                    transaction_id,
                    stage,
                    json.dumps(details, default=str),
                    outcome,
                ),
            )


def get_transaction(transaction_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT transaction_id, account_id, merchant, amount,
                       transaction_time, location, status, decline_code, csr_reason
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            return cur.fetchone()


def get_account(account_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT account_id, customer_id, account_status,
                       available_balance, card_last4
                FROM accounts
                WHERE account_id = %s
                """,
                (account_id,),
            )
            return cur.fetchone()


def get_safe_fraud_events(transaction_id: int, employee_role: str):
    """Return only fields explicitly allowed for the caller's role."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            if employee_role == "FRAUD_ANALYST":
                cur.execute(
                    """
                    SELECT fraud_event_id, transaction_id, rule_code,
                           safe_description, fraud_score, internal_notes
                    FROM fraud_events
                    WHERE transaction_id = %s
                    ORDER BY fraud_event_id
                    """,
                    (transaction_id,),
                )
            else:
                # CUSTOMER_SERVICE never receives fraud_score or internal_notes.
                cur.execute(
                    """
                    SELECT fraud_event_id, transaction_id, safe_description
                    FROM fraud_events
                    WHERE transaction_id = %s
                    ORDER BY fraud_event_id
                    """,
                    (transaction_id,),
                )
            return cur.fetchall()


def create_action_request(transaction_id: int, employee_id: str, proposed_action: str) -> int:
    """Create a PENDING request; the agent does not approve its own action."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO action_requests (
                    transaction_id, employee_id, proposed_action, approval_status
                ) VALUES (%s, %s, %s, 'PENDING')
                RETURNING action_id
                """,
                (transaction_id, employee_id, proposed_action),
            )
            return int(cur.fetchone()[0])
