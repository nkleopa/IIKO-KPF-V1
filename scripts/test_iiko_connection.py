#!/usr/bin/env python3
"""
iiko Server API — Connection Diagnostic Script
Tests: DNS → HTTPS → Auth (query params & form body) → Data endpoints
"""

import hashlib
import json
import socket
import ssl
import sys
import urllib.request
import urllib.error
import urllib.parse
from xml.etree import ElementTree as ET

# ─── Configuration ──────────────────────────────────────────────
SERVERS = {
    "production": {
        "host": "starikhinkalich-co.iiko.it",
        "login": "nkleopa",
        "password": "gazrok-3Qumfu-ceztex",
    },
    "demo": {
        "host": "571-709-897.iiko.it",
        "login": "user",
        "password": "user#test",
    },
}

TIMEOUT = 15  # seconds


# ─── Helpers ────────────────────────────────────────────────────
def sha1_hash(password: str) -> str:
    """SHA1 of password (this server does NOT use the 'resto#' prefix)."""
    return hashlib.sha1(password.encode("utf-8")).hexdigest()


def log(label: str, msg: str, ok: bool | None = None):
    icon = {True: "✓", False: "✗", None: "→"}[ok]
    print(f"  [{icon}] {label}: {msg}")


def http_request(url: str, method: str = "GET", data: bytes | None = None,
                 headers: dict | None = None) -> tuple[int, str, dict]:
    """Returns (status_code, body, response_headers)."""
    req = urllib.request.Request(url, data=data, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            resp_headers = dict(resp.headers)
            return resp.status, body, resp_headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body, dict(e.headers) if e.headers else {}
    except urllib.error.URLError as e:
        return 0, str(e.reason), {}


# ─── Phase 1: DNS ──────────────────────────────────────────────
def test_dns(host: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  Phase 1: DNS Resolution — {host}")
    print(f"{'='*60}")
    try:
        ips = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        unique_ips = {addr[4][0] for addr in ips}
        for ip in sorted(unique_ips):
            log("DNS", f"{host} → {ip}", True)
        return True
    except socket.gaierror as e:
        log("DNS", f"FAILED — {e}", False)
        return False


# ─── Phase 2: HTTPS ────────────────────────────────────────────
def test_https(host: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  Phase 2: HTTPS Connectivity — {host}")
    print(f"{'='*60}")

    base = f"https://{host}"

    # Test 1: Root page
    status, body, hdrs = http_request(f"{base}/")
    if status > 0:
        log("HTTPS root", f"HTTP {status} — Content-Type: {hdrs.get('Content-Type', '?')}", status < 500)
    else:
        log("HTTPS root", f"Connection failed: {body}", False)
        return False

    # Test 2: API root (may return 401 or a welcome page)
    status, body, hdrs = http_request(f"{base}/resto/api/")
    if status > 0:
        log("API root", f"HTTP {status} — Body preview: {body[:120].strip()!r}", True)
    else:
        log("API root", f"Connection failed: {body}", False)

    # Test 3: Licence info (no auth needed for some servers)
    status, body, hdrs = http_request(f"{base}/resto/api/licence/info")
    if status > 0:
        log("Licence info", f"HTTP {status} — {body[:200].strip()!r}", status == 200)
    else:
        log("Licence info", f"Not reachable: {body}", None)

    return True


# ─── Phase 3: Authentication ───────────────────────────────────
def test_auth(host: str, login: str, password: str) -> str | None:
    print(f"\n{'='*60}")
    print(f"  Phase 3: Authentication — {login}@{host}")
    print(f"{'='*60}")

    base = f"https://{host}"
    pass_hash = sha1_hash(password)
    log("Hash", f"SHA1('{password}') = {pass_hash}", None)

    token = None

    # Method A: Query parameters (as documented)
    print("\n  --- Method A: Query parameters ---")
    auth_url = f"{base}/resto/api/auth?login={urllib.parse.quote(login)}&pass={pass_hash}"
    status, body, hdrs = http_request(auth_url, method="POST")
    log("Auth (query params)", f"HTTP {status}", status == 200)
    if status == 200:
        token = body.strip().strip('"')
        log("Token", f"{token[:20]}...", True)
    else:
        log("Response", f"{body[:300].strip()!r}", False)

    # Method B: Form-encoded body (alternative)
    if not token:
        print("\n  --- Method B: Form-encoded body ---")
        form_data = urllib.parse.urlencode({"login": login, "pass": pass_hash}).encode()
        status, body, hdrs = http_request(
            f"{base}/resto/api/auth",
            method="POST",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        log("Auth (form body)", f"HTTP {status}", status == 200)
        if status == 200:
            token = body.strip().strip('"')
            log("Token", f"{token[:20]}...", True)
        else:
            log("Response", f"{body[:300].strip()!r}", False)

    # Method C: GET with query params (some older servers accept GET)
    if not token:
        print("\n  --- Method C: GET with query parameters ---")
        status, body, hdrs = http_request(auth_url, method="GET")
        log("Auth (GET)", f"HTTP {status}", status == 200)
        if status == 200:
            token = body.strip().strip('"')
            log("Token", f"{token[:20]}...", True)
        else:
            log("Response", f"{body[:300].strip()!r}", False)

    if not token:
        log("AUTH", "ALL METHODS FAILED", False)
    return token


# ─── Phase 4: Data Retrieval ───────────────────────────────────
def test_data_endpoints(host: str, token: str):
    print(f"\n{'='*60}")
    print(f"  Phase 4: Data Retrieval")
    print(f"{'='*60}")

    base = f"https://{host}"

    # 4a. Corporation departments (XML)
    print("\n  --- 4a. Corporation Departments ---")
    url = f"{base}/resto/api/corporation/departments?key={token}"
    status, body, hdrs = http_request(url)
    if status == 200:
        log("Departments", f"HTTP {status}, {len(body)} bytes", True)
        try:
            root = ET.fromstring(body)
            items = root.findall(".//corporateItemDto")
            for item in items[:10]:
                name = item.findtext("name", "?")
                dtype = item.findtext("type", "?")
                iid = item.findtext("id", "?")
                print(f"      • [{dtype}] {name} (id: {iid[:12]}...)")
            if len(items) > 10:
                print(f"      ... and {len(items) - 10} more")
        except ET.ParseError as e:
            log("XML Parse", f"Failed: {e}. Raw: {body[:200]!r}", False)
    else:
        log("Departments", f"HTTP {status} — {body[:200].strip()!r}", False)

    # 4b. Entity list: OrderType (JSON, v2)
    print("\n  --- 4b. OrderType Entities (v2) ---")
    url = f"{base}/resto/api/v2/entities/list?rootType=OrderType&key={token}&includeDeleted=false"
    status, body, hdrs = http_request(url)
    if status == 200:
        log("OrderTypes", f"HTTP {status}", True)
        try:
            items = json.loads(body)
            for item in items:
                svc = item.get("orderServiceType", "?")
                print(f"      • {item['name']} (id: {item['id'][:12]}..., service: {svc})")
        except json.JSONDecodeError as e:
            log("JSON Parse", f"Failed: {e}. Raw: {body[:200]!r}", False)
    else:
        log("OrderTypes", f"HTTP {status} — {body[:200].strip()!r}", False)

    # 4c. OLAP columns (v2, SALES)
    print("\n  --- 4c. OLAP Columns (SALES) ---")
    url = f"{base}/resto/api/v2/reports/olap/columns?reportType=SALES&key={token}"
    status, body, hdrs = http_request(url)
    if status == 200:
        log("OLAP Columns", f"HTTP {status}", True)
        try:
            cols = json.loads(body)
            col_names = [c.get("name", c.get("id", "?")) for c in cols] if isinstance(cols, list) else list(cols.keys()) if isinstance(cols, dict) else []
            print(f"      Available: {len(col_names)} columns")
            # Show key columns we need
            key_cols = ["OpenDate.Typed", "OrderType", "DishName", "DishSumInt", "DishAmountInt",
                        "UniqOrderId", "GuestNum", "DeletedWithWriteoff", "OrderDeleted"]
            for kc in key_cols:
                found = kc in str(cols)
                log(f"  {kc}", "present" if found else "NOT FOUND", found)
        except json.JSONDecodeError as e:
            log("JSON Parse", f"Failed: {e}. Raw: {body[:200]!r}", False)
    else:
        log("OLAP Columns", f"HTTP {status} — {body[:200].strip()!r}", False)


# ─── Phase 5: Logout ───────────────────────────────────────────
def logout(host: str, token: str):
    print(f"\n{'='*60}")
    print(f"  Phase 5: Logout (release license)")
    print(f"{'='*60}")
    base = f"https://{host}"

    # Try form-encoded POST body first (matches auth behavior)
    form_data = urllib.parse.urlencode({"key": token}).encode()
    status, body, _ = http_request(
        f"{base}/resto/api/logout",
        method="POST",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if status == 200:
        log("Logout (form body)", f"HTTP {status}", True)
        return

    # Fallback: GET with query param
    status, body, _ = http_request(f"{base}/resto/api/logout?key={token}", method="GET")
    log("Logout (GET)", f"HTTP {status}", status == 200)


# ─── Main ───────────────────────────────────────────────────────
def run_diagnostics(server_name: str):
    cfg = SERVERS[server_name]
    host, login, password = cfg["host"], cfg["login"], cfg["password"]

    print(f"\n{'#'*60}")
    print(f"  iiko API Diagnostics — {server_name.upper()}")
    print(f"  Host: {host}")
    print(f"  Login: {login}")
    print(f"{'#'*60}")

    if not test_dns(host):
        print("\n  ⛔ DNS failed. Cannot continue.")
        return

    if not test_https(host):
        print("\n  ⛔ HTTPS failed. Cannot continue.")
        return

    token = test_auth(host, login, password)
    if not token:
        print("\n  ⛔ Authentication failed. Cannot retrieve data.")
        return

    try:
        test_data_endpoints(host, token)
    finally:
        logout(host, token)

    print(f"\n{'#'*60}")
    print(f"  DIAGNOSTICS COMPLETE — {server_name.upper()}")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["production"]
    for target in targets:
        if target not in SERVERS:
            print(f"Unknown server: {target}. Available: {', '.join(SERVERS)}")
            continue
        run_diagnostics(target)
