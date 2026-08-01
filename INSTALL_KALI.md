# TechFinger Installation & Usage Guide for Kali Linux

Complete guide to install, configure, and run TechFinger on Kali Linux.

---

## 📋 Prerequisites

- **Kali Linux 2024+** (or any Debian-based Linux)
- **Python 3.11+** (check: `python3 --version`)
- **Git** (for cloning: `sudo apt install git`)
- **pip** (usually comes with Python, check: `pip3 --version`)

---

## 🚀 Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/HaQtor/TechFinger.git
cd TechFinger

# 2. (Optional but recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test installation
python3 techfinger.py --help
```

**Expected output:**
```
usage: techfinger [-h] -u URL [--profile {fast,balanced,deep}] ...
TechFinger — Explainable heuristic technology fingerprinting.
```

---

### Method 2: System-Wide Installation

If you want to run `techfinger` from anywhere on your Kali system:

```bash
# 1. Clone the repo
git clone https://github.com/HaQtor/TechFinger.git
cd TechFinger

# 2. Install dependencies globally
pip install -r requirements.txt

# 3. Create symlink to /usr/local/bin
sudo ln -s $(pwd)/techfinger.py /usr/local/bin/techfinger

# 4. Make executable
chmod +x techfinger.py

# 5. Test from anywhere
techfinger -u https://example.com --profile fast
```

Now you can run `techfinger` directly without `python3 techfinger.py`.

---

### Method 3: Install in Kali's Python Environment

For persistent installation across system updates:

```bash
# 1. Install dependencies system-wide
sudo pip install -r requirements.txt

# 2. Copy files
sudo cp techfinger.py /usr/local/bin/
sudo cp patterns.py /usr/local/lib/python3/dist-packages/

# 3. Ensure executable
sudo chmod +x /usr/local/bin/techfinger.py
```

---

## ✅ Verification

After installation, verify everything works:

```bash
# Test 1: Python imports
python3 -c "import requests, bs4, rich; print('✓ Dependencies OK')"

# Test 2: CLI help
python3 techfinger.py --help

# Test 3: Quick scan (use example.com or your own target)
python3 techfinger.py -u https://example.com --profile fast

# Expected: TechFinger banner + scan results
```

---

## 🎯 Common Usage Patterns

### 1. Quick Recon (Fast Profile)

```bash
python3 techfinger.py -u https://target.com --profile fast

# Time: ~0.3-0.8s
# Use: Large-scope scans, mass reconnaissance
```

### 2. Balanced Pentesting (Default)

```bash
python3 techfinger.py -u https://target.com

# or explicitly:
python3 techfinger.py -u https://target.com --profile balanced

# Time: ~1.0-2.5s
# Use: Standard pentest workflow
# Features: Deep JS analysis (3 files), version extraction
```

### 3. Deep Assessment (Deep Profile)

```bash
python3 techfinger.py -u https://target.com --profile deep

# Time: ~3.0-8.0s
# Use: Thorough assessment, source map hunting
# Features: Fetch up to 10 external JS files, API endpoint detection
```

### 4. Full Report with Explanations

```bash
python3 techfinger.py -u https://target.com \
  --profile deep \
  --explain \
  --report \
  --evidence

# Outputs:
# - Terminal: confidence breakdowns for every finding
# - report.md: professional Markdown report for clients
# - evidence/: raw data directory (headers, cookies, findings.json, etc.)
```

### 5. JSON Output for Scripting

```bash
# Redirect to file
python3 techfinger.py -u https://target.com -o json > scan.json

# Parse with jq
cat scan.json | jq '.technologies[] | select(.confidence >= 70)'

# Check for specific technology
python3 techfinger.py -u https://target.com -o json | \
  jq '.technologies[] | select(.name == "Laravel")'
```

### 6. Compare Scans Over Time

```bash
# First scan (baseline)
python3 techfinger.py -u https://target.com --profile balanced -o json > baseline.json

