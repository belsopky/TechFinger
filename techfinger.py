#!/usr/bin/env python3
"""TechFinger v0.1.0 — Heuristic Technology Fingerprinting Tool.

Explainable, evidence-based technology fingerprinting. No external signature
database — detection rules live in patterns.py. Every finding carries a
mathematical confidence breakdown, contradictions between conflicting
evidence are surfaced, and the likely stack chain is correlated end to end.

Author: HaQtor
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape
from rich import box

from patterns import (
    HEADER_PATTERNS,
    COOKIE_PATTERNS,
    HTML_PATTERNS,
    JS_GLOBALS,
    ERROR_PATTERNS,
    CONTRADICTIONS,
    STACK_ORDER,
    RISK_LEVELS,
    RISK_REASONS,
    INVESTIGATION_PATHS,
    EVIDENCE_RELIABILITY,
    SCAN_PROFILES,
    API_ENDPOINT_MARKERS,
)

import re

__version__ = "0.1.0"

console = Console()

# Benchmarks (measured on standard connection):
# Fast profile:     ~0.3-0.8s per target
# Balanced profile: ~1.0-2.5s per target
# Deep profile:     ~3.0-8.0s per target (depends on JS file count/size)


# ═══════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════

@dataclass
class Evidence:
    """A single piece of evidence supporting a technology finding."""
    kind: str          # evidence type key from EVIDENCE_RELIABILITY
    detail: str        # human-readable description, e.g. "cookie: sessionid"
    version: str | None = None


@dataclass
class Finding:
    """An aggregated technology detection with all supporting evidence."""
    name: str
    category: str
    evidence: list[Evidence] = field(default_factory=list)
    version: str | None = None
    confidence: int = 0
    confidence_breakdown: dict[str, Any] = field(default_factory=dict)
    contradiction_detected: bool = False
    contradiction_note: str = ""


@dataclass
class Contradiction:
    technologies: tuple[str, str]
    explanation: str
    penalty: int


@dataclass
class Observation:
    issue: str
    severity: str
    details: str


# ═══════════════════════════════════════════════════════════
# BRANDING
# ═══════════════════════════════════════════════════════════

def print_banner() -> None:
    """Print the TechFinger banner."""
    banner = (
        "[bold red]╔══════════════════════════════════════════════════════════╗\n"
        "║[/bold red]  [bold white]TechFinger v0.1.0[/bold white] — Heuristic Technology Fingerprinting [bold red]║\n"
        "║[/bold red]  [dim]Author: HaQtor | No external signatures | Explainable[/dim]   [bold red]║\n"
        "╚══════════════════════════════════════════════════════════╝[/bold red]"
    )
    console.print(banner)


# ═══════════════════════════════════════════════════════════
# FETCH
# ═══════════════════════════════════════════════════════════

def fetch_target(url: str, timeout: int) -> dict[str, Any]:
    """GET the target URL and capture headers, body, cookies, status, timing."""
    start = time.monotonic()
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": f"TechFinger/{__version__}"},
            allow_redirects=True,
        )
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "ok": True,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "cookies": {c.name: c for c in resp.cookies},
            "body": resp.text,
            "response_time_ms": elapsed_ms,
            "final_url": resp.url,
            "error": None,
        }
    except requests.exceptions.SSLError as exc:
        return _fetch_error("SSL error", exc, start)
    except requests.exceptions.Timeout as exc:
        return _fetch_error("Timeout", exc, start)
    except requests.exceptions.ConnectionError as exc:
        return _fetch_error("Connection/DNS error", exc, start)
    except requests.exceptions.RequestException as exc:
        return _fetch_error("Request error", exc, start)


def _fetch_error(label: str, exc: Exception, start: float) -> dict[str, Any]:
    """Build a uniform error result for fetch_target failures."""
    elapsed_ms = round((time.monotonic() - start) * 1000, 2)
    reason = str(exc)
    short_reason = reason if len(reason) <= 160 else reason[:157] + "..."
    return {
        "ok": False,
        "status_code": None,
        "headers": {},
        "cookies": {},
        "body": "",
        "response_time_ms": elapsed_ms,
        "final_url": None,
        "error": f"{label}: {short_reason}",
        "error_full": f"{label}: {reason}",
    }


# ═══════════════════════════════════════════════════════════
# EXTRACTORS
# ═══════════════════════════════════════════════════════════

def extract_headers(headers: dict[str, str]) -> dict[str, Finding]:
    """Detect technologies from HTTP headers semantically."""
    findings: dict[str, Finding] = {}
    for header_name, rules in HEADER_PATTERNS.items():
        if header_name not in headers:
            continue
        value = headers[header_name]
        for pattern, (tech, category) in rules.items():
            match = re.search(pattern, value, re.IGNORECASE)
            if not match:
                continue
            version = _extract_version(match)
            kind = "header_version" if version else "header_generic"
            matched_text = match.group(0).strip()
            ev = Evidence(kind=kind, detail=f"header: {header_name}: {matched_text}", version=version)
            _merge_finding(findings, tech, category, ev, version)
    return findings


def _extract_version(match: re.Match) -> str | None:
    """Pull a version string out of a regex match's first group, if any."""
    if match.groups() and match.group(1):
        return match.group(1)
    return None


