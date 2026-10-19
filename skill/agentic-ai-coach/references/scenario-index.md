# Scenario index

All 360 scenarios by topic. Use `scripts/aap.py scenario <id>` for the full answer.

## 1. RAG (`rag`)

Most RAG failures are retrieval failures that look like LLM failures. If the right chunk is not in the top-k, no prompt will save you. And if a fact already lives as structured data in a system of record (product catalog, core banking, billing), call that system as a tool instead of retrieving a PDF copy of it.

- `rag-01` [telco, high] Fixed-size chunking splits the roaming tariff table
- `rag-02` [fintech, high] Vector-only search confuses chargeback reason codes
- `rag-03` [telco, medium] No reranker for broadband troubleshooting articles
- `rag-04` [fintech, high] Stuffing 30 chunks mixes fund share classes
- `rag-05` [fintech, high] Stale index quotes the old savings APY
- `rag-06` [fintech, critical] Relationship-manager copilot surfaces a SAR memo
- `rag-07` [telco, high] Embedding model upgraded without reindexing
- `rag-08` [telco, medium] Follow-up question retrieved without its history
- `rag-09` [fintech, high] Scanned loan agreements parsed as flat text
- `rag-10` [fintech, high] Card benefits bot invents trip insurance
- `rag-11` [telco, medium] Early termination fee chunk has no context
- `rag-12` [fintech, medium] RAG used to total quarterly dining spend
- `rag-13` [telco, medium] Six copies of the SIM activation guide after a merger
- `rag-14` [fintech, high] Old and new overdraft fee policies both retrieved
- `rag-15` [fintech, high] AML policy assistant gives answers with no citations
- `rag-16` [telco, medium] KB migration drops quality and nobody can localize it
- `rag-17` [telco, medium] Multi-hop question about maintenance and SLA penalties
- `rag-18` [fintech, high] Fraud-call agent assist too slow to use
- `rag-19` [fintech, critical] Merchant evidence PDF carries a hidden instruction
- `rag-20` [telco, medium] Spanish questions miss Spanish knowledge articles

## 2. LLM Evals (`llm-evals`)

An eval suite is a product spec written as tests. If your evals do not fail when customers are unhappy or regulators would be, they measure the wrong thing. In Telco and FinTech that means slicing by intent, product and risk tier, and treating compliance failures as release blockers rather than averages.

- `eval-01` [telco, high] Bill-explanation prompt shipped after a vibe check
- `eval-02` [fintech, critical] ROUGE scores a collections-call summary that drops the dispute
- `eval-03` [telco, medium] LLM judge loves retention chats humans rate poorly
- `eval-04` [fintech, medium] Complaint classifier judged on a 1-10 scale
- `eval-05` [telco, medium] Eval set frozen before the eSIM-only phone launch
- `eval-06` [fintech, high] Investment-app assistant tested only on friendly questions
- `eval-07` [telco, medium] Prompt A/B declared a winner on 100 examples
- `eval-08` [fintech, high] KYC extraction few-shots leaked into the eval set
- `eval-09` [telco, high] 92% overall hides 55% on business billing disputes
- `eval-10` [fintech, critical] No safety suite before the investing assistant launch
- `eval-11` [telco, medium] Offline gains that never move first-contact resolution
- `eval-12` [fintech, medium] Same model grades its own dispute letters
- `eval-13` [telco, medium] Order-capture pipeline regresses and nobody knows which step
- `eval-14` [fintech, medium] Best fraud-summary prompt is too slow and too costly
- `eval-15` [telco, high] Prompt tweak breaks the B2B quote JSON for a key account
- `eval-16` [fintech, high] Engineers label SAR narrative quality
- `eval-17` [telco, medium] Fifty prompt iterations overfit the eval set
- `eval-18` [fintech, high] Payment instructions from emails fail to parse 3% of the time
- `eval-19` [telco, high] Unpinned model alias changes refusal behaviour overnight
- `eval-20` [fintech, medium] Eval dashboard with no owner and no threshold

## 3. Agent Frameworks (`agent-frameworks`)

The best production agent is often a workflow with one or two LLM decisions in it. Give the model autonomy only where the path can't be known in advance, and keep money movement, provisioning and security decisions in deterministic, idempotent, permission-scoped code.

