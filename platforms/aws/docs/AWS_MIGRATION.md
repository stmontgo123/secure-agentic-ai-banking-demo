# Oracle/OCI-to-AWS Migration Map

| Original implementation | AWS-native implementation |
|---|---|
| OCI compute / local host | Amazon EC2 (or ECS/Fargate) |
| Oracle AI Database | Amazon Aurora PostgreSQL-compatible or RDS PostgreSQL |
| Oracle `VECTOR(768)` | `pgvector vector(1024)` |
| `VECTOR_DISTANCE(..., COSINE)` | pgvector cosine operator `<=>` |
| Oracle wallet / mTLS connection | TLS PostgreSQL + Secrets Manager |
| Ollama local LLM | Amazon Bedrock |
| Qwen 2.5 generation | Amazon Nova Lite by default |
| nomic-embed-text | Amazon Titan Text Embeddings V2 |
| local secrets in `.env` | IAM role + Secrets Manager preferred |
| Oracle audit tables | Same audit pattern in PostgreSQL |

## What did not change

The security architecture is intentionally preserved:

1. Employee role is evaluated deterministically.
2. Restricted fraud fields are filtered before model context.
3. Policy rows are filtered by role before semantic ranking.
4. Only minimum authorized context is sent to Bedrock.
5. The model proposes; it does not approve or execute.
6. A separate human approval step is required.
7. Every material stage is written to `ai_audit_log`.

The LLM is still not the authorization layer.