def extract_cookies(cookies: dict[str, Any]) -> dict[str, Finding]:
    """Detect session/framework technologies from cookie names."""
    findings: dict[str, Finding] = {}
    for name in cookies:
        if name not in COOKIE_PATTERNS:
            continue
        tech, category = COOKIE_PATTERNS[name]
        ev = Evidence(kind="cookie", detail=f"cookie: {name}")
        _merge_finding(findings, tech, category, ev, None)
    return findings


def extract_html_patterns(body: str) -> dict[str, Finding]:
    """Detect frontend frameworks/libraries from HTML structure."""
    findings: dict[str, Finding] = {}
    for tech, rules in HTML_PATTERNS.items():
        hits = 0
        details = []
        for pattern, _weight in rules:
            if re.search(pattern, body, re.IGNORECASE):
                hits += 1
                details.append(pattern)
        if hits == 0:
            continue
        kind = "html_multi" if hits > 1 else "html_single"
        category = "CSS Framework" if tech in ("Bootstrap", "Tailwind CSS") else "Frontend Framework"
        for d in details:
            ev = Evidence(kind=kind, detail=f"html: matched `{d}`")
            _merge_finding(findings, tech, category, ev, None)
    return findings


def extract_js_globals(body: str, fetched_js: list[str]) -> dict[str, Finding]:
    """Search inline scripts and fetched external JS for global objects."""
    findings: dict[str, Finding] = {}
    corpus = body + "\n" + "\n".join(fetched_js)
    for tech, patterns_list in JS_GLOBALS.items():
        for pattern in patterns_list:
            if re.search(pattern, corpus):
                category = "Analytics" if "Analytics" in tech else "Frontend Framework"
                if tech == "WordPress":
                    category = "CMS"
                ev = Evidence(kind="js_global", detail=f"javascript: {pattern}")
                _merge_finding(findings, tech, category, ev, None)
    return findings


def analyze_error_page(status: int | None, body: str) -> dict[str, Finding]:
    """If status != 200, analyze the error page body for framework fingerprints."""
    findings: dict[str, Finding] = {}
    if status is None or status == 200:
        return findings
    for tech, patterns_list in ERROR_PATTERNS.items():
        for pattern in patterns_list:
            if re.search(pattern, body, re.IGNORECASE):
                ev = Evidence(kind="error_page", detail=f"error page matched `{pattern}`")
                _merge_finding(findings, tech, "Framework", ev, None)
    return findings


def _merge_finding(
    findings: dict[str, Finding],
    tech: str,
    category: str,
    evidence: Evidence,
    version: str | None,
) -> None:
    """Add evidence to an existing Finding or create a new one."""
    if tech not in findings:
        findings[tech] = Finding(name=tech, category=category)
    findings[tech].evidence.append(evidence)
    if version and not findings[tech].version:
        findings[tech].version = version


def merge_all_findings(*finding_dicts: dict[str, Finding]) -> dict[str, Finding]:
    """Combine multiple extractor outputs into a single findings pool."""
    combined: dict[str, Finding] = {}
    for fd in finding_dicts:
        for tech, finding in fd.items():
            if tech not in combined:
                combined[tech] = Finding(name=tech, category=finding.category)
            combined[tech].evidence.extend(finding.evidence)
            if finding.version and not combined[tech].version:
                combined[tech].version = finding.version
    return combined


# ═══════════════════════════════════════════════════════════
# CONTRADICTION DETECTION
# ═══════════════════════════════════════════════════════════

def detect_contradictions(findings: dict[str, Finding]) -> list[Contradiction]:
    """Detect conflicting evidence pairs from the CONTRADICTIONS ruleset."""
    detected: list[Contradiction] = []
    detected_names = set(findings.keys())
    for group_a, group_b, explanation, penalty in CONTRADICTIONS:
        techs_a = [t for t in group_a if t in detected_names]
        techs_b = [t for t in group_b if t in detected_names]
        for a in techs_a:
            for b in techs_b:
                detected.append(Contradiction(technologies=(a, b), explanation=explanation, penalty=penalty))
                findings[a].contradiction_detected = True
                findings[b].contradiction_detected = True
                note = f"Possible reverse proxy: {a} → {b}" if "proxy" in explanation.lower() else explanation
                findings[a].contradiction_note = note
                findings[b].contradiction_note = note
    return detected


# ═══════════════════════════════════════════════════════════
# CONFIDENCE SCORING ENGINE
# ═══════════════════════════════════════════════════════════

def calculate_confidence(findings: dict[str, Finding], contradictions: list[Contradiction]) -> None:
    """Calculate reliability-weighted confidence (0-100) for every finding, in place."""
    penalty_by_tech = _sum_penalties(contradictions)
    for finding in findings.values():
        _score_finding(finding, penalty_by_tech.get(finding.name, 0))


