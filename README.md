# TechFinger v0.1.0

> **Explainable Technology Fingerprinting** — Heuristic analysis that reveals *why* each technology was detected, with mathematical confidence breakdowns, contradiction detection, and full-stack correlation.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-stable-green)

---

## 🎯 The Problem

Traditional fingerprinting tools (Wappalyzer, BuiltWith) rely on massive, constantly-updated external signature databases. They miss custom/modified stacks, require perpetual maintenance, and provide limited insight into *why* a detection was made.

**TechFinger** is different:
- **No External Database** — All 300+ detection rules embedded in source code
- **Explainable AI** — Every finding includes confidence math breakdown
- **Contradiction Detection** — Flags conflicting evidence (e.g., Apache + Nginx)
- **Stack Correlation** — Builds the likely tech chain: CDN → Web Server → Language → Framework → Frontend
- **Heuristic + Evidence** — Combines weighted evidence scoring with human reasoning

Perfect for:
- **Penetration Testing** — Quick stack reconnaissance, zero dependencies on external DBs
- **OSINT** — Understand target architecture without noisy signatures
- **Portfolio/Research** — Show confidence reasoning in reports
- **Incident Response** — Rapid tech stack assessment

---

## ⚡ Quick Start

### 1. Install

```bash
# Clone repo
git clone https://github.com/HaQtor/TechFinger.git
cd TechFinger

# Install dependencies (Python 3.11+)
pip install -r requirements.txt
```

### 2. Run

```bash
# Default (balanced profile: 10s timeout, deep JS analysis)
python techfinger.py -u https://target.com

# Fast scan (large scope, quick recon)
python techfinger.py -u https://target.com --profile fast

# Deep scan (thorough, JS fetching, 30s timeout)
python techfinger.py -u https://target.com --profile deep

# With full explainability + report + evidence export
python techfinger.py -u https://target.com --explain --report --evidence

# JSON output (scripting/automation)
python techfinger.py -u https://target.com -o json

# Compare against previous scan
python techfinger.py -u https://target.com --compare previous_scan.json
```

### 3. Output

Terminal output includes:
- **High/Medium/Low Confidence Tables** — with risk levels
- **Confidence Breakdown** (`--explain`) — mathematical proof of each finding
- **Stack Correlation Chain** — CDN → Web Server → Framework → Frontend
- **Contradictions Panel** — conflicting evidence with penalties
- **Security Observations** — CSP, HSTS, cookie flags, version leaks
- **Investigation Paths** — suggested manual tests for each tech

Optional side-effects:
- **`--evidence`** → `evidence/` directory with raw response, headers, cookies, findings JSON
- **`--report`** → `report.md` Markdown report for clients
- **`-o json`** → structured JSON output for CI/CD pipelines

---

## 📊 Features

### Scan Profiles

| Profile | Timeout | Deep JS | Max Files | Purpose |
|---------|---------|---------|-----------|---------|
| `fast` | 5s | ❌ | 0 | Quick reconnaissance, large-scope scans |
| `balanced` | 10s | ✅ | 3 files | Default pentesting workflow |
| `deep` | 30s | ✅ | 10 files | Thorough assessment, source map hunting |

Override any profile parameter:
```bash
python techfinger.py -u https://target.com --profile balanced --timeout 15 --max-js 5
```

### Detection Coverage

**Headers** — X-Powered-By, Server, X-Generator, X-AspNet-Version, etc.

**Cookies** — Django, Express, Laravel, PHP, ASP.NET, WordPress, JWT, Analytics

**HTML DOM** — React, Vue.js, Angular, Bootstrap, Tailwind, Next.js, Nuxt, jQuery, Gatsby, Svelte

**JavaScript Globals** — window.React, window.Vue, window.angular, window.gtag, etc.

**Error Pages** — Django, Flask, Laravel, ASP.NET, Spring Boot, Nginx, Apache, Ruby on Rails

**Session Patterns** — PHPSESSID, sessionid, connect.sid, laravel_session, rack.session

**1,000+ Technology Fingerprints** — All regex-based, no ML, no AI lookups

### Confidence Scoring Engine

Every finding shows:
```
Primary Evidence:        cookie: sessionid (reliability: 0.90)
Bonus Evidence:          +16 (2 additional types)
Version Bonus:           +12 (version extracted)
Conflict Penalty:        -20 (contradicts Laravel)
─────────────────────────
Final Confidence:        95%
```

**Reliability Weights:**
- Direct version in header: **1.0** (100 base score)
- Official framework cookie: **0.9** (90 base score)
- Error page match: **0.85** (85 base score)
- DOM pattern (multi): **0.75** (75 base score)
- JS global object: **0.65** (65 base score)
- Single DOM pattern: **0.5** (50 base score)
- Generic header: **0.4** (40 base score)

