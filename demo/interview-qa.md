# Architecture / Interview Q&A

**Why Oracle instead of a dedicated vector database?**  
The demo already needs relational transaction data, authorization metadata, action state, and audit records. Oracle AI Database can store those facts and vectorized policy content in one governed platform, avoiding another data store solely for the proof of concept.

**Why use vector search if the transaction is relational?**  
Structured facts use SQL. Semantic policy retrieval uses vector search. The design intentionally uses the appropriate retrieval method for each data type.

**Why is this agentic and not just RAG?**  
Retrieval-Augmented Generation (RAG) is one capability inside a larger workflow. The agent pursues a goal, calls multiple tools, gathers evidence, retrieves policy, synthesizes a recommendation, creates a pending action, pauses for human approval, and records the result.

**What prevents the model from exposing a fraud score?**  
For customer-service users, the database tool never selects the fraud-score or internal-notes fields. The model cannot disclose information that never enters its context.

**Why keep a human approval gate?**  
Evidence gathering and recommendation are reversible information tasks. Changing customer or transaction state is consequential. The approval gate separates machine-speed investigation from human accountability.

**What if the model hallucinates?**  
Generation is constrained to supplied evidence and authorized policy, the evidence can be shown to the reviewer, and consequential action remains behind human approval. A production system would add automated evaluation and policy-validation gates.

**Is this production-ready for a bank?**  
No. It is an architectural proof. Production would strengthen identity, private networking, secrets, model governance, high availability, observability, evaluation, authenticated action APIs, compliance controls, and disaster recovery.