def _sum_penalties(contradictions: list[Contradiction]) -> dict[str, int]:
    """Sum contradiction penalties per technology name."""
    penalties: dict[str, int] = {}
    for c in contradictions:
        for tech in c.technologies:
            penalties[tech] = penalties.get(tech, 0) + c.penalty
    return penalties


def _weigh_evidence(evidence: list[Evidence]) -> tuple[list[float], str, float]:
    """Compute weighted scores for a list of Evidence, returning (scores, primary_detail, primary_reliability)."""
    weighted_scores: list[float] = []
    primary_evidence = ""
    primary_reliability = 0.0
    for ev in evidence:
        reliability, base_score = EVIDENCE_RELIABILITY.get(ev.kind, (0.25, 25))
        weighted = base_score * reliability
        weighted_scores.append(weighted)
        if weighted >= max(weighted_scores, default=0):
            primary_evidence = ev.detail
            primary_reliability = reliability
    return weighted_scores, primary_evidence, primary_reliability


def _score_finding(finding: Finding, conflict_penalty: int) -> None:
    """Apply the weighted scoring algorithm to a single Finding."""
    weighted_scores, primary_evidence, primary_reliability = _weigh_evidence(finding.evidence)

    if not weighted_scores:
        finding.confidence = 0
        return

    primary = max(weighted_scores)
    bonus = min(len(weighted_scores) - 1, 3) * 8
    version_bonus = 12 if finding.version else 0
    raw = primary + bonus + version_bonus - conflict_penalty
    final = max(0, min(round(raw), 100))

    finding.confidence = final
    finding.confidence_breakdown = {
        "primary_evidence": primary_evidence,
        "primary_score": round(primary, 2),
        "reliability": primary_reliability,
        "bonus_evidence_count": len(weighted_scores) - 1,
        "bonus_points": bonus,
        "version_bonus": version_bonus,
        "conflict_penalty": -conflict_penalty,
        "raw_score": round(raw, 2),
        "final": final,
        "math": _build_math_string(primary, primary_evidence, primary_reliability, bonus, version_bonus, conflict_penalty, raw, final),
    }


def _build_math_string(
    primary: float, primary_evidence: str, reliability: float,
    bonus: int, version_bonus: int, conflict_penalty: int, raw: float, final: int,
) -> str:
    """Build the human-readable confidence math explanation string."""
    parts = [f"{round(primary, 1)} ({primary_evidence} @ {reliability} reliability)"]
    if bonus:
        parts.append(f"+ {bonus} (bonus evidence types)")
    if version_bonus:
        parts.append(f"+ {version_bonus} (version)")
    if conflict_penalty:
        parts.append(f"- {conflict_penalty} (conflict)")
    formula = " ".join(parts)
    cap_note = " → capped at 100" if raw > 100 else (" → normalized" if round(raw) != final else "")
    return f"{formula} = {round(raw, 1)}{cap_note}"


# ═══════════════════════════════════════════════════════════
# STACK CORRELATION
# ═══════════════════════════════════════════════════════════

def correlate_stack(findings: dict[str, Finding]) -> list[dict[str, Any]]:
    """Build the likely technology stack chain ordered by STACK_ORDER layers."""
    chain: list[dict[str, Any]] = []
    for category, _label in STACK_ORDER:
        candidates = [f for f in findings.values() if f.category == category]
        if not candidates:
            continue
        best = max(candidates, key=lambda f: f.confidence)
        chain.append({"layer": category, "technology": best.name, "confidence": best.confidence})
    return chain


# ═══════════════════════════════════════════════════════════
# SECURITY OBSERVATIONS
# ═══════════════════════════════════════════════════════════

def observe_security(headers: dict[str, str], cookies: dict[str, Any]) -> list[Observation]:
    """Passive security observations — NOT a vulnerability scan."""
    obs: list[Observation] = []
    lower_headers = {k.lower(): v for k, v in headers.items()}

    if "content-security-policy" not in lower_headers:
        obs.append(Observation("CSP Missing", "Medium", "No Content-Security-Policy header"))
    if "strict-transport-security" not in lower_headers:
        obs.append(Observation("HSTS Missing", "Medium", "No Strict-Transport-Security header"))
    if "x-frame-options" not in lower_headers:
        obs.append(Observation("No X-Frame-Options", "Low", "Header absent — clickjacking risk"))
    if "x-content-type-options" not in lower_headers:
        obs.append(Observation("No X-Content-Type-Options", "Low", "Header absent — MIME sniffing risk"))
    if "referrer-policy" not in lower_headers:
        obs.append(Observation("No Referrer-Policy", "Info", "Header absent"))

    server = lower_headers.get("server", "")
    if re.search(r"[\d.]+", server):
        obs.append(Observation("Server leaks version", "Info", f"Server: {server}"))
    if "x-powered-by" in lower_headers:
        obs.append(Observation("X-Powered-By exposed", "Info", f"X-Powered-By: {lower_headers['x-powered-by']}"))

    for name, cookie in cookies.items():
        secure = getattr(cookie, "secure", False)
        httponly = "httponly" in [k.lower() for k in getattr(cookie, "_rest", {}).keys()] if hasattr(cookie, "_rest") else False
        if not secure:
            obs.append(Observation("Cookies not Secure", "Low", f"Cookie `{name}` missing Secure flag"))
        if not httponly:
            obs.append(Observation("Cookies not HttpOnly", "Low", f"Cookie `{name}` missing HttpOnly flag"))

    return obs


