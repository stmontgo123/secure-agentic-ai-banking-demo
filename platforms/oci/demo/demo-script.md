# Five-Minute Demo Script

## 0:00 - Business problem

A customer calls because a $1,250 card purchase was declined. A service representative would normally gather transaction details, account status, fraud context, and policy guidance across several systems.

**Narration:** "The goal is not to replace the employee. The goal is to let AI perform the investigation and evidence assembly while keeping authorization and accountability with the human."

## 0:30 - Reset the demo

```bash
./scripts/reset_demo.sh
```

Confirm that generated `ACTION_REQUESTS` and `AI_AUDIT_LOG` rows are removed while source data and policy embeddings remain.

## 1:00 - Run the agent

```bash
python src/bank_agent.py 847291
```

Call out each visible step:

1. Transaction evidence retrieved.
2. Account evidence retrieved.
3. Safe fraud evidence retrieved.
4. Role-authorized policies retrieved with Oracle vector similarity search.
5. Grounded prompt assembled.
6. Local LLM recommendation generated.
7. A `PENDING` action request created.

## 2:30 - Explain the security boundary

For `CUSTOMER_SERVICE`, the fraud tool does not select `fraud_score` or `internal_notes`. The restricted `FR-09` policy is also filtered out before vector results are returned to the LLM.

**Narration:** "The AI does not decide what the employee is allowed to see. Authorization is deterministic and happens before the model receives context."

## 3:15 - Human approval

```bash
python src/review_action.py
```

Select the pending action and enter `APPROVE` or `REJECT`.

**Narration:** "The model can recommend, but it cannot approve its own consequential action."

## 4:00 - Show the audit trail

Query `AI_AUDIT_LOG` and show the sequence from evidence gathering through human review. The AI recommendation and human decision are separate events.

## 4:40 - Close

**Close:** "Agentic AI increases employee capacity by investigating, assembling evidence, interpreting authorized policy, and proposing an action - while the final controlled decision stays with the human and the full workflow remains auditable."
