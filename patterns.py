"""Embedded detection rules for TechFinger — NO external signature database.

This file contains ONLY constants: regex patterns, weights, risk levels, and
mappings used by techfinger.py. No logic lives here beyond simple literal
data structures, so it stays trivially auditable and easy to extend.
"""

import re

__version__ = "0.1.0"

# ═══════════════════════════════════════════════════════════
# SECTION 1: HEADER PATTERNS
# Maps HTTP header name -> {regex: (technology, category)}
# ═══════════════════════════════════════════════════════════
HEADER_PATTERNS: dict[str, dict[str, tuple[str, str]]] = {
    "X-Powered-By": {
        r"PHP[/\s]?([\d.]+)?": ("PHP", "Language/Runtime"),
        r"ASP\.NET": ("ASP.NET", "Framework"),
        r"Express": ("Express.js", "Framework"),
    },
    "X-AspNet-Version": {
        r"([\d.]+)": ("ASP.NET", "Framework"),
    },
    "Server": {
        r"nginx[/\s]?([\d.]+)?": ("Nginx", "Web Server"),
        r"Apache[/\s]?([\d.]+)?": ("Apache", "Web Server"),
        r"Microsoft-IIS[/\s]?([\d.]+)?": ("IIS", "Web Server"),
        r"cloudflare": ("Cloudflare", "CDN/WAF"),
        r"Caddy": ("Caddy", "Web Server"),
    },
    "X-Generator": {
        r"Drupal\s*([\d.]+)?": ("Drupal", "CMS"),
        r"WordPress\s*([\d.]+)?": ("WordPress", "CMS"),
        r"Joomla": ("Joomla", "CMS"),
        r"Ghost": ("Ghost", "CMS"),
    },
    "X-Frame-Options": {
        r".*": ("Modern Framework", "Framework"),
    },
    "X-Request-ID": {
        r".*": ("Reverse Proxy / Load Balancer", "Infrastructure"),
    },
    "X-AspNetMvc-Version": {
        r"([\d.]+)": ("ASP.NET MVC", "Framework"),
    },
    "X-Drupal-Cache": {
        r".*": ("Drupal", "CMS"),
    },
}

# ═══════════════════════════════════════════════════════════
# SECTION 2: COOKIE PATTERNS
# Maps cookie name -> (technology, category)
# ═══════════════════════════════════════════════════════════
COOKIE_PATTERNS: dict[str, tuple[str, str]] = {
    "sessionid": ("Django", "Framework"),
    "PHPSESSID": ("PHP", "Language/Runtime"),
    "ASP.NET_SessionId": ("ASP.NET", "Framework"),
    "connect.sid": ("Express.js", "Framework"),
    "laravel_session": ("Laravel", "Framework"),
    "rack.session": ("Ruby/Rack", "Framework"),
    "auth_token": ("JWT/Custom Auth", "Authentication"),
    "jwt": ("JWT", "Authentication"),
    "csrfmiddlewaretoken": ("Django", "Framework"),
    "XSRF-TOKEN": ("Laravel/Angular", "Framework"),
    "__cfduid": ("Cloudflare", "CDN/WAF"),
    "_cf_bm": ("Cloudflare", "CDN/WAF"),
    "wp-settings": ("WordPress", "CMS"),
    "wp-settings-time": ("WordPress", "CMS"),
    "_ga": ("Google Analytics", "Analytics"),
    "_gid": ("Google Analytics", "Analytics"),
    "_gat": ("Google Analytics", "Analytics"),
}