# (Wait days/weeks/months)

# Later scan (comparison)
python3 techfinger.py -u https://target.com --profile balanced --compare baseline.json

# Output: Shows added/removed/updated technologies and new contradictions
```

### 7. Timeout & Deep Settings Override

```bash
# Increase timeout, fetch more JS files
python3 techfinger.py -u https://target.com \
  --profile balanced \
  --timeout 20 \
  --max-js 8 \
  --max-size 2000000

# Only fetch same-origin JS
python3 techfinger.py -u https://target.com \
  --profile deep \
  --same-origin-only
```

---

## 🔧 Troubleshooting

### ImportError: No module named 'requests'

```bash
# Solution 1: Install via pip
pip install requests beautifulsoup4 rich

# Solution 2: Use --break-system-packages (Kali-specific)
pip install --break-system-packages requests beautifulsoup4 rich

# Solution 3: Upgrade pip first
python3 -m pip install --upgrade pip
pip install requests beautifulsoup4 rich
```

### SSL Certificate Verification Error

```bash
# If you get: "SSL: CERTIFICATE_VERIFY_FAILED"
# This is normal in lab/testing environments

# Solution 1 (Recommended): Update CA certificates
sudo update-ca-certificates --fresh

# Solution 2: Use a testing proxy (Burp Suite, ZAP)
# Just run TechFinger normally, it will work through the proxy
```

### Connection Timeout

```bash
# If scans timeout on slow networks:
python3 techfinger.py -u https://target.com --timeout 30

# Increase from default 10s to 30s
```

### Permission Denied Running Script

```bash
# Make it executable
chmod +x techfinger.py

# Then run with ./
./techfinger.py -u https://target.com
```

### "Command not found: techfinger"

If you installed system-wide but get this error:

```bash
# Check if symlink exists
ls -l /usr/local/bin/techfinger

# If missing, create it
sudo ln -s $(pwd)/techfinger.py /usr/local/bin/techfinger

# Then verify
techfinger --help
```

---

## 📂 Output Files

After running TechFinger with flags, you'll get:

### `report.md` (with `--report`)

Professional Markdown report including:
- Detected technologies table
- Stack correlation chain
- Contradictions
- Security observations
- Investigation paths

Use in:
- Client deliverables
- Pentest reports
- GitHub wikis
- Confluence pages

### `evidence/` directory (with `--evidence`)

Raw scan artifacts:
- `headers.txt` — HTTP response headers
- `cookies.txt` — Cookie names
- `body.html` — HTML response (first 1MB)
- `scripts.txt` — External + inline script count
- `findings.json` — Structured detection data
- `contradictions.txt` — Conflict details
- `observations.txt` — Security observations

Use for:
- Evidence preservation
- Detailed review
- Compliance documentation

---

## 🔄 Automation & CI/CD

### Bash Script for Batch Scanning

```bash
#!/bin/bash
# batch_scan.sh

TARGETS=("https://site1.com" "https://site2.com" "https://site3.com")

for target in "${TARGETS[@]}"; do
    echo "[*] Scanning: $target"
    python3 techfinger.py -u "$target" --profile fast -o json > "${target//https:\/\//}.json"
    sleep 2  # Rate limiting
done

echo "[✓] Batch scan complete"
```

Usage:
```bash
chmod +x batch_scan.sh
./batch_scan.sh
```

### Parse Results with jq

```bash
# Find all high-risk techs across all scans
for f in *.json; do
    echo "=== $f ==="
    cat "$f" | jq '.technologies[] | select(.risk == "High") | .name'
done
```

### Generate Summary Report

```bash
# Count unique technologies found
cat *.json | jq -r '.technologies[].name' | sort | uniq -c

# Find most common framework
cat *.json | jq -r '.technologies[] | select(.category == "Framework") | .name' | sort | uniq -c | sort -rn | head -5
```

---

## 🛡️ Security Best Practices

### 1. Always Get Permission

- Written authorization before scanning any target
- Follow scope defined in authorization
- Respect rate limiting and DoS policies

### 2. Use Responsibly

```bash
# Good: Single target, balanced profile
python3 techfinger.py -u https://authorized-client.com

