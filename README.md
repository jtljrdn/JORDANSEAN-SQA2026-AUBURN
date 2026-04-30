# COMP-5710-project

Group project for Auburn University **COMP-5710: Software Quality Assurance**.

## Objective

Verification & Validation of regulatory requirements (21 CFR 117.130). The pipeline:

1. Parse a CFR Markdown section into atomic `requirements.json`.
2. Build an `expected_structure.json` mapping parent requirements → child letters.
3. Generate minimal `test_cases.json` (one case per requirement).
4. Run **verification** (structure matches expectation) and **validation** (every requirement has a test case).
5. Emit a forensic log of the run.

CI runs the same pipeline on every push via GitHub Actions.

## Reproducing locally

### mac

```bash
git clone https://github.com/jtljrdn/JORDANSEAN-SQA2026-AUBURN/
cd JORDANSEAN-SQA2026-AUBURN
python3 -m venv .venv
source .venv/bin/activate

cd scripts
python generate_requirements.py -i "../Input CFR File/CFR-117.130.md" \
    -o requirements.json -c "21 CFR 117.130" -e expected_structure.json
python generate_test_cases.py
python verify.py
python validate.py
```

### windows

```powershell
git clone https://github.com/jtljrdn/JORDANSEAN-SQA2026-AUBURN/
cd JORDANSEAN-SQA2026-AUBURN
python -m venv .venv
.\.venv\Scripts\Activate.ps1

cd scripts
python generate_requirements.py -i "..\Input CFR File\CFR-117.130.md" `
    -o requirements.json -c "21 CFR 117.130" -e expected_structure.json
python generate_test_cases.py
python verify.py
python validate.py
```

Outputs (`requirements.json`, `expected_structure.json`, `test_cases.json`) should match the files in `sample outputs/`. `FORENSIC-LOG.log` is appended to on each run.