# ═══════════════════════════════════════════════════════════
# SECTION 3: HTML DOM PATTERNS
# Maps technology -> [(regex, weight), ...]
# ═══════════════════════════════════════════════════════════
HTML_PATTERNS: dict[str, list[tuple[str, int]]] = {
    "React": [
        (r'<div[^>]*id=["\']root["\']', 50),
        (r'data-reactroot', 60),
        (r'data-reactid', 50),
        (r'react-refresh', 40),
        (r'__REACT_', 50),
    ],
    "Vue.js": [
        (r'data-v-[a-f0-9]{8}', 70),
        (r'v-if|v-for|v-model', 60),
        (r'vue-router', 50),
    ],
    "Angular": [
        (r'ng-app|ng-controller|ng-model', 70),
        (r'\[ng\w+', 50),
        (r'_nghost', 60),
    ],
    "Bootstrap": [
        (r'class=["\'][^"\']*container[^"\']*["\']', 40),
        (r'class=["\'][^"\']*row[^"\']*["\']', 40),
        (r'class=["\'][^"\']*col-[\w-]+[^"\']*["\']', 40),
    ],
    "Tailwind CSS": [
        (r'class=["\'][^"\']*flex\s+', 40),
        (r'class=["\'][^"\']*grid\s+', 40),
        (r'class=["\'][^"\']*md:[\w-]+', 50),
        (r'class=["\'][^"\']*lg:[\w-]+', 50),
    ],
    "Next.js": [
        (r'<script[^>]*>window\.__NEXT_DATA__', 80),
        (r'__NEXT_LOADED_PAGES__', 70),
    ],
    "Nuxt.js": [
        (r'window\.__NUXT__', 80),
        (r'<div[^>]*id=["\']__nuxt["\']', 70),
    ],
    "jQuery": [
        (r'\$\s*\(document\)\.ready', 60),
        (r'jquery[\w/-]*\.js', 50),
    ],
    "Gatsby": [
        (r'___gatsby', 70),
    ],
    "Svelte": [
        (r'svelte-', 60),
    ],
}

# ═══════════════════════════════════════════════════════════
# SECTION 4: JAVASCRIPT GLOBAL PATTERNS
# Maps technology -> [regex, ...] searched in inline/external JS
# ═══════════════════════════════════════════════════════════
JS_GLOBALS: dict[str, list[str]] = {
    "React": [r"window\.React\b", r"window\.ReactDOM\b"],
    "Vue.js": [r"window\.Vue\b", r"window\.vue\b"],
    "Angular": [r"window\.angular\b"],
    "jQuery": [r"window\.jQuery\b", r"\$\s*\(", r"jQuery\s*\("],
    "Lodash": [r"window\._\b"],
    "Google Analytics 4": [r"window\.gtag\b"],
    "Google Analytics": [r"window\.ga\b"],
    "WordPress": [r"window\.wp\b"],
    "Next.js": [r"window\.__NEXT_DATA__"],
    "Nuxt.js": [r"window\.__NUXT__"],
    "Gatsby": [r"window\.__GATSBY"],
    "Svelte": [r"window\.__svelte"],
}

# ═══════════════════════════════════════════════════════════
# SECTION 5: ERROR PAGE PATTERNS
# Maps technology -> [regex, ...] searched in non-200 response bodies
# ═══════════════════════════════════════════════════════════
ERROR_PATTERNS: dict[str, list[str]] = {
    "Django": [r"Using the URLconf defined in", r"CSRF verification failed", r"Django", r"Traceback.*django"],
    "Flask": [r"Traceback \(most recent call last\)", r"Werkzeug"],
    "Laravel": [r"Whoops, looks like something went wrong", r"laravel", r"Ignition"],
    "ASP.NET": [r"ASP\.NET", r"Server Error in", r"__VIEWSTATE", r"Runtime Error"],
    "Spring Boot": [r"Whitelabel Error Page", r"spring", r"application\.json"],
    "Nginx": [r"nginx/[\d.]+", r"404 Not Found.*nginx"],
    "Apache": [r"Apache/[\d.]+", r"The requested URL was not found on this server"],
    "Express.js": [r"Cannot GET", r"Cannot POST", r"Error: .*at .*node_modules"],
    "Ruby on Rails": [r"Routing Error", r"Rails", r"ActiveRecord"],
}

