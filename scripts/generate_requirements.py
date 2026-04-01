# scripts/extract_requirements.py

import json
import re
import sys

def parse_md_to_requirements(md_file):
    """
    Parses a Markdown file with CFR section atomic rules and produces requirements.json
    """
    requirements = []
    current_parent_id = None
    current_parent_desc = None
    parent_counter = {}

    with open(md_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        # Match top-level section (a), (b), (c) with REQ ID
        parent_match = re.match(r"^\(([a-z])\)\s+(.*)→\s+(REQ-[\d\.]+-\d+)", line)
        if parent_match:
            letter, desc, req_id = parent_match.groups()
            current_parent_id = req_id
            current_parent_desc = desc
            parent_counter[current_parent_id] = 0
            continue

        # Match child atomic units (numbered or lettered)
        child_match = re.match(r"^(?:\(?(\d+|[a-zA-Z])\)?[:\s]*)?(.*?)(?:→\s*([A-Z0-9]+))?$", line)
        if child_match and current_parent_id:
            identifier, desc, child_letter = child_match.groups()
            if not child_letter:
                # Auto-assign letters for children if not provided
                parent_counter[current_parent_id] += 1
                child_letter = chr(64 + parent_counter[current_parent_id])  # A, B, C...
            req = {
                "requirement_id": f"{current_parent_id}{child_letter}",
                "description": desc.strip(),
                "source": "21 CFR " + current_parent_id.split('-')[1],
                "parent": current_parent_id
            }
            requirements.append(req)

    return requirements

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_requirements.py atomic_rules.md")
        sys.exit(1)

    md_file = sys.argv[1]
    requirements = parse_md_to_requirements(md_file)

    with open("requirements.json", "w") as f:
        json.dump(requirements, f, indent=2)

    print(f"Extracted {len(requirements)} requirements to requirements.json")
