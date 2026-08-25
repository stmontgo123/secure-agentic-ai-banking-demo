# Supporting Artifact Index

The repository includes selected presentation and runbook artifacts that support different audiences.

| Artifact | Best audience | Purpose |
|---|---|---|
| `Banking_Agent_Master_Guide.md` | Everyone | Canonical overview and navigation document |
| `PUBLIC_BUILD_RUNBOOK.md` | Engineer / architect | Sanitized reproducible setup and demo flow |
| `Agentic_AI_Banking_Demo_Decision_Rationale_and_Defense_Guide.pdf` | Architect / interviewer | Explains why major design decisions were made and what alternatives were deferred |
| `Bank_Agent_Demo_Reset_Runbook.pdf` | Demo operator | Detailed reset, rerun, expected output and troubleshooting |
| `Oracle_26ai_Agentic_AI_Compute_Node_Runbook.pdf` | Engineer / architect | Supporting compute-node and runtime guidance |
| `Agentic_AI_Banking_Demo_Plain_Language_Deck.pptx` | Executive / business | Plain-language walkthrough of the scenario and controls |
| `Oracle_AI_Agent_Vector_Database_Expanded.pptx` | Technical audience | Deeper vector / RAG concepts |
| `Enterprise_AI_Agents_Oracle26ai_Executive_Deck_v1.0.pptx` | Executive | Broader enterprise agent / Oracle 26ai story |

**Version note:** Some early supporting artifacts document the initial free-tier model sizing (`qwen2.5:1.5b`). The final working command-line demo was validated with `qwen2.5:3b`. The repository source, `.env.example`, Master Guide, and Public Build Runbook use the final `3b` configuration and should be treated as authoritative for v1.0.