- `agf-01` [telco, high] Port-in processing built as a free-roaming agent
- `agf-02` [fintech, high] Reconciliation agent loops all night on one break
- `agf-03` [telco, medium] Care agent exposed to 60 BSS APIs
- `agf-04` [fintech, critical] Payment tool amount in cents read as dollars
- `agf-05` [telco, high] Care agent issues a $400 goodwill credit on its own
- `agf-06` [fintech, critical] Retry after timeout sends a wire twice
- `agf-07` [telco, medium] B2B order agent loses state on a pod restart
- `agf-08` [fintech, medium] Five agents for a loan pre-qualification
- `agf-09` [telco, medium] Framework default prompt overrides the brand voice
- `agf-10` [telco, medium] 80 KB of usage records dumped into the agent context
- `agf-11` [fintech, medium] Agent retries an opaque KYC vendor error ten times
- `agf-12` [telco, critical] Care agent runs with an admin BSS service account
- `agf-13` [fintech, medium] Account-closure plan ignores pending transactions
- `agf-14` [telco, medium] Diagnosis agent tells the dispatch agent to see above
- `agf-15` [fintech, medium] Mortgage document agent runs inside a 30-second HTTP call
- `agf-16` [telco, high] Provider outage takes the care bot down at bill-run time
- `agf-17` [fintech, high] Agent computes a loan payoff and gets daily interest wrong
- `agf-18` [telco, medium] Three-hour troubleshooting session forgets the original fault
- `agf-19` [fintech, critical] Pay John sends money to the wrong John
- `agf-20` [telco, medium] Frontier model used for every care-flow step

## 4. Agent Evals (`agent-evals`)

Agents are judged on outcomes, trajectories and side effects, not on a single reply. Check the final state of the BSS or core-banking system, the path the agent took to get there, what it cost, and whether it would do the same thing ten times out of ten.

- `aev-01` [telco, high] eSIM agent says activated, but no profile was installed
- `aev-02` [fintech, high] Dispute agent grants provisional credit before verifying identity
- `aev-03` [telco, medium] Plan-change evals demand one exact tool sequence
- `aev-04` [fintech, critical] Collections agent eval sends real emails to customers
- `aev-05` [telco, high] Clean mocks hide real BSS behaviour
- `aev-06` [fintech, high] KYC remediation agent passes once, fails three runs in ten
- `aev-07` [telco, medium] Plan-change agent tested with complete one-line requests
- `aev-08` [fintech, medium] New agent version is 3% better and 4 times the cost
- `aev-09` [telco, high] Retention agent waives the termination fee under pressure
- `aev-10` [fintech, medium] 20% failure rate with no idea which decision failed
- `aev-11` [telco, medium] Port-in agent gives up on the first rejection
- `aev-12` [fintech, critical] Agent says the card is frozen but never called the tool
- `aev-13` [telco, medium] Framework chosen on a public benchmark fails on BSS workflows
- `aev-14` [fintech, medium] Agent eval scores swing with live FX rates
- `aev-15` [telco, medium] B2B move agent fine at 3 steps, lost at 30
- `aev-16` [fintech, critical] Accounts-payable agent changes a vendor's bank details from an email
- `aev-17` [telco, medium] Automated scores look fine, but nobody reads the traces
- `aev-18` [fintech, high] Planner prompt change silently breaks the payment executor
- `aev-19` [telco, medium] Judge approves an answer that contradicts the tool result
- `aev-20` [fintech, high] Offline evals pass while customers redo tasks by hand

## 5. Observability (`observability`)

Observability means you can answer a new question about production behaviour without shipping new code. In LLM systems a 200 OK can still be a wrong answer, a promise the company must honour, or a regulatory breach, so you need traces of what the model saw and did, quality signals, cost per tenant, and SLOs with owners.

