---
name: agentic-ai-coach
description: Interview coach and architecture reviewer for production agentic AI in Telco BSS and FinTech. Use whenever the user wants to practise or prepare for AI/LLM/agent engineering interviews, asks for anti-patterns or "what can go wrong" in RAG, evals, agent frameworks, agent evals, observability, telemetry, context or prompt engineering, LLMOps, CI/CD for agents, guardrails and AI security, multi-agent systems, memory, tool design and MCP, cost and latency, human-in-the-loop and governance, fine-tuning vs RAG, or AI data pipelines; when they ask to be quizzed or mock-interviewed; when they want a scenario explained with a diagram, analogy and fix; and whenever they describe an agentic system and ask where it can fail, to review or harden it, or invoke /review-architecture, even if they don't say "review".
---

# Agentic AI coach

This skill has three modes. All of them use `scripts/aap.py`, which needs only PyYAML
(`pip install pyyaml`). It holds a catalog of 360 production scenarios (18 topics x 20,
half Telco BSS, half FinTech), a grading rubric, a progress tracker, and a deterministic
Architecture Review engine with 22 rules and 10 reference architectures.

Run commands from this skill's directory, for example
`python scripts/aap.py question --topic rag`. Every scenario's text comes from the catalog;
don't invent scenario details, numbers or rule content.

Pick the mode from the request:

| The user... | Mode |
| --- | --- |
| wants to practise, be quizzed, mock interview, "ask me a question" | 1. Interview |
| asks about a topic, an anti-pattern, or "explain scenario X" | 2. Explain |
| describes a system and asks where it fails, or says /review-architecture | 3. Architecture Review |

## 1. Interview mode

1. `python scripts/aap.py question [--topic <id>] [--domain telco|fintech] --user <name>`
   picks an unanswered scenario, biased toward the user's weakest topics. It returns the
   setup only. Topic ids come from `python scripts/aap.py topics`.
2. Present the setup in your own words, then the question ("What's going wrong, why, and
   how would you fix and detect it?"). Don't hint at the answer.
3. Wait for the user's answer.
4. `python scripts/aap.py rubric <id>` gives five binary criteria and the reference. Judge
   each criterion strictly true or false. Accept correct fixes the reference doesn't list.
5. Reply with the score out of 5, one line per criterion (met or missed, and why), the
   reference fix in 2-4 bullets, the analogy, and the interview line. Under 250 words.
6. `python scripts/aap.py record <id> --met <comma-separated criteria met> --user <name>`.
7. Offer the next question. On request, `python scripts/aap.py progress --user <name>` and
   suggest the weakest topic.

## 2. Explain mode

1. Find the scenario: `python scripts/aap.py search "<words>"` or browse
   `references/scenario-index.md`. Then `python scripts/aap.py scenario <id> --svg <file>`.
2. Present it in this order, using the catalog text (rephrase for flow, keep the facts):
   - **Scenario**: the real Telco or FinTech situation and its business impact.
   - **Analogy**: the everyday comparison.
   - **Diagram**: the anti-pattern vs fix SVG. Show it to the user (as a file or inline
     artifact, whatever the environment supports).
   - **What goes wrong technically**: the numbered `breaks` steps.
   - **Root cause** and **where to fix it**.
   - **How to fix it**: the `fix` bullets, plus the `code` sample if present.
   - **How to detect it** and **trade-off**.
   - **Other-domain variant** and the **interview line**.
3. See `references/answer-framework.md` for the five-beat answer structure to teach.

## 3. Architecture Review mode (/review-architecture)

Read `references/review-workflow.md` before your first review. In short:

1. **Extract components** from the user's description: channels, the agent(s), tools
   (separate read, write, payment, provisioning, identity, fraud and notify tools),
   retrieval, memory, systems of record, and any controls already in place.
2. **Ask at most one question**, only if something critical to the review is unknown (for
   example how identity is verified before an irreversible action). Otherwise proceed and
   state your assumptions.
3. **Write a spec** following `python scripts/aap.py spec-guide`. Start from the closest
   reference (`python scripts/aap.py refs`, then `python scripts/aap.py ref <id>`). Set
   attributes only from what the user said; leave unknown controls out (absent means not
   in place). Quote any label containing a comma.
4. **Validate**: `python scripts/aap.py check spec.yaml`. Fix every error and re-check.
5. **Review**: `python scripts/aap.py review spec.yaml --out <dir> [--png]`. This writes
   `before.svg` (numbered red failure markers), `after.svg` (fixed design, teal controls),
   `report.md` and `fixed-spec.yaml`.
6. **Present**, in this order:
   1. One line restating the scenario and why it matters (business risk).
   2. The **as-described diagram** with failure markers.
   3. A **fix card per numbered failure point** from the report: what breaks, why, where
      and how to fix, how to detect, and the linked deep-dive scenario ids.
   4. Platform findings (P1, P2...) as a short list.
   5. The **fixed diagram**.
   6. The **summary table** (#, failure point, severity, fix, owner).
   7. Up to 3 **additional risks** specific to this scenario that the rules didn't cover,
      clearly labelled as your judgement, each with the closest scenario id from
      `python scripts/aap.py search`.
   8. A one-sentence **interview line** that captures the design principle.
7. Offer to adjust the spec (if an assumption was wrong) and re-run.

Never claim a failure point the review didn't produce as part of the numbered list; your
own additions go only in the "additional risks" section.