# ═══════════════════════════════════════════════════════════
# SECTION 6: CONTRADICTION RULES
# (tech_group_a, tech_group_b, explanation, penalty)
# If any tech in group A AND any tech in group B are both detected,
# a contradiction is flagged and confidence for the involved techs
# is reduced by `penalty` points.
# ═══════════════════════════════════════════════════════════
CONTRADICTIONS: list[tuple[list[str], list[str], str, int]] = [
    (["Apache"], ["Nginx"], "Web server mismatch suggests reverse proxy", 15),
    (["PHP"], ["ASP.NET"], "Language mismatch", 20),
    (["Django"], ["Laravel"], "Framework mismatch", 20),
    (["React"], ["Vue.js"], "Frontend framework conflict", 10),
    (["Nginx"], ["IIS"], "Web server mismatch", 15),
    (["Apache"], ["Caddy"], "Web server mismatch", 15),
]

# ═══════════════════════════════════════════════════════════
# SECTION 7: STACK ORDER
# Defines the layer ordering used when correlating the likely stack.
# (category, layer_label)
# ═══════════════════════════════════════════════════════════
STACK_ORDER: list[tuple[str, str]] = [
    ("CDN/WAF", "Infrastructure"),
    ("Web Server", "Infrastructure"),
    ("Language/Runtime", "Backend"),
    ("Framework", "Backend"),
    ("CMS", "Backend"),
    ("Authentication", "Security"),
    ("Frontend Framework", "Frontend"),
    ("CSS Framework", "Frontend"),
    ("Analytics", "Frontend"),
]

# ═══════════════════════════════════════════════════════════
# SECTION 8: RISK LEVELS
# Maps technology -> qualitative risk level for pentest triage.
# ═══════════════════════════════════════════════════════════
RISK_LEVELS: dict[str, str] = {
    "PHP": "Medium",
    "Django": "Medium",
    "Express.js": "High",
    "ASP.NET": "Medium",
    "ASP.NET MVC": "Medium",
    "React": "Low",
    "Angular": "Low",
    "Vue.js": "Low",
    "Laravel": "High",
    "Laravel/Angular": "High",
    "WordPress": "High",
    "Nginx": "Low",
    "Apache": "Medium",
    "IIS": "Medium",
    "Caddy": "Low",
    "LiteSpeed": "Low",
    "Gunicorn": "Low",
    "Cloudflare": "Low",
    "Vercel": "Low",
    "Varnish Cache": "Low",
    "Drupal": "Medium",
    "Ruby on Rails": "Medium",
    "Ruby/Rack": "Medium",
    "Flask": "Medium",
    "Spring Boot": "Medium",
    "Joomla": "High",
    "Ghost": "Low",
    "jQuery": "Low",
    "Lodash": "Low",
    "Bootstrap": "Low",
    "Tailwind CSS": "Low",
    "Next.js": "Low",
    "Nuxt.js": "Low",
    "Gatsby": "Low",
    "Svelte": "Low",
    "Modern Framework": "Low",
    "Reverse Proxy / Load Balancer": "Low",
    "JWT": "Medium",
    "JWT/Custom Auth": "Medium",
    "Google Analytics": "Low",
    "Google Analytics 4": "Low",
}

# Human-readable justification shown alongside a risk level.
RISK_REASONS: dict[str, str] = {
    "High": "Large attack surface, known CVEs, common misconfigurations",
    "Medium": "Moderate attack surface, framework-specific issues",
    "Low": "Frontend/minimal direct attack surface",
}

