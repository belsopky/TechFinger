
# TechFinger

Passive web technology fingerprinting using evidence-driven heuristic analysis.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

TechFinger is a passive technology fingerprinting tool that identifies web technologies using embedded heuristic rules.

Detection is based on evidence collected from HTTP headers, cookies, HTML, JavaScript, and response behavior. Every finding includes the evidence used during scoring.

---

## Features

| Capability | Details |
|------------|---------|
| HTTP Headers | `Server`, `X-Powered-By`, `X-Generator`, `X-AspNet-Version`, etc. |
| Cookies | Session identifiers, framework cookies, JWT, analytics |
| HTML DOM | Framework-specific attributes, meta tags, generator tags |
| JavaScript Globals | `window.React`, `window.Vue`, `window.gtag`, etc. |
| Error Pages | Framework fingerprints from 404/500 response bodies |
| Session Patterns | `PHPSESSID`, `sessionid`, `connect.sid`, `laravel_session` |
| Stack Correlation | CDN → Web Server → Language → Framework → Frontend |
| Contradiction Detection | Flags conflicting evidence with penalty scoring |
| Passive Security Checks | CSP, HSTS, cookie flags, version leaks |
| Report Generation | Markdown reports and JSON export |
| Embedded Detection Rules | All patterns in source code, no external database |

---

## Supported Technologies

| Category | Technologies |
|----------|--------------|
| Web Servers | Apache, Nginx, IIS, Caddy |
| Languages / Runtimes | PHP, Python, Node.js, Java, Ruby, ASP.NET |
| Frameworks | Laravel, Django, Flask, Express.js, Spring Boot, ASP.NET, Ruby on Rails |
| Frontend | React, Vue.js, Angular, Next.js, Nuxt, Svelte, jQuery, Bootstrap, Tailwind CSS |
| CDN / WAF | Cloudflare, AWS CloudFront, Fastly, Sucuri |

---

## Installation

### From Source

```bash
git clone https://github.com/belsopky/TechFinger.git
cd TechFinger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Supported Platforms

- Linux
- macOS
- Windows

---

## Usage

```bash
python techfinger.py -u https://target.example [OPTIONS]
```

### Scan Profiles

| Profile | Timeout | Deep JS | Max JS Files | Use Case |
|---------|---------|---------|--------------|----------|
| `fast` | 5s | No | 0 | Large-scope reconnaissance |
| `balanced` | 10s | Yes | 3 | Default penetration testing |
| `deep` | 30s | Yes | 10 | Thorough assessment |

Override any profile parameter:

```bash
python techfinger.py -u https://target.example --profile balanced --timeout 15 --max-js 5
```

---

## CLI Reference

```
Options:
  -u, --url TEXT          Target URL (required)
  --profile TEXT          Scan profile: fast, balanced, deep [default: balanced]
  --timeout INTEGER       Request timeout in seconds [default: profile-based]
  --max-js INTEGER        Maximum external JS files to fetch [default: profile-based]
  --explain               Show confidence math breakdown for each finding
  --report                Generate report.md
  --evidence              Export raw evidence to evidence/ directory
  --no-color              Disable colored terminal output
  -o, --output TEXT       Output format: terminal, json [default: terminal]
  -h, --help              Show this message and exit.
```

---

## Output Formats

- **Terminal** — Rich-formatted tables with confidence tiers and stack correlation
- **JSON** — Structured output for scripting and CI/CD integration
- **Markdown Report** — Client-ready report generated with `--report`

---

## Examples

### Default Scan

```bash
python techfinger.py -u https://demo.local
```

### Deep Scan with Evidence Export

```bash
python techfinger.py -u https://demo.local \
  --profile deep \
  --explain \
  --report \
  --evidence
```

### JSON Output for Scripting

```bash
python techfinger.py -u https://demo.local -o json > scan.json
cat scan.json | jq '.technologies[] | select(.confidence >= 70)'
```

### Inspect a Laravel Application

```bash
python techfinger.py -u https://target.example --explain
```

### Inspect a React Application

```bash
python techfinger.py -u https://target.example --profile deep --max-js 10
```

### Inspect Cloudflare + Nginx

```bash
python techfinger.py -u https://demo.local
```

### Generate Markdown Report

```bash
python techfinger.py -u https://target.example --report
```

---

## Architecture

```
                    patterns.py
                         │
                         ▼
