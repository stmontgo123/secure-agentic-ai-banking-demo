# Expected Demo Output

A successful run should visibly demonstrate this sequence:

```text
TRANSACTION_LOOKUP -> SUCCESS
ACCOUNT_LOOKUP     -> SUCCESS
FRAUD_LOOKUP       -> SAFE_DATA_ONLY
POLICY_RETRIEVAL   -> AUTHORIZED_ONLY
PROMPT_ASSEMBLY    -> GROUNDED
LLM_RESPONSE       -> GENERATED
ACTION_REQUEST     -> PENDING_HUMAN_APPROVAL
HUMAN_REVIEW       -> APPROVED or REJECTED
```

For the synthetic transaction `847291`, the expected evidence is:

- Merchant: Best Buy
- Amount: $1,250
- Status: DECLINED
- Account: ACTIVE
- Available balance: $4,250
- Safe fraud description: high-value purchase inconsistent with recent activity
- Customer-service policies expected near the top: `CV-04` and `CA-12`
- Restricted policy `FR-09`: not returned to the `CUSTOMER_SERVICE` role

The model should explain that unusual-spending/fraud protection controls are the likely cause, that sufficient funds appear available, that customer verification is required before a retry, and that internal fraud scores/thresholds must not be disclosed.
