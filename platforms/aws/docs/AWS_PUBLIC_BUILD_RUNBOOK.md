# AWS Public Build Runbook

This is the sanitized AWS version of the build/run instructions. It intentionally omits account IDs, private endpoints, database passwords, and other environment-specific secrets.

## 1. Prerequisites

- An AWS account with access to Amazon Bedrock in the selected Region
- Amazon Nova Lite (or a compatible text model) available through Bedrock
- Amazon Titan Text Embeddings V2
- Aurora PostgreSQL-compatible or RDS PostgreSQL with the `vector` extension
- Python 3.10+
- An EC2 instance role or local AWS CLI profile authorized to call Bedrock
- AWS Secrets Manager recommended for database credentials

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

Do not store AWS access keys in `.env`. On EC2, use an instance role.

## 3. Configure the database

Create the demo database and application user, then apply:

```text
sql/schema.sql
sql/synthetic_data.sql
sql/policy_chunks.sql
```

The schema enables pgvector and uses `vector(1024)` for policy embeddings. All banking data is fictional.

## 4. Validate Amazon Bedrock

```bash
python src/test_bedrock.py
```

Expected embedding dimensions: `1024` with the default Titan V2 configuration in this project.

## 5. Validate PostgreSQL connectivity

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

Expected for the sample corpus: `3`.

## 7. Test role-filtered semantic retrieval

```bash
python src/search_policy.py
```

For `EMPLOYEE_ROLE=CUSTOMER_SERVICE`, `CV-04` and `CA-12` should be eligible; restricted `FR-09` should not appear.

## 8. Run the demonstration

```bash
./scripts/reset_demo.sh
python src/bank_agent.py 847291
python src/review_action.py
```

The AI should create a `PENDING` action and stop. The human review process separately changes it to `APPROVED` or `REJECTED`.

## 9. Verify the audit chronology

```sql
SELECT audit_id, event_time, employee_id, employee_role, stage, outcome
FROM ai_audit_log
WHERE transaction_id = 847291
ORDER BY audit_id;
```

## 10. Recommended AWS security posture for the demo

- Use an EC2 IAM role instead of long-lived AWS keys.
- Use Systems Manager Session Manager rather than opening SSH to the internet.
- Keep the database private and restrict 5432 to the application security group.
- Store database credentials in Secrets Manager where possible.
- For production, add private endpoints, centralized observability, formal model evaluation, and stronger action APIs.
