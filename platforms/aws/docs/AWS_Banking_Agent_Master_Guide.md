# Banking Agent Demo - AWS Master Guide

## Purpose

This repository demonstrates an enterprise pattern for agentic AI in a regulated environment: use AI to accelerate investigation and decision support without transferring authorization or accountability to the model.

The AWS edition uses Amazon Bedrock for generation and embeddings, Aurora PostgreSQL-compatible / RDS PostgreSQL for deterministic data and workflow state, and pgvector for semantic policy retrieval.

## Core thesis

> Agentic AI can increase employee capacity without removing human accountability.

## Business flow

1. Employee supplies the goal: investigate a declined transaction.
2. Agent queries deterministic transaction and account facts from PostgreSQL.
3. Fraud retrieval returns only fields permitted for the employee role.
4. Role filtering limits eligible policy rows before pgvector similarity ranking.
5. Amazon Bedrock synthesizes the authorized evidence into a recommendation.
6. The agent creates a `PENDING` action request.
7. A human explicitly approves or rejects the action.
8. The database records the AI stages and human decision in an audit trail.

## AWS services demonstrated

**Amazon Bedrock.** Managed model inference through AWS APIs. The reference implementation defaults to Amazon Nova Lite for generation.

**Amazon Titan Text Embeddings V2.** Converts policy text and employee questions into 1024-dimensional vectors in this demo.

**Aurora PostgreSQL-compatible / RDS PostgreSQL.** Stores deterministic banking evidence, action state, and audit state.

**pgvector.** Provides cosine vector similarity using the `<=>` operator. Authorization is applied before similarity ranking.

**AWS Identity and Access Management (IAM).** Workload identity for Bedrock and Secrets Manager calls.

**AWS Secrets Manager.** Recommended location for database credentials.

**AWS Systems Manager Session Manager.** Recommended administrative path for EC2 without opening inbound SSH.

## Security model

`identity/role -> deterministic authorization -> permitted retrieval -> minimum context -> Bedrock -> approval gate -> action -> audit`

The LLM remains downstream of authorization. A customer-service role cannot cause the model to reveal `fraud_score` or `internal_notes` because those fields are not returned by the tool. Restricted policy `FR-09` is excluded before vector ranking.

## Productionization roadmap

- enterprise identity federation and service identities
- private endpoints / VPC endpoints and segmented networking
- KMS-backed encryption strategy and secret rotation
- highly available application tiers and Aurora resilience
- model gateway / model-routing governance
- formal prompt, retrieval, and generation evaluation
- policy compliance tests and adversarial testing
- CloudWatch logs/metrics/traces and SIEM integration
- authenticated, idempotent, rate-limited action APIs
- data classification, retention, and lineage controls
- disaster recovery, SLOs, and operational runbooks

## Portfolio positioning

> Designed and built an AWS-native secure agentic AI banking proof of concept using Amazon Bedrock, Titan embeddings, Aurora PostgreSQL + pgvector, Python, role-filtered RAG, human approval controls, and auditable workflow state. The project demonstrates how enterprise AI can automate evidence gathering and policy interpretation while preserving least privilege and human accountability.