# Bad: Mass scanning without authorization
for i in {1..1000}; do
    python3 techfinger.py -u "https://random-site-${i}.com" &
done
```

### 3. Protect Output Files

```bash
# Reports may contain sensitive info
chmod 600 report.md
chmod 700 evidence/
```

### 4. Clean Up After Scans

```bash
# Remove evidence if not needed
rm -rf evidence/

# Securely wipe if highly sensitive
shred -vfz -n 3 report.md  # Kali has shred by default
```

---

## 🐛 Debugging

### Verbose Output

Currently TechFinger doesn't have a `--verbose` flag, but you can inspect the JSON output:

```bash
python3 techfinger.py -u https://target.com -o json | jq .
```

### Check Confidence Breakdown

```bash
python3 techfinger.py -u https://target.com --explain | grep -A 10 "Confidence Breakdown"
```

### Test Specific Features

```bash
# Test --explain flag
python3 techfinger.py -u https://target.com --explain | head -50

# Test --report flag
python3 techfinger.py -u https://target.com --report && cat report.md

# Test --evidence flag
python3 techfinger.py -u https://target.com --evidence && ls -la evidence/
```

---

## 📚 Advanced Usage

### Custom Request Headers

Currently TechFinger doesn't support custom headers, but you can modify source:

Edit `techfinger.py`, line ~150:
```python
headers={"User-Agent": f"TechFinger/{__version__}"},
```

Change to:
```python
headers={
    "User-Agent": f"TechFinger/{__version__}",
    "X-Custom-Header": "value",
},
```

### Proxy Support

TechFinger uses `requests` library, which respects HTTP(S) proxy environment variables:

```bash
# Via Burp Suite
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"
python3 techfinger.py -u https://target.com

# Via Fiddler
export HTTPS_PROXY="http://127.0.0.1:8888"
python3 techfinger.py -u https://target.com --profile fast
```

### Add Custom Detection Rules

Edit `patterns.py` and add your rule:

```python
HEADER_PATTERNS: dict[str, dict[str, tuple[str, str]]] = {
    "X-Custom-Header": {
        r"MyTech[/\s]?([\d.]+)?": ("MyTech", "Framework"),
    },
}
```

Restart TechFinger, it will auto-load your new rule.

---

## 📖 Next Steps

1. **Read README.md** — full feature documentation
2. **Review examples** — in README.md "Usage Examples" section
3. **Contribute** — see CONTRIBUTING.md for adding detection rules
4. **Report issues** — found a bug? GitHub Issues

---

## 🆘 Support

- 📖 **Documentation** — README.md, this file
- 🐛 **Bug reports** — GitHub Issues
- 💡 **Feature requests** — GitHub Issues with label `enhancement`
- 💬 **Questions** — GitHub Discussions (coming soon)

---

## 🎓 Learning Resources

- **Fingerprinting Concepts** — [OWASP](https://owasp.org/)
- **Python 3.11+ Features** — [Real Python](https://realpython.com/)
- **Penetration Testing** — [HackTheBox](https://www.hackthebox.com/), [TryHackMe](https://tryhackme.com/)
- **jq for JSON** — [jq Manual](https://stedolan.github.io/jq/)

---

## 🎯 TechFinger on Kali — Checklist

- [ ] Cloned from GitHub
- [ ] `pip install -r requirements.txt` succeeded
- [ ] `python3 techfinger.py --help` works
- [ ] Scanned example.com successfully
- [ ] Generated `--report` and `--evidence`
- [ ] Compared two scans with `--compare`
- [ ] Integrated with your pentest workflow

---

**You're all set! Happy fingerprinting. 🔍🎯**

For more: `python3 techfinger.py --help` or check [README.md](README.md)
