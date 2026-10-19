# Architecture Review workflow

## From description to spec

Map each thing the user mentions to a node:

| User says | Node type | Attributes to consider |
| --- | --- | --- |
| app, IVR, chat, email inbox, alarm stream | `channel` | `untrusted_content: true` for email/uploads from third parties |
| "the agent", assistant, copilot, planner | `agent` | `budget: true` only if step/cost limits are mentioned; `makes_regulated_decision: true` if it decides credit, AML or similar |
| looks up, checks, quotes | `tool_read` | `legacy: true` for mainframe/OSS/bureau; `timeout: true` if mentioned |
| creates, updates, cancels, changes config | `tool_write` | `irreversible`, `approval`, `idempotent`, `shared_admin_credentials` |
| pays, refunds, credits, transfers | `tool_payment` | same as write |
| activates, swaps SIM, ports, provisions | `tool_provision` | same as write |
| verifies identity (OTP, KBA, voice, passkey) | `tool_identity` | `auth_strength: weak` for KBA, SMS OTP to the line at risk, voice alone |
| fraud or risk score | `tool_fraud` | `fail_mode: closed` only if stated |
| sends confirmation, SMS, email | `tool_notify` | `notifies_existing_contacts: true` only if old contacts are notified |
| searches documents, RAG | `retriever` | `acl_filter`, `public`, `structured_facts` (prices/balances from docs), `untrusted_content` |
| runs code | `tool_code` | `sandboxed: true` only if stated |
| remembers, memory, cache | `memory` / `cache` | `user_scoped: true` only if stated |
| partner's agent, A2A | `external_agent` | `verified: true` only if stated |
| human approves, analyst reviews | `human_approval` | `sees_evidence: true` if approvers see system facts |
| CRM, BSS, OSS, core banking, ERP | `system_of_record` | `legacy: true` |

Rules of thumb:

- One lane per layer: inputs/channel, orchestration, tools/knowledge, systems of record.
  Max 4 nodes per lane; put a `spacer` next to a lone agent so the fix can add a policy engine beside it.
- Use a `bus` from the agent to its tools, and edges from tools down to systems of record.
- Titles about 16 characters, subtitles about 19. Quote labels containing commas.
- Unknown means absent. The review then flags it, and you say in your answer that it's an
  assumption the user can correct.

## Reading the output

- Numbered findings (1, 2, 3...) are component failure points with red markers on the
  boxes, ordered top to bottom, left to right.
- P1, P2... are platform gaps (tracing, audit, eval gate, gateway, guardrails). They appear
  as a *Platform controls* lane in the fixed design.
- Each finding lists 2-3 scenario ids. Offer them as deep dives (`aap.py scenario <id>`).

## Worked example

`python scripts/aap.py ref telco-sim-swap-agent > sim.yaml` then
`python scripts/aap.py review sim.yaml --out sim-review` gives six failure points:
policy only in the prompt (agent), weak identity check, fraud check fails open, no human
gate and non-idempotent swap (both on the swap tool), and confirmation only to the new SIM,
plus five platform gaps. Interview line: "In an agentic SIM swap, the LLM is the
receptionist, not the vault keeper."
