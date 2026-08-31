#!/usr/bin/env bash
# =============================================================================
# BANK AGENT DEMO RESET
# =============================================================================
# Deletes only generated demo state for one transaction:
#   - ACTION_REQUESTS
#   - AI_AUDIT_LOG
# Preserves source transaction/account/fraud/policy data and vector embeddings.
#
# Typical OCI demo host:
#   Linux user : opc
#   Directory  : /home/opc/bank-agent
#   DB user    : loaded from .env (normally BANKAPP)
# =============================================================================
set -euo pipefail

TRANSACTION_ID="${1:-847291}"
EXPECTED_OS_USER="${EXPECTED_OS_USER:-opc}"

if [[ "$(id -un)" != "$EXPECTED_OS_USER" ]]; then
  echo "ERROR: Run this as Linux user '$EXPECTED_OS_USER', not '$(id -un)'."
  exit 1
fi

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
import oracledb
from dotenv import load_dotenv

load_dotenv()
required = ["DB_USER", "DB_PASSWORD", "DB_DSN", "WALLET_DIR", "WALLET_PASSWORD"]
missing = [name for name in required if not os.getenv(name)]
if missing:
    sys.exit("ERROR: Missing required .env variables: " + ", ".join(missing))

transaction_id = int(os.environ["DEMO_TRANSACTION_ID"])
wallet_dir = os.environ["WALLET_DIR"]

conn = oracledb.connect(
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    dsn=os.environ["DB_DSN"],
    config_dir=wallet_dir,
    wallet_location=wallet_dir,
    wallet_password=os.environ["WALLET_PASSWORD"],
)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id=:id", id=transaction_id)
if cur.fetchone()[0] != 1:
    print(f"ERROR: Source transaction {transaction_id} was not found. No delete performed.")
    cur.close(); conn.close(); sys.exit(1)

cur.execute("SELECT COUNT(*) FROM action_requests WHERE transaction_id=:id", id=transaction_id)
actions_before = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ai_audit_log WHERE transaction_id=:id", id=transaction_id)
audit_before = cur.fetchone()[0]
print("\nCurrent generated state:")
print("  Action requests:", actions_before)
print("  Audit records  :", audit_before)

cur.execute("DELETE FROM action_requests WHERE transaction_id=:id", id=transaction_id)
actions_deleted = cur.rowcount
cur.execute("DELETE FROM ai_audit_log WHERE transaction_id=:id", id=transaction_id)
audit_deleted = cur.rowcount
conn.commit()

cur.execute("SELECT COUNT(*) FROM action_requests WHERE transaction_id=:id", id=transaction_id)
actions_after = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ai_audit_log WHERE transaction_id=:id", id=transaction_id)
audit_after = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM fraud_events WHERE transaction_id=:id", id=transaction_id)
fraud_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM policy_chunks WHERE embedding IS NOT NULL")
policy_vector_count = cur.fetchone()[0]

print("\nDeleted:")
print("  Action requests:", actions_deleted)
print("  Audit records  :", audit_deleted)
print("\nVerification:")
print("  Action requests remaining:", actions_after)
print("  Audit records remaining  :", audit_after)
print("  Source transaction       : PRESERVED")
print("  Fraud events             :", fraud_count)
print("  Embedded policies        :", policy_vector_count)

cur.close(); conn.close()
if actions_after or audit_after:
    sys.exit("ERROR: Reset did not produce an empty generated state.")
print("\nRESET COMPLETE")
PYCODE

echo
echo "NEXT:"
echo "  python src/bank_agent.py $TRANSACTION_ID"
echo "  python src/review_action.py"