- `obs-01` [telco, high] All dashboards green while the bot invents outage ETAs
- `obs-02` [fintech, high] Wrong escrow answer cannot be reconstructed
- `obs-03` [telco, medium] Two thousand thumbs-down clicks with no trace
- `obs-04` [fintech, medium] Average latency hides 40-second dispute answers
- `obs-05` [telco, high] One MVNO tenant burns the monthly LLM budget in a week
- `obs-06` [fintech, medium] Tax-season questions drift outside what the bot knows
- `obs-07` [telco, high] Nobody can explain why the agent cancelled a line
- `obs-08` [fintech, medium] Forty dashboards and no SLO during an incident
- `obs-09` [telco, medium] Team rewrites prompts while an index shard is empty
- `obs-10` [fintech, medium] PII filter blocks 15% of legitimate account questions
- `obs-11` [telco, medium] Quality dip that can't be split by prompt version
- `obs-12` [fintech, medium] Payday 429s blamed on application bugs
- `obs-13` [telco, medium] Every reply looks fine but customers abandon long chats
- `obs-14` [fintech, medium] Silent fallback to a weaker model for three days
- `obs-15` [telco, high] Diagnosis agent repeats the same check 200 times overnight
- `obs-16` [fintech, medium] Traces redacted so heavily that nothing can be debugged
- `obs-17` [telco, medium] Every failure logged as "LLM error"
- `obs-18` [fintech, medium] Online judge on 100% of traffic costs more than the product
- `obs-19` [telco, high] Bot promises outage credits and nobody knows how to stop it
- `obs-20` [fintech, high] First-week incident with no data to debug

## 6. Telemetry (`telemetry`)

Telemetry is the data pipeline under observability: what you emit, in which schema, at what cost, and under which privacy rules. In Telco (CPNI) and FinTech (PCI DSS, GLBA, GDPR) prompts are customer data, so the telemetry pipeline inherits the same security, retention and residency obligations as the systems of record.

- `tel-01` [fintech, medium] Switching trace vendors means rewriting 30 services
- `tel-02` [telco, critical] Customer addresses and call records found in the logging platform
- `tel-03` [fintech, medium] Account ID as a metric label explodes the metrics bill
- `tel-04` [telco, medium] Three teams report token usage three different ways
- `tel-05` [fintech, medium] The 1% trace sample contains almost no failed disputes
- `tel-06` [telco, high] Slow tracing backend slows down customer replies
- `tel-07` [fintech, medium] Traces stop at the Kafka topic between fraud scoring and the agent
- `tel-08` [telco, medium] Voice bot feels slow, but total latency looks fine
- `tel-09` [fintech, high] GDPR deletion request no one can fulfil in the trace store
- `tel-10` [telco, medium] Which prompt produced last Tuesday's bad answer?
- `tel-11` [fintech, medium] A 12-second gap in the trace is an uninstrumented bureau call
- `tel-12` [telco, low] Cost estimates 15% off the provider bill
- `tel-13` [fintech, medium] Support tickets are the only quality signal
- `tel-14` [telco, medium] Finding failed refunds means regex over 500 GB of logs
- `tel-15` [fintech, critical] BaaS partner sees another partner's prompts in shared dashboards
- `tel-16` [telco, medium] Eval results live only in CI logs
- `tel-17` [fintech, low] Child spans appear to start before their parents
- `tel-18` [telco, medium] Telemetry is 40% of infrastructure cost
- `tel-19` [fintech, medium] Logs show the template, not the prompt the model saw
- `tel-20` [telco, medium] Bill explanations cut off mid-sentence for large accounts

## 7. Context Engineering (`context-engineering`)

Context engineering decides what the model sees on every call: instructions, customer and account state, retrieved knowledge, tool results, memory and conversation. Prompt engineering is how you phrase one message; context engineering is how you assemble the whole window, every turn, within a budget, with provenance and isolation.

- `ctx-01` [fintech, medium] Whole credit agreement and two years of statements in one prompt
- `ctx-02` [telco, high] At step 40 the agent forgets the change-window constraint
- `ctx-03` [fintech, high] Card-number rule buried among 8,000 tokens of policy
- `ctx-04` [telco, high] Customer email instruction changes the ticket agent's behaviour
- `ctx-05` [fintech, medium] Intent classifier receives 20k tokens it doesn't need
- `ctx-06` [telco, medium] Timestamp at the top kills prompt caching
- `ctx-07` [fintech, medium] Chat history squeezes out the retrieved fee schedule
- `ctx-08` [telco, high] Second half of a 300-page MSA silently truncated
- `ctx-09` [fintech, high] Wealth assistant brings up a client's divorce in a portfolio review
- `ctx-10` [telco, medium] Device ships to the old address
- `ctx-11` [fintech, medium] Forty-five tool schemas use 18k tokens before the customer speaks
- `ctx-12` [telco, medium] Half-finished trade-in restarts the next day
- `ctx-13` [fintech, medium] Full SEC filing HTML sent to answer a dividend question
- `ctx-14` [telco, medium] Retrieved text with no source or date
- `ctx-15` [fintech, high] Compaction drops that the account needs two signatures
- `ctx-16` [telco, medium] Five sub-agents each receive the full 100k context
- `ctx-17` [fintech, critical] Semantic cache serves one customer's balance to another
- `ctx-18` [telco, low] Refund examples copied into shipping answers
- `ctx-19` [fintech, medium] Engineers argue about what the model saw
- `ctx-20` [telco, medium] Config agent tries to hold 300 router configs in context

