# Secure Agentic AI Banking Platform

A multicloud enterprise AI reference architecture demonstrating secure agentic AI, Retrieval-Augmented Generation (RAG), deterministic authorization, human-in-the-loop controls, vector search, and auditability.

## Choose Your Platform

### Oracle Cloud Infrastructure (OCI)

[View the OCI implementation](platforms/oci/README.md)

- Oracle AI Database
- Oracle Vector Search
- Oracle Cloud Infrastructure (OCI)
- Python orchestration
- Local Large Language Model (LLM)
- Role-aware Retrieval-Augmented Generation (RAG)
- Human-in-the-loop approval
- Auditable AI workflow

### Amazon Web Services (AWS)

[View the AWS implementation](platforms/aws/README.md)

- Amazon Bedrock
- Amazon Nova
- Amazon Titan Text Embeddings
- Amazon Aurora PostgreSQL / Amazon RDS for PostgreSQL
- pgvector
- AWS Identity and Access Management (IAM)
- AWS Secrets Manager
- Python orchestration
- Retrieval-Augmented Generation (RAG)
- Human-in-the-loop approval
- Auditable AI workflow

## Common Security Model

Both implementations preserve the same security model:

```text
Employee Identity / Role
        |
        v
Deterministic Authorization
        |
        v
Permitted Data + Policy Retrieval
        |
        v
Minimum Authorized Context
        |
        v
Large Language Model
        |
        v
Recommended Action
        |
        v
PENDING Human Approval
        |
        v
APPROVED / REJECTED
        |
        v
Audit Trail
```

The Large Language Model is not the authorization layer.

Restricted information is removed before model reasoning, consequential actions remain subject to human approval, and material AI and human decisions are auditable.

## Multicloud Design

```text
                Secure Agentic AI Banking
                         |
             +-----------+-----------+
             |                       |
             v                       v
      OCI Implementation       AWS Implementation

      Oracle AI Database       Aurora PostgreSQL
      Oracle Vector Search     pgvector
      OCI                      AWS
      Local / OCI models       Amazon Bedrock
                               Nova + Titan
```

The cloud implementation can change without changing the enterprise governance model.

> **AI governance should survive a change in cloud provider.**

## Common Business Scenario

A customer calls because a **$1,250 card purchase has been declined**.

The AI agent:

1. retrieves deterministic transaction and account facts;
2. retrieves only fraud information authorized for the employee role;
3. performs role-filtered semantic policy retrieval;
4. supplies only approved context to the Large Language Model;
5. generates a grounded recommendation;
6. creates a `PENDING` action request;
7. requires explicit human approval or rejection; and
8. records material AI and human activity for auditability.

## Repository Structure

```text
secure-agentic-ai-banking-demo/
|
├── README.md
|
└── platforms/
    |
    ├── oci/
    |   ├── README.md
    |   ├── src/
    |   ├── sql/
    |   ├── scripts/
    |   ├── architecture/
    |   ├── demo/
    |   └── docs/
    |
    └── aws/
        ├── README.md
        ├── src/
        ├── sql/
        ├── scripts/
        ├── infra/
        └── docs/
```

## What This Portfolio Demonstrates

- Enterprise Agentic AI architecture
- Generative Artificial Intelligence (GenAI)
- Retrieval-Augmented Generation (RAG)
- Vector search and embeddings
- Multicloud architecture
- Least-privilege model context
- Deterministic authorization before AI reasoning
- Human-in-the-loop controls
- AI governance and auditability
- Vendor-independent architecture design

## Design Philosophy

This project is not simply about making a Large Language Model answer a banking question.

It demonstrates how an enterprise can introduce AI without surrendering security boundaries, authorization controls, operational accountability, or human decision authority.

The cloud services may change.

**The governance model should not.**
