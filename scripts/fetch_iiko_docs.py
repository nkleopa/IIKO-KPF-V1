#!/usr/bin/env python3
"""
Bulk extractor for iiko documentation via ClickHelp helper API.

Fetches all iikoServer API articles, strips HTML to text,
and produces:
  - /docs/iiko_api_raw/{slug}.html  (raw HTML per article)
  - /docs/iiko_api_raw/{slug}.txt   (stripped text per article)
  - /docs/iiko_api_db.json          (structured index)
  - IIKO_MASTER_REFERENCE.md        (single searchable document)
"""

import html
import json
import os
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# ---------- configuration ----------

PROJECT = "api-documentations"
BASE_URL = "https://ru.iiko.help"
HELPER_URL = f"{BASE_URL}/helper/articles/{PROJECT}"

# All slugs in the iikoServer API section (discovered from sidebar navigation)
ARTICLE_SLUGS = [
    # Core
    "iikoserver-api",
    "ogranicheniya-i-rekomendatsii",
    "printsipy-raboty",
    "avtorizatsiya",
    "opisanie-oshibok",
    # Nomenclature
    "elementy-nomenklatury",
    "nomenklaturnye-gruppy",
    "polzovatelskie-kategorii",
    "tekhnologicheskie-karty",
    "rabota-s-izobrazheniyami",
    "rabota-so-shkaloy-i-razmerami",
    # Documents
    "zagruzka-i-redaktirovanie-prikhodnoy-nakladnoy",
    "rasprovedenie-prikhodnoy-i-raskhodnoy-nakladnoy",
    "vygruzka-prikhodnykh-nakladnykh",
    "vygruzka-prikhodnoy-nakladnoy-po-ee-nomeru",
    "zagruzka-i-redaktirovanie-raskhodnoy-nakladnoy",
    "vygruzka-raskhodnykh-nakladnykh",
    "vygruzka-raskhodnoy-nakladnoy-po-ee-nomeru",
    "zagruzka-akta-prigotovleniya",
    "zagruzka-akta-realizatsii",
    "zagruzka-vozvratnoy-nakladnoy",
    "zagruzka-inventarizatsii",
    "akty-spisaniya",
    "vnutrennie-peremescheniya",
    # Cash register sessions
    "kassovye-smeny-v2",
    "rabota-s-izyatiyami",
    # Corporation
    "korporatsii",
    "statusy-replikatsii",
    "sobytiya",
    # OLAP Reports
    "formirovanie-olap-otcheta-v-api",
    "olap-otchety-v1",
    "otchety-dostavka-v1",
    "otchety-v1",
    "olap-otchety-v2",
    "otchety-vv2",
    "primery-vyzova-olap-otchet-v2",
    "prednastroennye-olap-otchety-vv2",
    # Suppliers
    "rabota-s-postavschikami",
    # Employees
    "rabota-s-dannymi-sotrudnikovv",
    "rabota-s-dannymi-dolzhnostey",
    "rabota-s-dannymi-oklada",
    "rabota-s-dannymi-smeny-i-raspisaniy",
    "rabota-s-dannymi-yavok",
    "rabota-s-dannymi-brigad",
    # EDI
    "api-edi-5-0",
    "api-edi-5-1-6-4",
    # Other
    "kody-bazovykh-tipov",
    "spravochniki",
    "prikazy",
    "tseny-zadannye-prikazami",
    "tsenovye-kategorii",
    "periody-deystviya",
    "scheta",
    "rabota-s-bystrym-menyu",
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "iiko_api_raw"
MASTER_REF = Path(__file__).resolve().parent.parent / "IIKO_MASTER_REFERENCE.md"
DB_FILE = OUTPUT_DIR / "iiko_api_db.json"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (iiko-kpf-scraper/1.0)",
    "Referer": f"{BASE_URL}/articles/",
    "Accept": "application/json",
}


# ---------- HTML-to-text converter ----------

class HTMLToText(HTMLParser):
    """Simple HTML tag stripper that preserves structure."""

    def __init__(self):
        super().__init__()
        self._pieces: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self._skip = True
        if tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self._pieces.append("\n")
        if tag == "td":
            self._pieces.append("\t")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self._skip = False
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._pieces.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._pieces.append(data)

    def get_text(self) -> str:
        raw = "".join(self._pieces)
        # Collapse blank lines
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def html_to_text(html_str: str) -> str:
    parser = HTMLToText()
    parser.feed(html_str)
    return parser.get_text()


# ---------- fetcher ----------

def fetch_article(slug: str) -> dict | None:
    """Fetch a single article from the ClickHelp helper API."""
    url = f"{HELPER_URL}/{slug}/"
    payload = json.dumps({
        "curUrl": f"{BASE_URL}/articles/#!{PROJECT}/{slug}",
        "articleChangedFromTabName": None,
        "articleChangedRefEntityId": None,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8-sig"))
        return data
    except Exception as e:
        print(f"  ERROR fetching {slug}: {e}", file=sys.stderr)
        return None


# ---------- main ----------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    db: list[dict] = []
    md_parts: list[str] = [
        "# iiko Server API — Master Reference\n",
        "> Auto-generated from ru.iiko.help via ClickHelp API.\n",
        f"> Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n",
    ]

    total = len(ARTICLE_SLUGS)
    success = 0
    failed = 0

    for i, slug in enumerate(ARTICLE_SLUGS, 1):
        print(f"[{i}/{total}] Fetching: {slug} ...", end=" ", flush=True)
        data = fetch_article(slug)

        if data is None:
            failed += 1
            print("FAILED")
            continue

        raw_html = data.get("viewFrameHtml", "") or ""
        text = html_to_text(raw_html)
        title = (data.get("title") or slug).strip()

        # Save raw HTML
        html_path = OUTPUT_DIR / f"{slug}.html"
        html_path.write_text(raw_html, encoding="utf-8")

        # Save stripped text
        txt_path = OUTPUT_DIR / f"{slug}.txt"
        txt_path.write_text(text, encoding="utf-8")

        # Build DB entry
        entry = {
            "slug": slug,
            "internalId": data.get("internalId"),
            "title": title,
            "project": data.get("projectExternalId"),
            "timeToRead": data.get("timeToRead"),
            "htmlLength": len(raw_html),
            "textLength": len(text),
            "url": f"{BASE_URL}/articles/#!{PROJECT}/{slug}",
        }
        db.append(entry)

        # Add to master reference markdown
        md_parts.append(f"\n## {title}\n")
        md_parts.append(f"*Source: [{slug}]({entry['url']})*\n\n")
        md_parts.append(text)
        md_parts.append("\n\n---\n")

        success += 1
        print(f"OK ({len(text)} chars)")

        # Rate-limit: be polite to the server
        time.sleep(0.5)

    # Save DB
    DB_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDB saved to {DB_FILE}")

    # Save master reference
    MASTER_REF.write_text("\n".join(md_parts), encoding="utf-8")
    print(f"Master reference saved to {MASTER_REF}")

    print(f"\nDone: {success} OK, {failed} failed out of {total} articles.")


if __name__ == "__main__":
    main()