## 8. Prompt Engineering (`prompt-engineering`)

In production a prompt is code: versioned, reviewed, tested and owned. Most prompt anti-patterns come from treating it as a magic string, or from asking it to enforce rules (limits, permissions, disclosures) that belong in code and in the systems of record.

- `prm-01` [telco, medium] Care-bot prompts scattered through the codebase
- `prm-02` [fintech, high] Adding be empathetic makes the collections bot promise payment plans
- `prm-03` [telco, medium] Nine thousand tokens of contradictory rules
- `prm-04` [fintech, medium] NEVER GIVE FINANCIAL ADVICE makes the bot refuse to explain APR
- `prm-05` [telco, low] Don't use jargon produces vague router instructions
- `prm-06` [fintech, medium] Transaction categories parsed from prose with regex
- `prm-07` [telco, low] Summarise this ticket gives one line or three paragraphs
- `prm-08` [fintech, medium] One prompt classifies, extracts, computes redress and drafts the reply
- `prm-09` [telco, medium] Model migration drops quality 15% with the same prompts
- `prm-10` [fintech, high] AML alert disposition written before its rationale
- `prm-11` [telco, low] Every device description starts with Introducing
- `prm-12` [fintech, high] Ignore the above prints internal fee-waiver codes
- `prm-13` [telco, medium] Port-in form extraction differs between runs
- `prm-14` [fintech, low] You are a world-class tax attorney doesn't improve accuracy
- `prm-15` [telco, high] SIM registration extractor invents an ID number from a blurry photo
- `prm-16` [fintech, high] Max fee waiver of $25 in the prompt, $100 in practice
- `prm-17` [telco, low] A magic prompt template adds 800 tokens and no gain
- `prm-18` [fintech, medium] French-Canadian customers get English replies and US date formats
- `prm-19` [telco, medium] Hello {customer_name} reaches customers
- `prm-20` [fintech, low] Weeks of hand-tuning for a 1% gain

## 9. MLOps / LLMOps (`llmops`)

In LLM systems the "model" is a bundle: base model, prompts, retrieval index, embeddings, tools, guardrails and config. LLMOps means versioning, deploying, monitoring and retiring that bundle as one unit, with lineage that a model-risk team or regulator can follow.

- `ops-01` [fintech, high] Last week's bad answer can't be reproduced
- `ops-02` [telco, medium] Intent model trained on clean text, served on raw transcripts
- `ops-03` [telco, high] Fine-tuning a model on monthly price plans
- `ops-04` [fintech, high] Collections model fine-tuned on raw call transcripts
- `ops-05` [fintech, high] Nobody knows which data trained the credit-memo model
- `ops-06` [telco, high] All traffic switched to a new model at once
- `ops-07` [fintech, medium] Twelve teams call four providers directly
- `ops-08` [telco, high] Self-hosted model runs out of GPU memory at 50 users
- `ops-09` [fintech, medium] Cost per call falls while cost per resolved dispute triples
- `ops-10` [telco, medium] Thirty percent of questions are the same and all pay full price
- `ops-11` [fintech, medium] Notebook works, the production rewrite doesn't
- `ops-12` [telco, medium] A year of care-bot feedback never used
- `ops-13` [fintech, medium] Minor framework update changes default chunk size
- `ops-14` [telco, medium] Staging uses a small model and a tiny index
- `ops-15` [fintech, high] Compliance asks which systems use AI for credit decisions
- `ops-16` [telco, high] Model deprecation forces an emergency migration
- `ops-17` [fintech, high] Tax-day traffic hits provider quotas
- `ops-18` [telco, medium] Re-embedding 50 million chunks by hand
- `ops-19` [fintech, high] API key in a public notebook runs up the bill
- `ops-20` [telco, low] Forty old prompts, nine indexes and three fine-tunes still billed

