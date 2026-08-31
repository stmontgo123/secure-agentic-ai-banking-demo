# Banking Agent Demo - Master Guide

## Purpose

This repository demonstrates an enterprise pattern for agentic AI in a regulated environment: use AI to accelerate investigation and decision support without transferring authorization or accountability to the model.

The scenario is deliberately simple: a customer calls about a declined card purchase. The agent collects transaction and account evidence, retrieves only role-authorized policy and fraud context, asks a local Large Language Model (LLM) for a grounded recommendation, and creates a pending action for a human employee to approve or reject.

## Core thesis

> Agentic AI can increase employee capacity without removing human accountability.

## Business flow

1. Employee supplies the goal: investigate a declined transaction.
2. Agent queries deterministic transaction and account facts.
3. Fraud retrieval returns only fields permitted for the employee role.
4. Oracle vector search retrieves semantically relevant policy only from rows the role is authorized to see.
5. The LLM synthesizes the authorized evidence into a recommendation.
6. The agent creates a `PENDING` action request.
7. A human explicitly approves or rejects the action.
8. Oracle records the AI stages and human decision in an audit trail.

## AI concepts demonstrated

**Large Language Model (LLM).** Qwen2.5 runs locally through Ollama and performs bounded synthesis over supplied evidence.

**Embeddings.** `nomic-embed-text` converts policy text and the employee question into 768-dimensional vectors.

**Vector similarity.** Oracle `VECTOR_DISTANCE(..., COSINE)` ranks semantically similar authorized policy chunks. Lower cosine distance means a closer semantic match.

**Retrieval-Augmented Generation (RAG).** Approved policy content is retrieved at runtime and supplied to the LLM rather than relying on model memory.

**Agentic workflow.** The system pursues a goal, invokes multiple tools, gathers evidence, retrieves knowledge, reasons, proposes an action, stops for approval, and records the outcome.

**Human-in-the-loop (HITL).** The model does not approve its own consequential action. Human review is a separate state transition and audit event.

## Security model

The critical security idea is not a prompt instruction. It is the data-flow boundary.

`identity/role -> deterministic authorization -> permitted retrieval -> minimum context -> LLM -> approval gate -> action -> audit`

A customer-service employee cannot cause the model to reveal an internal fraud score because the customer-service query never returns that field. Likewise, restricted policy `FR-09` is filtered by role before vector results are returned.

This pattern is stronger than placing all data in the prompt and asking the model not to disclose sensitive content.

## What to show in a live demo

Use `demo/demo-script.md`. The strongest moments are:

- Show the evidence retrieval stages.
- Show that only `CV-04` and `CA-12` are retrieved for customer service.
- Explain that `FR-09` is not merely hidden in the UI; it is excluded before LLM context assembly.
- Pause when `ACTION_REQUEST` is `PENDING`.
- Run the separate human-review command.
- Show the later `HUMAN_REVIEW` audit event.

## Repository map

- `src/` - sanitized reference implementation
- `sql/` - schema, fictional source data, and policy chunks
- `scripts/reset_demo.sh` - safe transaction-scoped demo reset
- `demo/` - five-minute script, expected output, interview Q&A
- `architecture/` - Mermaid architecture plus visual assets
- `docs/PUBLIC_BUILD_RUNBOOK.md` - public setup/run instructions
- `docs/supporting/` - selected presentation/runbook artifacts
- `SECURITY.md` - public security posture and production-hardening notes

## Productionization roadmap

The proof of concept intentionally uses a small number of moving parts. A production banking implementation would normally introduce:

- enterprise identity and service identities
- private endpoints and segmented networking
- enterprise secrets management
- highly available application/model tiers
- model gateway/provider governance
- formal prompt/retrieval/generation evaluation
- policy compliance tests and adversarial testing
- centralized logs, metrics, traces, and SIEM integration
- authenticated, idempotent, rate-limited action APIs
- data classification, retention, and lineage controls
- disaster recovery and operational service-level objectives

The governance pattern should survive those substitutions: authorize first, minimize context, keep consequential authority explicit, and make important actions auditable.

## Portfolio positioning

A concise description for a recruiter or hiring manager:

> Designed and built a secure agentic AI banking proof of concept using Oracle AI Database vector search, Python, local LLMs, role-filtered RAG, human approval controls, and auditable workflow state. The project demonstrates how enterprise AI can automate evidence gathering and policy interpretation while preserving least privilege and human accountability.