### Contradiction Detection

If Apache *and* Nginx headers detected:
```
⚠️ Possible reverse proxy: Apache → Nginx (-15 confidence penalty)
```

Supports 6+ contradiction rules out-of-the-box, easily extensible.

### Stack Correlation

Outputs the likely technology chain:
```
Cloudflare (CDN/WAF) — 95%
    ↓
Nginx (Web Server) — 100%
    ↓
PHP (Language/Runtime) — 90%
    ↓
Laravel (Framework) — 95%
    ↓
React (Frontend Framework) — 93%
```

### Passive Security Observations

**Not** a vuln scanner. Just observations:
- CSP Missing / HSTS Missing (Medium severity)
- Cookies missing Secure/HttpOnly flags (Low)
- Server version leaks (Info)
- X-Powered-By exposed (Info)
- X-Frame-Options, X-Content-Type-Options missing (Low)

### Investigation Paths

Per-technology suggested manual tests:

```
Laravel
  • Check .env file exposure
  • Laravel debug mode
  • Ignition RCE (CVE-2021-3129)
  • Queue workers

React
  • Check source maps (*.js.map)
  • Exposed API endpoints in JS bundles
  • Hardcoded secrets in JS
```

---

## 📁 File Structure

```
TechFinger/
├── techfinger.py          # Main CLI tool (1,049 lines)
├── patterns.py            # Embedded detection rules (320 lines)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT
└── plugins/               # Future plugin architecture
    ├── __init__.py
    └── README.md
```

**Two-file design by spec:**
- `patterns.py` — pure constants (regex patterns, weights, risk levels, investigation paths)
- `techfinger.py` — all logic (extractors, scorers, renderers, CLI)

**No external signature databases.** All detection lives in source code → auditable, forkable, versioned.

---

## 🛠️ Usage Examples

### 1. Pentesting Recon (Default)

```bash
$ python techfinger.py -u https://example.com

╔══════════════════════════════════════════════════════════╗
║  TechFinger v0.1.0 — Heuristic Technology Fingerprinting ║
║  Author: HaQtor | No external signatures | Explainable   ║
╚══════════════════════════════════════════════════════════╝

[*] Plugin system ready. 0 plugins discovered.

                             Scan Info
┌────────────────────────────────────────────────────────────┐
│ Target: https://example.com                                │
│ Status: 200   Response Time: 245ms   Profile: balanced     │
└────────────────────────────────────────────────────────────┘

                         High Confidence (≥70%)
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┳━━━━┓
┃ Technology ┃Category┃ Version  ┃ Risk ┃ Evidence  ┃Conf┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━╇━━━━┩
│ Nginx      │Web Srv │ 1.18.0   │Low   │3 items    │100%│
│ PHP        │Runtime │ 8.1.2    │Med   │2 items    │92% │
│ Laravel    │Frwk    │ 10.x     │High  │4 items    │95% │
└────────────────────────────────────────────────────────────┘

                    Likely Stack Chain
┌─────────────────────────────────────────────────────────┐
│ Nginx (Web Server) — 100%                               │
│     ↓                                                   │
│ PHP (Language/Runtime) — 92%                            │
│     ↓                                                   │
│ Laravel (Framework) — 95%                               │
└─────────────────────────────────────────────────────────┘
```

### 2. Full Assessment with Reports

```bash
python techfinger.py -u https://example.com \
  --profile deep \
  --explain \
  --report \
  --evidence

# Outputs:
# - report.md (Markdown report)
# - evidence/ directory (headers, cookies, findings.json, etc.)
# - Terminal: confidence breakdowns for every finding
```

### 3. Scripting / CI/CD

```bash
# JSON output
python techfinger.py -u https://example.com -o json > scan.json

# Parse with jq
cat scan.json | jq '.technologies[] | select(.confidence >= 70)'

# Check for specific tech
python techfinger.py -u https://example.com -o json | \
  jq '.technologies[] | select(.name == "Laravel")'
```

### 4. Compare Scans

Track changes over time:

```bash
# Scan 1 (baseline)
python techfinger.py -u https://example.com -o json > baseline.json

# Later: Scan 2
python techfinger.py -u https://example.com --compare baseline.json

# Output:
# [+] Added: Cloudflare (CDN/WAF) — 95%
# [-] Removed: Apache (Web Server)
# [~] Updated: Laravel 10 → Laravel 11
# [!] New contradiction: Nginx vs IIS
```

---

## 🔧 Installation on Kali Linux

```bash
# 1. Clone the repo
git clone https://github.com/HaQtor/TechFinger.git
cd TechFinger

# 2. (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make executable (optional)
chmod +x techfinger.py

# 5. Run
python3 techfinger.py -u https://target.com --profile fast

# Or add to PATH for system-wide access:
sudo cp techfinger.py /usr/local/bin/
cd /usr/local/bin && python3 -m pip install -r /path/to/requirements.txt
```

