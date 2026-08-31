# Secure Agentic AI Banking Demo — AWS Edition

**AWS-native enterprise AI proof of concept showing how agentic AI can increase employee capacity without removing human accountability.**

This version runs the banking demo on **Amazon Web Services (AWS)** using **Amazon Bedrock**, **Amazon Aurora PostgreSQL / Amazon RDS for PostgreSQL**, **pgvector**, Python orchestration, role-aware authorization, human approval, and auditability.

> Portfolio note: all banking records and policies in this repository are fictional. Do not place real customer data, AWS keys, database passwords, or production secrets in Git.

## AWS architecture

```text
Employee
   |
Python Agent on EC2 / ECS / local workstation
   |
   +--> Aurora PostgreSQL / RDS PostgreSQL
   |      - deterministic transaction/account evidence
   |      - role-scoped fraud evidence
   |      - pgvector policy RAG
   |      - action_requests
   |      - ai_audit_log
   |
   +--> Amazon Bedrock
          - Titan Text Embeddings V2
          - Amazon Nova Lite
```

## Why this remains a secure agentic demo

```text
Employee role
    -> deterministic authorization
    -> permitted data and policy retrieval
    -> minimum context
    -> Amazon Bedrock reasoning
    -> PENDING action
    -> human approval / rejection
    -> audit
```

Amazon Bedrock is **not** the authorization layer. For `CUSTOMER_SERVICE`, restricted fields such as `fraud_score` and `internal_notes` are removed before any model call.

## Technology

| Area | AWS implementation |
|---|---|
| Relational data | Aurora PostgreSQL or RDS PostgreSQL |
| Vector search | pgvector |
| Embeddings | Amazon Titan Text Embeddings V2 |
| Generation | Amazon Nova Lite through Amazon Bedrock |
| Orchestration | Python |
| AWS auth | IAM role / standard AWS credential chain |
| DB secrets | AWS Secrets Manager recommended |
| Authorization | deterministic SQL/tool filtering before Bedrock |
| Human control | separate PENDING -> APPROVED/REJECTED step |
| Audit | `ai_audit_log` in PostgreSQL |

## Quick start

### 1. Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure AWS credentials

For EC2, attach an IAM role. For a workstation, use your normal AWS CLI profile:

```bash
aws sts get-caller-identity
```

Do not put AWS access keys in this repository.

### 3. Create Aurora PostgreSQL or RDS PostgreSQL

Use PostgreSQL with the `vector` extension available. Keep the database private and allow port 5432 only from the application security group.

Create database/user as appropriate, then run:

```bash
psql "$YOUR_CONNECTION_STRING" -f sql/schema.sql
psql "$YOUR_CONNECTION_STRING" -f sql/synthetic_data.sql
psql "$YOUR_CONNECTION_STRING" -f sql/policy_chunks.sql
```

### 4. Configure `.env`

Set the database endpoint/credentials or, preferably, `DB_SECRET_ARN`.

Default Bedrock models:

```text
BEDROCK_GEN_MODEL=amazon.nova-lite-v1:0
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
EMBED_DIMENSIONS=1024
```

### 5. Test services

```bash
python src/test_bedrock.py
python src/test_db.py
```

### 6. Create policy embeddings

```bash
python src/embed_policies.py
```

### 7. Run the demo

```bash
./scripts/reset_demo.sh
python src/bank_agent.py 847291
python src/review_action.py
```

## Successful run proves

- deterministic structured evidence retrieval
- Bedrock embeddings + pgvector semantic policy search
- Retrieval-Augmented Generation (RAG)
- explicit multi-step agent orchestration
- role-aware least-privilege context
- data minimization before model reasoning
- grounded recommendation generation
- human-in-the-loop approval
- independent audit events for AI and human decisions
- provider separation: governance is outside the model

## Production boundary

This is a proof of concept, not production banking software. A production implementation should add stronger identity federation, private endpoints/VPC endpoints, AWS KMS encryption strategy, Secrets Manager rotation, database high availability and backup policy, CloudWatch observability, Security Hub/GuardDuty integration, formal model evaluation, prompt-injection testing, authenticated action APIs, approval segregation of duties, data classification, and compliance/change-management controls.

See `docs/AWS_MIGRATION.md` and `infra/README.md`.


## AWS supporting portfolio artifacts

See `docs/AWS_ARTIFACT_INDEX.md` for the AWS-native slide decks, deployment runbooks, reset runbook, and architecture defense guide.
