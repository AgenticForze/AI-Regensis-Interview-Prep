"""Command-line entry point for the coach agent.

  aap-coach interview [--user you]          mock interview (needs ANTHROPIC_API_KEY)
  aap-coach review "scenario text" [--out reviews/my-system]
  aap-coach review --file scenario.txt      LLM extracts the spec, rules review it
  aap-coach review --arch telco-sim-swap-agent   reference design, no API key needed
  aap-coach review --spec my-spec.yaml           your own spec, no API key needed
  aap-coach progress [--user you]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml  # noqa: E402

from antipatterns import tools as T  # noqa: E402


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        where = f" ({f['node_title']})" if f.get("node_title") else ""
        refs = ", ".join(s["id"] for s in f["scenarios"])
        print(f"  {f['label']:>3}  [{f['severity']}] {f['title']}{where}  -> {refs}")


def cmd_interview(args) -> None:
    from antipatterns.agent import Coach
    coach = Coach(user_id=args.user)
    print("Mock interview. Type 'next' for a question, 'progress' for your stats, 'quit' to stop.\n")
    print(coach.chat("Start the interview: ask me the first question." + (f" Topic: {args.topic}." if args.topic else "")))
    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in ("quit", "exit"):
            break
        if text:
            print("\ncoach> " + coach.chat(text))


def cmd_review(args) -> None:
    out = args.out
    if args.arch or args.spec:
        spec = T.get_reference_architecture(args.arch) if args.arch else yaml.safe_load(Path(args.spec).read_text())
        out = out or f"reviews/{args.arch or Path(args.spec).stem}"
        res = T.review_architecture(spec, out_dir=out)
        print(f"Review of {res['title']}:")
        _print_findings(res["findings"])
        print(f"\nReport: {res['files']['report']}")
        return
    from antipatterns.agent import Coach
    scenario = Path(args.file).read_text() if args.file else args.scenario
    if not scenario:
        sys.exit("Give a scenario string, --file, --arch or --spec.")
    coach = Coach()
    ask = None if args.no_questions else (lambda q: input(f"\nOne question first: {q}\n> "))
    res = coach.review_scenario(scenario, out or "reviews/latest", answer_question=ask)
    print(f"\nReview of {res['spec']['title']}:")
    _print_findings(res["findings"])
    print(f"\nReport, diagrams and spec: {res['out_dir']}")


def cmd_progress(args) -> None:
    print(yaml.safe_dump(T.get_progress(args.user), sort_keys=False))


def main() -> None:
    p = argparse.ArgumentParser(description="Agentic AI interview coach and Architecture Review")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("interview")
    i.add_argument("--user", default="default")
    i.add_argument("--topic")
    r = sub.add_parser("review")
    r.add_argument("scenario", nargs="?")
    r.add_argument("--file")
    r.add_argument("--arch")
    r.add_argument("--spec")
    r.add_argument("--out")
    r.add_argument("--no-questions", action="store_true")
    g = sub.add_parser("progress")
    g.add_argument("--user", default="default")
    args = p.parse_args()
    {"interview": cmd_interview, "review": cmd_review, "progress": cmd_progress}[args.cmd](args)


if __name__ == "__main__":
    main()
