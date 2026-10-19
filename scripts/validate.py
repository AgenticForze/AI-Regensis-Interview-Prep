"""Validate the scenario catalog and architecture library. Exit 1 on any problem."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from antipatterns.catalog import load_topics, validate  # noqa: E402


def main() -> int:
    errs = validate()
    try:
        from antipatterns.review import validate_library
        errs += validate_library()
    except ImportError:
        pass
    topics = load_topics()
    n = sum(len(t["scenarios"]) for t in topics)
    by_domain: dict[str, int] = {}
    for t in topics:
        for s in t["scenarios"]:
            by_domain[s["domain"]] = by_domain.get(s["domain"], 0) + 1
    print(f"{len(topics)} topics, {n} scenarios, by domain: {by_domain}")
    for e in errs:
        print("  -", e)
    print("OK" if not errs else f"{len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