## 10. CI/CD for Agentic AI (`cicd`)

An agentic system changes through code, prompts, models, indexes, tools and policies. Every one of those is a deployable change that needs the same pipeline: tests, evals, security checks, staged rollout, monitoring and one-click rollback. In regulated Telco and FinTech environments, the pipeline is also your evidence for auditors.

- `cicd-01` [fintech, high] Pipeline runs unit tests but no evals
- `cicd-02` [telco, high] Prompts edited live in a vendor console
- `cicd-03` [fintech, medium] Tool wrappers and templates have no unit tests
- `cicd-04` [telco, medium] Two-hour eval suite on every PR gets skipped
- `cicd-05` [fintech, high] New prompt goes to all customers at once
- `cicd-06` [telco, high] Model version bumped as a one-line config change
- `cicd-07` [fintech, medium] Same commit builds two different agents
- `cicd-08` [telco, critical] CI agent evals call the production BSS
- `cicd-09` [fintech, high] Rollback restores the code but not the index
- `cicd-10` [telco, medium] Flaky evals fixed with retry until green
- `cicd-11` [fintech, medium] Knowledge articles published straight into the live index
- `cicd-12` [telco, medium] Planner and executor agents never tested together
- `cicd-13` [fintech, high] No red-team stage in the release pipeline
- `cicd-14` [telco, high] Provider API key printed in CI logs
- `cicd-15` [fintech, high] Regulated disclosure change shipped without sign-off
- `cicd-16` [telco, medium] No way to switch off one agent capability
- `cicd-17` [fintech, medium] Eval set changed and scores aren't comparable
- `cicd-18` [telco, high] BSS API change breaks the agent's tools in production
- `cicd-19` [fintech, medium] Cost regression merged without anyone noticing
- `cicd-20` [telco, medium] Deployment succeeds but the bot can't reach the catalog

## 11. Guardrails & AI Security (`guardrails-security`)

Treat every model as a component that can be talked into anything. Security comes from what the system lets the model do (least privilege, deterministic policy, human approval), layered input and output controls, and the assumption that prompts, retrieved content and tool results are all attacker-controlled. The OWASP Top 10 for LLM Applications is a good checklist.

- `sec-01` [fintech, critical] Bank bot role-played into explaining deposit structuring
- `sec-02` [telco, high] Field-tech agent obeys hidden text on a vendor web page
- `sec-03` [telco, medium] Retention offer tiers extracted from the system prompt
- `sec-04` [telco, critical] Store copilot shows another subscriber's call records
- `sec-05` [fintech, critical] Banking agent can pay new payees on its own
- `sec-06` [telco, high] EU subscriber data sent to a model in another region
- `sec-07` [fintech, high] Model output rendered as HTML in the agent desktop
- `sec-08` [telco, medium] Bot promises 5G coverage at an address it can't check
- `sec-09` [fintech, high] Guardrails on input only
- `sec-10` [telco, critical] The LLM is asked whether the caller is authorised
- `sec-11` [telco, medium] Content filter bypassed with base64 and another language
- `sec-12` [telco, critical] Cloned voice passes voice biometrics on the IVR agent
- `sec-13` [fintech, medium] Coordinated thumbs-up teaches the bot to waive fees
- `sec-14` [telco, high] Community MCP server installed in the NOC agent
- `sec-15` [fintech, medium] Huge pasted inputs exhaust the assistant's capacity
- `sec-16` [telco, high] Deleted customer still found in the vector store
- `sec-17` [fintech, critical] Analytics agent's code runs with network access
- `sec-18` [telco, high] Agent installs a hallucinated package name
- `sec-19` [fintech, high] Approvers rubber-stamp the agent's persuasive summaries
- `sec-20` [telco, medium] An AI security incident with no playbook

## 12. Multi-Agent Systems (`multi-agent`)

Multiple agents earn their place when work truly parallelises, when contexts must be isolated, or when duties must be separated (maker and checker). Every extra agent adds handoffs, shared state, budgets and failure modes, so treat agent-to-agent interfaces like service APIs: typed, versioned, authorised, traced and tested.