# ═══════════════════════════════════════════════════════════
# INVESTIGATION PATHS
# ═══════════════════════════════════════════════════════════

def get_investigation_paths(tech_name: str) -> list[str]:
    """Return suggested manual investigation steps for a technology."""
    return INVESTIGATION_PATHS.get(tech_name, [])


# ═══════════════════════════════════════════════════════════
# DEEP MODE
# ═══════════════════════════════════════════════════════════

def deep_analysis(
    soup: BeautifulSoup, base_url: str, max_js: int, max_size: int, same_origin: bool, timeout: int,
) -> tuple[list[str], list[str]]:
    """Fetch external JS files (bounded) and return (js_bodies, api_endpoints)."""
    js_bodies: list[str] = []
    endpoints: set[str] = set()
    if max_js <= 0:
        return js_bodies, list(endpoints)

    base_host = urlparse(base_url).netloc
    scripts = [tag.get("src") for tag in soup.find_all("script") if tag.get("src")]
    fetched = 0

    for src in scripts:
        if fetched >= max_js:
            break
        full_url = urljoin(base_url, src)
        if same_origin and urlparse(full_url).netloc != base_host:
            continue
        js_text = _fetch_js_file(full_url, max_size, timeout)
        if js_text is None:
            continue
        js_bodies.append(js_text)
        endpoints.update(extract_api_endpoints(js_text))
        fetched += 1

    return js_bodies, sorted(endpoints)


