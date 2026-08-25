"""Human approval gate for pending banking-agent actions."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from transaction_tool import get_connection, write_audit

load_dotenv()


def list_pending():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT action_id, transaction_id, employee_id,
                       proposed_action, approval_status, created_at
                FROM action_requests
                WHERE approval_status = 'PENDING'
                ORDER BY created_at, action_id
                """
            )
            return cur.fetchall()


def decide(action_id: int, decision: str) -> bool:
    decision = decision.upper()
    if decision not in {"APPROVE", "REJECT"}:
        raise ValueError("Decision must be APPROVE or REJECT")

    new_status = "APPROVED" if decision == "APPROVE" else "REJECTED"
    reviewer = os.getenv("EMPLOYEE_ID", "CSR001")
    role = os.getenv("EMPLOYEE_ROLE", "CUSTOMER_SERVICE")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT transaction_id FROM action_requests WHERE action_id=:id AND approval_status='PENDING'",
                id=action_id,
            )
            row = cur.fetchone()
            if not row:
                return False
            transaction_id = int(row[0])

            cur.execute(
                """
                UPDATE action_requests
                SET approval_status = :status,
                    approved_by = :reviewer,
                    approved_at = SYSTIMESTAMP
                WHERE action_id = :id
                  AND approval_status = 'PENDING'
                """,
                status=new_status,
                reviewer=reviewer,
                id=action_id,
            )
            updated = cur.rowcount
        conn.commit()

    if updated:
        write_audit(
            transaction_id,
            "HUMAN_REVIEW",
            new_status,
            {"action_id": action_id, "decision": decision},
            employee_id=reviewer,
            employee_role=role,
        )
        return True
    return False


def main() -> None:
    pending = list_pending()
    if not pending:
        print("No PENDING action requests found. Run bank_agent.py first.")
        return

    print("\n=== PENDING ACTION REQUESTS ===\n")
    for row in pending:
        print(f"Action ID       : {row[0]}")
        print(f"Transaction ID  : {row[1]}")
        print(f"Requested by    : {row[2]}")
        print(f"Proposed action : {row[3]}")
        print(f"Status          : {row[4]}")
        print(f"Created at      : {row[5]}")
        print()

    action_id = int(input("Action ID to review: ").strip())
    decision = input("Type APPROVE, REJECT, or SKIP: ").strip().upper()
    if decision == "SKIP":
        print("No change made.")
        return
    if decision not in {"APPROVE", "REJECT"}:
        print("Invalid decision. No change made.")
        return

    if decide(action_id, decision):
        print(f"Action {action_id} is now {'APPROVED' if decision == 'APPROVE' else 'REJECTED'}.")
    else:
        print("No update performed. The action may no longer be PENDING.")


if __name__ == "__main__":
    main()
