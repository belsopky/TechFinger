markdown
TechFinger Installation Guide Kali Linux
==========================================

Prerequisites
-------------

- Kali Linux 2024+ (or any Debian-based distribution)
- Python 3.11+
- Git
- pip

Check versions:

    python3 --version
    pip3 --version

Installation
------------

### From Source

    git clone https://github.com/belsopky/TechFinger.git
    cd TechFinger
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### System-Wide (Optional)

    sudo ln -s $(pwd)/techfinger.py /usr/local/bin/techfinger
    chmod +x techfinger.py

Verification
------------

    python3 -c "import requests, bs4, rich; print('Dependencies OK')"
    python3 techfinger.py --help
    python3 techfinger.py -u https://example.com --profile fast

Usage
-----

### Scan Profiles

| Profile | Timeout | Deep JS | Max JS Files | Purpose |
|---------|---------|---------|--------------|---------|
| fast | 5s | No | 0 | Quick reconnaissance |
| balanced | 10s | Yes | 3 | Default pentesting |
| deep | 30s | Yes | 10 | Thorough assessment |

Override parameters:

    python3 techfinger.py -u https://target.com --profile balanced --timeout 15 --max-js 5

### Common Commands

Default scan:

    python3 techfinger.py -u https://target.com

Fast scan:

    python3 techfinger.py -u https://target.com --profile fast

Deep scan with full output:

    python3 techfinger.py -u https://target.com \
      --profile deep \
      --explain \
      --report \
      --evidence

JSON output:

    python3 techfinger.py -u https://target.com -o json > scan.json

Parse with jq:

    cat scan.json | jq '.technologies[] | select(.confidence >= 70)'

Proxy Support
-------------

TechFinger uses the `requests` library and respects standard proxy environment variables:

    export HTTP_PROXY="http://127.0.0.1:8080"
    export HTTPS_PROXY="http://127.0.0.1:8080"
    python3 techfinger.py -u https://target.com

Troubleshooting
---------------

### ImportError: No module named 'requests'

    pip install requests beautifulsoup4 rich

Or on Kali with system Python:

    pip install --break-system-packages requests beautifulsoup4 rich

### SSL Certificate Verification Failed

    sudo update-ca-certificates --fresh

Or ensure your target's certificate is valid. TechFinger does not bypass certificate verification by default.

### Connection Timeout

    python3 techfinger.py -u https://target.com --timeout 30

### Permission Denied

    chmod +x techfinger.py
    ./techfinger.py -u https://target.com

Output Files
------------

### report.md (generated with --report)

Contains:
- Detected technologies table
- Stack correlation chain
- Contradictions
- Security observations
- Investigation paths

### evidence/ directory (generated with --evidence)

Contains:
- headers.txt
- cookies.txt
- body.html
- scripts.txt
- findings.json
- contradictions.txt
- observations.txt

Automation
----------

### Batch Scanning

    #!/bin/bash
    TARGETS=("https://site1.com" "https://site2.com" "https://site3.com")

    for target in "${TARGETS[@]}"; do
        echo "[*] Scanning: $target"
        python3 techfinger.py -u "$target" --profile fast -o json > "${target//https:\/\//}.json"
        sleep 2
    done

### Parse Results

Find high-risk technologies:

    cat *.json | jq '.technologies[] | select(.risk == "High") | .name'

Count unique technologies:

    cat *.json | jq -r '.technologies[].name' | sort | uniq -c

Security Notes
--------------

- Use only on authorized targets
- Follow defined scope and rate limits
- Protect output files: `chmod 600 report.md`
- Remove evidence when no longer needed: `rm -rf evidence/`

Adding Custom Rules
-------------------

Edit `patterns.py`:

1. Add regex to `HEADER_PATTERNS`, `HTML_PATTERNS`, `JS_GLOBALS`, or `ERROR_PATTERNS`
2. Add risk level to `RISK_LEVELS`
3. Add investigation paths to `INVESTIGATION_PATHS`
4. Test with `python3 techfinger.py -u <target> --explain`

See CONTRIBUTING.md for detailed guidelines.

---
For full documentation: README.md
For adding rules: CONTRIBUTING.md
```
