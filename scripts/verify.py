import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

from myLogger import giveMeLoggingObject
"""
Verification script for requirements and test cases.

Rules:
1. Required fields exist (requirement_id, description, source)
2. Requirement ID format: REQ-[CATEGORY]-[3 digits][letter], e.g., REQ-HAZ-001A
3. Each requirement must have at least one test case
4. No vague phrases like "all hazards" in description
5. Parent-child ID consistency (child must start with parent ID)
"""

DIR = Path(__file__).resolve().parent
LOGGER = giveMeLoggingObject()


def load_inputs(dir_path: Path):
    ts = datetime.now(timezone.utc).astimezone().isoformat()
    requirements_path = dir_path / "requirements.json"
    test_cases_path = dir_path / "test_cases.json"

    try:
        with open(requirements_path) as f:
            requirements = json.load(f)
        LOGGER.info(
            "[%s] component=verify action=load resource=requirements.json from_where=%s status=success count=%s",
            ts,
            str(requirements_path),
            len(requirements) if isinstance(requirements, list) else "unknown",
        )
    except Exception:
        LOGGER.exception(
            "[%s] component=verify action=load resource=requirements.json from_where=%s status=failure",
            ts,
            str(requirements_path),
        )
        raise

    try:
        with open(test_cases_path) as f:
            test_cases = json.load(f)
        LOGGER.info(
            "[%s] component=verify action=load resource=test_cases.json from_where=%s status=success count=%s",
            ts,
            str(test_cases_path),
            len(test_cases) if isinstance(test_cases, list) else "unknown",
        )
    except Exception:
        LOGGER.exception(
            "[%s] component=verify action=load resource=test_cases.json from_where=%s status=failure",
            ts,
            str(test_cases_path),
        )
        raise

    return requirements, test_cases


def verify_requirements(requirements, test_cases):
    ts = datetime.now(timezone.utc).astimezone().isoformat()
    failures = []

    # Set of requirement_ids referenced by test cases
    try:
        test_ids = {t["requirement_id"] for t in test_cases if isinstance(t, dict) and "requirement_id" in t}
    except Exception:
        LOGGER.exception(
            "[%s] component=verify action=derive resource=test_cases status=failure",
            ts,
        )
        raise

    for r in requirements:
        if not isinstance(r, dict):
            failures.append("Invalid requirement object (not a dict)")
            continue

        rid = r.get("requirement_id", "")

        # Rule 1: Required fields exist (don't log entire object)
        for field in ["requirement_id", "description", "source"]:
            if field not in r:
                failures.append(f"Missing field '{field}' in requirement_id: {rid or '<missing>'}")

        # Rule 2: Requirement ID format
        if rid and not re.match(r"REQ-[A-Z]+-\d{3}[A-Z]$", rid):
            failures.append(f"Invalid requirement_id format: {rid}")

        # Rule 3: Each requirement must have at least one test case
        if rid and rid not in test_ids:
            failures.append(f"No test case for requirement: {rid}")

        # Rule 4: No vague phrases
        desc = r.get("description")
        if isinstance(desc, str) and "all hazards" in desc.lower():
            failures.append(f"Vague description in requirement: {rid}")

        # Rule 5: Parent-child ID consistency
        parent = r.get("parent")
        if isinstance(parent, str) and rid and not rid.startswith(parent):
            failures.append(f"Parent-child ID mismatch: {rid} (parent {parent})")

    LOGGER.info(
        "[%s] component=verify action=check resource=requirements status=%s failure_count=%s",
        ts,
        "failure" if failures else "success",
        len(failures),
    )
    return failures


def emit_results_and_exit(failures):
    ts = datetime.now(timezone.utc).astimezone().isoformat()
    if failures:
        print("Verification FAILED:")
        for f in failures:
            print("-", f)
        LOGGER.info(
            "[%s] component=verify action=exit status=failure failure_count=%s",
            ts,
            len(failures),
        )
        sys.exit(1)  # Exit with failure code for GitHub Actions
    else:
        print("Verification passed: all requirements meet structural rules.")
        LOGGER.info("[%s] component=verify action=exit status=success", ts)
        sys.exit(0)

if __name__ == "__main__":
    requirements, test_cases = load_inputs(DIR)
    failures = verify_requirements(requirements, test_cases)
    emit_results_and_exit(failures)