### Troubleshooting

**ImportError: No module named 'requests'**
```bash
pip install requests beautifulsoup4 rich --break-system-packages
```

**SSL Certificate Errors**
```bash
# Kali: update certificates
sudo update-ca-certificates

# Or bypass (not recommended for prod):
python techfinger.py -u https://target.com  # Uses urllib3 cert verification
```

**Permission Denied**
```bash
chmod +x techfinger.py
./techfinger.py -u https://target.com
```

---

## 📦 Requirements

- **Python 3.11+** (3.12+ tested and verified)
- **requests** — HTTP client
- **beautifulsoup4** — HTML parsing
- **rich** — terminal rendering

Install all:
```bash
pip install -r requirements.txt
```

No external signature databases, no API keys, no cloud calls.

---

## 🔍 How It Works

### 1. Fetch
GET the target URL, capture:
- HTTP headers (Server, X-Powered-By, X-Generator, etc.)
- Response cookies (session identifiers, tracking)
- HTML body (DOM structure)
- Response status code

### 2. Extract
Run all extractors in parallel:
- **Header patterns** → regex against header names/values
- **Cookie names** → direct mapping (PHPSESSID → PHP)
- **HTML DOM patterns** → Vue data attributes, React div#root, ng-app, etc.
- **JS globals** → window.React, window.gtag, etc. (inline + fetched external)
- **Error pages** → 404/500 body analysis for framework fingerprints

### 3. Analyze
For each detected technology:
- Gather all supporting evidence (multiple evidence types = higher confidence)
- Apply reliability weights per evidence type
- Calculate weighted score with bonuses for multiple evidence types + version info
- Cap at 100%

### 4. Contradict
Cross-reference against CONTRADICTIONS ruleset:
- Detect conflicting evidence (Apache + Nginx = reverse proxy indicator)
- Apply penalty to confidence scores
- Flag with human-readable note

### 5. Correlate
Order findings by STACK_ORDER (CDN → Web Server → Language → Framework → Frontend):
- Build the likely technology chain
- Show interdependencies

### 6. Observe
Passive security checks:
- CSP/HSTS headers missing
- Cookie security flags (Secure, HttpOnly)
- Version information leaks
- Recommended security headers absent

### 7. Report
Render findings with:
- Confidence-tier tables (High/Med/Low)
- Explain mode (confidence math + evidence for every finding)
- Stack chain visualization
- Contradictions highlighted
- Security observations with severity
- Investigation paths per technology

---

## 🎯 Risk Levels

Each technology is assigned a qualitative risk for triage:

| Risk | Reason | Examples |
|------|--------|----------|
| **High** | Large attack surface, known CVEs, common misconfigurations | Laravel, Express.js, WordPress |
| **Medium** | Moderate attack surface, framework-specific issues | Django, PHP, ASP.NET, Flask |
| **Low** | Frontend/minimal direct attack surface | React, Angular, Vue.js, Nginx |

Risk doesn't imply vulnerability—it's context for penetration testing prioritization.

---

## 📝 Architecture

### Modular Design

**All functions < 30 lines** — easy to audit, test, fork.

**Extractors** — pluggable evidence collectors:
- `extract_headers()`
- `extract_cookies()`
- `extract_html_patterns()`
- `extract_js_globals()`
- `analyze_error_page()`

**Scorers** — confidence calculation:
- `_weigh_evidence()` — map evidence to reliability weights
- `_score_finding()` — compute final confidence with bonuses
- `calculate_confidence()` — batch scoring with contradiction penalties

**Renderers** — output generation:
- `render_terminal()` — rich-formatted tables + panels
- `render_json()` — structured data export
- `generate_report()` — Markdown report

**Utilities** — dev/ops features:
- `deep_analysis()` — fetch external JS files
- `detect_contradictions()` — cross-reference tech conflicts
- `correlate_stack()` — order findings by layer
- `compare_scans()` — diff previous vs current

**Plugin Stub** — future extensibility:
- `load_plugins()` — discovers plugins/ directory
- Planned: custom patterns, extractors, report formatters

---

## 🚀 Performance

Typical scan times (balanced profile, standard network):

- **Fast Profile** (no deep JS) — **0.3–0.8s**
- **Balanced Profile** (3 JS files) — **1.0–2.5s**
- **Deep Profile** (10 JS files) — **3.0–8.0s**

Scales linearly with:
- Response body size (HTML parsing)
- Number of external JS files (–max-js)
- Network latency (timeout applies to each request)

---

## 📊 JSON Output Schema

