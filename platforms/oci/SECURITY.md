# Security Notes

This repository is a public-safe reference implementation of a synthetic banking proof of concept. It is not a production banking platform and it does not contain real customer data, production credentials, Oracle wallet files, or employer/client source material.

## Security model demonstrated

The most important control is the order of operations:

`employee identity -> deterministic authorization -> permitted data/tool retrieval -> minimum context -> LLM reasoning -> human approval -> action -> audit`

The Large Language Model (LLM) is downstream of authorization. For the `CUSTOMER_SERVICE` role, the fraud retrieval tool intentionally selects only safe fields. Restricted fraud scores and internal notes are never placed into the model context. Policy retrieval is also role-filtered before vector similarity ranking is returned to the model.

Consequential action is separated from recommendation. The agent creates a `PENDING` action request; a human must explicitly approve or reject it. The decision is then written to an audit table as a separate event.

## Never commit

Do not commit `.env`, database passwords, wallet passwords, Oracle wallet files, SSH private keys, tokens, certificates, or screenshots containing credentials. The repository `.gitignore` blocks common secret-bearing files, but that is only a safety net.

Before publishing, run a secret scanner such as Gitleaks or TruffleHog and manually review the Git history. Removing a secret from the latest commit does not remove it from prior Git history.

## Production hardening

A production implementation would require stronger identity and access management, private networking, enterprise secret management, model governance, centralized logging/metrics/tracing, Security Information and Event Management (SIEM) integration, high availability, disaster recovery, authenticated action APIs, formal AI evaluation, red-team testing, data classification, and change-management controls.
