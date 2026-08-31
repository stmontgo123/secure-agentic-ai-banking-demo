# Architecture

## End-to-end control flow

```mermaid
flowchart TD
    U[Bank Employee] --> A[Python Banking Agent]
    A --> T[Transaction / Account SQL]
    A --> F[Role-scoped Fraud Tool]
    A --> R[Role-filtered Oracle VECTOR Retrieval]
    T --> C[Minimum Authorized Context]
    F --> C
    R --> C
    C --> L[Local LLM - Ollama / Qwen2.5]
    L --> P[Recommendation]
    P --> Q[ACTION_REQUEST = PENDING]
    Q --> H{Human Review}
    H -->|Approve| AP[APPROVED]
    H -->|Reject| RJ[REJECTED]
    A --> AU[AI_AUDIT_LOG]
    H --> AU
```

## Trust sequence

```mermaid
flowchart LR
    I[Employee Identity / Role] --> Z[Deterministic Authorization]
    Z --> D[Permitted Data + Policy]
    D --> M[Minimum Context]
    M --> L[LLM Reasoning]
    L --> G[Human Approval Gate]
    G --> X[Controlled Action]
    X --> A[Audit]
```

## Core design rule

**Retrieval relevance never overrides authorization.** The system first determines what the employee is permitted to retrieve; semantic similarity ranking is performed only within that permitted set.