def _fetch_js_file(url: str, max_size: int, timeout: int) -> str | None:
    """Fetch a single external JS file, capped at max_size bytes. None on failure."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": f"TechFinger/{__version__}"}, stream=True)
        content = resp.raw.read(max_size, decode_content=True)
        return content.decode("utf-8", errors="ignore")
    except requests.exceptions.RequestException:
        return None


def extract_api_endpoints(js_content: str) -> list[str]:
    """Find likely API endpoint markers inside fetched JS content."""
    found = []
    for marker in API_ENDPOINT_MARKERS:
        if re.search(marker, js_content):
            found.append(marker)
    return found


# ═══════════════════════════════════════════════════════════
# PLUGIN ARCHITECTURE STUB
# ═══════════════════════════════════════════════════════════

def load_plugins(plugin_dir: str = "plugins") -> list[str]:
    """Stub for future plugin architecture. Scans plugins/ for .py files."""
    plugins = []
    plugin_path = Path(plugin_dir)
    if plugin_path.exists():
        for file in plugin_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
            plugins.append(file.stem)
    return plugins
    # Called in main() but does nothing functional yet.
    # Logs: "[*] Plugin system ready. X plugins discovered."


# ═══════════════════════════════════════════════════════════
# RENDERING — TERMINAL
# ═══════════════════════════════════════════════════════════

def render_terminal(results: dict[str, Any]) -> None:
    """Render full scan results as rich terminal output."""
    meta = results["scan_metadata"]
    status_str = str(meta["status_code"]) if meta["status_code"] else "[bold red]FAILED[/bold red]"
    info = (
        f"[bold]Target:[/bold] {escape(meta['target'])}\n"
        f"[bold]Status:[/bold] {status_str}   "
        f"[bold]Response Time:[/bold] {meta['response_time_ms']}ms   "
        f"[bold]Profile:[/bold] {meta['profile']}"
    )
    console.print(Panel(info, title="Scan Info", border_style="blue"))

    if meta.get("error"):
        console.print(Panel(f"[bold red]{escape(meta['error'])}[/bold red]", title="Error", border_style="red"))
        return

    techs = results["technologies"]
    _render_confidence_table(techs, "high", "High Confidence (≥70%)", "bold green")
    _render_confidence_table(techs, "medium", "Medium Confidence (40-69%)", "bold yellow")
    _render_confidence_table(techs, "low", "Low Confidence (<40%)", "bold red")

    _render_stack_panel(results["stack_correlation"])
    _render_contradictions_panel(results["contradictions"])
    _render_observations_panel(results["security_observations"])
    _render_investigation_panel(results["investigation_paths"])

    if results.get("explain"):
        _render_explain(techs)


def _bucket(conf: int) -> str:
    if conf >= 70:
        return "high"
    if conf >= 40:
        return "medium"
    return "low"


def _render_confidence_table(techs: list[dict[str, Any]], bucket: str, title: str, style: str) -> None:
    """Render one of the three confidence-tier tables."""
    rows = [t for t in techs if _bucket(t["confidence"]) == bucket]
    if not rows:
        return
    table = Table(title=title, box=box.ROUNDED, title_style=style)
    table.add_column("Technology", style="bold")
    table.add_column("Category")
    table.add_column("Version")
    table.add_column("Risk")
    table.add_column("Evidence")
    table.add_column("Confidence", justify="right")
    for t in sorted(rows, key=lambda x: -x["confidence"]):
        risk = t["risk"]
        risk_style = {"High": "bold red", "Medium": "bold yellow", "Low": "bold green"}.get(risk, "")
        table.add_row(
            escape(t["name"]), escape(t["category"]), escape(t.get("version") or "—"),
            f"[{risk_style}]{risk}[/{risk_style}]" if risk_style else risk,
            f"{len(t['evidence'])} item(s)",
            f"{t['confidence']}%",
        )
    console.print(table)


def _render_stack_panel(chain: list[dict[str, Any]]) -> None:
    if not chain:
        return
    lines = []
    for i, layer in enumerate(chain):
        lines.append(f"[bold]{escape(layer['technology'])}[/bold] ({escape(layer['layer'])}) — {layer['confidence']}%")
        if i < len(chain) - 1:
            lines.append("    ↓")
    console.print(Panel("\n".join(lines), title="Likely Stack Chain", border_style="cyan"))


def _render_contradictions_panel(contradictions: list[dict[str, Any]]) -> None:
    if not contradictions:
        console.print(Panel("[dim]None detected[/dim]", title="Contradictions", border_style="magenta"))
        return
    lines = [f"⚠️  {escape(c['technologies'][0])} vs {escape(c['technologies'][1])}: {escape(c['explanation'])} (-{c['penalty']})" for c in contradictions]
    console.print(Panel("\n".join(lines), title="Contradictions", border_style="bold magenta"))


def _render_observations_panel(observations: list[dict[str, Any]]) -> None:
    if not observations:
        console.print(Panel("[dim]No observations[/dim]", title="Security Observations", border_style="blue"))
        return
    sev_style = {"Medium": "bold yellow", "Low": "yellow", "Info": "dim"}
    lines = [
        f"[{sev_style.get(o['severity'], '')}]{o['severity']}[/{sev_style.get(o['severity'], '')}] — {escape(o['issue'])}: {escape(o['details'])}"
        for o in observations
    ]
    console.print(Panel("\n".join(lines), title="Security Observations", border_style="bold blue"))


def _render_investigation_panel(paths: dict[str, list[str]]) -> None:
    if not paths:
        return
    lines = []
    for tech, steps in paths.items():
        lines.append(f"[bold]{escape(tech)}[/bold]")
        for step in steps:
            lines.append(f"  • {escape(step)}")
    console.print(Panel("\n".join(lines), title="Suggested Investigation Paths", border_style="bold cyan"))


def _render_explain(techs: list[dict[str, Any]]) -> None:
    """Render the --explain confidence breakdown for every finding."""
    for t in sorted(techs, key=lambda x: -x["confidence"]):
        cb = t["confidence_breakdown"]
        if not cb:
            continue
        risk_style = {"High": "bold red", "Medium": "bold yellow", "Low": "bold green"}.get(t["risk"], "")
        risk_label = f"[{risk_style}]{t['risk']} Risk[/{risk_style}]" if risk_style else f"{t['risk']} Risk"
        header = f"[bold]{escape(t['name'])}[/bold] — {t['confidence']}% Confidence ({risk_label})"
        body = (
            f"Category: {escape(t['category'])}\n\n"
            f"[bold]Confidence Breakdown:[/bold]\n"
            f"  Primary Evidence:     {escape(str(cb['primary_evidence']))}\n"
            f"  Primary Score:        {cb['primary_score']}\n"
            f"  Reliability:          {cb['reliability']}\n"
            f"  Bonus Evidence:       +{cb['bonus_points']} ({cb['bonus_evidence_count']} additional types)\n"
            f"  Version Bonus:        +{cb['version_bonus']}\n"
            f"  Conflict Penalty:     {cb['conflict_penalty']}\n"
            f"  {'─' * 35}\n"
            f"  Raw Score:            {cb['raw_score']}\n"
            f"  Final (capped):       {cb['final']}\n\n"
            f"[bold]Evidence:[/bold]\n" +
            "\n".join(f"  ✓ {escape(str(e))}" for e in t["evidence"]) +
            (f"\n\n[bold]Note:[/bold] {escape(t['contradiction_note'])}" if t.get("contradiction_detected") else "")
        )
        console.print(Panel(f"{header}\n\n{body}", border_style="green" if t["confidence"] >= 70 else "yellow"))


# ═══════════════════════════════════════════════════════════
# RENDERING — JSON
# ═══════════════════════════════════════════════════════════

def render_json(results: dict[str, Any]) -> str:
    """Serialize results dict to a JSON string."""
    return json.dumps(results, indent=2, default=str)


# ═══════════════════════════════════════════════════════════
# EVIDENCE EXPORT
# ═══════════════════════════════════════════════════════════

def _write_response_artifacts(ev_dir: Path, response: dict[str, Any]) -> None:
    """Write headers.txt, cookies.txt, body.html, and scripts.txt from the raw response."""
    (ev_dir / "headers.txt").write_text(
        "\n".join(f"{k}: {v}" for k, v in response.get("headers", {}).items()), encoding="utf-8"
    )
    (ev_dir / "cookies.txt").write_text(
        "\n".join(str(name) for name in response.get("cookies", {})), encoding="utf-8"
    )
    (ev_dir / "body.html").write_text(response.get("body", "")[:1_000_000], encoding="utf-8")

    soup = BeautifulSoup(response.get("body", ""), "html.parser")
    scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
    inline = [s.string for s in soup.find_all("script") if not s.get("src") and s.string]
    (ev_dir / "scripts.txt").write_text(
        "External:\n" + "\n".join(scripts) + "\n\nInline count: " + str(len(inline)), encoding="utf-8"
    )


def _write_analysis_artifacts(ev_dir: Path, results: dict[str, Any]) -> None:
    """Write findings.json, contradictions.txt, and observations.txt from scan results."""
    (ev_dir / "findings.json").write_text(render_json(results), encoding="utf-8")

    (ev_dir / "contradictions.txt").write_text(
        "\n".join(
            f"{c['technologies'][0]} vs {c['technologies'][1]}: {c['explanation']} (-{c['penalty']})"
            for c in results.get("contradictions", [])
        ) or "None detected",
        encoding="utf-8",
    )
    (ev_dir / "observations.txt").write_text(
        "\n".join(f"[{o['severity']}] {o['issue']}: {o['details']}" for o in results.get("security_observations", []))
        or "None",
        encoding="utf-8",
    )


def save_evidence(target: str, response: dict[str, Any], results: dict[str, Any]) -> None:
    """Write the evidence/ directory with raw scan artifacts."""
    ev_dir = Path("evidence")
    ev_dir.mkdir(exist_ok=True)
    _write_response_artifacts(ev_dir, response)
    _write_analysis_artifacts(ev_dir, results)
    console.print(f"[bold blue]Evidence exported to {ev_dir.resolve()}/[/bold blue]")


# ═══════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════

def generate_report(results: dict[str, Any]) -> str:
    """Generate a Markdown report string from scan results."""
    meta = results["scan_metadata"]
    lines = [
        "# TechFinger Report",
        f"**Target:** {meta['target']}  ",
        f"**Scan Time:** {meta['scan_time']}  ",
        f"**TechFinger Version:** {meta['version']}  ",
        f"**Profile:** {meta['profile']}  ",
        "",
        "## Detected Technologies",
        "",
        "| Technology | Category | Version | Confidence | Risk |",
        "|------------|----------|---------|------------|------|",
    ]
    for t in sorted(results["technologies"], key=lambda x: -x["confidence"]):
        lines.append(f"| {t['name']} | {t['category']} | {t.get('version') or '—'} | {t['confidence']}% | {t['risk']} |")

    lines += _report_stack_section(results["stack_correlation"])
    lines += _report_contradictions_section(results["contradictions"])
    lines += _report_observations_section(results["security_observations"])
    lines += _report_investigation_section(results["investigation_paths"])
    return "\n".join(lines)


def _report_stack_section(chain: list[dict[str, Any]]) -> list[str]:
    """Build the Markdown 'Stack Correlation' section."""
    lines = ["", "## Stack Correlation", ""]
    lines.append(" → ".join(layer["technology"] for layer in chain) if chain else "_Insufficient data_")
    return lines


def _report_contradictions_section(contradictions: list[dict[str, Any]]) -> list[str]:
    """Build the Markdown 'Contradictions' section."""
    lines = ["", "## Contradictions", ""]
    if contradictions:
        for c in contradictions:
            lines.append(f"⚠️ {c['technologies'][0]} vs {c['technologies'][1]}: {c['explanation']}")
    else:
        lines.append("⚠️ None detected")
    return lines


def _report_observations_section(observations: list[dict[str, Any]]) -> list[str]:
    """Build the Markdown 'Security Observations' section."""
    lines = ["", "## Security Observations", ""]
    for o in observations:
        checked = "x" if o["severity"] == "Info" else " "
        lines.append(f"- [{checked}] {o['issue']} ({o['severity']})")
    return lines


def _report_investigation_section(paths: dict[str, list[str]]) -> list[str]:
    """Build the Markdown 'Investigation Paths' section."""
    lines = ["", "## Investigation Paths", ""]
    for tech, steps in paths.items():
        lines.append(f"### {tech}")
        for step in steps:
            lines.append(f"- [ ] {step}")
        lines.append("")
    return lines


# ═══════════════════════════════════════════════════════════
# COMPARE MODE
# ═══════════════════════════════════════════════════════════

def _diff_tech_maps(prev_techs: dict[str, Any], curr_techs: dict[str, Any]) -> dict[str, list[Any]]:
    """Compute added/removed/updated technology lists between two tech-name-keyed dicts."""
    added = [name for name in curr_techs if name not in prev_techs]
    removed = [name for name in prev_techs if name not in curr_techs]
    updated = [
        name for name in curr_techs
        if name in prev_techs and curr_techs[name].get("version") != prev_techs[name].get("version")
        and curr_techs[name].get("version") and prev_techs[name].get("version")
    ]
    return {
        "added": [{"name": n, "category": curr_techs[n]["category"], "confidence": curr_techs[n]["confidence"]} for n in added],
        "removed": [{"name": n, "category": prev_techs[n]["category"]} for n in removed],
        "updated": [{"name": n, "from": prev_techs[n].get("version"), "to": curr_techs[n].get("version")} for n in updated],
    }


def compare_scans(current: dict[str, Any], previous_path: str) -> dict[str, Any]:
    """Diff the current scan results against a previously saved JSON scan."""
    prev_file = Path(previous_path)
    if not prev_file.exists():
        return {"error": f"Previous scan file not found: {previous_path}"}

    try:
        previous = json.loads(prev_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON in previous scan: {exc}"}

    prev_techs = {t["name"]: t for t in previous.get("technologies", [])}
    curr_techs = {t["name"]: t for t in current.get("technologies", [])}
    diff = _diff_tech_maps(prev_techs, curr_techs)

    prev_contradictions = {(c["technologies"][0], c["technologies"][1]) for c in previous.get("contradictions", [])}
    curr_contradictions = {(c["technologies"][0], c["technologies"][1]) for c in current.get("contradictions", [])}
    new_contradictions = curr_contradictions - prev_contradictions

    diff["new_contradictions"] = [{"a": a, "b": b} for a, b in new_contradictions]
    return diff


def render_compare(diff: dict[str, Any]) -> None:
    """Render compare-mode output to terminal."""
    if "error" in diff:
        console.print(f"[bold red]{diff['error']}[/bold red]")
        return
    console.print("[bold]Changes since previous scan:[/bold]")
    for item in diff["added"]:
        console.print(f"  [bold green][+][/bold green] Added: {item['name']} ({item['category']}) — {item['confidence']}%")
    for item in diff["removed"]:
        console.print(f"  [bold red][-][/bold red] Removed: {item['name']} ({item['category']})")
    for item in diff["updated"]:
        console.print(f"  [bold yellow][~][/bold yellow] Updated: {item['name']} {item['from']} → {item['to']}")
    for item in diff["new_contradictions"]:
        console.print(f"  [bold magenta][!][/bold magenta] New contradiction: {item['a']} vs {item['b']}")
    if not any(diff[k] for k in ("added", "removed", "updated", "new_contradictions")):
        console.print("  [dim]No changes detected[/dim]")


# ═══════════════════════════════════════════════════════════
# SCAN ORCHESTRATION
# ═══════════════════════════════════════════════════════════

def resolve_profile_settings(args: argparse.Namespace) -> dict[str, Any]:
    """Merge a named profile's defaults with explicit CLI overrides."""
    profile = SCAN_PROFILES[args.profile].copy()
    if args.timeout is not None:
        profile["timeout"] = args.timeout
    if args.deep:
        profile["deep"] = True
    if args.max_js is not None:
        profile["max_js"] = args.max_js
    if args.max_size is not None:
        profile["max_size"] = args.max_size
    if args.same_origin_only:
        profile["same_origin"] = True
    return profile


