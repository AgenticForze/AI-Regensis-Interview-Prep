# The five-beat answer

Interviewers describe a production failure. Strong answers name the anti-pattern, explain
the mechanism, and give a concrete fix with a way to detect it.

| Beat | What to say | Example (rag-01) |
| --- | --- | --- |
| Symptom | What the team sees in production | Roaming answers wrong, bill disputes rising |
| Anti-pattern | The design mistake behind it | Fixed-size chunking splits the tariff table |
| Why it breaks | The mechanism, in the scenario's terms | The retrieved chunk has rates but no plan names, so the model borrows a neighbouring column |
| Fix | Concrete change, in the right layer, with a tool or number | Prices from the TMF620 catalog as a tool; row-level chunks with context headers |
| Interview line | One sentence that signals seniority | "If the BSS holds the fact, don't retrieve it from a PDF." |

Three habits that lift any answer:

1. **Ask one clarifying question first.** Scale, latency budget and risk level change the right fix.
2. **Say how you'd detect it.** A fix without a metric or alert is half an answer.
3. **Name the trade-off.** Every fix costs latency, money or complexity. Say which.

## Grading rubric (used by interview mode)

| Criterion | Met when the answer... |
| --- | --- |
| `names_antipattern` | Names the anti-pattern or root cause, not just the symptom |
| `explains_mechanism` | Explains why it breaks, in the scenario's terms |
| `concrete_fix` | Gives a concrete fix in the right layer (tool, pipeline, policy, data), not "improve the prompt" |
| `detection` | Says how to detect or measure it in production or CI |
| `tradeoff` | Names a trade-off or cost of the fix |

## Principles that recur across the catalog

- If a system of record holds the fact, call it as a tool; use RAG for explanations.
- Prompts guide; code enforces. Limits, permissions and approvals live in tools and policy engines.
- Assume every tool call can run twice (idempotency keys) and every input is untrusted.
- The less reversible the action, the more human the decision.
- Evaluate the parts and the whole; slice by intent, segment and risk; gate releases on evals.
- Trace what the model saw and did, meter cost per tenant, and plan the rollback before you need it.
