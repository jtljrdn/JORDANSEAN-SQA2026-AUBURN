from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent


def main() -> None:
    requirements = json.loads((DIR / "requirements.json").read_text())
    # (parent, sub_rule)
    seen: dict[tuple[str, str], int] = defaultdict(int)

    test_cases: list[dict[str, str]] = []
    for req in requirements:
        req_id: str = req["requirement_id"]
        parent: str = req["parent"]
        if not req_id.startswith(parent):
            raise ValueError(
                f"requirement_id {req_id!r} does not start with parent {parent!r}"
            )
        sub = req_id[len(parent) :]
        parent_tail = parent.rsplit("-", 1)[-1]
        key = (parent, sub)
        seen[key] += 1
        n = seen[key]
        tag = f"{parent_tail}{sub}" if n == 1 else f"{parent_tail}{sub}{n}"

        test_cases.append(
            {
                "test_id": f"TC-HAZ-{tag}",
                "requirement_id": f"REQ-HAZ-{tag}",
            }
        )

    out = DIR / "test_cases.json"
    out.write_text(json.dumps(test_cases, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(test_cases)} test case(s) to {out}")


if __name__ == "__main__":
    main()
