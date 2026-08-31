# AWS infrastructure notes

Recommended demo topology:

```text
Browser/SSH
   |
EC2 demo host (private or tightly restricted security group)
   |-- IAM role --> Amazon Bedrock
   |                 |-- Amazon Nova Lite (generation)
   |                 `-- Titan Text Embeddings V2
   |
   `-- TLS 5432 --> Aurora PostgreSQL / RDS PostgreSQL
                     `-- pgvector
```

## Security groups

- Database inbound: TCP 5432 only from the EC2 application security group.
- EC2 inbound: restrict SSH to your IP, or better, use AWS Systems Manager Session Manager.
- Do not make PostgreSQL public for the portfolio demo.

## IAM

Attach `bedrock-iam-policy.json` to the EC2 instance role. Tighten the Resource values for production.

For Secrets Manager, store a secret with this shape:

```json
{
  "username": "bankapp",
  "password": "REPLACE_ME",
  "host": "your-cluster.cluster-xxxx.us-east-1.rds.amazonaws.com",
  "port": 5432,
  "dbname": "bankdemo"
}
```

Set only `DB_SECRET_ARN` in `.env` when using the secret.

## Bedrock model access

Use a Region where the selected Bedrock models are available. If your account/Region requires
an inference profile rather than the direct model ID, set `BEDROCK_GEN_MODEL` to that profile ID.
The code does not hard-code AWS access keys; use an IAM role on EC2/ECS/Lambda.
