# CodeAlpha — Secure Coding Review (CodeShield)

A local Flask-based static review tool for small `.py`, `.php`, `.js`, `.html`, and `.sql` source files. It checks a set of common risky patterns and returns severity, line numbers, excerpts, remediation advice, and a downloadable JSON report. Includes deliberately vulnerable training samples.

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5003`, download a sample, then upload it to see findings.

## What it checks
Potential SQL injection patterns, hardcoded secrets, weak password hashing, dynamic code execution, shell command construction, XSS-prone output, CSRF review cues, disabled TLS verification, insecure randomness, and unsafe upload patterns.

## Important limitations
This is a teaching/demo heuristic scanner, not a complete SAST product. Regex-based rules can miss issues, flag safe code, and lack full data-flow/context analysis. A finding is not proof of exploitability, and no findings do not prove code is secure. Confirm findings manually and use mature tools (for example Semgrep or Bandit) for a more complete review.

## Safety
The sample files are intentionally vulnerable and must never be deployed. Use only code you own or are authorized to audit. Uploaded source is processed locally and not transmitted to third parties. The app binds to localhost.
