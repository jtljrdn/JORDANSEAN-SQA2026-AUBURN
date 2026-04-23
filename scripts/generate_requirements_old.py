# scripts/extract_requirements.py

import json
import re
import sys

def parse_md_to_requirements(md_file):
    """
    Parses a Markdown file with CFR section atomic rules and produces:
    1. requirements.json-style list
    2. expected structure mapping of parent -> child codes
    """

    requirements = []
    expected_structure = {}
    current_parent_id = None

    with open(md_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        # Match parent section headers, e.g.
        # ## (a) Requirement for a hazard analysis → REQ-117.130-001
        parent_match = re.match(r"^##\s+\(([a-z])\)\s+(.*?)\s*→\s*(REQ-[\d\.]+-\d+)\s*$", line)
        if parent_match:
            _, _, req_id = parent_match.groups()
            current_parent_id = req_id
            expected_structure[current_parent_id] = []
            continue

        # Match child bullet lines, e.g.
        # - (1) Conduct hazard analysis → A
        # - Identify known hazards → B
        # - (i) Assess severity... → A1
        child_match = re.match(r"^-\s*(?:\([^)]+\)\s*)?(.*?)\s*(?:→\s*([A-Z0-9]+))?\s*$", line)
        if child_match and current_parent_id:
            desc, child_code = child_match.groups()
            desc = desc.strip()

            # Ignore structural lines with no explicit child code
            # Example:
            # - (1) Known or reasonably foreseeable hazards include:
            # - (2) Consider hazards for origin:
            if not child_code:
                continue

            req = {
                "requirement_id": f"{current_parent_id}{child_code}",
                "description": desc,
                "source": "21 CFR " + current_parent_id.split("-")[1],
                "parent": current_parent_id
            }
            requirements.append(req)
            expected_structure[current_parent_id].append(child_code)

    return requirements, expected_structure


def parse_json_to_expected_structure(req_file):
    """
    Reads requirements.json and builds:
    {
      "REQ-117.130-001": ["A", "B", ...],
      ...
    }
    """
    with open(req_file, "r", encoding="utf-8") as f:
        requirements = json.load(f)

    expected_structure = {}

    for req in requirements:
        parent = req["parent"]
        requirement_id = req["requirement_id"]

        child_code = requirement_id.replace(parent, "", 1)

        if parent not in expected_structure:
            expected_structure[parent] = []

        expected_structure[parent].append(child_code)

    return expected_structure


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_requirements.py atomic_rules.md")
        sys.exit(1)

    md_file = sys.argv[1]
    requirements, expected_structure = parse_md_to_requirements(md_file)

    with open("requirements.json", "w", encoding="utf-8") as f:
        json.dump(requirements, f, indent=2, ensure_ascii=False)

    with open("expected_structure.json", "w", encoding="utf-8") as f:
        json.dump(expected_structure, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(requirements)} requirements to requirements.json")
    print(f"Wrote expected structure for {len(expected_structure)} parents to expected_structure.json")
