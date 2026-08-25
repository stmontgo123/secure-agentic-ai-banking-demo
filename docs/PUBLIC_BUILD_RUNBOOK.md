# Public Build Runbook

This is the sanitized GitHub version of the build/run instructions. It intentionally omits tenancy-specific addresses, wallet contents, passwords, and private keys.

## 1. Prerequisites

- Oracle AI Database with native `VECTOR(768, FLOAT32)` support
- An application database user capable of creating the demo tables
- Oracle wallet / mTLS connectivity configured locally
- Python 3.10+
- Ollama reachable only from the local host or trusted application network
- `qwen2.5:3b` (generation) and `nomic-embed-text` (embeddings)

## 2. Clone and configure

```bash
git clone <your-repository-url>
cd secure-agentic-ai-banking-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Edit `.env` locally. Never commit it. The Python utilities read it with `python-dotenv`; the public scripts do not print secret values.

## 3. Create demo schema and data

Run, as the demo application schema owner:

```text
sql/schema.sql
sql/synthetic_data.sql
sql/policy_chunks.sql
```

All customer, account, transaction, fraud, and policy data are fictional.

## 4. Validate local model runtime

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
python src/test_ollama.py
```

Expected embedding dimensions: `768`.

## 5. Validate Oracle connectivity

```bash
python src/test_db.py
```

## 6. Create policy vectors

```bash
python src/embed_policies.py
```

Verify:

```sql
SELECT COUNT(*)
FROM policy_chunks
WHERE embedding IS NOT NULL;
```

Expected: `3`.

## 7. Test role-filtered semantic retrieval

```bash
python src/search_policy.py
```

For `EMPLOYEE_ROLE=CUSTOMER_SERVICE`, `CV-04` and `CA-12` should be eligible; restricted `FR-09` should not appear.

## 8. Run a demonstration

```bash
./scripts/reset_demo.sh
python src/bank_agent.py 847291
python src/review_action.py
```

The agent should create a `PENDING` action and stop. The human review process separately changes it to `APPROVED` or `REJECTED`.

## 9. Verify audit chronology

```sql
SELECT audit_id, event_time, employee_id, employee_role, stage, outcome
FROM ai_audit_log
WHERE transaction_id = 847291
ORDER BY audit_id;
```

The expected sequence is documented in `demo/expected-output.md`.
