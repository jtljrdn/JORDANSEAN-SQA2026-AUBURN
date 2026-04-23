import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from myLogger import giveMeLoggingObject

DIR = Path(__file__).resolve().parent
LOGGER = giveMeLoggingObject()

def load_inputs(dir_path: Path):
    ts = datetime.now(timezone.utc).astimezone().isoformat()
    requirements_path = dir_path / "requirements.json"
    expected_path = dir_path / "expected_structure.json"

    try:
        with open(requirements_path) as f:
            requirements = json.load(f)
        LOGGER.info(
            "[%s] component=validate action=load resource=requirements.json from_where=%s status=success count=%s",
            ts,
            str(requirements_path),
            len(requirements) if isinstance(requirements, list) else "unknown",
        )
    except Exception:
        LOGGER.exception(
            "[%s] component=validate action=load resource=requirements.json from_where=%s status=failure",
            ts,
            str(requirements_path),
        )
        raise

    try:
        with open(expected_path) as f:
            expected_structure = json.load(f)
        LOGGER.info(
            "[%s] component=validate action=load resource=expected_structure.json from_where=%s status=success count=%s",
            ts,
            str(expected_path),
            len(expected_structure) if isinstance(expected_structure, dict) else "unknown",
        )
    except Exception:
        LOGGER.exception(
            "[%s] component=validate action=load resource=expected_structure.json from_where=%s status=failure",
            ts,
            str(expected_path),
        )
        raise

    return requirements, expected_structure


def validate_structure(requirements, expected_structure):
    ts = datetime.now(timezone.utc).astimezone().isoformat()
    failures = []

    try:
        actual_ids = {
            r["requirement_id"]
            for r in requirements
            if isinstance(r, dict) and isinstance(r.get("requirement_id"), str)
        }
    except Exception:
        LOGGER.exception("[%s] component=validate action=derive resource=requirements status=failure", ts)
        raise

    # Check all expected enumerations exist
    if isinstance(expected_structure, dict):
        for parent, suffixes in expected_structure.items():
            if not isinstance(parent, str) or not isinstance(suffixes, list):
                continue
            for s in suffixes:
                if not isinstance(s, str):
                    continue
                rid = f"{parent}{s}"
                if rid not in actual_ids:
                    failures.append(f"Missing requirement: {rid}")

    # Optional: check for extra/unexpected requirements
    for rid in actual_ids:
        parent = rid[:11]  # REQ-HAZ-001 + A/B/C
        if isinstance(expected_structure, dict) and parent in expected_structure:
            suffix = rid[-1]
            allowed = expected_structure.get(parent)
            if isinstance(allowed, list) and suffix not in allowed:
                failures.append(f"Unexpected requirement: {rid}")

    LOGGER.info(
        "[%s] component=validate action=check resource=requirements status=%s failure_count=%s",
        ts,
        "failure" if failures else "success",
        len(failures),
    )
    return failures


if __name__ == "__main__":
    requirements, expected_structure = load_inputs(DIR)
    failures = validate_structure(requirements, expected_structure)

    if failures:
        print("\n".join(failures))
        sys.exit(1)
    else:
        print(" Validation passed: all enumerations complete.")
