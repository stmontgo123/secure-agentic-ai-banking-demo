"""AWS-native secure agentic banking demo.

The agent gathers deterministic evidence, retrieves only role-authorized policy,
asks Amazon Bedrock to synthesize a grounded recommendation, and creates a
PENDING action request. It never approves or executes the consequential decision.
"""

from __future__ import annotations

import os
import sys

from bedrock_models import generate_text
from search_policy import retrieve_policy
from transaction_tool import (
    create_action_request,
    get_account,
    get_safe_fraud_events,
    get_transaction,
    write_audit,
)


def build_prompt(transaction, account, fraud_events, policies) -> str:
    policy_context = "\n\n".join(
        f"{p[0]} - {p[1]}:\n{p[2]}" for p in policies
    )

    return f"""
You are assisting a bank employee with a declined-card investigation.

RULES
1. Answer only from the evidence and policies supplied below.
2. Do not invent facts or fill gaps with model memory.
3. Do not speculate about restricted fraud details.
4. Do not claim insufficient funds if the available balance covers the amount.
5. Explain the likely decline reason using the authorized evidence.
6. Explain the permitted next employee action.
7. Cite the policy IDs supporting the recommendation.
8. State when customer verification is required.
9. Do not approve, override, or retry the transaction yourself.
10. The human employee remains responsible for any consequential decision.

TRANSACTION EVIDENCE
{transaction}

ACCOUNT EVIDENCE
{account}

AUTHORIZED FRAUD EVIDENCE
{fraud_events}

AUTHORIZED POLICY EVIDENCE
{policy_context}

Return a concise employee-facing explanation with:
- likely cause
- account/funds assessment
- what may be communicated to the customer
- required verification
- recommended next action
- supporting policy IDs
""".strip()


def investigate(transaction_id: int) -> int:
    employee_id = os.getenv("EMPLOYEE_ID", "CSR001")
    employee_role = os.getenv("EMPLOYEE_ROLE", "CUSTOMER_SERVICE")

    transaction = get_transaction(transaction_id)
    if not transaction:
        raise RuntimeError(f"Transaction {transaction_id} was not found.")
    write_audit(transaction_id, "TRANSACTION_LOOKUP", "SUCCESS", {"found": True})
    print("[1] Transaction evidence retrieved from Aurora PostgreSQL")

    account = get_account(transaction[1])
    if not account:
        raise RuntimeError(f"Account {transaction[1]} was not found.")
    write_audit(transaction_id, "ACCOUNT_LOOKUP", "SUCCESS", {"account_id": account[0]})
    print("[2] Account evidence retrieved")

    fraud_events = get_safe_fraud_events(transaction_id, employee_role)
    write_audit(
        transaction_id,
        "FRAUD_LOOKUP",
        "SAFE_DATA_ONLY",
        {"event_count": len(fraud_events), "role": employee_role},
    )
    print(f"[3] Authorized fraud evidence retrieved ({len(fraud_events)} event(s))")

    question = "How should an employee resolve this declined card transaction caused by unusual spending?"
    policies = retrieve_policy(question, employee_role, limit=3)
    write_audit(
        transaction_id,
        "POLICY_RETRIEVAL",
        "AUTHORIZED_ONLY",
        {"policy_ids": [row[0] for row in policies], "role": employee_role},
    )
    print(f"[4] Authorized pgvector policy retrieval completed ({len(policies)} chunk(s))")
    for policy in policies:
        print(f"    - {policy[0]} {policy[1]}")

    prompt = build_prompt(transaction, account, fraud_events, policies)
    write_audit(
        transaction_id,
        "PROMPT_ASSEMBLY",
        "GROUNDED",
        {"policy_ids": [row[0] for row in policies], "fraud_event_count": len(fraud_events)},
    )
    print("[5] Grounded prompt assembled")

    recommendation = generate_text(prompt)
    write_audit(
        transaction_id,
        "LLM_RESPONSE",
        "GENERATED",
        {
            "provider": "Amazon Bedrock",
            "model": os.getenv("BEDROCK_GEN_MODEL", "amazon.nova-lite-v1:0"),
            "response": recommendation,
        },
    )
    print("[6] Amazon Bedrock response generated\n")
    print("=== GROUNDED RECOMMENDATION ===")
    print(recommendation)
    print()

    proposed_action = (
        f"Verify that the customer attempted transaction {transaction_id}. "
        "If verification succeeds and bank policy permits, allow the transaction to be retried."
    )
    action_id = create_action_request(transaction_id, employee_id, proposed_action)
    write_audit(
        transaction_id,
        "ACTION_REQUEST",
        "PENDING_HUMAN_APPROVAL",
        {"action_id": action_id, "proposed_action": proposed_action},
    )
    print(f"[7] Action request {action_id} created with status PENDING")
    print("    AI has NOT approved or executed the action.")
    return action_id


def main() -> None:
    transaction_id = int(sys.argv[1]) if len(sys.argv) > 1 else 847291
    investigate(transaction_id)


if __name__ == "__main__":
    main()