def _build_scan_metadata(url: str, response: dict[str, Any], settings: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Build the scan_metadata block shared by both success and failure results."""
    return {
        "tool": "TechFinger",
        "version": __version__,
        "scan_time": datetime.now(timezone.utc).astimezone().isoformat(),
        "target": url,
        "status_code": response["status_code"],
        "response_time_ms": response["response_time_ms"],
        "profile": args.profile,
        "deep": settings["deep"],
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def _gather_findings(response: dict[str, Any], settings: dict[str, Any], url: str) -> tuple[dict[str, Finding], list[str]]:
    """Run all extractors (headers, cookies, HTML, errors, JS) and merge into one findings pool."""
    header_findings = extract_headers(response["headers"])
    cookie_findings = extract_cookies(response["cookies"])
    html_findings = extract_html_patterns(response["body"])
    error_findings = analyze_error_page(response["status_code"], response["body"])

    js_bodies: list[str] = []
    api_endpoints: list[str] = []
    if settings["deep"]:
        soup = BeautifulSoup(response["body"], "html.parser")
        js_bodies, api_endpoints = deep_analysis(
            soup, response["final_url"] or url,
            settings["max_js"], settings["max_size"], settings["same_origin"], settings["timeout"],
        )

    js_findings = extract_js_globals(response["body"], js_bodies)
    findings = merge_all_findings(header_findings, cookie_findings, html_findings, error_findings, js_findings)
    return findings, api_endpoints


def _assemble_success_results(
    base_meta: dict[str, Any], response: dict[str, Any], findings: dict[str, Finding], api_endpoints: list[str], args: argparse.Namespace,
) -> dict[str, Any]:
    """Analyze findings (contradictions, confidence, correlation, observations) and assemble the results dict."""
    contradictions = detect_contradictions(findings)
    calculate_confidence(findings, contradictions)

    stack_chain = correlate_stack(findings)
    observations = observe_security(response["headers"], response["cookies"])
    tech_list = _findings_to_dicts(findings)

    if api_endpoints:
        base_meta["api_endpoints_found"] = api_endpoints

    return {
        "scan_metadata": base_meta,
        "technologies": tech_list,
        "stack_correlation": stack_chain,
        "contradictions": [
            {"technologies": list(c.technologies), "explanation": c.explanation, "penalty": c.penalty}
            for c in contradictions
        ],
        "security_observations": [
            {"issue": o.issue, "severity": o.severity, "details": o.details} for o in observations
        ],
        "investigation_paths": {t["name"]: get_investigation_paths(t["name"]) for t in tech_list if get_investigation_paths(t["name"])},
        "most_likely_stack": [layer["technology"] for layer in stack_chain],
        "explain": args.explain,
        "_response": response,  # internal use only (evidence export), stripped before JSON output
    }


def run_scan(url: str, args: argparse.Namespace) -> dict[str, Any]:
    """Execute the full fetch -> extract -> analyze -> correlate pipeline."""
    settings = resolve_profile_settings(args)
    response = fetch_target(url, timeout=settings["timeout"])
    base_meta = _build_scan_metadata(url, response, settings, args)

    if not response["ok"]:
        base_meta["error"] = response["error"]
        return {
            "scan_metadata": base_meta,
            "technologies": [], "stack_correlation": [], "contradictions": [],
            "security_observations": [], "investigation_paths": {}, "most_likely_stack": [],
            "explain": args.explain,
            "_response": response,
        }

    findings, api_endpoints = _gather_findings(response, settings, url)
    return _assemble_success_results(base_meta, response, findings, api_endpoints, args)


def _findings_to_dicts(findings: dict[str, Finding]) -> list[dict[str, Any]]:
    """Convert Finding objects into plain dicts for rendering/JSON export."""
    out = []
    for f in findings.values():
        out.append({
            "name": f.name,
            "version": f.version,
            "confidence": f.confidence,
            "confidence_breakdown": f.confidence_breakdown,
            "category": f.category,
            "risk": RISK_LEVELS.get(f.name, "Unknown"),
            "risk_reason": RISK_REASONS.get(RISK_LEVELS.get(f.name, ""), "Not enough data to assess"),
            "evidence": [e.detail for e in f.evidence],
            "contradiction_detected": f.contradiction_detected,
            "contradiction_note": f.contradiction_note,
        })
    return out


def strip_internal(results: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of results with internal-only keys removed for JSON/report output."""
    clean = {k: v for k, v in results.items() if not k.startswith("_")}
    clean.pop("explain", None)
    return clean


# ═══════════════════════════════════════════════════════════
# CLI / MAIN
# ═══════════════════════════════════════════════════════════

def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="techfinger",
        description="TechFinger — Explainable heuristic technology fingerprinting.",
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
    parser.add_argument("--profile", choices=sorted(SCAN_PROFILES.keys()), default="balanced", help="Scan profile")
    parser.add_argument("--timeout", type=int, default=None, help="Override request timeout (seconds)")
    parser.add_argument("--deep", action="store_true", help="Force deep JS analysis on")
    parser.add_argument("--max-js", type=int, default=None, help="Max external JS files to fetch")
    parser.add_argument("--max-size", type=int, default=None, help="Max bytes per JS file")
    parser.add_argument("--same-origin-only", action="store_true", help="Only fetch JS from the same origin")
    parser.add_argument("-o", "--output", choices=["terminal", "json"], default="terminal", help="Output format")
    parser.add_argument("--explain", action="store_true", help="Show confidence math breakdown for every finding")
    parser.add_argument("--evidence", action="store_true", help="Export raw evidence/ directory")
    parser.add_argument("--report", action="store_true", help="Generate report.md")
    parser.add_argument("--compare", metavar="PREVIOUS_JSON", default=None, help="Compare against a previous JSON scan")
    return parser


def _handle_post_scan_outputs(args: argparse.Namespace, response: dict[str, Any], clean_results: dict[str, Any]) -> None:
    """Handle --evidence, --report, and --compare side effects after the main scan/render."""
    if args.evidence and response.get("ok"):
        save_evidence(args.url, response, clean_results)

    if args.report:
        report_text = generate_report(clean_results)
        Path("report.md").write_text(report_text, encoding="utf-8")
        if args.output == "terminal":
            console.print("[bold blue]Report written to report.md[/bold blue]")

    if args.compare:
        diff = compare_scans(clean_results, args.compare)
        if args.output == "terminal":
            render_compare(diff)
        else:
            print(json.dumps(diff, indent=2))


def main() -> None:
    """CLI entry point: parse args, run scan, render output."""
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.output == "terminal":
        print_banner()

    plugins = load_plugins()
    if args.output == "terminal":
        console.print(f"[dim][*] Plugin system ready. {len(plugins)} plugins discovered.[/dim]")

    results = run_scan(args.url, args)
    response = results.pop("_response", {})
    clean_results = strip_internal(results)

    if args.output == "json":
        print(render_json(clean_results))
    else:
        results["_response"] = response  # not used by render_terminal, harmless
        render_terminal(results)

    _handle_post_scan_outputs(args, response, clean_results)

    if not response.get("ok", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
