# TechFinger — Quick Start (5 Minutes)

Get TechFinger running on Kali Linux in 5 minutes.

---

## Step 1️⃣: Clone

```bash
git clone https://github.com/HaQtor/TechFinger.git
cd TechFinger
```

## Step 2️⃣: Install

```bash
pip install -r requirements.txt
```

Or with virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3️⃣: Run

```bash
python3 techfinger.py -u https://example.com
```

**That's it!** You should see:

```
╔══════════════════════════════════════════════════════════╗
║  TechFinger v0.1.0 — Heuristic Technology Fingerprinting ║
╚══════════════════════════════════════════════════════════╝

[Technologies detected...]
[Stack correlation chain...]
[Security observations...]
```

---

## Common Commands

```bash
# Fast scan (5s timeout)
python3 techfinger.py -u https://target.com --profile fast

# Deep scan (30s, 10 JS files)
python3 techfinger.py -u https://target.com --profile deep

# Show confidence math
python3 techfinger.py -u https://target.com --explain

# Generate report + export evidence
python3 techfinger.py -u https://target.com --report --evidence

# JSON output (for scripts)
python3 techfinger.py -u https://target.com -o json > scan.json
```

---

## What You Get

✅ Technology stack detected  
✅ Confidence % for each tech  
✅ Risk assessment (High/Med/Low)  
✅ Security observations (CSP, HSTS, etc.)  
✅ Stack correlation chain  
✅ Investigation paths (next steps to test)  

---

## Next

- Full docs: [README.md](README.md)
- Kali setup: [INSTALL_KALI.md](INSTALL_KALI.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy fingerprinting! 🔍**