- `mas-01` [fintech, medium] Supervisor agent becomes the bottleneck for every request
- `mas-02` [telco, medium] Planner and critic agents debate for 40 rounds
- `mas-03` [fintech, high] Two agents update the same fraud case at once
- `mas-04` [telco, medium] Facts lost in a chain of agent summaries
- `mas-05` [fintech, medium] Three agents message the customer at once
- `mas-06` [telco, medium] Agents delegate a task back and forth
- `mas-07` [fintech, high] Maker and checker agents share the same permissions and model
- `mas-08` [telco, high] Two parallel agents provision the same line
- `mas-09` [fintech, medium] Each agent has a budget, the system has none
- `mas-10` [telco, medium] Customer asked to verify identity again after every handoff
- `mas-11` [fintech, high] Reviewer agent approves its sibling's credit memos
- `mas-12` [telco, critical] Partner carrier's agent sends instructions the agent follows
- `mas-13` [fintech, high] Collections agent and hardship agent contradict each other
- `mas-14` [telco, medium] Debugging a multi-agent failure from six separate logs
- `mas-15` [fintech, medium] Thirty agents and nobody knows who owns which
- `mas-16` [telco, medium] Five levels of sub-agents add 30 seconds
- `mas-17` [fintech, medium] Majority vote of three identical agents
- `mas-18` [telco, medium] Group chat of agents with no end condition
- `mas-19` [fintech, high] One failing agent takes down the whole onboarding flow
- `mas-20` [telco, medium] Only the orchestrator's final answer is evaluated

## 13. Memory Management (`memory`)

Agent memory comes in layers: working memory (this conversation), task state (this job), long-term facts and preferences (this customer), and procedural memory (how we solve this kind of problem). Each needs write rules, a source of truth, expiry, isolation and evaluation. In regulated industries, consent, vulnerability and contact preferences belong in systems of record, not in an agent's notes.

- `mem-01` [telco, medium] Customer moves from chat to the IVR and repeats everything
- `mem-02` [fintech, medium] Long-term memory is a pile of raw transcripts
- `mem-03` [fintech, high] Assistant remembers things customers never knew it stored
- `mem-04` [telco, medium] Household tablet mixes two family members' memories
- `mem-05` [fintech, medium] Remembered preference outlives the customer's change
- `mem-06` [telco, medium] Memories kept forever with no retention rule
- `mem-07` [fintech, high] Remember that I'm a VIP and always waive my fees
- `mem-08` [telco, high] Agent remembers its own wrong promise as a fact
- `mem-09` [fintech, medium] Memory retrieval ignores recency and importance
- `mem-10` [telco, medium] Billing agent forgets what the care agent learned
- `mem-11` [fintech, medium] Every memory injected into every prompt
- `mem-12` [telco, medium] NOC agent never learns from resolved incidents
- `mem-13` [fintech, high] Agent writes its own rules from experience, unchecked
- `mem-14` [fintech, high] One advisor's client notes surface for another advisor
- `mem-15` [fintech, medium] Client disputes what the assistant remembered, no audit
- `mem-16` [telco, high] Do not market to me becomes market to me in a summary
- `mem-17` [fintech, high] Vulnerability flag remembered by one agent, ignored by others
- `mem-18` [fintech, low] Assistant assumes memory that new customers don't have
- `mem-19` [telco, medium] Memory feature launched with no memory evals
- `mem-20` [fintech, critical] Branch kiosk shows the previous customer's context

## 14. Tool Design & MCP (`tool-design-mcp`)

Tools are the agent's hands, and their design decides most of an agent's reliability. Good tools are task-shaped, typed, documented like an API for a new hire, safe to retry, authorised per object, observable and versioned. MCP standardises how tools are exposed, but it doesn't make a badly designed tool safe.

