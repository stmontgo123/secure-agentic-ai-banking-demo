#!/usr/bin/env bash
set -euo pipefail

TRANSACTION_ID="${1:-847291}"

if [[ ! -f .env ]]; then
  echo "ERROR: .env was not found in $(pwd)."
  exit 1
fi

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if ! [[ "$TRANSACTION_ID" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Transaction ID must be numeric."
  exit 1
fi

export DEMO_TRANSACTION_ID="$TRANSACTION_ID"

echo "This will delete generated action/audit rows for transaction $TRANSACTION_ID."
echo "Source banking data and policy vectors will be preserved."
read -r -p "Type RESET to continue: " confirmation
[[ "$confirmation" == "RESET" ]] || { echo "Reset cancelled."; exit 0; }

python - <<'PYCODE'
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "src")
from transaction_tool import get_connection

transaction_id = int(os.environ["DEMO_TRANSACTION_ID"])

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id=%s", (transaction_id,))
        if cur.fetchone()[0] != 1:
            raise SystemExit(f"ERROR: Source transaction {transaction_id} was not found.")

        cur.execute("SELECT COUNT(*) FROM action_requests WHERE transaction_id=%s", (transaction_id,))
        actions_before = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM ai_audit_log WHERE transaction_id=%s", (transaction_id,))
        audit_before = cur.fetchone()[0]

        print("\nCurrent generated state:")
        print("  Action requests:", actions_before)
        print("  Audit records  :", audit_before)

        cur.execute("DELETE FROM action_requests WHERE transaction_id=%s", (transaction_id,))
        actions_deleted = cur.rowcount
        cur.execute("DELETE FROM ai_audit_log WHERE transaction_id=%s", (transaction_id,))
        audit_deleted = cur.rowcount

        cur.execute("SELECT COUNT(*) FROM policy_chunks WHERE embedding IS NOT NULL")
        vectors = cur.fetchone()[0]

print("\nDeleted:")
print("  Action requests:", actions_deleted)
print("  Audit records  :", audit_deleted)
print("  Embedded policies preserved:", vectors)
print("\nRESET COMPLETE")
PYCODE

echo
echo "NEXT:"
echo "  python src/bank_agent.py $TRANSACTION_ID"
echo "  python src/review_action.py"