# ═══════════════════════════════════════════════════════════
# SECTION 9: SUGGESTED INVESTIGATION PATHS
# Maps technology -> [suggested manual test, ...]
# ═══════════════════════════════════════════════════════════
INVESTIGATION_PATHS: dict[str, list[str]] = {
    "PHP": ["Check phpinfo.php exposure", "PHP serialization (unserialize)", "File upload bypass", "LFI/RFI"],
    "Django": ["Check /admin panel", "Django debug mode (/?debug)", "SQL injection patterns", "CSRF bypass"],
    "Express.js": ["Check exposed routes (/api, /routes)", "NoSQL injection", "JWT weaknesses", "npm audit"],
    "ASP.NET": ["Check ViewState deserialization", "ASP.NET debugging", "IIS shortname enumeration"],
    "React": ["Check source maps (*.js.map)", "Exposed API endpoints in JS bundles", "Hardcoded secrets in JS"],
    "Angular": ["Template injection", "Exposed API calls", "Environment.ts exposure"],
    "Laravel": ["Check .env file exposure", "Laravel debug mode", "Ignition RCE (CVE-2021-3129)", "Queue workers"],
    "WordPress": ["Check /wp-admin", "Plugin enumeration", "XML-RPC abuse", "wp-json API exposure"],
    "Nginx": ["Path traversal via alias misconfig", "Reverse proxy bypass"],
    "Cloudflare": ["Origin IP exposure", "Cloudflare bypass techniques"],
    "Drupal": ["Check /user/login", "Drupalgeddon-style RCE", "Module enumeration"],
    "Ruby on Rails": ["Check /rails/info/routes", "Mass assignment", "Secret token exposure"],
    "Flask": ["Werkzeug debugger RCE", "Jinja2 SSTI", "Secret key exposure"],
    "Spring Boot": ["Check /actuator endpoints", "Spring4Shell-style RCE", "Heap dump exposure"],
}

# ═══════════════════════════════════════════════════════════
# SECTION 10: EVIDENCE RELIABILITY WEIGHTS
# Maps evidence type -> (reliability_multiplier, base_score)
# Used by the confidence scoring engine.
# ═══════════════════════════════════════════════════════════
EVIDENCE_RELIABILITY: dict[str, tuple[float, int]] = {
    "header_version": (1.0, 100),   # Direct version in header
    "cookie": (0.9, 90),            # Official framework cookie
    "error_page": (0.85, 85),       # Error page match
    "html_multi": (0.75, 75),       # DOM pattern (multiple indicators)
    "js_global": (0.65, 65),        # JS global object
    "html_single": (0.5, 50),       # Single DOM indicator
    "header_generic": (0.4, 40),    # Generic header
    "behavioral": (0.25, 25),       # Behavioral guess
}

# ═══════════════════════════════════════════════════════════
# SECTION 11: SECURITY OBSERVATION CHECKS
# (observation_label, severity) — logic lives in techfinger.py,
# this just centralizes the label/severity pairing for consistency.
# ═══════════════════════════════════════════════════════════
SECURITY_CHECKS: dict[str, str] = {
    "csp_missing": "Medium",
    "hsts_missing": "Medium",
    "cookie_not_secure": "Low",
    "cookie_not_httponly": "Low",
    "server_version_leak": "Info",
    "x_powered_by_exposed": "Info",
    "no_x_frame_options": "Low",
    "no_x_content_type_options": "Low",
    "no_referrer_policy": "Info",
}

# ═══════════════════════════════════════════════════════════
# SECTION 12: SCAN PROFILES
# name -> (timeout_seconds, deep, max_js, max_size_bytes, same_origin_only)
# ═══════════════════════════════════════════════════════════
SCAN_PROFILES: dict[str, dict[str, object]] = {
    "fast": {"timeout": 5, "deep": False, "max_js": 0, "max_size": 0, "same_origin": False},
    "balanced": {"timeout": 10, "deep": True, "max_js": 3, "max_size": 300_000, "same_origin": False},
    "deep": {"timeout": 30, "deep": True, "max_js": 10, "max_size": 1_000_000, "same_origin": False},
}

# API endpoint markers searched for in fetched JS during deep analysis.
API_ENDPOINT_MARKERS: list[str] = [r"/api/", r"/v1/", r"/graphql", r"/wp-json/"]

# Compiled convenience: version-capturing group presence check.
VERSION_GROUP_RE = re.compile(r"\(([^)]*[\d.][^)]*)\)")