- `tool-01` [telco, critical] Agent given a raw SQL tool on the billing database
- `tool-02` [fintech, high] Wire value date in the wrong time zone
- `tool-03` [telco, medium] get_bill, get_invoice and get_statement all exist
- `tool-04` [fintech, medium] Transaction tool returns 10,000 rows
- `tool-05` [telco, high] Plan change executed without a preview
- `tool-06` [telco, high] Bulk suspension reports success when 3 of 50 lines failed
- `tool-07` [fintech, critical] Statement tool trusts the account id the model supplies
- `tool-08` [telco, medium] Legacy OSS call with no timeout hangs the conversation
- `tool-09` [fintech, high] Tool schema changed in place breaks deployed agents
- `tool-10` [telco, critical] MCP server exposes the whole BSS API with an admin token
- `tool-11` [fintech, medium] Tool description promises something the tool doesn't do
- `tool-12` [telco, medium] Port-in tool blocks for hours waiting for completion
- `tool-13` [fintech, high] Agent hammers the mainframe core-banking system
- `tool-14` [telco, medium] Agent trusts a coverage tool's malformed response
- `tool-15` [fintech, high] Balance unchanged right after the payment, so the agent pays again
- `tool-16` [telco, high] A generic http_request tool for everything
- `tool-17` [fintech, medium] Tool returns ACH return code R03 with no explanation
- `tool-18` [telco, low] Tool returns a formatted paragraph the agent must parse
- `tool-19` [fintech, high] Two MCP servers both offer a tool named transfer
- `tool-20` [telco, medium] No one knows which tools agents actually use

## 15. Cost, Latency & Model Routing (`cost-latency-routing`)

Cost and latency are product requirements, not afterthoughts. Measure cost per successful outcome per intent, give every stage a latency budget, route each step to the smallest model that passes its evals, cache what is general, batch what can wait, and never let an optimisation ship without a quality check.

- `cost-01` [fintech, medium] No one knows what a resolved card dispute costs
- `cost-02` [fintech, high] Router sends hard complaints to the small model
- `cost-03` [telco, high] Voice agent pauses for 3 seconds before every reply
- `cost-04` [fintech, medium] Fifteen-thousand-token system prompt for a balance question
- `cost-05` [telco, low] Prompt caching enabled, but the cache expires between turns
- `cost-06` [fintech, high] Semantic cache confuses cancel my card with cancel my card payment
- `cost-07` [telco, medium] One conversation costs $40
- `cost-08` [fintech, low] Replies three times longer than customers need
- `cost-09` [telco, medium] Nightly ticket summaries run on the real-time API
- `cost-10` [fintech, medium] Extended reasoning turned on for every request
- `cost-11` [telco, medium] Customers stare at a spinner for 8 seconds
- `cost-12` [fintech, medium] Independent lookups run one after another
- `cost-13` [telco, low] Speculative prefetching that's mostly wasted
- `cost-14` [fintech, medium] Large model classifying 100 million transactions a month
- `cost-15` [telco, medium] Retry storm doubles cost during a provider incident
- `cost-16` [fintech, low] Embeddings recomputed for unchanged documents every night
- `cost-17` [telco, low] AI costs land in one central budget
- `cost-18` [fintech, medium] Self-hosted GPUs sit idle 80% of the day
- `cost-19` [telco, medium] Latency SLO with no plan for when it's missed
- `cost-20` [fintech, high] Prompt compression saves tokens and drops the disclosures

## 16. Human-in-the-Loop & Governance (`hitl-governance`)

Governance turns "we think it's safe" into evidence: an inventory, risk tiers, model validation, approvals for irreversible actions, audit trails, disclosure, fairness testing and clear incident ownership. Humans in the loop only help when they have time, evidence and authority. In FinTech this maps to model risk management, fair lending and record-keeping rules; in Telco to CPNI, consumer protection and accessibility rules; in the EU, to the AI Act and GDPR.

- `gov-01` [fintech, high] LLM credit-memo tool deployed outside model risk management
- `gov-02` [telco, critical] Disconnect and port-out executed with no human gate
- `gov-03` [fintech, medium] Customers aren't told they're talking to an AI
- `gov-04` [fintech, high] Customers trapped in a chatbot doom loop
- `gov-05` [fintech, critical] LLM-assisted credit decline can't give specific reasons
- `gov-06` [telco, high] Retention offers differ by customer name and dialect
- `gov-07` [fintech, high] Broker's AI client chats aren't archived
- `gov-08` [telco, medium] AI incident with no clear owner
- `gov-09` [telco, high] Call records used to fine-tune a model without a legal basis
- `gov-10` [telco, critical] Real-time emotion detection on call-centre agents
- `gov-11` [fintech, high] AI vendor dependency never assessed as third-party risk
- `gov-12` [telco, medium] AI policy document says one thing, the system does another
- `gov-13` [fintech, medium] Human overrides are never fed back
- `gov-14` [telco, high] Automated postpaid decline with no human review option
- `gov-15` [fintech, high] Human review queue with no SLA or capacity plan
- `gov-16` [telco, high] Staff paste customer data into public chatbots
- `gov-17` [fintech, medium] Pilot runs for two years with no success criteria
- `gov-18` [telco, medium] Voice bot unusable for customers with speech impairments
- `gov-19` [fintech, high] Nobody knows the regulator notification deadline for an AI incident
- `gov-20` [telco, medium] Governance checklist signed but never checked

