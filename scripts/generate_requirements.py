# scripts/generate_requirements.py from https://github.com/effat/CFR_TEST/blob/main/scripts/generate_requirements.py
import json
import re
import argparse
from collections import defaultdict

# ---------- Arguments ----------
parser = argparse.ArgumentParser(description="Generate requirement JSON from CFR Markdown")
parser.add_argument("--input", "-i", required=True, help="Input Markdown file (.md)")
parser.add_argument("--output", "-o", required=True, help="Output JSON file")
parser.add_argument("--cfr", "-c", required=True, help="CFR section (e.g., 21 CFR 117.130)")
parser.add_argument(
    "--expected-structure",
    "-e",
    required=True,
    help="Output JSON mapping parent requirement id -> list of child letters",
)

args = parser.parse_args()

INPUT_MD = args.input
OUTPUT_JSON = args.output
CFR_SECTION = args.cfr
EXPECTED_STRUCTURE_JSON = args.expected_structure
CATEGORY = "HAZ"

# ---------- Read File ----------
with open(INPUT_MD, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

requirements = []
current_req = None
expected_structure: dict[str, list[str]] = defaultdict(list)
child_index_by_parent: dict[str, int] = defaultdict(int)


def _clean_description(text: str) -> str:
    # Remove leading markdown bullets and leading numbering tokens like "(1)" "(i)" "(a)".
    text = re.sub(r"^\s*[-*]\s+", "", text)
    text = re.sub(r"^\(\s*[\wivxIVX]+\s*\)\s*", "", text)
    return text.strip()


def _extract_section_number(raw_req: str) -> str:
    # raw_req looks like "REQ-117.130-001" -> want "001"
    m = re.search(r"-(\d{3})$", raw_req)
    if not m:
        raise ValueError(f"Could not extract 3-digit section number from {raw_req!r}")
    return m.group(1)


def _next_letter(parent_id: str) -> str:
    i = child_index_by_parent[parent_id]
    if i >= 26:
        raise ValueError(f"Too many children under {parent_id}: only A-Z supported")
    child_index_by_parent[parent_id] += 1
    return chr(ord("A") + i)

# ---------- Parse ----------
for line in lines:

    # Capture REQ ID
    req_match = re.search(r"→\s*(REQ-[\d\.]+-\d+)", line)
    if req_match:
        current_req = req_match.group(1)
        continue

    # Capture atomic rules
    atomic_match = re.match(r"^(.*?)\s*→\s*([A-Z]\d*)$", line)
    if atomic_match and current_req:
        description = _clean_description(atomic_match.group(1))
        # Ignore the markdown-provided suffix (A/A1/B10/etc). The verifier expects a
        # single trailing letter, so we assign letters sequentially per parent.
        _ = atomic_match.group(2)

        section_num = _extract_section_number(current_req)
        parent = f"REQ-{CATEGORY}-{section_num}"
        letter = _next_letter(parent)
        requirement_id = f"{parent}{letter}"

        requirements.append({
            "requirement_id": requirement_id,
            "description": description,
            "source": CFR_SECTION,
            "parent": parent
        })
        expected_structure[parent].append(letter)

# ---------- Save ----------
with open(OUTPUT_JSON, "w") as f:
    json.dump(requirements, f, indent=2)

print(f"Saved {len(requirements)} requirements → {OUTPUT_JSON}")

if EXPECTED_STRUCTURE_JSON:
    with open(EXPECTED_STRUCTURE_JSON, "w") as f:
        json.dump(expected_structure, f, indent=2)
    print(f"Saved expected structure → {EXPECTED_STRUCTURE_JSON}")