
# TechFinger Quick Start

Get TechFinger running in under 5 minutes.

---

## Installation

```bash
git clone https://github.com/belsopky/TechFinger.git
cd TechFinger
pip install -r requirements.txt
```

Or with a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## First Scan

```bash
python3 techfinger.py -u https://example.com
```

Expected output:

```text
TechFinger v0.1.0
Target: https://example.com | Status: 200 | Profile: balanced

High Confidence (>=70%)
+----------------+----------+---------+------+-----------+------------+
| Technology     | Category | Version | Risk | Evidence  | Confidence |
+----------------+----------+---------+------+-----------+------------+
| Nginx          | Web Srv  | 1.18.0  | Low  | 3 items   | 100%       |
| PHP            | Runtime  | 8.1.2   | Med  | 2 items   | 92%        |
| Laravel        | Frwk     | 10.x    | High | 4 items   | 95%        |
+----------------+----------+---------+------+-----------+------------+

Likely Stack Chain
Nginx (Web Server) — 100%
    |
    v
PHP (Language) — 92%
    |
    v
Laravel (Framework) — 95%
```

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `python3 techfinger.py -u https://target.com --profile fast` | Quick reconnaissance (5s timeout) |
| `python3 techfinger.py -u https://target.com --profile deep` | Thorough scan (30s, 10 JS files) |
| `python3 techfinger.py -u https://target.com --explain` | Show confidence math breakdown |
| `python3 techfinger.py -u https://target.com --report --evidence` | Generate report.md and evidence/ directory |
| `python3 techfinger.py -u https://target.com -o json > scan.json` | JSON output for scripting |

---

## Output

- Detected technologies with confidence percentages
- Risk assessment (High / Medium / Low)
- Security observations (CSP, HSTS, cookie flags)
- Technology stack correlation chain
- Investigation paths for manual follow-up

---

## Next Steps

- Full documentation: [README.md](README.md)
- Kali Linux setup: [INSTALL_KALI.md](INSTALL_KALI.md)
- Contributing guidelines: [CONTRIBUTING.md](CONTRIBUTING.md)
```