┌─────────┐     ┌─────────────┐     ┌─────────────┐
│ Target  │────▶│ HTTP Fetch  │────▶│ Extractors  │
│   URL   │     │  (requests) │     │             │
└─────────┘     └─────────────┘     └──────┬──────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
            │   Headers   │      │   Cookies   │      │  HTML/JS    │
            │  Extractor  │      │  Extractor  │      │  Extractor  │
            └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
                   │                      │                      │
                   └──────────────────────┼──────────────────────┘
                                          ▼
                                   ┌─────────────┐
                                   │   Evidence  │
                                   │    Store    │
                                   └──────┬──────┘
                                          ▼
                                   ┌─────────────┐
                                   │  Confidence │
                                   │   Engine    │
                                   └──────┬──────┘
                                          ▼
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
            │Correlation  │      │Contradiction│      │  Security   │
            │   Engine    │      │  Detection  │      │   Checks    │
            └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
                   │                      │                      │
                   └──────────────────────┼──────────────────────┘
                                          ▼
                                   ┌─────────────┐
                                   │  Renderers  │
                                   │(Terminal/   │
                                   │ JSON/Report)│
                                   └─────────────┘
```

---

## Detection Pipeline

```
HTTP Request
      │
      ▼
Evidence Extraction
      │
      ▼
Evidence Aggregation
      │
      ▼
Confidence Scoring
      │
      ▼
Stack Correlation
      │
      ▼
Output Rendering
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Network error (DNS, connection refused, SSL) |
| 2 | Invalid URL or arguments |
| 3 | Request timeout |
| 4 | Unexpected error |

---

## JSON Output

> Simplified example:

```json
{
  "schema_version": "1.0",
  "scan_metadata": {
    "tool": "TechFinger",
    "version": "0.1.0",
    "target": "https://demo.local",
    "status_code": 200,
    "profile": "balanced",
    "scan_time": "2026-08-01T21:30:00Z"
  },
  "technologies": [
    {
      "name": "Laravel",
      "version": "10.x",
      "confidence": 95,
      "category": "Framework",
      "risk": "High",
      "evidence": ["cookie: laravel_session", "header: X-Frame-Options"]
    }
  ],
  "stack_correlation": [
    {"layer": "Web Server", "technology": "Nginx", "confidence": 100},
    {"layer": "Language", "technology": "PHP", "confidence": 92},
    {"layer": "Framework", "technology": "Laravel", "confidence": 95}
  ],
  "contradictions": [],
  "security_observations": [
    {"issue": "CSP Missing", "severity": "Medium"}
  ]
}
```

---

## Design Goals

- Offline operation with no external signature database
- Embedded detection rules for auditability
- Evidence transparency for every finding
- Simple modular architecture
- JSON-friendly output for scripting and CI/CD integration

---

## Roadmap

### Near Term
- Batch scanning from file input
- HTTP/2 support

### Mid Term
- HTTP/3 and QUIC fingerprinting
- TLS fingerprinting (JA3/JA4)

### Long Term
- Plugin architecture
- Stable v1.0 release with comprehensive test suite

---

## Contributing

Please open an issue before submitting large changes.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Commit your changes (`git commit -am 'Add feature'`)
4. Push to the branch (`git push origin feature/name`)
5. Open a Pull Request

### Adding Detection Rules

Edit `patterns.py`:

1. Add regex to `HEADER_PATTERNS`, `HTML_PATTERNS`, `JS_GLOBALS`, or `ERROR_PATTERNS`
2. Add risk level to `RISK_LEVELS`
3. Add investigation paths to `INVESTIGATION_PATHS`
4. Test with `python techfinger.py -u <target> --explain`

---

## FAQ

**Q: Does TechFinger require an internet connection?**
A: Only to fetch the target. All detection rules are embedded in source code.

**Q: Can I use this in CI/CD pipelines?**
A: Yes. Use `-o json` for structured output.

**Q: Does it detect versions accurately?**
A: When version information is exposed in headers, cookies, or error pages. It does not perform active exploitation to determine versions.

**Q: Is this a vulnerability scanner?**
A: No. TechFinger performs passive analysis only. It does not exploit vulnerabilities or brute-force credentials.

**Q: Does TechFinger make more than one request?**
A: By default, one request. With `--profile deep` or `--max-js`, it may fetch additional external JavaScript files referenced in the HTML.

**Q: Does TechFinger execute JavaScript?**
A: No. It scans JavaScript source code for global variable patterns and framework signatures. It does not run a browser engine or execute code.

---

## Author

**Bassam Elsopky (HaQtor)**

- Junior Penetration Tester
- Bug Bounty Hunter
- [GitHub](https://github.com/belsopky)
- [LinkedIn](https://www.linkedin.com/in/bassam-elsopky-814ba1331/)
- [Docker Hub](https://hub.docker.com/r/haqtor)

---

## License

MIT License — see [LICENSE](LICENSE).
```
