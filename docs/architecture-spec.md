# Architecture spec format

Architecture Review takes a small YAML (or JSON) description of an agentic system and
returns numbered failure points, fixes linked to the scenario catalog, and two
swimlane diagrams: as described, and fixed. The skill and the agent write this spec for you
from a plain-language scenario; you can also write or edit it by hand, or paste it into the
website's **Review** page.

## Shape

```yaml
title: SIM-swap agent            # short name, used in diagram titles
domain: telco                    # telco | fintech (free text is fine)
scenario: >-                     # the plain-language description you started from
  Agentic assistant in the app and IVR that handles SIM swap requests...
lanes:                           # top-to-bottom swimlanes, max 4 nodes each
  - name: Channel
    nodes:
      - {id: channel, title: Customer channel, sub: "App, IVR, chat", type: channel}
      - {id: s1, title: "", type: spacer}          # keeps the channel box half width
  - name: Orchestration
    nodes:
      - {id: agent, title: SIM-swap agent, sub: "LLM decides + acts", type: agent, attrs: {budget: true}}
      - {id: s2, title: "", type: spacer}          # the fix puts the policy engine here
  - name: Tools
    nodes:
      - {id: verify, title: Verify ID, sub: OTP or KBA, type: tool_identity, attrs: {auth_strength: weak}}
      - {id: swap, title: Swap SIM, sub: HSS + ICCID, type: tool_provision, attrs: {irreversible: true}}
edges:                           # straight arrows; same-lane edges route under boxes if blocked
  - {from: channel, to: agent}
bus: {from: agent, to: [verify, swap]}   # one shared line from the agent down to its tools
```

Keep titles to about 16 characters and subtitles to about 19 for a four-box lane;
wider lanes (fewer boxes) allow longer labels. `span: 2` makes a node twice as wide.

## Node types

| Type | Use for |
| --- | --- |
| `channel` | App, web, IVR, email inbox, alarm stream: where requests come from |
| `agent`, `router` | The LLM agent or router that plans and decides |
| `retriever`, `knowledge`, `vector_store` | RAG retrieval and knowledge stores |
| `tool_read` | Read-only tools (lookups, quotes, KPIs) |
| `tool_write` | Tools that change records (orders, vendor master, configuration) |
| `tool_payment` | Money movement (credits, transfers, payments) |
| `tool_provision` | Network or service provisioning (SIM swap, activation, porting) |
| `tool_identity` | Identity verification |
| `tool_fraud` | Fraud or risk scoring |
| `tool_notify` | Customer or staff notifications |
| `tool_code` | Code execution |
| `system_of_record` | BSS/OSS, core banking, CRM, ERP and other backends |
| `policy`, `human_approval`, `guardrail`, `audit`, `observability`, `eval`, `gateway` | Controls |
| `memory`, `cache`, `queue`, `external_agent` | Memory, caches, queues, partner agents |
| `spacer` | Empty slot to control box widths |

## Attributes the rules read

| Attribute | On | Meaning |
| --- | --- | --- |
| `irreversible: true` | write, payment, provision tools | Can't be undone (SIM swap, wire, disconnect) |
| `approval: true` | same | A human approves before execution |
| `idempotent: true` | same | Calls carry an idempotency key |
| `fail_mode: open/closed` | `tool_fraud`, `guardrail` | What happens on error or timeout |
| `auth_strength: weak/strong` | `tool_identity` | KBA, SMS OTP to the line at risk, or voice alone = weak |
| `notifies_existing_contacts: true` | `tool_notify` | Confirms to old line, email on file, app push |
| `acl_filter: true`, `public: true` | `retriever` | Filters by caller entitlements, or the corpus is public |
| `structured_facts: true` | `retriever` | Prices, balances or eligibility are read from documents |
| `untrusted_content: true`, `sanitized: true` | inputs, retrievers | Third-party content, and whether it's sanitised |
| `shared_admin_credentials: true` | tools | The tool runs with a broad service account |
| `sandboxed: true` | `tool_code` | Isolated, no egress |
| `user_scoped: true` | `memory`, `cache` | Keyed by tenant and user |
| `verified: true` | `external_agent` | Authenticated, claims verified |
| `sees_evidence: true` | `human_approval` | Approvers see system facts, not just a summary |
| `legacy: true`, `timeout: true` | tools, systems | Slow legacy backend, and whether calls time out |
| `budget: true` | `agent` | Step, time and cost caps on the loop |
| `makes_regulated_decision: true` | `agent` | The LLM decides credit, AML or similar outcomes |

Leave an attribute out when you don't know. Missing attributes count as "not in place",
which is the safe assumption for a review.

## Rules

The rules live in [`content/rules.yaml`](../content/rules.yaml). Component rules (R01-R17)
put numbered markers on boxes; platform rules (P01-P05) are listed as P1, P2... and become
a *Platform controls* lane in the fixed design. Every rule links to two or three scenarios
in the catalog for the full deep dive.
