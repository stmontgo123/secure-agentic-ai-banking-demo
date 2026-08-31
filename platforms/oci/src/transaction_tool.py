"""Database access helpers for the secure banking-agent demo.

The key design point is deterministic data minimization: callers receive only
fields appropriate for the employee role. The LLM is never used to decide
what data a user is allowed to see.
"""

from __future__ import annotations

import json
import os
from typing import Any

import oracledb
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> oracledb.Connection:
    """Open an mTLS wallet connection to Oracle Autonomous AI Database."""
    required = ["DB_USER", "DB_PASSWORD", "DB_DSN", "WALLET_DIR", "WALLET_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    wallet_dir = os.environ["WALLET_DIR"]
    return oracledb.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dsn=os.environ["DB_DSN"],
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=os.environ["WALLET_PASSWORD"],
    )


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
                ) VALUES (
                    :employee_id, :employee_role, :transaction_id,
                    :stage, :details, :outcome
                )
                """,
                employee_id=employee_id,
                employee_role=employee_role,
                transaction_id=transaction_id,
                stage=stage,
                details=json.dumps(details, default=str),
                outcome=outcome,
            )
        conn.commit()


def get_transaction(transaction_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT transaction_id, account_id, merchant, amount,
                       transaction_time, location, status, decline_code, csr_reason
                FROM transactions
                WHERE transaction_id = :id
                """,
                id=transaction_id,
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
                WHERE account_id = :id
                """,
                id=account_id,
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
                    WHERE transaction_id = :id
                    ORDER BY fraud_event_id
                    """,
                    id=transaction_id,
                )
            else:
                # CUSTOMER_SERVICE never receives fraud_score or internal_notes.
                cur.execute(
                    """
                    SELECT fraud_event_id, transaction_id, safe_description
                    FROM fraud_events
                    WHERE transaction_id = :id
                    ORDER BY fraud_event_id
                    """,
                    id=transaction_id,
                )
            return cur.fetchall()


def create_action_request(transaction_id: int, employee_id: str, proposed_action: str) -> int:
    """Create a PENDING request; the agent does not approve its own action."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            action_id_var = cur.var(oracledb.NUMBER)
            cur.execute(
                """
                INSERT INTO action_requests (
                    transaction_id, employee_id, proposed_action, approval_status
                ) VALUES (
                    :transaction_id, :employee_id, :proposed_action, 'PENDING'
                )
                RETURNING action_id INTO :action_id
                """,
                transaction_id=transaction_id,
                employee_id=employee_id,
                proposed_action=proposed_action,
                action_id=action_id_var,
            )
            action_id = int(action_id_var.getvalue()[0])
        conn.commit()
    return action_id