```json
{
  "scan_metadata": {
    "tool": "TechFinger",
    "version": "0.1.0",
    "scan_time": "2026-08-01T17:44:56+00:00",
    "target": "https://example.com",
    "status_code": 200,
    "response_time_ms": 245,
    "profile": "balanced",
    "deep": true,
    "python_version": "3.12.3",
    "api_endpoints_found": ["/api/", "/graphql"]
  },
  "technologies": [
    {
      "name": "Laravel",
      "version": "10.x",
      "confidence": 95,
      "confidence_breakdown": {
        "primary_evidence": "cookie: laravel_session",
        "primary_score": 81,
        "reliability": 0.9,
        "bonus_evidence_count": 2,
        "bonus_points": 16,
        "version_bonus": 12,
        "conflict_penalty": 0,
        "raw_score": 109,
        "final": 95,
        "math": "81 (cookie @ 0.9) + 16 (2 bonus) + 12 (version) = 109 → capped at 100"
      },
      "category": "Framework",
      "risk": "High",
      "evidence": ["cookie: laravel_session", "header: X-Frame-Options", "error_page: Ignition"],
      "contradiction_detected": false
    }
  ],
  "stack_correlation": [
    {"layer": "Web Server", "technology": "Nginx", "confidence": 100},
    {"layer": "Language/Runtime", "technology": "PHP", "confidence": 92},
    {"layer": "Framework", "technology": "Laravel", "confidence": 95}
  ],
  "contradictions": [],
  "security_observations": [
    {"issue": "CSP Missing", "severity": "Medium", "details": "No Content-Security-Policy header"},
    {"issue": "Server leaks version", "severity": "Info", "details": "Server: nginx/1.18.0"}
  ],
  "investigation_paths": {
    "Laravel": ["Check .env file exposure", "Laravel debug mode", "Ignition RCE (CVE-2021-3129)"],
    "React": ["Check source maps (*.js.map)", "Exposed API endpoints in JS bundles"]
  },
  "most_likely_stack": ["Nginx", "PHP", "Laravel", "React"]
}
```

---

## 🔐 Security & Disclaimer

**TechFinger is for authorized testing only.**

- Does NOT perform active exploitation
- Does NOT brute-force credentials
- Does NOT scan for known CVEs (use Nuclei, Snyk, etc. for that)
- Respects `robots.txt`, timeouts, and rate-limiting
- No data exfiltration—all results stay local

**Ethical use:**
- Obtain written permission before scanning any target
- Use responsibly on your own infrastructure
- Follow local laws and regulations

---

## 🤝 Contributing

Contributions welcome!

### Add Detection Rules

Edit `patterns.py`:
1. Add regex to HEADER_PATTERNS / HTML_PATTERNS / JS_GLOBALS / ERROR_PATTERNS
2. Add risk level to RISK_LEVELS
3. Add investigation paths to INVESTIGATION_PATHS
4. Test via `python techfinger.py -u <test_target> --explain`

### Report Issues

- Bug? → Open an Issue with target URL + error output
- Feature request? → Discuss in Issues

### Future Roadmap

- v0.2 — Fingerprint cache, batch scanning
- v0.3 — HTTP/2 support, header compression analysis
- v0.4 — HTTP/3 support, QUIC fingerprinting
- v0.5 — TLS fingerprinting (JA3/JA4)
- v0.6 — Full plugin architecture
- v1.0 — Stable release, comprehensive test suite

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

**Use freely. Modify freely. Redistribute freely.**

---

## 👤 Author

**HaQtor** — Cybersecurity Researcher | Penetration Tester | Bug Bounty Hunter

- 🔗 [LinkedIn](https://linkedin.com/in/bassam-haqtor)
- 🐙 [GitHub](https://github.com/HaQtor)
- 🔐 [Twitter/X](https://twitter.com/HaQtor)
- 📧 Email — Contact via GitHub

---

## 📖 Inspiration & Philosophy

TechFinger stands on the principle of **explainable, evidence-based fingerprinting**:

1. **Transparency** — Every finding backed by evidence + math
2. **Auditability** — Rules live in source code, no black-box signatures
3. **Practicality** — Designed for pentesters who think, not just scan
4. **Portability** — No external APIs, works offline, works everywhere

Built with ❤️ for the security community.

---

## 🙏 Acknowledgments

- Inspired by Wappalyzer, BuiltWith, and the spirit of open-source security tools
- Thanks to the Python security community (requests, BeautifulSoup4, Rich)
- Special thanks to penetration testers who demanded better explanations

---

## 💬 Feedback

Found TechFinger useful? Let me know:

- ⭐ Star the repo on GitHub
- 🐦 Share on Twitter/LinkedIn
- 📸 Tag `@HaQtor` with your screenshots
- 💡 Suggest features via Issues

---

**TechFinger v0.1.0** — *Heuristic Technology Fingerprinting. Explainable. Evidence-Based. No Signatures.*

Happy fingerprinting! 🔍🎯