## 17. Fine-tuning vs RAG vs Prompting (`finetune-vs-rag`)

Choose the approach from error analysis, not fashion. Prompting fixes instructions and format; RAG and tools supply fresh, citable knowledge from systems of record; fine-tuning changes behaviour, style, narrow classification and cost at scale. Most production systems combine them, and every choice needs a baseline, a held-out eval and a plan for when the base model changes.

- `ft-01` [fintech, high] Fine-tuning a model to answer credit-card policy questions
- `ft-02` [telco, medium] Adding more retrieval to fix the bot's tone
- `ft-03` [telco, medium] Prompt with 400 ticket categories for routing
- `ft-04` [fintech, high] Fine-tuned model shipped without a held-out evaluation
- `ft-05` [telco, high] Fine-tuning on the bot's own past answers
- `ft-06` [fintech, high] Fine-tune makes the model forget its refusals
- `ft-07` [telco, medium] Fine-tuning teaches a confident tone, not correct answers
- `ft-08` [fintech, medium] Fifty examples expected to teach a complex task
- `ft-09` [telco, high] Fine-tuned model's base version is being retired
- `ft-10` [fintech, critical] Fine-tuned model repeats customers' account numbers
- `ft-11` [telco, medium] Twenty thousand documents stuffed into long context
- `ft-12` [fintech, high] RAG over documents to trace beneficial ownership
- `ft-13` [telco, medium] Small model distilled from a provider's outputs against its terms
- `ft-14` [fintech, medium] Prompt change and fine-tune shipped together
- `ft-15` [telco, medium] Fine-tuning chosen because a competitor announced it
- `ft-16` [fintech, high] Fine-tuned model can't show where its answers come from
- `ft-17` [telco, medium] Generic embeddings don't understand telco jargon
- `ft-18` [fintech, medium] Fine-tuned on synthetic disputes, fails on real ones
- `ft-19` [telco, medium] Fine-tune saves on tokens, costs more to host
- `ft-20` [fintech, medium] Fine-tuned model never A/B tested against the old one

## 18. Data Pipelines & Governance for AI (`data-pipelines`)

An AI system is only as good as the data that reaches it: knowledge content, structured records behind tools, events, labels and logs. Production pipelines need data contracts, quality checks, freshness SLOs, lineage, classification, permission sync and owners, the same disciplines as analytics data, applied to documents and embeddings too.

- `data-01` [telco, high] CRM export column renamed, plan names vanish from the index
- `data-02` [fintech, high] OCR misreads income documents with no confidence check
- `data-03` [telco, high] No freshness SLO for promotion pages
- `data-04` [fintech, critical] After a bank merger, customer ids collide across systems
- `data-05` [telco, medium] Can't tell which version of a document produced an answer
- `data-06` [telco, medium] Intent labels from three vendors disagree
- `data-07` [fintech, critical] HR and legal files indexed into the employee assistant
- `data-08` [telco, medium] Usage events arrive late and the bill-shock alert is wrong
- `data-09` [fintech, medium] Backfill job duplicates every chunk in the vector store
- `data-10` [telco, critical] Production call records copied unmasked into dev
- `data-11` [fintech, critical] Null APR in the rates table becomes a 0% quote
- `data-12` [telco, medium] Agents compute active subscribers three different ways
- `data-13` [fintech, medium] CMS overwrites documents with no version history
- `data-14` [telco, high] Ingestion copies EU customer data into a US vector database
- `data-15` [fintech, high] SharePoint permission changes take a week to reach the index
- `data-16` [telco, medium] Chunks without product, region or date metadata
- `data-17` [fintech, medium] Scraped competitor rates ingested without validation
- `data-18` [telco, high] Ingestion job failing silently for three weeks
- `data-19` [fintech, high] Deletion job removes AI logs under legal hold
- `data-20` [telco, medium] Knowledge articles with no owner go stale
